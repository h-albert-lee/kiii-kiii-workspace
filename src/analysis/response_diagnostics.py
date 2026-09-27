"""Post-hoc response decomposition, with the original strict score preserved.

No inference, fuzzy anchoring, gold-guided repair, or partial-run export.
See docs/guide/response-diagnostics.md and ADR-0036 for metric definitions.
"""
import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess

from src.eval import metrics, protocol
from src.generate.taxonomy import Taxonomy, DEFAULT_PATH

VERSION = 'response_diagnostics_v1'
STAGES = ('strict', 'itemwise', 'fence_itemwise')
UNASSIGNED = '__unassigned_invalid_item__'
FENCE = re.compile(r'```(?:json)?[ \t]*\r?\n([\s\S]*?)\r?\n```', re.IGNORECASE)


def file_sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read_rows(path):
    with Path(path).open(encoding='utf-8') as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def itemwise_decode(request, response, text, categories, unwrap=False):
    """Reuse strict single-item validation; only response atomicity is relaxed."""
    info = {'route': 'terminal_failure', 'parsed': False, 'items': 0,
            'valid_items': 0, 'invalid_items': 0, 'invalid_by_category': {},
            'errors': {}}
    if (response.get('status') != 'ok' or
            response.get('finish_reason') not in {'stop', 'end_turn', 'STOP'}):
        info['errors'] = {'request_failed_or_truncated': 1}
        return [], info
    value = response.get('text')
    info['route'] = 'raw_json'
    if unwrap and isinstance(value, str):
        match = FENCE.fullmatch(value.strip())
        if match:
            value = match.group(1)
            info['route'] = 'whole_json_fence'
    try:
        parsed = json.loads(value)
        if (not isinstance(parsed, dict) or set(parsed) != {'spans'} or
                not isinstance(parsed['spans'], list)):
            raise ValueError('schema')
    except (ValueError, TypeError):
        info['errors'] = {'invalid_json_or_schema': 1}
        return [], info
    info.update(parsed=True, items=len(parsed['spans']))
    spans, invalid, errors = [], Counter(), Counter()
    for item in parsed['spans']:
        one = {**response, 'text': json.dumps({'spans': [item]}, ensure_ascii=False)}
        accepted, rejected = protocol.decode(request, one, text, categories)
        if rejected:
            category = item.get('category') if isinstance(item, dict) else None
            label = category if isinstance(category, str) and category in categories else UNASSIGNED
            invalid[label] += 1
            errors.update(e.split(':', 1)[-1] if e.startswith('item_') else e for e in rejected)
        else:
            info['valid_items'] += 1
            spans.extend(accepted)
    info.update(invalid_items=sum(invalid.values()), invalid_by_category=dict(invalid), errors=dict(errors))
    # Same deterministic duplicate policy as strict decode, not a boundary repair.
    spans = [dict(start=a, end=b, category=c) for a, b, c in sorted({metrics.key(s) for s in spans})]
    return spans, info


def merged_intervals(spans):
    merged = []
    for start, end in sorted((s['start'], s['end']) for s in spans):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    return merged


def character_counts(gold, predictions):
    """Union coverage in Unicode characters; inputs must have the same category."""
    g, p = merged_intervals(gold), merged_intervals(predictions)
    i = j = overlap = 0
    while i < len(g) and j < len(p):
        overlap += max(0, min(g[i][1], p[j][1]) - max(g[i][0], p[j][0]))
        if g[i][1] <= p[j][1]:
            i += 1
        else:
            j += 1
    return Counter(tp=overlap, fp=sum(b-a for a, b in p)-overlap,
                   fn=sum(b-a for a, b in g)-overlap)


def counts_prf(counts):
    return metrics.prf(*(counts[k] for k in ('tp', 'fp', 'fn')))


