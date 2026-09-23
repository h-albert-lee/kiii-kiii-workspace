"""Export comparable, completed benchmark results to a CSV; never pilot scores."""
import argparse
import csv
import json
from pathlib import Path


def export(paths, output):
    records=[]; cohort=None; comparison=None; seen=set(); gate=None
    for path in paths:
        r=json.loads(Path(path).read_text());m=r['manifest']
        if m.get('purpose')!='benchmark':raise ValueError('pilot/smoke results cannot enter the leaderboard')
        if cohort is not None and cohort != m['data_sha256']:raise ValueError('different evaluation cohorts')
        cohort=m['data_sha256'];model=r['model'];baseline='baseline_context' in r
        definition=(m['taxonomy_sha256'],{k:v for k,v in m['protocol'].items() if k!='mode'})
        if comparison is not None and comparison != definition:raise ValueError('different taxonomy or output partitions')
        comparison=definition
        if not baseline:
            current_gate=r.get('execution',{}).get('cohort_sha256')
            if gate is not None and gate!=current_gate:raise ValueError('different cohort gates')
            gate=current_gate
        if not baseline and (not r.get('execution',{}).get('accounting',{}).get('complete') or not r['execution'].get('cohort_sha256')):
            raise ValueError('require finalized, cohort-gated inference results')
        if any(x in model.lower() for x in ('glm-5.2','astra','gpt-6')):
            raise ValueError('generator excluded from headline table')
        mode=r.get('baseline_context',m['protocol']['mode']);key=(model,mode)
        if key in seen:raise ValueError('duplicate model/condition')
        seen.add(key)
        exact=r['metrics']['exact_micro']
        records.append(dict(model=model,condition=mode,documents=m['documents'],
            data_version=m.get('dataset_source',{}).get('release_version','unrecorded'),prompt_version=m['protocol'].get('version',''),
            git_commit=r.get('execution',{}).get('git_commit',m.get('git_commit','')), precision=exact['precision'],recall=exact['recall'],f1_micro=exact['f1'],
            failed_requests=r.get('reliability',{}).get('failed_requests',0),
            spent_or_reserved_usd=r.get('execution',{}).get('accounting',{}).get('spent_or_reserved_usd',''),
            data_sha256=cohort,result_file=str(path)))
    if not records:raise ValueError('no results')
    with Path(output).open('x',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
    return len(records)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--results',nargs='+',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();print(export(a.results,a.output))
