"""Budgeted, serial Batch waves. Local polling uses no LLM tokens."""
import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.generate import batch
from src.generate.compose import Plan
from src.generate.run import fill_one
from src.generate.taxonomy import Taxonomy


def reserve(request):
    body = request['body']
    # Worst-case cache-write input rate; UTF-8 bytes upper-bound text tokens.
    return ((len(body['messages'][0]['content'].encode()) + 1024) * 6.25
            + body['max_completion_tokens'] * 25) / 1e6


def response_cost(usage, reserved):
    if not usage or not all(isinstance(usage.get(k), (int, float)) and math.isfinite(usage[k]) and usage[k] >= 0
                            for k in ('prompt_tokens', 'completion_tokens')):
        return reserved, False
    # Conservatively charge all input at cache-write price, no discount assumptions.
    return (usage['prompt_tokens'] * 6.25 + usage['completion_tokens'] * 25) / 1e6, True


def prepare(root, source, budget=100, data_version="main-720-v2"):
    if not math.isfinite(budget) or budget <= 0:
        raise ValueError("positive finite budget required")
    plans = [json.loads(s) for s in Path(source).read_text().splitlines() if s.strip()]
    if not plans or len({p['doc_id'] for p in plans}) != len(plans):
        raise ValueError('expected unique nonempty plans')
    for p in plans:
        p['generator_slice'] = 'api-main'
    # Select a deterministic, type-diverse canary; keep all original plan seeds.
    first, rest, seen = [], [], set()
    for p in plans:
        if p['doc_type'] not in seen:
            seen.add(p['doc_type']); first.append(p)
        else:
            rest.append(p)
    root.mkdir(parents=True, exist_ok=False)
    ordered = first + rest
    batch._atomic(root / 'plan.jsonl', batch._jsonl(ordered))
    batch.prepare(root / 'plan.jsonl', root / 'frozen', 'gpt-6-astra', 'compose_v7')
    frozen, _, requests = batch._load(root / 'frozen')
    sources = list(Path('src/generate').glob('*.py')) + [Path(__file__), Path('src/prompts/compose_v7.txt'), Path('taxonomy/taxonomy.yaml')]
    manifest = {'run_id': root.name, 'model': 'gpt-6-astra', 'prompt_version': 'compose_v7',
                'budget_usd': budget, 'data_version': data_version, 'target': len(plans), 'canary_size': len(first), 'wave_size': 40,
                'git_commit': subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip(),
                'sources': {str(p.resolve()): batch._sha(p.read_bytes()) for p in sources},
                'frozen_manifest_sha256': batch._sha((root / 'frozen/manifest.json').read_bytes()),
                'prices': {'input_conservative': 6.25, 'output': 25},
                'quality_gate': 'complete and validated >=80% per wave; canary must include accepted 16k',
                'price_source': 'https://developers.openai.com/api/docs/models/gpt-6-astra'}
    batch._atomic(root / 'manifest.json', batch._json(manifest))
    batch._atomic(root / 'state.json', batch._json({'manifest_sha256':batch._sha(batch._json(manifest).encode()),
                  'cursor':0,'waves':[],'estimated_committed_usd':0,'status':'prepared'}))
    return {'planned':len(plans),'canary':len(first),'canary_reserve_usd':sum(map(reserve,requests[:len(first)])),'budget_usd':budget}


def settle(root, wave, tax):
    job = root / wave['name']
    manifest, _, requests = batch._load(job)
    rows = batch._read_jsonl((job / 'raw.jsonl').read_text())
    by_id = {r['doc_id']:r for r in rows}
    docs, errors, total, known = [], [], 0, True
    long_ok = False
    for request in requests:
        row = by_id.get(request['custom_id'])
        usage = row['completion'].get('usage') if row else None
        amount, certain = response_cost(usage, reserve(request))
        total += amount; known &= certain
        if not row:
            errors.append({'doc_id':request['custom_id'],'errors':['no successful API response']}); continue
        doc, errs = fill_one(tax, Plan(**row['plan']), row['raw'], row['model'], row['prompt_version'])
        if row['completion'].get('finish_reason') != 'stop' or not row['raw'].strip():
            errs.append('incomplete/empty response')
        if errs:
            errors.append({'doc_id':row['doc_id'],'errors':errs})
        else:
            doc.generator.update(run_id=root.name, data_version=json.loads((root/'manifest.json').read_text()).get('data_version', 'main-720-v2'),
                                 git_commit=json.loads((root/'manifest.json').read_text())['git_commit'],
                                 batch_id=row['completion']['batch_id'], transport='batch')
            docs.append(doc.to_json())
            long_ok |= row['plan']['context_len_bucket']=='16k' and doc.context_len_bucket=='16k'
    batch._atomic(job/'docs.jsonl', batch._jsonl(docs))
    batch._atomic(job/'validation-errors.json', batch._json(errors))
    return {'cost_usd':total,'usage_known':known,'accepted':len(docs),'failed':len(errors),'long_ok':long_ok}


