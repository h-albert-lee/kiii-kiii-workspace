"""Count, budget, resume and score frozen extraction plans. Explicit --execute for inference."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import importlib.metadata
import json
import math
import os
from pathlib import Path
import subprocess

from .protocol import sha
from .providers import Provider, endpoint
from .run import load_plan, read_jsonl, unique, score, write_json


def digest(value):
    return sha(json.dumps(value, sort_keys=True, ensure_ascii=False))


def load_config(path):
    c = json.loads(Path(path).read_text())
    allowed_fields = {'model','model_revision','tokenizer_revision','operator','run_id','price_date','provider','input_limit','output_limit','total_limit','input_usd_per_million','output_usd_per_million','budget_usd','settings_frozen','generation','tokenize_options','tokenize_url','concurrency','base_url','base_url_env','api_key_env','allow_private_http','timeout_seconds'}
    if set(c) - allowed_fields:
        raise ValueError('unknown config fields; credentials belong only in environment variables')
    for k in ('model', 'model_revision', 'tokenizer_revision', 'operator', 'run_id', 'price_date'):
        if not isinstance(c.get(k), str) or not c[k] or 'REPLACE' in c[k]:
            raise ValueError(f'fill config field: {k}')
    if c.get('provider') not in {'anthropic', 'gemini', 'openai_compatible'}:
        raise ValueError('unknown provider')
    for k in ('input_limit', 'output_limit', 'total_limit'):
        if type(c.get(k)) is not int or c[k] < 1:
            raise ValueError(f'verify config field: {k}')
    for k in ('input_usd_per_million', 'output_usd_per_million', 'budget_usd'):
        if type(c.get(k)) not in (int, float) or not math.isfinite(c[k]) or c[k] < 0:
            raise ValueError(f'fill nonnegative config field: {k}')
    if c.get('settings_frozen') is not True:
        raise ValueError('calibrate on separate pilot, then set settings_frozen=true')
    generation = c.get('generation', {})
    allowed = {'anthropic': {'temperature', 'top_p', 'thinking'},
               'gemini': {'temperature', 'topP', 'thinkingConfig', 'responseMimeType'},
               'openai_compatible': {'temperature', 'top_p', 'seed', 'chat_template_kwargs', 'reasoning_effort'}}[c['provider']]
    if set(generation) - allowed:
        raise ValueError('unsupported generation keys; cannot override model/messages/output cap')
    if set(c.get('tokenize_options', {})) - {'chat_template_kwargs'}:
        raise ValueError('unsupported tokenize options')
    if c['provider'] == 'openai_compatible' and generation.get('chat_template_kwargs', {}) != c.get('tokenize_options', {}).get('chat_template_kwargs', {}):
        raise ValueError('generation and counting chat-template kwargs must match')
    if c.get('tokenize_url'):
        from urllib.parse import urlparse
        target = urlparse(endpoint({'base_url':c['tokenize_url'], 'allow_private_http':c.get('allow_private_http',False)}))
        base = urlparse(endpoint(c))
        if (target.scheme,target.netloc) != (base.scheme,base.netloc):
            raise ValueError('tokenize endpoint must share inference origin')
    if type(c.get('concurrency', 1)) is not int or not 1 <= c.get('concurrency', 1) <= 32:
        raise ValueError('concurrency must be 1..32')
    if type(c.get('timeout_seconds',180)) not in (int,float) or not math.isfinite(c.get('timeout_seconds',180)) or c.get('timeout_seconds',180)<=0:
        raise ValueError('positive finite timeout required')
    endpoint(c)
    return c


def config_hash(c):
    # Allow only operational controls to change on resume. Resolved endpoint is bound.
    return digest({**{k: v for k, v in c.items() if k not in {'budget_usd', 'concurrency', 'timeout_seconds'}},
                   'resolved_endpoint': endpoint(c)})


def rows(path):
    return read_jsonl(path) if Path(path).exists() else []


def append(path, record):
    with Path(path).open('a') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')
        f.flush()
        os.fsync(f.fileno())


@contextmanager
def lock(path):
    with Path(path).open('a') as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('another process owns this run/count journal') from None
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def count(directory, c, output, provider=None):
    manifest, _, requests, _ = load_plan(directory)
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with lock(str(output) + '.lock'):
        done = unique(rows(output), 'request_id')
        known = {r['request_id']: r for r in requests}
        for rid, row in done.items():
            if rid not in known or row.get('config_sha256') != config_hash(c) or row['request_sha256'] != known[rid]['request_sha256']:
                raise ValueError('stale token count journal')
        provider = provider or Provider(c)
        for r in requests:
            if r['request_id'] in done:
                continue
            n = provider.count(r)
            append(output, {k: r[k] for k in ('request_id', 'request_sha256')} | {
                'model': c['model'], 'tokenizer_revision': c['tokenizer_revision'], 'input_tokens': n,
                'input_limit': c['input_limit'], 'output_limit': c['output_limit'], 'total_limit': c['total_limit'],
                'config_sha256': config_hash(c)})
    return {'requests': len(requests), 'counts': str(output), 'requests_sha256': manifest['requests_sha256']}


def checked_counts(requests, c, path):
    counts = unique(read_jsonl(path), 'request_id')
    if set(counts) != {r['request_id'] for r in requests}:
        raise ValueError('measure every request for this exact plan')
    for r in requests:
        row = counts[r['request_id']]
        if row.get('config_sha256') != config_hash(c) or row['request_sha256'] != r['request_sha256'] or row['model'] != c['model']:
            raise ValueError('token counts do not match frozen model settings/plan')
        n = row['input_tokens']
        if type(n) is not int or n < 1 or n > c['input_limit'] or r['max_output_tokens'] > c['output_limit'] or n + r['max_output_tokens'] > c['total_limit']:
            raise ValueError('capacity exclusion required: rebuild BOTH conditions on common eligible set')
    return counts


def cost(c, inp, out):
    return (inp*c['input_usd_per_million'] + out*c['output_usd_per_million'])/1_000_000


def estimate(directory, c, measurements):
    _, docs, requests, _ = load_plan(directory)
    counts = checked_counts(requests, c, measurements)
    amount = sum(cost(c, counts[r['request_id']]['input_tokens'], r['max_output_tokens']) for r in requests)
    return {'documents': len(docs), 'requests': len(requests), 'conservative_usd': amount,
            'budget_usd': c['budget_usd'], 'fits_budget': amount <= c['budget_usd'],
            'note': 'Configured upper-bound rates, uncached input, maximum output; no implicit retries. Not a billing quote.'}


def source_hashes():
    return {p.name: sha(p.read_text()) for p in sorted(Path(__file__).parent.glob('*.py'))}


def execute(directory, c, measurements, output, provider=None, max_new=None, cohort=None):
    manifest, docs, requests, _ = load_plan(directory)
    counts = checked_counts(requests, c, measurements)
    cohort_hash = None
    if manifest.get('purpose') == 'benchmark':
        if not cohort: raise ValueError('benchmark requires --cohort from the all-model capacity gate')
        from .cohort import verify
        cohort_hash = verify(cohort, manifest, c, measurements)
    root = Path(output); root.mkdir(parents=True, exist_ok=True)
    with lock(root/'run.lock'):
        stamp = {'cohort_sha256': cohort_hash, 'config_sha256': config_hash(c), 'requests_sha256': manifest['requests_sha256'],
                 'data_sha256': manifest['data_sha256'], 'source_sha256': source_hashes()}
        meta = root/'run.json'
        if meta.exists():
            if any(json.loads(meta.read_text()).get(k) != v for k, v in stamp.items()):
                raise ValueError('run changed: use a new directory')
        else:
            commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
            write_json(meta, {**stamp, 'config': c, 'git_commit': commit,
                             'created_at': datetime.now(timezone.utc).isoformat(),
                             'dependencies': {d.metadata['Name']: d.version for d in importlib.metadata.distributions()}})
        journal = root/'events.jsonl'
        events = rows(journal)
        starts = {e['request_id']: e for e in events if e['event'] == 'reserved'}
        finishes = {e['request_id']: e for e in events if e['event'] == 'finished'}
        # An interrupted in-flight call may have been billed. Keep its full reservation;
        # never blindly resend it. Missing result remains an explicit failure.
        for rid in starts.keys() - finishes.keys():
            e = {'event': 'finished', 'request_id': rid, 'charged_usd': starts[rid]['reserved_usd'],
                 'response': {'request_id': rid, 'request_sha256': starts[rid]['request_sha256'],
                              'model': c['model'], 'status': 'uncertain', 'finish_reason': 'interrupted', 'text': '', 'usage': {}}}
            append(journal, e); finishes[rid] = e
        spent = sum(e['charged_usd'] for e in finishes.values())
        provider = provider or Provider(c)
        pending = [r for r in requests if r['request_id'] not in finishes]
        if max_new is not None:
            pending = pending[:max_new]
        stop = 'complete'
        with ThreadPoolExecutor(max_workers=c.get('concurrency', 1)) as pool:
            cursor = 0
            while cursor < len(pending):
                batch = []; reserved = 0
                for r in pending[cursor:cursor+c.get('concurrency', 1)]:
                    reserve = cost(c, counts[r['request_id']]['input_tokens'], r['max_output_tokens'])
                    if spent + reserved + reserve > c['budget_usd'] + 1e-12:
                        stop = 'budget_exhausted'; break
                    append(journal, {'event': 'reserved', 'request_id': r['request_id'],
                                     'request_sha256': r['request_sha256'], 'reserved_usd': reserve})
                    batch.append((r, reserve)); reserved += reserve
                if not batch:
                    break
                # Reserve all calls before dispatch; any crash between the two is conservative.
                futures = [pool.submit(provider.generate, r) for r, _ in batch]
                for (r, reserve), future in zip(batch, futures):
                    try:
                        response = future.result()
                    except Exception as exc:
                        response = {'status': 'failed', 'finish_reason': 'transport_error', 'text': '', 'usage': {},
                                    'error_type': type(exc).__name__}
                        if type(getattr(exc,'status',None)) is int:
                            response['http_status'] = exc.status
                    if response.get('finish_reason') == 'transport_error':
                        stop = 'transport_error'
                    response.update({k: r[k] for k in ('request_id', 'request_sha256')}, model=c['model'])
                    usage = response.get('usage', {})
                    valid_usage = all(type(usage.get(k)) is int and usage[k] >= 0 for k in ('input_tokens', 'output_tokens'))
                    charged = cost(c, usage['input_tokens'], usage['output_tokens']) if valid_usage else reserve
                    e = {'event': 'finished', 'request_id': r['request_id'], 'charged_usd': charged,
                         'usage_known': valid_usage, 'response': response}
                    append(journal, e); finishes[r['request_id']] = e; spent += charged
                    if charged > reserve + 1e-9:
                        stop = 'reservation_exceeded'
                cursor += len(batch)
                if stop != 'complete':
                    break
        response_path = root/'responses.jsonl'
        temp = root/'responses.tmp'
        with temp.open('w') as f:
            for r in requests:
                if r['request_id'] in finishes:
                    f.write(json.dumps(finishes[r['request_id']]['response'], ensure_ascii=False)+'\n')
        os.replace(temp, response_path)
        complete = len(finishes) == len(requests)
        report = {'model': c['model'], 'complete': complete, 'finished_requests': len(finishes),
                  'planned_requests': len(requests), 'spent_or_reserved_usd': spent,
                  'budget_usd': c['budget_usd'], 'stop_reason': ('max_new_reached' if stop == 'complete' else stop) if not complete else 'complete'}
        (root/'progress.json').write_text(json.dumps(report, indent=2))
        return report


def finalize(directory, c, output):
    root = Path(output)
    manifest, _, requests, _ = load_plan(directory)
    meta = json.loads((root/'run.json').read_text())
    if meta['config_sha256'] != config_hash(c) or meta['requests_sha256'] != manifest['requests_sha256'] or meta['source_sha256'] != source_hashes():
        raise ValueError('run/config/source changed')
    responses = rows(root/'responses.jsonl')
    if {r['request_id'] for r in responses} != {r['request_id'] for r in requests}:
        raise ValueError('unfinished run: resume first; do not publish a partial leaderboard')
    result = score(directory, root/'responses.jsonl', c['model'])
    result['execution'] = meta
    result['execution']['accounting'] = json.loads((root/'progress.json').read_text())
    write_json(root/'result.json', result)
    return {'result': str(root/'result.json'), 'f1_micro': result['metrics']['f1_micro']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['doctor', 'count', 'estimate', 'run', 'finalize'])
    p.add_argument('--config', required=True); p.add_argument('--directory')
    p.add_argument('--measurements'); p.add_argument('--output'); p.add_argument('--execute', action='store_true')
    p.add_argument('--max-new', type=int); p.add_argument('--cohort')
    a = p.parse_args(); c = load_config(a.config)
    if a.command == 'doctor':
        result = {'config_valid': True, 'model': c['model'], 'key_present': bool(os.environ.get(c.get('api_key_env', ''))),
                  'note': 'Offline config validation only; no credentials or endpoint access tested.'}
    else:
        if not a.directory: p.error('--directory required')
        if a.command in {'count', 'run', 'finalize'} and not a.output: p.error('--output required')
        if a.command in {'estimate', 'run'} and not a.measurements: p.error('--measurements required')
        if a.max_new is not None and a.max_new < 1: p.error('--max-new must be positive')
        if a.command == 'count': result = count(a.directory, c, a.output)
        elif a.command == 'estimate': result = estimate(a.directory, c, a.measurements)
        elif a.command == 'finalize': result = finalize(a.directory, c, a.output)
        else:
            if not a.execute: p.error('inference requires --execute and an explicitly allocated budget')
            result = execute(a.directory, c, a.measurements, a.output, max_new=a.max_new, cohort=a.cohort)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
