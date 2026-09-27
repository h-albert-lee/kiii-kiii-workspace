import gzip
import json

import pytest

from src.analysis.response_diagnostics import (
    UNASSIGNED, analyze, character_counts, file_sha, itemwise_decode, stage_score,
)
from src.eval import metrics, protocol
from src.eval.run import load_plan, prepare, score, write_jsonl
from src.generate.taxonomy import Taxonomy


def doc():
    return dict(doc_id='fixture', text='😀김민수 김민수 끝', doc_type='fixture',
                variation_level='T0', context_len_bucket='1k', num_subjects=1,
                generator={'model': 'synthetic'}, hard_negatives=[],
                spans=[dict(start=a, end=b, category='person_name', entity_id='e1',
                            subject_role='customer') for a, b in [(1, 4), (5, 8)]])


def item(text='김민수', category='person_name', occurrence=1):
    return dict(text=text, category=category, occurrence=occurrence)


def reply(request, items):
    return dict(request_id=request['request_id'], request_sha256=request['request_sha256'],
                model='fixture-model', status='ok', finish_reason='stop',
                text=json.dumps({'spans': items}, ensure_ascii=False))


def test_atomic_vs_itemwise_invalid_fp_and_unchanged_gold():
    d = doc(); taxonomy = Taxonomy()
    r = next(protocol.requests_for(d['doc_id'], d['text'], taxonomy, protocol.Protocol()))
    response = reply(r, [item(), item('없는 이름'), item(category=['bad'])])
    assert protocol.decode(r, response, d['text'], taxonomy.categories)[0] == []
    spans, info = itemwise_decode(r, response, d['text'], taxonomy.categories)
    assert spans == [dict(start=1, end=4, category='person_name')]
    assert info['invalid_by_category'] == {'person_name': 1, UNASSIGNED: 1}
    scored = stage_score([d], {d['doc_id']: spans}, {d['doc_id']: info['invalid_by_category']}, taxonomy)
    assert scored['metrics']['exact_micro'] == metrics.prf(1, 2, 1)
    assert scored['metrics']['anchored_exact_micro'] == metrics.prf(1, 0, 1)
    assert scored['metrics']['category_character_micro'] == metrics.prf(3, 0, 3)
    for partition in ('by_category', 'tier_kind_tlevel'):
        for key in ('tp', 'fp', 'fn'):
            assert sum(v[key] for v in scored[partition].values()) == scored['metrics']['exact_micro'][key]
    assert scored['by_axis']['variation_level']['T0'] == metrics.prf(1, 2, 1)


def test_unicode_partial_boundary_dedup_and_wrong_label():
    d = doc(); t = Taxonomy()
    r = next(protocol.requests_for(d['doc_id'], d['text'], t, protocol.Protocol()))
    spans, info = itemwise_decode(r, reply(r, [item('민수'), item('민수'), item('김민수', 'address')]), d['text'], t.categories)
    assert info['valid_items'] == 3 and len(spans) == 2
    result = stage_score([d], {d['doc_id']: spans}, {}, t)
    assert result['metrics']['exact_micro'] == metrics.prf(0, 2, 2)
    assert result['metrics']['category_character_micro'] == metrics.prf(2, 3, 4)
    assert result['character_coverage_breakdowns']['by_category']['person_name'] == metrics.prf(2, 0, 4)
    assert result['character_coverage_breakdowns']['by_category']['address']['tp'] == 0


def test_interval_union_matches_character_sets():
    import random
    rng = random.Random(36)
    for _ in range(100):
        groups = [[dict(start=a, end=a+rng.randrange(1, 8), category='person_name')
                   for a in [rng.randrange(20) for _ in range(rng.randrange(8))]] for _ in range(2)]
        g, p = [metrics.chars(v) for v in groups]
        assert character_counts(*groups) == dict(tp=len(g & p), fp=len(p-g), fn=len(g-p))


@pytest.mark.parametrize('wrapper,accepted', [
    ('```json\n{}\n```', True), ('```\n{}\n```', True),
    ('answer: ```json\n{}\n```', False), ('```python\n{}\n```', False),
    ('```json\n{}\n```\nextra', False),
])
def test_only_whole_json_fence_is_unwrapped(wrapper, accepted):
    d = doc(); t = Taxonomy(); r = next(protocol.requests_for('fixture', d['text'], t, protocol.Protocol()))
    response = reply(r, [item()]); response['text'] = wrapper.format(response['text'])
    assert not itemwise_decode(r, response, d['text'], t.categories)[0]
    spans, info = itemwise_decode(r, response, d['text'], t.categories, unwrap=True)
    assert bool(spans) == accepted