def report(root):
    state = json.loads((root/'state.json').read_text())
    docs=[]
    for w in state['waves']:
        if w.get('settled'):
            docs += batch._read_jsonl((root/w['name']/'docs.jsonl').read_text())
    batch._atomic(root/'docs.jsonl',batch._jsonl(docs))
    summary={'target':json.loads((root/'manifest.json').read_text())['target'],'accepted':len(docs),'submitted':state['cursor'],
             'estimated_committed_usd':state['estimated_committed_usd'],'budget_usd':json.loads((root/'manifest.json').read_text())['budget_usd'],
             'status':state['status'],'human_reviewed':False,'waves':state['waves']}
    batch._atomic(root/'summary.json',batch._json(summary))
    return summary


def run(root):
    with batch._locked(root):
        manifest=json.loads((root/'manifest.json').read_text())
        state=json.loads((root/'state.json').read_text())
        if batch._sha((root/'manifest.json').read_bytes())!=state['manifest_sha256']:
            raise ValueError('manifest changed')
        for path,digest in manifest['sources'].items():
            if batch._sha(Path(path).read_bytes())!=digest: raise ValueError('source changed')
        if batch._sha((root/'frozen/manifest.json').read_bytes())!=manifest['frozen_manifest_sha256']:
            raise ValueError('frozen manifest changed')
        frozen,_,requests=batch._load(root/'frozen')
        tax=Taxonomy()
        if state['status'] not in {'prepared','running','waiting'}: return report(root)
        while True:
            if state['waves'] and not state['waves'][-1].get('settled'):
                wave=state['waves'][-1]; job=root/wave['name']
            else:
                if state['cursor']>=len(requests): state['status']='all_attempted'; break
                count=manifest['canary_size'] if not state['waves'] else manifest['wave_size']
                chosen=[]; reservation=0
                for request in requests[state['cursor']:state['cursor']+count]:
                    price=reserve(request)
                    if state['estimated_committed_usd']+reservation+price>manifest['budget_usd']: break
                    chosen.append(request);reservation+=price
                if not chosen: state['status']='budget'; break
                name=f'wave-{len(state["waves"]):03d}'; job=root/name
                child={**frozen,'records':{r['custom_id']:frozen['records'][r['custom_id']] for r in chosen}}
                if not job.exists(): batch._new_job(job,child,chosen)
                else:
                    _,_,existing=batch._load(job)
                    if existing!=chosen: raise ValueError('orphan wave mismatch')
                wave={'name':name,'count':len(chosen),'reserved_usd':reservation,'settled':False}
                state['waves'].append(wave);state['cursor']+=len(chosen)
                state['estimated_committed_usd']+=reservation
                state['status']='running'
                batch._atomic(root/'state.json',batch._json(state))
            submitted=batch.submit(job)
            wave['batch_id']=submitted.get('id') or submitted.get('batch_id')
            remote=batch.status(job)
            wave['remote_status']=remote['status']
            if remote['status'] not in batch.TERMINAL:
                state['status']='waiting'
                batch._atomic(root/'state.json',batch._json(state));report(root)
                time.sleep(60)
                continue
            batch.collect(job)
            outcome=settle(root,wave,tax)
            state['estimated_committed_usd']+=outcome['cost_usd']-wave['reserved_usd']
            wave.update(outcome,settled=True)
            state['status']='running'
            if outcome['cost_usd']>wave['reserved_usd']: state['status']='reservation_exceeded'
            elif not outcome['usage_known']: state['status']='usage_unknown'
            elif outcome['accepted']/wave['count']<.8: state['status']='quality_gate'
            elif len(state['waves'])==1 and not outcome['long_ok']: state['status']='long_canary_failed'
            batch._atomic(root/'state.json',batch._json(state));print(json.dumps(report(root)),flush=True)
            if state['status']!='running': break
        batch._atomic(root/'state.json',batch._json(state))
        return report(root)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['prepare','run','report'])
    p.add_argument('--directory',required=True,type=Path);p.add_argument('--plan')
    p.add_argument('--budget', type=float, default=100)
    p.add_argument('--data-version', default='main-720-v2')
    a=p.parse_args()
    try:
        result=prepare(a.directory,a.plan,a.budget,a.data_version) if a.command=='prepare' else run(a.directory) if a.command=='run' else report(a.directory)
    except Exception as exc:
        # Do not expose API bodies/credentials. Intent and reservations remain durable.
        if a.command=='run':
            s=json.loads((a.directory/'state.json').read_text());s.update(status='execution_error',error_type=type(exc).__name__)
            batch._atomic(a.directory/'state.json',batch._json(s));report(a.directory)
        raise
    print(json.dumps(result,ensure_ascii=False,indent=2))
