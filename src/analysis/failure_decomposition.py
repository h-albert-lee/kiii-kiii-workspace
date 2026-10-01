"""Post-hoc format, grounding and detection diagnostics (ADR-0037).

Never changes the live decoder or reconstructs invalid output with gold.
"""
import argparse
from collections import Counter
import csv
import gzip
import hashlib
import json
from pathlib import Path

from .response_diagnostics import FENCE, file_sha, read_rows, itemwise_decode
from src.eval import protocol, metrics
from src.generate.taxonomy import Taxonomy, DEFAULT_PATH

VERSION = 'failure_decomposition_v1'


def parsed_body(value):
    """Parse only raw JSON or a single whole-response fence; observe duplicates."""
    if not isinstance(value, str):
        return None, 'invalid_json', 0
    match = FENCE.fullmatch(value.strip())
    route = 'fence' if match else 'raw'
    duplicates = []
    def hook(pairs):
        seen = set()
        for k, _ in pairs:
            if k in seen:
                duplicates.append(k)
            seen.add(k)
        return dict(pairs)  # Preserve frozen parser last-value behavior.
    try:
        body = json.loads(match.group(1) if match else value, object_pairs_hook=hook)
    except (ValueError, TypeError):
        return None, 'invalid_json', 0
    if not isinstance(body, dict) or set(body) != {'spans'} or not isinstance(body['spans'], list):
        return None, 'root_schema', len(duplicates)
    return body['spans'], route, len(duplicates)


def structure_ok(item):
    return (isinstance(item, dict) and set(item) == {'category', 'text', 'occurrence'}
            and isinstance(item['category'], str) and isinstance(item['text'], str)
            and bool(item['text']) and type(item['occurrence']) is int and item['occurrence'] >= 1)


def item_outcome(item, request, text, categories):
    """One ordered cause per parsed item; gold is deliberately unavailable."""
    if not isinstance(item, dict) or set(item) != {'category', 'text', 'occurrence'}:
        return 'item_schema'
    if not isinstance(item['category'], str) or item['category'] not in categories:
        return 'invalid_category'
    if not isinstance(item['text'], str) or not item['text']:
        return 'invalid_quote_field'
    n = item['occurrence']
    if type(n) is not int or n < 1:
        return 'invalid_occurrence_field'
    w = request['window']
    found = list(protocol.occurrences(text[w['target_start']:w['target_end']], item['text']))
    if not found:
        return 'quote_absent_from_target'
    if n > len(found):
        return 'occurrence_out_of_range'
    start = w['target_start'] + found[n-1]
    if not w['core_start'] <= start < w['core_end']:
        return 'outside_owned_core'
    return 'valid'


def request_outcome(response, items, route):
    if response.get('status') != 'ok' or response.get('finish_reason') not in {'stop', 'end_turn', 'STOP'}:
        return 'output_truncated' if response.get('finish_reason') in {'length', 'MAX_TOKENS', 'max_tokens'} else 'other_terminal_failure'
    if items is None:
        return route
    return 'empty_list' if not items else 'nonempty_list'


def gold_outcome(gold, predictions, owner, rejected_items):
    """Descriptive priority partition, not causal attribution or matching repair."""
    g = metrics.key(gold)
    if g in predictions:
        return 'exact_hit'
    if owner in {'output_truncated', 'other_terminal_failure', 'invalid_json', 'root_schema', 'empty_list'}:
        return owner
    if any(p[:2] == g[:2] for p in predictions):
        return 'exact_boundary_wrong_category'
    overlap = [p for p in predictions if p[0] < g[1] and g[0] < p[1]]
    if any(p[2] == g[2] for p in overlap):
        return 'overlapping_boundary_same_category'
    if overlap:
        return 'overlapping_boundary_wrong_category'
    return 'unresolved_with_rejected_items' if rejected_items else 'no_overlapping_prediction'


def prf_sets(gold, pred, penalty=0):
    return metrics.prf(len(gold & pred), len(pred-gold)+penalty, len(gold-pred))


