"""Explicit foreign-runner replay under ADR-0038; no source-stamp substitution.

Shares frozen ADR-0036 scoring helpers but intentionally has a distinct provenance
contract. Native-run analyze() and all live execution/export guards are unchanged.
"""
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
from . import response_diagnostics as base
from .response_diagnostics import (VERSION, STAGES, FENCE, file_sha, read_rows,
                                   itemwise_decode, stage_score)
from src.eval import metrics, protocol
from src.generate.taxonomy import Taxonomy, DEFAULT_PATH


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
    if not execution.get('runner') or not execution.get('source_sha256'):
        raise ValueError('external runner identity and original source hashes required')
    if not benchmark:
        raise ValueError('external replay requires a completed benchmark')
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
            'external_runner_replay': True,
            'original_runner': execution['runner'],
            'original_runner_source_sha256': execution['source_sha256'],
            'diagnostic_algorithm_source_sha256': file_sha(base.__file__),
            'frozen_scoring_source_sha256': {Path(m.__file__).name: file_sha(m.__file__) for m in (protocol, metrics)},
            'requests_sha256': manifest['requests_sha256'],
            'recorded_cohort_sha256': execution.get('cohort_sha256'),
            'capacity_eligibility_independently_verified': False},
        'interpretation': [
            'External runner: input/output replay does not establish runner source or server equivalence.',
            'Original execution metadata and gate hashes were not changed; not eligible for headline export.',
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

