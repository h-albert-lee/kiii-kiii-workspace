"""Sequential streaming recovery with a single budget across prior and new runs."""
import argparse
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.generate.batch import _atomic, _json, _locked, _sha
from src.generate.campaign import prepare, run


def states(roots):
    return sorted({p.resolve() for root in roots for p in Path(root).rglob('state.json')})


def cost(roots):
    return sum(json.loads(p.read_text())['estimated_committed_usd'] for p in states(roots))


def accepted(roots):
    docs = {}
    for p in states(roots):
        state = json.loads(p.read_text())
        for doc_id, row in state['records'].items():
            if row['status'] == 'accepted':
                docs[doc_id] = json.loads((p.parent / f'document.{doc_id}.json').read_text())
    return docs


def selected_docs(manifest, roots):
    plans = {p['doc_id']: p for p in manifest['plans']}
    return {k: dict(v, generator=dict(v.get('generator', {}), data_version=manifest.get('data_version', v.get('generator', {}).get('data_version')))) for k, v in accepted(roots).items() if k in plans
            and v.get('generator', {}).get('run_id') not in manifest.get('excluded_source_runs', [])
            and (plans[k]['context_len_bucket'] != '16k' or v['context_len_bucket'] == '16k')}


def transient(entry):
    return entry.get('http_status') in {429, 500, 502, 503, 529}


def pause_seconds(entry):
    try:
        retry_after = float(entry.get('retry_after') or 0)
    except (ValueError, TypeError):
        retry_after = 0
    # Long Retry-After is handled as a stop, never silently shortened.
    return max(retry_after, 30 + random.uniform(0, 15))


def snapshot(root):
    manifest = json.loads((root / 'manifest.json').read_text())
    roots = manifest['prior_roots'] + [str(root / 'attempts')]
    docs = selected_docs(manifest, roots)
    progress = json.loads((root / 'progress.json').read_text())
    summary = {'target': len(manifest['plans']), 'accepted': len(docs),
               'estimated_committed_usd': cost(roots), 'budget_usd': manifest['budget_usd'],
               'stop_reason': progress['stop_reason'], 'processed_new': len(progress['processed']),
               'current_doc_id': progress.get('current_doc_id'),
               'human_reviewed': False}
    _atomic(root / 'docs.jsonl', ''.join(json.dumps(d, ensure_ascii=False) + '\n' for d in docs.values()))
    _atomic(root / 'summary.json', _json(summary))
    return summary


def initialize(root, plan_path, prior_roots, excluded_source_runs=(), budget=150, data_version="main-720-v2"):
    roots = [str(Path(p).resolve()) for p in prior_roots]
    if any(Path(p) == root.resolve() or root.resolve().is_relative_to(Path(p)) for p in roots):
        raise ValueError('prior roots must not contain recovery output')
    for path in states(roots):
        if any(e['status'] == 'in_flight' for e in json.loads(path.read_text())['records'].values()):
            raise ValueError('prior request is still in flight')
    plans = [json.loads(s) for s in Path(plan_path).read_text().splitlines() if s.strip()]
    if not plans or len({p['doc_id'] for p in plans}) != len(plans):
        raise ValueError('expected nonempty unique plans')
    root.mkdir(parents=True, exist_ok=False)
    prepare(plan_path, root / 'frozen', budget - cost(roots), prompt_version='compose_v7',
            transport={'stream': True, 'output_limit': 65536})
    manifest = {'plans': plans, 'budget_usd': budget, 'prior_roots': roots,
                'excluded_source_runs': list(excluded_source_runs),
                'run_id': root.name, 'data_version': data_version, 'prompt_version': 'compose_v7',
                'git_commit': json.loads((root / 'frozen/manifest.json').read_text())['git_commit'],
                'prior_states_sha256': {str(p): _sha(p.read_bytes()) for p in states(roots)},
                'script_sha256': _sha(Path(__file__).read_bytes()),
                'frozen_sha256': _sha((root / 'frozen/manifest.json').read_bytes()),
                'max_transport_attempts_per_document': 2, 'max_repairs_per_document': 1,
                'concurrency': 1, 'output_limit_all_buckets': 65536}
    _atomic(root / 'manifest.json', _json(manifest))
    _atomic(root / 'progress.json', _json({'processed': [], 'stop_reason': 'prepared'}))
    return snapshot(root)


