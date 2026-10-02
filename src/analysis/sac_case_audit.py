"""Deterministic, purposive illustrations from archived synthetic responses."""
import argparse
from collections import Counter
import hashlib
import gzip
import json
from pathlib import Path

from src.analysis.failure_decomposition import parsed_body, item_outcome, gold_outcome, request_outcome
from src.analysis.response_diagnostics import read_rows, itemwise_decode
from src.analysis.sac_error_atlas import sha
from src.eval import protocol, metrics
from src.generate.taxonomy import Taxonomy, DEFAULT_PATH

STRATA = [
    ('fence_only', '0929-05-gemma4-31b-fp8-local'),
    ('outside_owned_core', '0928-04-gemma4-26b-a4b-local'),
    ('exact_boundary_wrong_category', '0926-02-qwen-9b-local'),
    ('overlapping_boundary_same_category', '0929-05-gemma4-31b-fp8-local'),
    ('empty_list', '0928-03-qwen3-30b-full'),
]


def eligible(row, kind):
    if kind == 'fence_only':
        return row['route'] == 'fence' and not row['invalid_items'] and row['gold_outcomes'].get('exact_hit', 0) > 0
    if kind == 'outside_owned_core':
        return row['item_outcomes'].get(kind, 0) > 0
    return row['gold_outcomes'].get(kind, 0) > 0


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def audit(inputs, gold_path, output):
    entries = {e['run']: e for e in json.loads(Path(inputs).read_text())['runs']}
    docs = {d['doc_id']: d for d in read_rows(gold_path)}
    tax = Taxonomy(); cases = []
    gold_hash = sha(gold_path)
    for kind, run in STRATA:
        e = entries[run]; dp = Path(e['diagnostics']); rp = Path(e['result'])
        if sha(dp) != e['diagnostics_sha256'] or sha(rp) != e['result_sha256']:
            raise ValueError('analysis/result changed')
        d = json.loads(dp.read_text()); ref = json.loads(rp.read_text())
        ledger = dp.parent / 'per_request.jsonl.gz'
        manifest = dict(line.split(None, 1)[::-1] for line in (dp.parent/'ARTIFACTS.sha256').read_text().splitlines())
        if manifest.get(ledger.name) != sha(ledger):raise ValueError('ledger hash mismatch')
        prov = d['provenance']['inputs']; responses = rp.parent/'responses.jsonl'
        if gold_hash != prov['gold_sha256'] or sha(responses) != prov['responses_sha256'] or sha(DEFAULT_PATH) != prov['taxonomy_sha256']:
            raise ValueError('gold/raw/taxonomy hash mismatch')
        with gzip.open(ledger, 'rt', encoding='utf-8') as stream:
            candidates = [r for line in stream if eligible(r := json.loads(line), kind)]
        chosen = min(candidates, key=lambda r: digest(r['request_id']))
        rid = chosen['request_id']; doc = docs[rid.rsplit(':', 1)[0]]
        reqs = list(protocol.requests_for(doc['doc_id'], doc['text'], tax, protocol.Protocol(**ref['manifest']['protocol'])))
        wanted = {r['request_id'] for r in reqs}
        raw = {r['request_id']: r for r in read_rows(responses) if r['request_id'] in wanted}
        if set(raw) != wanted:raise ValueError('selected document coverage mismatch')
        predictions = set(); selected = None
        for req in reqs:
            r = raw[req['request_id']]
            if req['request_sha256'] != r['request_sha256'] or r['model'] != ref['model']:
                raise ValueError('request replay mismatch')
            spans, info = itemwise_decode(req, r, doc['text'], tax.categories, unwrap=True)
            predictions.update(map(metrics.key, spans))
            if req['request_id'] == rid:selected = req, r, info
        req, r, info = selected
        items, route, duplicates = parsed_body(r['text']); outcome = request_outcome(r, items, route)
        counts = Counter(item_outcome(i, req, doc['text'], tax.categories) for i in items)
        if dict(counts) != chosen['item_outcomes'] or outcome != chosen['outcome'] or info['invalid_items'] != chosen['invalid_items']:
            raise ValueError('selected request diagnostic mismatch')
        w = req['window']
        owned = [g for g in doc['spans'] if w['core_start'] <= g['start'] < w['core_end']]
        buckets = Counter(gold_outcome(g, predictions, outcome, info['invalid_items']) for g in owned)
        if dict(buckets) != chosen['gold_outcomes']:raise ValueError('selected gold outcomes mismatch')
        case = dict(kind=kind, run=run, model=ref['model'], condition=d['condition'],
                    request_id=rid, request_sha256=req['request_sha256'], eligible_requests=len(candidates),
                    selection='Minimum SHA256(request_id) in prespecified run/stratum; then lexicographic span/item order.',
                    source_inputs=prov, ledger_sha256=sha(ledger), window=w, route=route,
                    request_outcome=outcome, gold_outcomes=dict(buckets), item_outcomes=dict(counts))
        if kind == 'outside_owned_core':
            item = min((i for i in items if item_outcome(i, req, doc['text'], tax.categories) == kind),
                       key=lambda i: (i['category'], i['text'], i['occurrence']))
            start = w['target_start'] + list(protocol.occurrences(doc['text'][w['target_start']:w['target_end']], item['text']))[item['occurrence']-1]
            case.update(predicted_item=item, predicted_start=start, starts_after_core_by=start-w['core_end'])
        else:
            bucket = 'exact_hit' if kind == 'fence_only' else kind
            g = min((g for g in owned if gold_outcome(g, predictions, outcome, info['invalid_items']) == bucket), key=metrics.key)
            case['gold'] = dict(start=g['start'], end=g['end'], category=g['category'], text=doc['text'][g['start']:g['end']])
            if kind != 'empty_list':
                matches = [p for p in predictions if
                           (p == metrics.key(g) if kind == 'fence_only' else
                            p[:2] == metrics.key(g)[:2] if kind == 'exact_boundary_wrong_category' else
                            p[2] == g['category'] and p[0] < g['end'] and g['start'] < p[1])]
                p = min(matches)
                case['prediction'] = dict(start=p[0], end=p[1], category=p[2], text=doc['text'][p[0]:p[1]])
            case['context_excerpt'] = doc['text'][max(w['target_start'], g['start']-60):min(w['target_end'],g['end']+60)]
        cases.append(case)
    output = Path(output)
    if output.exists():raise ValueError('do not overwrite an existing audit')
    output.write_text(json.dumps(dict(purpose='Purposive illustrations, not representative human annotation or a new score.',
        source_sha256=sha(__file__), parent_inputs_sha256=sha(inputs), cases=cases),ensure_ascii=False,indent=2)+'\n')
    return cases


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inputs',required=True);p.add_argument('--gold',required=True);p.add_argument('--output',required=True)
    a = p.parse_args();print(f'{len(audit(a.inputs,a.gold,a.output))} verified illustrative cases; no predictions repaired.')
