"""Offline preparation, capacity preflight and scoring. Never calls an API."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

from src.generate.taxonomy import Taxonomy, DEFAULT_PATH
from .protocol import Protocol, requests_for, decode, sha
from .metrics import score_corpus, paired_bootstrap


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def unique(rows, field):
    result = {r[field]: r for r in rows}
    if len(result) != len(rows):
        raise ValueError(f'duplicate {field}')
    return result


def write_json(path, value):
    with Path(path).open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)


def write_jsonl(path, rows):
    with Path(path).open('x') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


def prepare(corpus, directory, protocol):
    docs = read_jsonl(corpus)
    unique(docs, 'doc_id')
    if not docs or any(not d['text'] for d in docs):
        raise ValueError('nonempty documents required')
    taxonomy = Taxonomy()
    for d in docs:
        validate_spans(d['spans'], d['text'], taxonomy)
    requests = [r for d in docs for r in requests_for(d['doc_id'], d['text'], taxonomy, protocol)]
    audit = []
    for d in docs:
        owned = [r['window'] for r in requests if r['doc_id'] == d['doc_id']]
        unrepresentable = sum(not any(w['core_start'] <= s['start'] < w['core_end'] and s['end'] <= w['target_end'] for w in owned) for s in d['spans'])
        audit.append({'doc_id': d['doc_id'], 'gold_spans': len(d['spans']), 'unrepresentable_spans': unrepresentable})
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=False)
    write_jsonl(root / 'gold.jsonl', docs)
    write_jsonl(root / 'requests.jsonl', requests)
    write_json(root / 'boundary-audit.json', audit)
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    except subprocess.CalledProcessError:
        commit = 'unknown'
    write_json(root / 'manifest.json', {
        'task': 'span_extraction', 'protocol': asdict(protocol), 'git_commit': commit,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'taxonomy_sha256': sha(DEFAULT_PATH.read_text()),
        'data_sha256': sha((root / 'gold.jsonl').read_text()),
        'requests_sha256': sha((root / 'requests.jsonl').read_text()),
        'documents': len(docs), 'requests': len(requests),
        'source_sha256': {p.name: sha(p.read_text()) for p in Path(__file__).parent.glob('*.py')}})
    return {'directory': str(root), 'documents': len(docs), 'requests': len(requests),
            'unrepresentable_spans': sum(a['unrepresentable_spans'] for a in audit)}


def load_plan(directory):
    root = Path(directory)
    manifest = json.loads((root / 'manifest.json').read_text())
    for filename, key in [('gold.jsonl', 'data_sha256'), ('requests.jsonl', 'requests_sha256')]:
        if sha((root / filename).read_text()) != manifest[key]:
            raise ValueError(f'changed plan: {filename}')
    taxonomy = Taxonomy()
    if sha(DEFAULT_PATH.read_text()) != manifest['taxonomy_sha256']:
        raise ValueError('taxonomy changed')
    return manifest, read_jsonl(root / 'gold.jsonl'), read_jsonl(root / 'requests.jsonl'), taxonomy


def preflight(directory, measurements):
    manifest, docs, requests, _ = load_plan(directory)
    records = read_jsonl(measurements)
    models = sorted({r['model'] for r in records})
    if not models:
        raise ValueError('actual token measurements required')
    reports = {}
    for model in models:
        counts = unique([r for r in records if r['model'] == model], 'request_id')
        if set(counts) != {r['request_id'] for r in requests}:
            raise ValueError('each model must measure every request')
        failed = set()
        for r in requests:
            c = counts[r['request_id']]
            if c['request_sha256'] != r['request_sha256'] or not c['tokenizer_revision']:
                raise ValueError('stale token measurement or missing tokenizer revision')
            for key in ('input_tokens', 'input_limit', 'output_limit', 'total_limit'):
                if type(c[key]) is not int or c[key] < 0:
                    raise ValueError(f'invalid {key}')
            if c['input_tokens'] > c['input_limit'] or r['max_output_tokens'] > c['output_limit'] or c['input_tokens'] + r['max_output_tokens'] > c['total_limit']:
                failed.add(r['doc_id'])
        reports[model] = {'ineligible_doc_ids': sorted(failed)}
    rejected = set().union(*(set(v['ineligible_doc_ids']) for v in reports.values()))
    return {'requests_sha256': manifest['requests_sha256'], 'models': reports,
            'common_eligible_doc_ids': sorted(d['doc_id'] for d in docs if d['doc_id'] not in rejected),
            'note': 'Counts must include the actual chat template and all prompt text; no character estimates.'}


def validate_spans(spans, text, taxonomy):
    for s in spans:
        if type(s['start']) is not int or type(s['end']) is not int or not 0 <= s['start'] < s['end'] <= len(text) or s['category'] not in taxonomy.categories:
            raise ValueError('invalid span offsets/category')


def score(directory, responses_path, model):
    manifest, docs, requests, taxonomy = load_plan(directory)
    responses = unique(read_jsonl(responses_path), 'request_id')
    if set(responses) - {r['request_id'] for r in requests}:
        raise ValueError('unknown response request ID')
    docmap = unique(docs, 'doc_id')
    predictions = {d['doc_id']: [] for d in docs}
    failures = []; usage = {}; missing_usage = 0
    for r in requests:
        response = responses.get(r['request_id'])
        if response is not None and (response.get('request_sha256') != r['request_sha256'] or response.get('model') != model):
            raise ValueError('response model or request hash mismatch')
        spans, errors = decode(r, response or {}, docmap[r['doc_id']]['text'], taxonomy.categories)
        predictions[r['doc_id']].extend(spans)
        if errors:
            failures.append({'request_id': r['request_id'], 'errors': errors})
        if response is None or not response.get('usage'):
            missing_usage += 1
        else:
            for k, v in response['usage'].items():
                if isinstance(v, (float, int)) and not isinstance(v, bool):
                    usage[k] = usage.get(k, 0) + v
    result = score_corpus(docs, predictions, taxonomy)
    result.update(model=model, task='span_extraction', manifest=manifest,
                  response_sha256=sha(Path(responses_path).read_text()),
                  reliability={'requests': len(requests), 'failed_requests': len(failures),
                               'failure_rate': len(failures) / len(requests), 'failures': failures},
                  usage=usage, requests_missing_usage=missing_usage)
    return result


def compare(first, second, samples=2000):
    a = json.loads(Path(first).read_text()); b = json.loads(Path(second).read_text())
    for key in ('data_sha256', 'taxonomy_sha256'):
        if a['manifest'][key] != b['manifest'][key]:
            raise ValueError('comparison requires identical data and taxonomy')
    pa = dict(a['manifest']['protocol']); pb = dict(b['manifest']['protocol'])
    pa.pop('mode'); pb.pop('mode')
    if pa != pb:
        raise ValueError('comparison requires identical output partition and limits')
    return paired_bootstrap(a['per_document'], b['per_document'], samples=samples)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('prepare'); p.add_argument('--corpus', required=True); p.add_argument('--directory', required=True)
    p.add_argument('--mode', choices=['full_context_targeted', 'local_window'], default='full_context_targeted')
    p.add_argument('--core-chars', type=int, default=1200); p.add_argument('--halo-chars', type=int, default=1200)
    p.add_argument('--max-output-tokens', type=int, default=4096)
    p = sub.add_parser('preflight'); p.add_argument('--directory', required=True); p.add_argument('--measurements', required=True); p.add_argument('--output', required=True)
    p = sub.add_parser('score'); p.add_argument('--directory', required=True); p.add_argument('--responses', required=True); p.add_argument('--model', required=True); p.add_argument('--output', required=True)
    p = sub.add_parser('compare'); p.add_argument('--first', required=True); p.add_argument('--second', required=True); p.add_argument('--output', required=True)
    args = parser.parse_args()
    if args.command == 'prepare':
        result = prepare(args.corpus, args.directory, Protocol(args.mode, args.core_chars, args.halo_chars, args.max_output_tokens))
    elif args.command == 'preflight':
        result = preflight(args.directory, args.measurements); write_json(args.output, result)
    elif args.command == 'score':
        result = score(args.directory, args.responses, args.model); write_json(args.output, result)
        result = {'metrics': result['metrics'], 'failed_requests': result['reliability']['failed_requests']}
    else:
        result = compare(args.first, args.second); write_json(args.output, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
