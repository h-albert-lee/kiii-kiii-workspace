"""ADR-0040: conserved, per-run views of replay-verified failure partitions."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

GOLD_GROUPS = {
    'exact_hit': ('exact_hit',),
    'unusable_output': ('invalid_json', 'root_schema', 'output_truncated', 'other_terminal_failure'),
    'empty_output': ('empty_list',),
    'boundary_or_category': ('exact_boundary_wrong_category', 'overlapping_boundary_same_category',
                             'overlapping_boundary_wrong_category'),
    'unresolved_rejected': ('unresolved_with_rejected_items',),
    'no_overlap': ('no_overlapping_prediction',),
}
ITEM_KEYS = {'valid', 'item_schema', 'invalid_category', 'invalid_quote_field',
             'invalid_occurrence_field', 'quote_absent_from_target',
             'occurrence_out_of_range', 'outside_owned_core'}
OWNER_KEYS = {'empty_list', 'nonempty_list', 'invalid_json', 'root_schema',
              'output_truncated', 'other_terminal_failure'}


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def summarize(d):
    if d.get('headline_eligible') is not False or not d['provenance'].get('strict_and_itemwise_replayed'):
        raise ValueError('replay-verified offline diagnostic required')
    gold, items, requests = d['gold_outcomes'], d['item_outcomes'], d['request_counts']
    allowed = {key for keys in GOLD_GROUPS.values() for key in keys}
    if set(gold)-allowed or set(items)-ITEM_KEYS:
        raise ValueError('unknown outcome must be reviewed explicitly')
    if any(type(v) is not int or v < 0 for counts in [gold, items, requests] for v in counts.values()):
        raise ValueError('nonnegative integer counts required')
    n = sum(gold.values())
    exact = d['itemwise_exact']
    if not n or n != exact['tp'] + exact['fn'] or gold.get('exact_hit', 0) != exact['tp']:
        raise ValueError('gold partition does not conserve all gold')
    if n != d['strict_exact']['tp'] + d['strict_exact']['fn']:
        raise ValueError('strict and diagnostic gold differ')
    invalid = sum(v for k, v in items.items() if k != 'valid')
    if invalid != d['invalid_item_fp'] or invalid > exact['fp']:
        raise ValueError('invalid-item penalty mismatch')
    if sum(requests.get(k, 0) for k in OWNER_KEYS) != requests['total']:
        raise ValueError('request outcome coverage mismatch')
    r = dict(model=d['model'], condition=d['condition'], documents=d['documents'],
             requests=requests['total'], gold=n, parsed_items=sum(items.values()),
             invalid_items=invalid, detection_recall=exact['tp']/n)
    for name, keys in GOLD_GROUPS.items():
        count = sum(gold.get(k, 0) for k in keys)
        r['gold_'+name] = count
        r['gold_'+name+'_rate'] = count/n
    for name in ['format_compliant', 'whole_fence_parseable', 'empty_list', 'invalid_json',
                 'root_schema', 'output_truncated', 'other_terminal_failure', 'duplicate_key_requests']:
        count = requests.get(name, 0)
        if count > requests['total']:raise ValueError('invalid all-request rate')
        r['request_'+name+'_rate'] = count/requests['total']
    for name in sorted(ITEM_KEYS - {'valid'}):
        count = items.get(name, 0)
        r['item_'+name] = count
        r['item_'+name+'_share_of_invalid'] = count/invalid if invalid else None
    return r


def build(inputs, output):
    out=Path(output)
    if out.exists():raise ValueError('use a new analysis directory')
    inventory=json.loads(Path(inputs).read_text())
    rows=[];fine=[];sources=[];seen=set()
    for entry in inventory['runs']:
        if entry.get('baseline'):continue
        p=Path(entry['diagnostics'])
        if sha(p)!=entry['diagnostics_sha256']:raise ValueError('diagnostic hash mismatch')
        ref=Path(entry['result'])
        if sha(ref)!=entry['result_sha256']:raise ValueError('result hash mismatch')
        d=json.loads(p.read_text());result=json.loads(ref.read_text())
        if d['provenance']['inputs']['strict_result_sha256']!=entry['result_sha256']:
            raise ValueError('diagnostic/reference provenance mismatch')
        if d['strict_exact']!=result['metrics']['exact_micro']:
            raise ValueError('strict result mismatch')
        if result['manifest']['purpose']!='benchmark' or not result['execution']['accounting']['complete']:
            raise ValueError('incomplete or pilot result')
        row=summarize(d);row={'run':entry['run'],**row}
        key=(row['model'],row['condition'])
        if key in seen:raise ValueError('duplicate model condition')
        seen.add(key);rows.append(row)
        for level,counts,denominator in [('gold',d['gold_outcomes'],row['gold']),
                                         ('item',d['item_outcomes'],row['parsed_items']),
                                         ('request',d['request_counts'],row['requests'])]:
            for outcome,count in sorted(counts.items()):
                fine.append(dict(run=entry['run'],level=level,outcome=outcome,count=count,
                                 denominator=denominator,rate=count/denominator if denominator else None))
        sources.append(dict(entry,external_runner=d['provenance'].get('external_runner_replay',False),
                            recorded_gate=d['provenance']['recorded_cohort_sha256'],
                            native_capacity_independently_verified=False))
    if len(rows)!=22:raise ValueError('ADR-0038 requires all 22 completed LLM conditions')
    out.mkdir(parents=True)
    for name,data in [('summary.csv',rows),('fine_outcomes.csv',fine)]:
        with (out/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    (out/'INPUTS.json').write_text(json.dumps(dict(adr='0040',parent_inputs=str(inputs),
        parent_sha256=sha(inputs),analysis_source_sha256=sha(__file__),runs=sources),indent=2)+'\n')
    (out/'ARTIFACTS.sha256').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in sorted(out.iterdir()) if p.is_file()))
    return rows


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--inputs',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();print(f'{len(build(a.inputs,a.output))} completed conditions; conserved gold and invalid-item counts.')