@pytest.mark.parametrize('bad', [item(occurrence=3), item(occurrence=True), item('金민수'), item(category='name')])
def test_no_occurrence_quote_or_label_repair(bad):
    d = doc(); t = Taxonomy(); r = next(protocol.requests_for('fixture', d['text'], t, protocol.Protocol()))
    spans, info = itemwise_decode(r, reply(r, [bad]), d['text'], t.categories, unwrap=True)
    assert spans == [] and info['invalid_items'] == 1


def test_no_truncation_or_core_ownership_repair():
    d = doc(); t = Taxonomy()
    r = next(protocol.requests_for('fixture', d['text'], t, protocol.Protocol(core_chars=4, halo_chars=10)))
    spans, info = itemwise_decode(r, reply(r, [item(occurrence=2)]), d['text'], t.categories)
    assert spans == [] and info['invalid_items'] == 1
    response = reply(r, [item()]); response['finish_reason'] = 'length'
    spans, info = itemwise_decode(r, response, d['text'], t.categories, unwrap=True)
    assert spans == [] and info['route'] == 'terminal_failure'


def fixture_run(tmp_path):
    corpus = tmp_path/'corpus.jsonl'; write_jsonl(corpus, [doc()])
    root = tmp_path/'plan'; prepare(corpus, root, protocol.Protocol())
    manifest, _, requests, _ = load_plan(root)
    responses = tmp_path/'responses.jsonl'; write_jsonl(responses, [reply(requests[0], [item(), item('없는 이름')])])
    result = score(root, responses, 'fixture-model')
    result['manifest']['purpose'] = 'benchmark'
    result['execution'] = dict(
        accounting=dict(complete=True, finished_requests=1, planned_requests=1),
        cohort_sha256='fixture-only-not-native-evidence',
        data_sha256=manifest['data_sha256'], requests_sha256=manifest['requests_sha256'],
        source_sha256={m.__name__.split('.')[-1]+'.py': file_sha(m.__file__) for m in (protocol, metrics)})
    reference = tmp_path/'result.json'; reference.write_text(json.dumps(result))
    return root/'gold.jsonl', responses, reference, result


def test_end_to_end_replay_immutable_inputs_and_audit(tmp_path):
    gold, responses, reference, result = fixture_run(tmp_path)
    before = [file_sha(p) for p in (gold, responses, reference)]
    output = tmp_path/'analysis'
    rows = analyze(gold, responses, reference, output)
    analysis = json.loads((output/'analysis.json').read_text())
    assert analysis['headline_eligible'] is False
    assert 'manifest' not in analysis
    assert analysis['provenance']['strict_replay_verified'] is True
    assert analysis['stages']['strict']['metrics']['exact_micro'] == result['metrics']['exact_micro']
    assert rows[1]['exact_f1'] == .5
    assert [file_sha(p) for p in (gold, responses, reference)] == before
    ledger = [json.loads(line) for line in gzip.open(output/'per_request.jsonl.gz', 'rt')]
    assert len(ledger) == 1 and ledger[0]['itemwise']['invalid_items'] == 1
    for line in (output/'ARTIFACTS.sha256').read_text().splitlines():
        digest, name = line.split('  ')
        assert digest == file_sha(output/name)
    with pytest.raises(ValueError, match='new directory'):
        analyze(gold, responses, reference, output)


@pytest.mark.parametrize('mutation,error', [
    ('pilot', 'allow-pilot'), ('incomplete', 'complete finalized'),
    ('source', 'scoring source'), ('score', 'score replay'), ('response', 'input hash'),
    ('gold', 'input hash'), ('request', 'model/request hash'), ('duplicate', 'duplicate response'),
])
def test_rejects_nonfinal_or_tampered_evidence(tmp_path, mutation, error):
    gold, responses, reference, result = fixture_run(tmp_path)
    if mutation == 'pilot': result['manifest']['purpose'] = 'pilot'
    elif mutation == 'incomplete': result['execution']['accounting']['complete'] = False
    elif mutation == 'source': result['execution']['source_sha256']['protocol.py'] = 'wrong'
    elif mutation == 'score': result['metrics']['exact_micro']['tp'] = 999
    elif mutation == 'response': responses.write_text(responses.read_text() + '\n')
    elif mutation == 'gold': gold.write_text(gold.read_text() + '\n')
    elif mutation == 'request':
        response = json.loads(responses.read_text()); response['request_sha256'] = 'wrong'
        responses.write_text(json.dumps(response)+'\n'); result['response_sha256'] = file_sha(responses)
    elif mutation == 'duplicate':
        responses.write_text(responses.read_text()*2); result['response_sha256'] = file_sha(responses)
    reference.write_text(json.dumps(result))
    with pytest.raises(ValueError, match=error):
        analyze(gold, responses, reference, tmp_path/'analysis')
    assert not (tmp_path/'analysis').exists()