def execute(root):
    with _locked(root):
        m = json.loads((root / 'manifest.json').read_text())
        if _sha(Path(__file__).read_bytes()) != m['script_sha256']:
            raise ValueError('recovery script changed')
        for p, digest in m['prior_states_sha256'].items():
            if _sha(Path(p).read_bytes()) != digest:
                raise ValueError('prior cost ledger changed')
        frozen = (root / 'frozen/manifest.json').read_bytes()
        if _sha(frozen) != m['frozen_sha256']:
            raise ValueError('frozen manifest changed')
        for p, digest in json.loads(frozen)['source_hashes'].items():
            if _sha(Path(p).read_bytes()) != digest:
                raise ValueError('generation code changed')
        progress = json.loads((root / 'progress.json').read_text())
        if progress['stop_reason'] not in {'prepared', 'running'}:
            return snapshot(root)
        roots = m['prior_roots'] + [str(root / 'attempts')]
        done = set(selected_docs(m, roots)) | {r['doc_id'] for r in progress['processed']}
        consecutive_errors = 0
        consecutive_output_limits = 0
        for plan in m['plans']:
            doc_id = plan['doc_id']
            if doc_id in done:
                continue
            progress.update(stop_reason='running', current_doc_id=doc_id)
            _atomic(root / 'progress.json', _json(progress))
            snapshot(root)
            for attempt in range(2):
                job = root / 'attempts' / f'{doc_id}-{attempt}'
                if not job.exists():
                    remaining = m['budget_usd'] - cost(roots)
                    if remaining <= 0:
                        progress['stop_reason'] = 'budget'
                        break
                    plan_path = root / 'current-plan.jsonl'
                    _atomic(plan_path, json.dumps(plan, ensure_ascii=False) + '\n')
                    prepare(plan_path, job, remaining, prompt_version='compose_v7',
                            transport={'stream': True, 'output_limit': 65536})
                result = run(job)
                if result['stop_reason'] in {'budget', 'reservation_exceeded'}:
                    progress['stop_reason'] = result['stop_reason']
                    break
                entry = result['records'][doc_id]
                if attempt == 0 and transient(entry):
                    delay = pause_seconds(entry)
                    if delay > 300:
                        progress['stop_reason'] = 'provider_retry_after'
                        break
                    print(json.dumps({'doc_id': doc_id, 'backoff_seconds': delay, 'status': entry['http_status']}), flush=True)
                    time.sleep(delay)
                    continue
                break
            if progress['stop_reason'] not in {'prepared', 'running'}:
                break
            response = job / f'response.{doc_id}.json'
            finish = json.loads(response.read_text())['completion'].get('finish_reason') if response.exists() else None
            if entry['status'] == 'rejected' and finish == 'stop':
                original = json.loads(response.read_text())
                repair = root / 'attempts' / f'{doc_id}-repair'
                if not repair.exists():
                    remaining = m['budget_usd'] - cost(roots)
                    if remaining <= 0:
                        progress['stop_reason'] = 'budget'
                        break
                    plan_path = root / 'current-plan.jsonl'
                    _atomic(plan_path, json.dumps(plan, ensure_ascii=False) + '\n')
                    prepare(plan_path, repair, remaining, repairs={doc_id: original}, prompt_version='compose_v7',
                            transport={'stream': True, 'output_limit': 65536})
                result = run(repair)
                if result['stop_reason'] in {'budget', 'reservation_exceeded'}:
                    progress['stop_reason'] = result['stop_reason']
                    break
                job = repair
                entry = result['records'][doc_id]
                response = job / f'response.{doc_id}.json'
                finish = json.loads(response.read_text())['completion'].get('finish_reason') if response.exists() else None
            outcome = ('accepted' if entry['status'] == 'accepted' else
                       'transport_error' if entry['status'] in {'request_error', 'usage_unknown'} else
                       'output_limit' if finish == 'length' else 'annotation_error')
            progress['processed'].append({'doc_id': doc_id, 'outcome': outcome, 'job': str(job)})
            progress.pop('current_doc_id', None)
            progress['stop_reason'] = 'running'
            consecutive_errors = consecutive_errors + 1 if outcome == 'transport_error' else 0
            consecutive_output_limits = consecutive_output_limits + 1 if outcome == 'output_limit' else 0
            completed = [r for r in progress['processed'] if r['outcome'] in {'accepted', 'annotation_error'}]
            if consecutive_errors >= 3:
                progress['stop_reason'] = 'provider_errors'
            elif consecutive_output_limits >= 3:
                progress['stop_reason'] = 'output_limit'
            elif len(completed) >= 10 and sum(r['outcome'] == 'accepted' for r in completed) / len(completed) < .7:
                progress['stop_reason'] = 'annotation_quality'
            _atomic(root / 'progress.json', _json(progress))
            print(json.dumps(snapshot(root)), flush=True)
            if progress['stop_reason'] != 'running':
                break
        else:
            progress['stop_reason'] = 'all_attempted'
        _atomic(root / 'progress.json', _json(progress))
        return snapshot(root)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('command', choices=['prepare', 'run', 'report'])
    p.add_argument('--directory', type=Path, required=True)
    p.add_argument('--plan')
    p.add_argument('--prior', action='append', default=[])
    p.add_argument('--exclude-run-id', action='append', default=[])
    a = p.parse_args()
    try:
        result = (initialize(a.directory, a.plan, a.prior, a.exclude_run_id) if a.command == 'prepare' else
                  execute(a.directory) if a.command == 'run' else snapshot(a.directory))
    except Exception as exc:
        progress_path = a.directory / 'progress.json'
        if a.command == 'run' and progress_path.exists():
            progress = json.loads(progress_path.read_text())
            progress.update(stop_reason='execution_error', error_type=type(exc).__name__)
            _atomic(progress_path, _json(progress))
            snapshot(a.directory)
        raise
    print(json.dumps(result, ensure_ascii=False, indent=2))