def stage_score(docs, predictions, invalid_by_doc, taxonomy):
    """Invalid items cost one FP each in exact metrics, never character units."""
    result = metrics.score_corpus(docs, predictions, taxonomy)
    result['metrics']['anchored_exact_micro'] = dict(result['metrics']['exact_micro'])
    invalid_total = sum(sum(v.values()) for v in invalid_by_doc.values())
    for row in result['per_document']:
        penalty = sum(invalid_by_doc.get(row['doc_id'], {}).values())
        row['anchored_exact'] = dict(row['exact'])
        row['invalid_items'] = penalty
        exact = row['exact']
        row['exact'] = metrics.prf(exact['tp'], exact['fp'] + penalty, exact['fn'])
    result['metrics']['exact_micro'] = metrics.aggregate(result['per_document'])
    result['metrics']['f1_micro'] = result['metrics']['exact_micro']['f1']
    result['metrics']['invalid_item_false_positives'] = invalid_total
    for axis in result['by_axis']:
        result['by_axis'][axis] = {
            str(v): metrics.aggregate([r for r in result['per_document'] if r[axis] == v])
            for v in sorted({r[axis] for r in result['per_document']}, key=str)}
    by_category = {k: Counter({n: v[n] for n in ('tp', 'fp', 'fn')})
                   for k, v in result['by_category'].items()}
    by_tier = {k: Counter({n: v[n] for n in ('tp', 'fp', 'fn')})
               for k, v in result['tier_kind_tlevel'].items()}
    char_category, char_tier = defaultdict(Counter), defaultdict(Counter)
    for doc in docs:
        for label, count in invalid_by_doc.get(doc['doc_id'], {}).items():
            by_category.setdefault(label, Counter())['fp'] += count
            c = taxonomy.categories.get(label)
            group = f'{c.tier}/{c.kind}' if c else 'unassigned/invalid_item'
            by_tier.setdefault(f'{group}/{doc["variation_level"]}', Counter())['fp'] += count
        gs, ps = defaultdict(list), defaultdict(list)
        for s in doc['spans']:
            gs[s['category']].append(s)
        for s in predictions.get(doc['doc_id'], []):
            ps[s['category']].append(s)
        for category in gs.keys() | ps.keys():
            count = character_counts(gs[category], ps[category])
            char_category[category].update(count)
            c = taxonomy.categories[category]
            char_tier[f'{c.tier}/{c.kind}/{doc["variation_level"]}'].update(count)
    result['by_category'] = {k: counts_prf(v) for k, v in sorted(by_category.items())}
    result['tier_kind_tlevel'] = {k: counts_prf(v) for k, v in sorted(by_tier.items())}
    result['character_coverage_breakdowns'] = {
        'by_axis': {axis: {
            str(v): metrics.aggregate([r for r in result['per_document'] if r[axis] == v], 'character')
            for v in sorted({r[axis] for r in result['per_document']}, key=str)}
            for axis in result['by_axis']},
        'by_category': {k: counts_prf(v) for k, v in sorted(char_category.items())},
        'tier_kind_tlevel': {k: counts_prf(v) for k, v in sorted(char_tier.items())}}
    return result


