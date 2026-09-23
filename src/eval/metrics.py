"""Strict mention metrics + category-aware character coverage; never TAB claims."""
from collections import Counter, defaultdict
import random


def key(span): return span['start'], span['end'], span['category']


def prf(tp, fp, fn):
    p = tp/(tp+fp) if tp+fp else 0.0
    r = tp/(tp+fn) if tp+fn else 0.0
    return {'precision':p,'recall':r,'f1':2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0.0,
            'tp':tp,'fp':fp,'fn':fn}


def chars(spans, categorized=True):
    return {(s['category'],i) if categorized else i for s in spans for i in range(s['start'],s['end'])}


def score_document(doc, predictions):
    gold = {key(s) for s in doc['spans']}; pred = {key(s) for s in predictions}
    gc, pc = chars(doc['spans']), chars(predictions)
    entities=defaultdict(set)
    for s in doc['spans']: entities[s['entity_id']].add(key(s))
    neg_hits=sum(any(p['start']<n['end'] and n['start']<p['end'] for p in predictions)
                 for n in doc.get('hard_negatives',[]))
    gu, pu = chars(doc['spans'],False), chars(predictions,False)
    return {'doc_id':doc['doc_id'],'exact':prf(len(gold&pred),len(pred-gold),len(gold-pred)),
            'character':prf(len(gc&pc),len(pc-gc),len(gc-pc)),
            'entity_all_mentions_exact':{'hit':sum(v<=pred for v in entities.values()),'total':len(entities)},
            'hard_negative':{'hit':neg_hits,'total':len(doc.get('hard_negatives',[]))},
            'non_pii_masked_chars':len(pu-gu),'non_pii_chars':len(doc['text'])-len(gu),
            'doc_type':doc['doc_type'],'variation_level':doc['variation_level'],
            'context_len_bucket':doc['context_len_bucket'],'num_subjects':doc['num_subjects'],
            'generator_model':doc.get('generator',{}).get('model','unknown')}


def aggregate(rows, metric='exact'):
    return prf(*(sum(r[metric][k] for r in rows) for k in ('tp','fp','fn')))


def score_corpus(docs, predictions, taxonomy):
    rows=[score_document(d,predictions.get(d['doc_id'],[])) for d in docs]
    groups={}
    for axis in ('doc_type','variation_level','context_len_bucket','num_subjects','generator_model'):
        groups[axis]={str(v):aggregate([r for r in rows if r[axis]==v]) for v in sorted({r[axis] for r in rows},key=str)}
    typed=defaultdict(Counter); ops=defaultdict(Counter); roles=defaultdict(Counter); categories=defaultdict(Counter)
    for d in docs:
        gold={key(s) for s in d['spans']}; pred={key(s) for s in predictions.get(d['doc_id'],[])}
        for k in gold|pred:
            c=taxonomy.categories[k[2]]
            group=f'{c.tier}/{c.kind}/{d["variation_level"]}'
            typed[group]['tp' if k in gold and k in pred else 'fn' if k in gold else 'fp']+=1
            categories[k[2]]['tp' if k in gold and k in pred else 'fn' if k in gold else 'fp']+=1
        for s in d['spans']:
            for op in set(s.get('applied_ops',[])):
                ops[op]['total']+=1;ops[op]['hit']+=key(s) in pred
            roles[s['subject_role']]['total']+=1;roles[s['subject_role']]['hit']+=key(s) in pred
    negative_total=sum(r['hard_negative']['total'] for r in rows)
    negative_hits=sum(r['hard_negative']['hit'] for r in rows)
    entity_total=sum(r['entity_all_mentions_exact']['total'] for r in rows)
    entity_hits=sum(r['entity_all_mentions_exact']['hit'] for r in rows)
    return {'metrics':{'f1_micro':aggregate(rows)['f1'],'exact_micro':aggregate(rows),
                       'category_character_micro':aggregate(rows,'character'),
                       'entity_all_mentions_exact_recall':entity_hits/entity_total if entity_total else None,
                       'hard_negative_false_positive_rate':negative_hits/negative_total if negative_total else None,
                       'non_pii_character_mask_rate':sum(r['non_pii_masked_chars'] for r in rows)/max(1,sum(r['non_pii_chars'] for r in rows))},
            'by_axis':groups,'by_category':{k:prf(v['tp'],v['fp'],v['fn']) for k,v in sorted(categories.items())},
            'tier_kind_tlevel':{k:prf(v['tp'],v['fp'],v['fn']) for k,v in sorted(typed.items())},
            'op_exact_recall':{k:dict(v,recall=v['hit']/v['total']) for k,v in ops.items()},
            'subject_role_exact_recall':{k:dict(v,recall=v['hit']/v['total']) for k,v in roles.items()},
            'per_document':rows}


def paired_bootstrap(a, b, samples=2000, seed=0):
    aa={r['doc_id']:r for r in a};bb={r['doc_id']:r for r in b}
    if not aa or set(aa)!=set(bb) or len(aa)!=len(a) or len(bb)!=len(b):
        raise ValueError('paired bootstrap needs identical unique document sets')
    if samples<100: raise ValueError('at least 100 bootstrap samples')
    ids=sorted(aa);rng=random.Random(seed);delta=[]
    for _ in range(samples):
        draw=rng.choices(ids,k=len(ids))
        delta.append(aggregate([aa[i] for i in draw])['f1']-aggregate([bb[i] for i in draw])['f1'])
    delta.sort()
    return {'delta_f1':aggregate(a)['f1']-aggregate(b)['f1'],
            'ci95':[delta[int(.025*(samples-1))],delta[int(.975*(samples-1))]],'samples':samples,'seed':seed}
