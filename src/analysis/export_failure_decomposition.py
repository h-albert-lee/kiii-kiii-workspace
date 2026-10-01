"""Export separate response-contract and all-gold detection axes, without pooling."""
import argparse
import csv
import json
from pathlib import Path
from .response_diagnostics import file_sha
from .failure_decomposition import VERSION

REQUEST_BUCKETS=('output_truncated','other_terminal_failure','invalid_json','root_schema','empty_list','nonempty_list')


def rows_for(result, run):
    if result.get('version')!=VERSION or result.get('headline_eligible') is not False or not result['provenance']['strict_and_itemwise_replayed']:
        raise ValueError('require replay-verified secondary decomposition')
    c=result['request_counts']; n=c['total']; gold=sum(result['gold_outcomes'].values()); items=sum(result['item_outcomes'].values())
    if sum(c.get(k,0) for k in REQUEST_BUCKETS)!=n:
        raise ValueError('request partition mismatch')
    if gold!=result['itemwise_exact']['tp']+result['itemwise_exact']['fn']:
        raise ValueError('gold denominator mismatch')
    def ratio(a,b):return a/b if b else None
    row=dict(run=run,model=result['model'],condition=result['condition'],documents=result['documents'],requests=n,
             typed_gold=gold,parsed_items=items,format_compliance=ratio(c.get('format_compliant',0),n),
             empty_list_rate=ratio(c.get('empty_list',0),n),invalid_json_rate=ratio(c.get('invalid_json',0),n),
             truncated_rate=ratio(c.get('output_truncated',0),n),strict_failure_rate=ratio(c.get('strict_rejected',0),n),
             valid_item_rate=ratio(result['item_outcomes'].get('valid',0),items),invalid_item_fp=result['invalid_item_fp'])
    for name,key in [('strict','strict_exact'),('detection','itemwise_exact'),('valid_item_location','valid_item_location_exact'),('typed_character','typed_character')]:
        row.update({name+'_'+k:result[key][k] for k in ('precision','recall','f1','tp','fp','fn')})
    counts=[]
    for axis,values,denom in [('request_outcome',{k:c.get(k,0) for k in REQUEST_BUCKETS},n),
                             ('item_outcome',result['item_outcomes'],items),('gold_outcome',result['gold_outcomes'],gold)]:
        for category,count in sorted(values.items()):
            counts.append(dict(run=run,model=result['model'],condition=result['condition'],axis=axis,
                               outcome=category,count=count,denominator=denom,rate=ratio(count,denom)))
    return row,counts


def export(paths,output):
    out=Path(output)
    if out.exists():raise ValueError('output must be new')
    if len({Path(p).parent.name for p in paths})!=len(paths):raise ValueError('duplicate run IDs')
    summaries=[];long=[]
    for p in map(Path,paths):
        row,counts=rows_for(json.loads(p.read_text()),p.parent.name);summaries.append(row);long.extend(counts)
    if not summaries:raise ValueError('no inputs')
    out.mkdir(parents=True)
    for name,rows in [('summary.csv',summaries),('failure_types.csv',long)]:
        with (out/name).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
    lines=['# Format grounding and detection diagnostics','',
           'Post-hoc secondary analysis under ADR-0037. Scores/rates below are on a 0–100 scale. Each row keeps its original cohort. No pooled ranking or native capacity validation.', '',
           '| Model | Condition | Docs | Format compliant % | Empty list % | Strict F1 | Detection P | Detection R | Detection F1 |',
           '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in summaries:
        fields=[r['format_compliance'],r['empty_list_rate'],r['strict_f1'],r['detection_precision'],r['detection_recall'],r['detection_f1']]
        lines.append(f"| {r['model']} | {r['condition']} | {r['documents']} | "+' | '.join(f'{100*v:.2f}' for v in fields)+' |')
    lines += ['',
        'Format compliance requires normal completion, raw JSON, exact root/item structure and field types, and no duplicate keys. It does not validate quote existence or category vocabulary. Empty lists may comply; empty-list rate uses ALL requests, including failures, as denominator.',
        '', 'Detection P/R/F1 reuses ADR-0036 whole-fence/itemwise scoring: all gold remain, valid items survive malformed siblings, and every rejected parsed item adds one exact FP. This is observable extraction under a fixed parser, not latent ability independently of format. Unparseable and truncated responses stay empty. Original strict scores are unchanged.',
        '', 'failure_types.csv has disjoint request, item and typed-gold partitions with explicit denominators. Gold miss buckets describe the first applicable observation, not a causal decomposition. Unresolved misses with rejected items cannot establish which PII an invalid item intended.',
        '', 'summary.csv additionally contains exact location-only scores on valid known-category items and category-aware character scores. Location scores retain invalid-item FP and collapse same-coordinate labels. Character scores cannot penalize unanchorable items and must be read with exact precision and invalid-item counts.',
        '', 'Duplicate JSON keys retain frozen last-value scoring, but fail structural compliance. Some lost items are unobservable to the original parser. Counts and scores do not correct this limitation.',
        '', 'Kanana 1.5 8B uses 1,438 documents; other runs use 1,440. Native counts/final gates remain unverified. Qwen3-30B/EXAONE are additional operator runs outside the accepted roster. Do not infer a scale effect across model generations or architectures. Baselines have no generative format-compliance task and should show N/A, not 100%.',
        '', 'No new inference, success-only scoring, prompt tuning, fuzzy anchoring or gold-guided repair.']
    (out/'REPORT.md').write_text('\n'.join(lines)+'\n')
    (out/'provenance.json').write_text(json.dumps(dict(source_sha256=file_sha(__file__),inputs={str(p):file_sha(p) for p in paths}),indent=2)+'\n')
    (out/'ARTIFACTS.sha256').write_text(''.join(f'{file_sha(p)}  {p.name}\n' for p in sorted(out.iterdir()) if p.is_file()))
    return len(summaries)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--analyses',nargs='+',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();print(export(a.analyses,a.output))
