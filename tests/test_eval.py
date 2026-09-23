import json
import pytest
from src.generate.taxonomy import Taxonomy
from src.eval.protocol import Protocol, requests_for, decode
from src.eval.metrics import score_document, paired_bootstrap
from src.eval.run import prepare, load_plan, score, preflight, write_jsonl


def document():
    return dict(doc_id='test', text='😀김민수 김민수 끝', doc_type='test', variation_level='T0',
                context_len_bucket='1k', num_subjects=1, generator={'model':'synthetic'},
                spans=[dict(start=a,end=b,category='person_name',entity_id='e1',subject_role='customer') for a,b in [(1,4),(5,8)]],
                hard_negatives=[dict(start=9,end=10)])


def response(request, spans):
    return dict(request_id=request['request_id'], request_sha256=request['request_sha256'],
                model='test-model', status='ok', finish_reason='stop',text=json.dumps({'spans':spans}))


def test_gold_blind_unicode_and_repeated_quotes():
    d=document(); t=Taxonomy()
    r=list(requests_for(d['doc_id'],d['text'],t,Protocol(core_chars=6,halo_chars=3)))[0]
    result, errors=decode(r,response(r,[dict(category='person_name',text='김민수',occurrence=2)]),d['text'],t.categories)
    assert not errors and result == [dict(start=5,end=8,category='person_name')]
    assert 'entity_id' not in json.dumps(r)
    local=list(requests_for(d['doc_id'],d['text'],t,Protocol(mode='local_window',core_chars=6,halo_chars=3)))[0]
    assert local['window']['core_start']==r['window']['core_start']
    assert local['window']['core_end']==r['window']['core_end']


@pytest.mark.parametrize('bad', [dict(category='person_name',text='金민수',occurrence=1), dict(category='unknown',text='김민수',occurrence=1), dict(category='person_name',text='김민수',occurrence=True)])
def test_invalid_prediction_rejects_entire_response(bad):
    d=document(); t=Taxonomy();r=next(requests_for('test',d['text'],t,Protocol()))
    spans,errors=decode(r,response(r,[dict(category='person_name',text='김민수',occurrence=1),bad]),d['text'],t.categories)
    assert errors and not spans


def test_missing_and_truncated_count_as_false_negatives(tmp_path):
    corpus=tmp_path/'corpus.jsonl';write_jsonl(corpus,[document()]);root=tmp_path/'plan'
    prepare(corpus,root,Protocol()); _,_,req,_=load_plan(root)
    responses=tmp_path/'responses.jsonl';r=response(req[0],[]);r['finish_reason']='length';write_jsonl(responses,[r])
    result=score(root,responses,'test-model')
    assert result['metrics']['exact_micro']['fn']==2
    assert result['reliability']['failed_requests']==1
    empty=tmp_path/'empty.jsonl';write_jsonl(empty,[])
    assert score(root,empty,'test-model')['metrics']['exact_micro']['fn']==2


def test_perfect_score_and_entity_consistency():
    d=document();perfect=score_document(d,d['spans']);partial=score_document(d,d['spans'][:1])
    assert perfect['exact']['f1']==1
    assert partial['entity_all_mentions_exact']['hit']==0
    assert paired_bootstrap([perfect],[partial],samples=100)['delta_f1']==pytest.approx(1/3)
    wrong=score_document(d,[dict(start=1,end=4,category='address')])
    assert wrong['character']['tp']==0


def test_preflight_and_frozen_plan(tmp_path):
    corpus=tmp_path/'corpus.jsonl';write_jsonl(corpus,[document()]);root=tmp_path/'plan';prepare(corpus,root,Protocol())
    _,_,req,_=load_plan(root)
    records=[dict(model=m,request_id=r['request_id'],request_sha256=r['request_sha256'],
                  tokenizer_revision='actual-test-tokenizer',input_tokens=100,input_limit=limit,
                  output_limit=4096,total_limit=5000) for m,limit in [('a',200),('b',99)] for r in req]
    measurements=tmp_path/'counts.jsonl';write_jsonl(measurements,records)
    assert preflight(root,measurements)['common_eligible_doc_ids']==[]
    with (root/'requests.jsonl').open('a') as f:f.write('\n')
    with pytest.raises(ValueError,match='changed plan'):load_plan(root)


def test_boundary_audit_does_not_drop_gold(tmp_path):
    corpus=tmp_path/'corpus.jsonl';write_jsonl(corpus,[document()]);root=tmp_path/'plan'
    result=prepare(corpus,root,Protocol(core_chars=2,halo_chars=0))
    assert result['unrepresentable_spans']==2
    assert len(load_plan(root)[1][0]['spans'])==2


def test_unknown_responses_rejected(tmp_path):
    corpus=tmp_path/'corpus.jsonl';write_jsonl(corpus,[document()]);root=tmp_path/'plan';prepare(corpus,root,Protocol())
    responses=tmp_path/'responses.jsonl';write_jsonl(responses,[{'request_id':'unknown'}])
    with pytest.raises(ValueError,match='unknown response'):score(root,responses,'test-model')
