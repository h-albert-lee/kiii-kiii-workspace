"""Configurable disjoint plan/budget lanes; no concurrent mutation of a cost ledger."""
import argparse
import json
import math
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import resume_mango as sequential
from src.generate.batch import _atomic, _json, _locked, _sha


def split_remaining(plans, done, spent, ceiling=150, concurrency=4):
    if not all(math.isfinite(x) for x in (spent, ceiling)) or spent < 0:
        raise ValueError('finite nonnegative cost and finite ceiling required')
    if type(concurrency) is not int or not 1 <= concurrency <= 8:
        raise ValueError('concurrency must be 1..8')
    remaining = [p for p in plans if p['doc_id'] not in done]
    if len({p['doc_id'] for p in plans}) != len(plans) or spent >= ceiling:
        raise ValueError('duplicate plans or exhausted budget')
    return [remaining[i::concurrency] for i in range(concurrency)], (ceiling - spent) / concurrency


def prepare(root, previous, plan_path=None, concurrency=4, retry_deferred=False, additional_budget=None, data_version="main-720-v2"):
    old = json.loads((previous / 'manifest.json').read_text())
    roots = old['prior_roots'] + ([str(p.resolve()) for p in sorted(previous.glob('lane-*/attempts'))] if list(previous.glob('lane-*')) else [str((previous / 'attempts').resolve())])
    if plan_path is not None:
        old['plans'] = [json.loads(s) for s in Path(plan_path).read_text().splitlines() if s.strip()]
    for p in sequential.states(roots):
        if any(r['status'] == 'in_flight' for r in json.loads(p.read_text())['records'].values()):
            raise ValueError('previous generation still in flight')
    docs = sequential.selected_docs(old, roots)
    spent = sequential.cost(roots)
    ceiling = spent + additional_budget if additional_budget is not None else 150
    deferred = {doc_id for p in sequential.states(roots) for doc_id, r in json.loads(p.read_text())['records'].items() if r['status'] == 'usage_unknown' and r.get('defer_retry')}
    lanes, allowance = split_remaining(old['plans'], set(docs) | (set() if retry_deferred else deferred), spent, ceiling=ceiling, concurrency=concurrency)
    root.mkdir(parents=True, exist_ok=False)
    for i, plans in enumerate(lanes):
        if not plans:
            continue
        plan_path = root / f'plan-{i}.jsonl'
        _atomic(plan_path, ''.join(json.dumps(p, ensure_ascii=False) + '\n' for p in plans))
        sequential.initialize(root / f'lane-{i}', plan_path, roots,
                              old.get('excluded_source_runs', []), budget=spent + allowance, data_version=data_version)
    manifest = {**old, 'prior_roots': roots, 'run_id': root.name, 'concurrency': concurrency, 'deferred_doc_ids': sorted(deferred) if not retry_deferred else [],
                'explicitly_retried_uncertain_ids': sorted(deferred) if retry_deferred else [],
                'budget_usd': ceiling, 'additional_budget_usd': additional_budget, 'data_version': data_version, 'prior_committed_usd': spent,
                'new_budget_per_lane': allowance,
                'script_sha256': _sha(Path(__file__).read_bytes())}
    _atomic(root / 'manifest.json', _json(manifest))
    return report(root)


def report(root):
    m = json.loads((root / 'manifest.json').read_text())
    lanes = sorted(root.glob('lane-*'))
    roots = m['prior_roots'] + [str(p / 'attempts') for p in lanes]
    docs = sequential.selected_docs(m, roots)
    statuses = []
    for p in lanes:
        s = json.loads((p / 'progress.json').read_text())
        statuses.append({'lane': p.name, 'stop_reason': s['stop_reason'],
                         'completed': len(s['processed']), 'current_doc_id': s.get('current_doc_id')})
    result = {'target': len(m['plans']), 'accepted': len(docs), 'concurrency': m.get('concurrency', 4),
              'deferred_doc_ids': m.get('deferred_doc_ids', []),
              'estimated_committed_usd': sequential.cost(roots), 'budget_usd': m['budget_usd'],
              'lanes': statuses, 'human_reviewed': False}
    _atomic(root / 'docs.jsonl', ''.join(json.dumps(d, ensure_ascii=False) + '\n' for d in docs.values()))
    _atomic(root / 'summary.json', _json(result))
    return result


def run(root):
    with _locked(root):
        m = json.loads((root / 'manifest.json').read_text())
        if _sha(Path(__file__).read_bytes()) != m['script_sha256']:
            raise ValueError('parallel runner changed')
        def lane_task(lane):
            try:
                return sequential.execute(lane)
            except Exception as exc:
                p = lane / 'progress.json'
                s = json.loads(p.read_text())
                s.update(stop_reason='execution_error', error_type=type(exc).__name__)
                _atomic(p, _json(s))
                raise
        try:
            with ThreadPoolExecutor(max_workers=m.get('concurrency', 4)) as pool:
                futures = [pool.submit(lane_task, p) for p in sorted(root.glob('lane-*'))]
                for f in futures:
                    f.result()
        finally:
            report(root)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['prepare', 'run', 'report'])
    parser.add_argument('--directory', required=True, type=Path)
    parser.add_argument('--previous', type=Path)
    parser.add_argument('--plan', type=Path)
    parser.add_argument('--concurrency', type=int, default=4)
    parser.add_argument('--retry-deferred', action='store_true', help='Explicit retry of interrupted calls; retains their full historical reservations')
    parser.add_argument('--additional-budget', type=float)
    parser.add_argument('--data-version', default='main-720-v2')
    args = parser.parse_args()
    result = (prepare(args.directory, args.previous, args.plan, args.concurrency, args.retry_deferred, args.additional_budget, args.data_version) if args.command == 'prepare' else
              run(args.directory) if args.command == 'run' else report(args.directory))
    print(json.dumps(result, ensure_ascii=False, indent=2))