def analyze(gold_path, responses_path, reference_path, diagnostics_path, output):
    out = Path(output)
    if out.exists():
        raise ValueError('output must be new')
    ref = json.loads(Path(reference_path).read_text())
    diag = json.loads(Path(diagnostics_path).read_text())
    m = ref['manifest']; ex = ref['execution']; prov = diag['provenance']
    if (m.get('purpose') != 'benchmark' or ex.get('accounting', {}).get('complete') is not True
            or not ex.get('cohort_sha256') or diag.get('input_scope') != 'completed_benchmark'
            or diag.get('headline_eligible') is not False or not prov.get('strict_replay_verified')):
        raise ValueError('complete replay-verified benchmark required')
    for p, expected in [(gold_path,m['data_sha256']), (responses_path,ref['response_sha256']),
                        (DEFAULT_PATH,m['taxonomy_sha256'])]:
        if file_sha(p) != expected:
            raise ValueError('input hash mismatch')
    expected_inputs = dict(gold_sha256=file_sha(gold_path), responses_sha256=file_sha(responses_path),
                           strict_result_sha256=file_sha(reference_path), taxonomy_sha256=file_sha(DEFAULT_PATH))
    if prov['inputs'] != expected_inputs or prov['recorded_cohort_sha256'] != ex['cohort_sha256']:
        raise ValueError('diagnostic provenance mismatch')
    for mod in (protocol, metrics):
        if file_sha(mod.__file__) != ex['source_sha256'][Path(mod.__file__).name]:
            raise ValueError('frozen scorer mismatch')
    if prov['analysis_source_sha256'] != file_sha(Path(__file__).with_name('response_diagnostics.py')):
        raise ValueError('diagnostic source mismatch')
    docs = list(read_rows(gold_path)); responses = list(read_rows(responses_path))
    reply = {r['request_id']:r for r in responses}
    if len(reply) != len(responses) or len(reply) != m['requests']:
        raise ValueError('response coverage mismatch')
    if len(docs) != m['documents'] or len({d['doc_id'] for d in docs}) != len(docs):
        raise ValueError('document coverage mismatch')
    tax = Taxonomy(); definition = protocol.Protocol(**m['protocol'])
    stage = diag['stages']['fence_itemwise']
    old_docs = {r['doc_id']:r for r in ref['per_document']}
    diag_docs = {r['doc_id']:r for r in stage['per_document']}
    request_counts, items_counts, gold_counts = Counter(), Counter(), Counter()
    doc_rows=[]; ledger=[]; failures=[]; seen=set(); plan_hash=hashlib.sha256()
    location_total=Counter(); exact_total=Counter()
    for doc in docs:
        predictions=set(); strict=set(); owner_rows=[]; invalid=0
        for req in protocol.requests_for(doc['doc_id'], doc['text'], tax, definition):
            plan_hash.update((json.dumps(req,ensure_ascii=False)+'\n').encode())
            rid=req['request_id']; r=reply.get(rid)
            if r is None or r.get('model') != ref['model'] or r.get('request_sha256') != req['request_sha256']:
                raise ValueError('model/request hash mismatch')
            seen.add(rid)
            spans, errors=protocol.decode(req,r,doc['text'],tax.categories)
            strict.update(map(metrics.key,spans))
            if errors: failures.append(dict(request_id=rid,errors=errors))
            spans, info=itemwise_decode(req,r,doc['text'],tax.categories,unwrap=True)
            predictions.update(map(metrics.key,spans)); invalid+=info['invalid_items']
            items,route,duplicates=parsed_body(r.get('text'))
            outcome=request_outcome(r,items,route)
            usable=outcome in {'empty_list','nonempty_list'}
            counts=Counter(item_outcome(i,req,doc['text'],tax.categories) for i in items) if usable else Counter()
            assert sum(v for k,v in counts.items() if k!='valid')==info['invalid_items']
            assert counts['valid']==info['valid_items']
            items_counts.update(counts)
            format_ok=usable and route=='raw' and duplicates==0 and all(structure_ok(i) for i in items)
            request_counts[outcome]+=1; request_counts['total']+=1
            request_counts['format_compliant']+=format_ok
            request_counts['duplicate_key_requests']+=duplicates>0
            request_counts['whole_fence_parseable']+=usable and route=='fence'
            request_counts['strict_rejected']+=bool(errors)
            row=dict(request_id=rid,outcome=outcome,format_compliant=format_ok,
                     duplicate_keys=duplicates,route=route,item_outcomes=dict(counts),
                     invalid_items=info['invalid_items'],gold_outcomes={})
            owner_rows.append((req['window'],row));ledger.append(row)
        gold={metrics.key(s) for s in doc['spans']}
        exact=prf_sets(gold,predictions,invalid)
        assert exact==diag_docs[doc['doc_id']]['exact']
        assert prf_sets(gold,strict)==old_docs[doc['doc_id']]['exact']
        assert invalid==diag_docs[doc['doc_id']]['invalid_items']
        location=prf_sets({g[:2] for g in gold},{p[:2] for p in predictions},invalid)
        local_gold=Counter()
        for g in sorted(gold):
            owners=[row for w,row in owner_rows if w['core_start']<=g[0]<w['core_end']]
            assert len(owners)==1
            owner=owners[0]
            label=gold_outcome(dict(start=g[0],end=g[1],category=g[2]),predictions,owner['outcome'],owner['invalid_items'])
            local_gold[label]+=1;owner['gold_outcomes'][label]=owner['gold_outcomes'].get(label,0)+1
        assert local_gold['exact_hit']==exact['tp'] and sum(local_gold.values())==len(gold)
        gold_counts.update(local_gold)
        exact_total.update({k:exact[k] for k in ('tp','fp','fn')})
        location_total.update({k:location[k] for k in ('tp','fp','fn')})
        doc_rows.append(dict(doc_id=doc['doc_id'],gold_outcomes=dict(local_gold),exact=exact,location=location))
    if seen!=set(reply) or plan_hash.hexdigest()!=m['requests_sha256'] or failures!=ref['reliability']['failures']:
        raise ValueError('plan/failure replay mismatch')
    exact=metrics.prf(**exact_total); location=metrics.prf(**location_total)
    assert exact==stage['metrics']['exact_micro']
    assert exact['tp']+exact['fn']==sum(gold_counts.values())
    result=dict(version=VERSION,purpose='posthoc_failure_decomposition',headline_eligible=False,
                model=ref['model'],condition=m['protocol']['mode'],documents=len(docs),
                request_counts=dict(request_counts),item_outcomes=dict(items_counts),gold_outcomes=dict(gold_counts),
                strict_exact=ref['metrics']['exact_micro'],itemwise_exact=exact,
                valid_item_location_exact=location,
                typed_character=stage['metrics']['category_character_micro'],
                invalid_item_fp=sum(v for k,v in items_counts.items() if k!='valid'),per_document=doc_rows,
                provenance=dict(inputs=expected_inputs,diagnostics_sha256=file_sha(diagnostics_path),
                                source_sha256=file_sha(__file__),recorded_cohort_sha256=ex['cohort_sha256'],
                                strict_and_itemwise_replayed=True,capacity_independently_verified=False),
                limitations=['Post-hoc descriptive partitions, not causal or latent detection ability.',
                             'All gold retained. No success-only performance or gold-guided repair.',
                             'Location-only scores use valid known-category anchored items; invalid labels remain penalized and excluded.',
                             'Duplicate keys retain last-value scoring but fail format compliance; counts after JSON collapse can undercount items.',
                             'Gold priority buckets may hide multiple simultaneous issues; rejected items cannot be aligned to individual gold misses.',
                             'Character scores cannot penalize unanchorable items. Location scores collapse identical boundaries across labels.'])
    out.mkdir(parents=True)
    (out/'analysis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    with (out/'per_request.jsonl.gz').open('wb') as stream:
        with gzip.GzipFile(filename='',mode='wb',fileobj=stream,mtime=0) as z:
            for row in ledger:z.write((json.dumps(row,ensure_ascii=False)+'\n').encode())
    (out/'ARTIFACTS.sha256').write_text(''.join(f'{file_sha(p)}  {p.name}\n' for p in sorted(out.iterdir()) if p.is_file()))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('gold','responses','reference','diagnostics','output'):p.add_argument('--'+name,required=True)
    args=p.parse_args();r=analyze(args.gold,args.responses,args.reference,args.diagnostics,args.output)
    print(json.dumps(dict(model=r['model'],condition=r['condition'],request_counts=r['request_counts'],gold_outcomes=r['gold_outcomes'])))