def analyze(gold_path, response_path, strict_path, output, allow_pilot=False):
    output = Path(output)
    if output.exists():
        raise ValueError('output must be a new directory; never overwrite runs or analyses')
    reference = json.loads(Path(strict_path).read_text())
    manifest = reference['manifest']
    execution = reference.get('execution', {})
    benchmark = manifest.get('purpose') == 'benchmark'
    if not benchmark and not allow_pilot:
        raise ValueError('pilot/smoke diagnostics require explicit --allow-pilot; never headline')
    accounting = execution.get('accounting', {})
    if (accounting.get('complete') is not True or
            accounting.get('finished_requests') != manifest['requests'] or
            accounting.get('planned_requests') != manifest['requests']):
        raise ValueError('require a complete finalized run, including failures')
    if benchmark and not execution.get('cohort_sha256'):
        raise ValueError('benchmark reference must record a cohort gate')
    if (execution.get('data_sha256') != manifest['data_sha256'] or
            execution.get('requests_sha256') != manifest['requests_sha256']):
        raise ValueError('execution/manifest mismatch')
    for module in (protocol, metrics):
        name = Path(module.__file__).name
        if file_sha(module.__file__) != execution.get('source_sha256', {}).get(name):
            raise ValueError(f'frozen scoring source differs: {name}')
    expected_files = [(gold_path, manifest['data_sha256']),
                      (response_path, reference['response_sha256']),
                      (DEFAULT_PATH, manifest['taxonomy_sha256'])]
    for path, expected in expected_files:
        if file_sha(path) != expected:
            raise ValueError(f'input hash mismatch: {Path(path).name}')
    docs = list(read_rows(gold_path))
    if len(docs) != manifest['documents'] or len({d['doc_id'] for d in docs}) != len(docs):
        raise ValueError('document inventory mismatch/duplicates')
    responses = {}
    for response in read_rows(response_path):
        rid = response['request_id']
        if rid in responses:
            raise ValueError('duplicate response request ID')
        responses[rid] = response
    if len(responses) != manifest['requests']:
        raise ValueError('response coverage differs from finalized plan')
    taxonomy = Taxonomy()
    definition = protocol.Protocol(**manifest['protocol'])
    predictions = {stage: defaultdict(list) for stage in STAGES}
    invalid = {stage: defaultdict(Counter) for stage in STAGES}
    summaries = {stage: Counter() for stage in STAGES}
    ledger, strict_failures, seen = [], [], set()
    request_hash = hashlib.sha256()
    for doc in docs:
        for request in protocol.requests_for(doc['doc_id'], doc['text'], taxonomy, definition):
            request_hash.update((json.dumps(request, ensure_ascii=False) + '\n').encode())
            rid = request['request_id']
            response = responses.get(rid)
            if (response is None or response.get('model') != reference['model'] or
                    response.get('request_sha256') != request['request_sha256']):
                raise ValueError('missing response or model/request hash mismatch')
            seen.add(rid)
            spans, errors = protocol.decode(request, response, doc['text'], taxonomy.categories)
            predictions['strict'][doc['doc_id']].extend(spans)
            summaries['strict']['requests_with_errors'] += bool(errors)
            summaries['strict']['requests_with_predictions'] += bool(spans)
            if errors:
                strict_failures.append({'request_id': rid, 'errors': errors})
            audit = {'request_id': rid, 'doc_id': doc['doc_id'],
                     'strict_errors': errors, 'strict_accepted_spans': len(spans)}
            raw_spans, raw_info = itemwise_decode(request, response, doc['text'], taxonomy.categories)
            for stage in STAGES[1:]:
                if stage == 'itemwise' or not FENCE.fullmatch(str(response.get('text', '')).strip()):
                    spans, info = raw_spans, raw_info
                else:
                    spans, info = itemwise_decode(request, response, doc['text'], taxonomy.categories, unwrap=True)
                predictions[stage][doc['doc_id']].extend(spans)
                invalid[stage][doc['doc_id']].update(info['invalid_by_category'])
                summary = summaries[stage]
                summary['requests_with_errors'] += bool(info['errors'])
                summary['requests_with_predictions'] += bool(spans)
                summary['requests_recovered_from_strict_failure'] += bool(errors and spans)
                summary['requests_parsed'] += info['parsed']
                summary['requests_fence_unwrapped'] += info['route'] == 'whole_json_fence'
                summary['requests_terminal_failure'] += info['route'] == 'terminal_failure'
                summary['invalid_items'] += info['invalid_items']
                summary['valid_items_before_deduplication'] += info['valid_items']
                audit[stage] = dict(info, accepted_spans=len(spans))
            ledger.append(audit)
    if seen != set(responses) or request_hash.hexdigest() != manifest['requests_sha256']:
        raise ValueError('reconstructed request plan differs from archived plan')
    if (strict_failures != reference['reliability']['failures'] or
            reference['reliability']['requests'] != manifest['requests'] or
            reference['reliability']['failed_requests'] != len(strict_failures)):
        raise ValueError('strict failure replay differs from archived result')
    original = metrics.score_corpus(docs, predictions['strict'], taxonomy)
    if any(value != reference.get(key) for key, value in original.items()):
        raise ValueError('strict score replay differs from archived result')
    stages = {}
    for stage in STAGES:
        stages[stage] = stage_score(docs, predictions[stage], invalid[stage], taxonomy)
        stages[stage]['request_diagnostics'] = dict(summaries[stage], requests=manifest['requests'])
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        commit = 'unavailable'
    result = {
        'analysis_version': VERSION, 'purpose': 'posthoc_secondary_diagnostics',
        'input_scope': 'completed_benchmark' if benchmark else 'pilot_or_smoke',
        'headline_eligible': False, 'model': reference['model'], 'protocol': manifest['protocol'],
        'documents': len(docs), 'requests': manifest['requests'],
        'provenance': {
            'git_commit': commit, 'strict_replay_verified': True,
            'inputs': {'gold_sha256': file_sha(gold_path), 'responses_sha256': file_sha(response_path),
                       'strict_result_sha256': file_sha(strict_path), 'taxonomy_sha256': file_sha(DEFAULT_PATH)},
            'analysis_source_sha256': file_sha(__file__),
            'frozen_scoring_source_sha256': {Path(m.__file__).name: file_sha(m.__file__) for m in (protocol, metrics)},
            'requests_sha256': manifest['requests_sha256'],
            'recorded_cohort_sha256': execution.get('cohort_sha256'),
            'capacity_eligibility_independently_verified': False},
        'interpretation': [
            'Selected after observing strict failures; exploratory, not preregistered.',
            'All gold and all requests remain in every denominator; no success-only scoring.',
            'Itemwise exact precision includes one FP per invalid parsed item; unknown labels use an unassigned bucket.',
            'Character coverage uses valid anchored predictions and all gold. Unanchorable invalid items cannot be assigned character FP; interpret with exact penalized precision and invalid-item counts.',
            'Whole-response parse/terminal failures remain empty. Their item count is unknown, not estimated.',
            'No quote, occurrence, category, truncation or boundary repair; no new model calls.',
            'Stage differences are diagnostic, not independent or necessarily monotonic gains.'],
        'stages': stages}
    output.mkdir(parents=True, exist_ok=False)
    (output/'analysis.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    with (output/'per_request.jsonl.gz').open('wb') as stream:
        with gzip.GzipFile(filename='', mode='wb', fileobj=stream, mtime=0) as compressed:
            for row in ledger:
                compressed.write((json.dumps(row, ensure_ascii=False) + '\n').encode())
    summary_rows = []
    for stage, values in stages.items():
        exact = values['metrics']['exact_micro']
        char = values['metrics']['category_character_micro']
        summary_rows.append(dict(model=reference['model'], condition=definition.mode, stage=stage,
            documents=len(docs), requests=manifest['requests'],
            exact_precision=exact['precision'], exact_recall=exact['recall'], exact_f1=exact['f1'],
            character_precision=char['precision'], character_recall=char['recall'], character_f1=char['f1'],
            invalid_items=values['metrics']['invalid_item_false_positives'],
            requests_with_errors=values['request_diagnostics']['requests_with_errors']))
    with (output/'summary.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=summary_rows[0])
        writer.writeheader()
        writer.writerows(summary_rows)
    lines = ['# Response diagnostics (secondary only)', '',
             f"Model: `{reference['model']}`. Condition: `{definition.mode}`. Scope: `{result['input_scope']}`.",
             '', 'Strict results were replayed and match the archived metrics and every document. Original inputs were not modified.',
             '', '| Stage | Exact F1 / 100 | Character F1 / 100 | Invalid items (exact FP penalty) |',
             '|---|---:|---:|---:|']
    for row in summary_rows:
        lines.append(f"| {row['stage']} | {100*row['exact_f1']:.4f} | {100*row['character_f1']:.4f} | {row['invalid_items']} |")
    lines += ['', *['- ' + s for s in result['interpretation']], '',
              'Native counts and the underlying cohort gate were not independently checked by this offline analysis. See analysis.json for input and code hashes; per_request.jsonl.gz retains diagnostics without copying completion text.']
    (output/'REPORT.md').write_text('\n'.join(lines) + '\n')
    (output/'ARTIFACTS.sha256').write_text(''.join(
        f'{file_sha(path)}  {path.name}\n' for path in sorted(output.iterdir()) if path.is_file()))
    return summary_rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gold', required=True)
    parser.add_argument('--responses', required=True)
    parser.add_argument('--strict-result', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--allow-pilot', action='store_true')
    args = parser.parse_args()
    rows = analyze(args.gold, args.responses, args.strict_result, args.output, args.allow_pilot)
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
