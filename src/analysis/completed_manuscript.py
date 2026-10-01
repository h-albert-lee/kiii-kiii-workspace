"""ADR-0038: descriptive completed-run tables; never a pooled gate/export."""
import argparse
import csv
import json
from pathlib import Path
from collections import defaultdict
from src.eval.metrics import paired_bootstrap
from .response_diagnostics import file_sha
from .export_failure_decomposition import rows_for


def pair_check(a,b):
    for key in ('model','task'):
        if a[key]!=b[key]: raise ValueError('pair identity mismatch')
    for key in ('data_sha256','taxonomy_sha256','documents','requests'):
        if a['manifest'][key]!=b['manifest'][key]: raise ValueError('pair manifest mismatch')
    pa=dict(a['manifest']['protocol']);pb=dict(b['manifest']['protocol'])
    if pa.pop('mode')!='full_context_targeted' or pb.pop('mode')!='local_window' or pa!=pb:
        raise ValueError('pair protocol mismatch')
    for key in ('cohort_sha256','source_sha256','server'):
        if a['execution'].get(key)!=b['execution'].get(key):raise ValueError('pair execution mismatch: '+key)
    for key in ('model_revision','tokenizer_revision','generation','tokenize_options','input_limit','output_limit','total_limit'):
        if a['execution']['config'].get(key)!=b['execution']['config'].get(key):raise ValueError('pair setting mismatch: '+key)


def build(inputs, output):
    out=Path(output)
    if out.exists():raise ValueError('output must be new')
    inventory=json.loads(Path(inputs).read_text());rows=[];groups=[];pairs=defaultdict(dict);settings=[]
    for entry in inventory['runs']:
        p=Path(entry['result'])
        if file_sha(p)!=entry['result_sha256']:raise ValueError('result hash mismatch')
        r=json.loads(p.read_text());base=entry.get('baseline',False)
        if not base:
            if r['manifest']['purpose']!='benchmark' or not r['execution']['accounting']['complete']:raise ValueError('incomplete/pilot')
            dpath=Path(entry['diagnostics'])
            if file_sha(dpath)!=entry['diagnostics_sha256']:raise ValueError('diagnostic hash mismatch')
            d=json.loads(dpath.read_text())
            if d['strict_exact']!=r['metrics']['exact_micro']:raise ValueError('strict diagnostic mismatch')
            row,_=rows_for(d,entry['run'])
            pairs[r['model']][r['manifest']['protocol']['mode']]=r
        else:
            row=dict(run=entry['run'],model=r['model'],condition='document',documents=len(r['per_document']),
                strict_f1=r['metrics']['exact_micro']['f1'],format_compliance=None,empty_list_rate=None,
                detection_precision=None,detection_recall=None,detection_f1=None,invalid_item_fp=None)
        rows.append({k:row[k] for k in ('run','model','condition','documents','strict_f1','format_compliance','empty_list_rate','detection_precision','detection_recall','detection_f1','invalid_item_fp')})
        g=defaultdict(lambda:dict(tp=0,fp=0,fn=0))
        for key,v in r['tier_kind_tlevel'].items():
            for count in ('tp','fp','fn'):g['/'.join(key.split('/')[:2])][count]+=v[count]
        for key,v in g.items():
            tp,fp,fn=(v[k] for k in ('tp','fp','fn'))
            groups.append(dict(run=entry['run'],model=r['model'],condition=row['condition'],group=key,**v,precision=tp/(tp+fp) if tp+fp else 0,recall=tp/(tp+fn) if tp+fn else 0,f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0))
        e=r.get('execution',{});c=e.get('config',{})
        settings.append(dict(run=entry['run'],model=r['model'],documents=row['documents'],config={k:c[k] for k in ('model_revision','tokenizer_revision','generation','tokenize_options','input_limit','output_limit','total_limit') if k in c},server=e.get('server'),runner=e.get('runner'),source_sha256=e.get('source_sha256'),recorded_gate=e.get('cohort_sha256'),native_capacity_independently_verified=False))
    paired=[]
    for model,conds in pairs.items():
        if len(conds)!=2:continue
        a,b=conds['full_context_targeted'],conds['local_window'];pair_check(a,b)
        effect=paired_bootstrap(a['per_document'],b['per_document'],samples=2000,seed=0)
        paired.append(dict(model=model,documents=len(a['per_document']),delta_f1=effect['delta_f1'],ci_low=effect['ci95'][0],ci_high=effect['ci95'][1],samples=2000,seed=0))
    out.mkdir(parents=True)
    for name,data in [('summary.csv',rows),('taxonomy_groups.csv',groups),('paired.csv',paired)]:
        with (out/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    (out/'settings.json').write_text(json.dumps(settings,indent=2)+'\n')
    (out/'provenance.json').write_text(json.dumps(dict(source_sha256=file_sha(__file__),inputs_sha256=file_sha(inputs),bootstrap_source_sha256=file_sha('src/eval/metrics.py'),pairs=len(paired),rows=len(rows),headline_export=False,native_capacity_independently_verified=False),indent=2)+'\n')
    (out/'ARTIFACTS.sha256').write_text(''.join(f'{file_sha(p)}  {p.name}\n' for p in sorted(out.iterdir()) if p.is_file()))
    return rows,paired


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--inputs',required=True);p.add_argument('--output',required=True);a=p.parse_args();r,b=build(a.inputs,a.output);print(f'{len(r)} conditions; {len(b)} descriptive paired contrasts')
