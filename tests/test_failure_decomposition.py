import json
import pytest
from src.analysis.failure_decomposition import (
    analyze, parsed_body, structure_ok, item_outcome, gold_outcome, request_outcome, prf_sets,
)
from src.analysis.response_diagnostics import analyze as diagnose
from src.eval import protocol
from src.generate.taxonomy import Taxonomy
from test_response_diagnostics import fixture_run, doc, item


def test_json_fence_duplicates_and_unicode_separator():
    assert parsed_body('```json\n{"spans":[]}\n```') == ([], 'fence', 0)
    assert parsed_body('prose {"spans":[]}')[1] == 'invalid_json'
    assert parsed_body('{"other":[]}')[1] == 'root_schema'
    assert parsed_body('{"spans":[{}],"spans":[]}') == ([], 'raw', 1)
    assert parsed_body('{"spans":[{"text":"a\u2028b"}]}')[1] == 'raw'
    assert request_outcome({'status':'failed','finish_reason':'length'},[], 'raw')=='output_truncated'
    assert request_outcome({'status':'failed','finish_reason':None},[], 'raw')=='other_terminal_failure'


def test_structure_does_not_consult_gold_or_category_vocabulary():
    assert structure_ok(item(category='unknown'))
    assert not structure_ok(item(occurrence=True))
    assert not structure_ok(item(category=[]))


def test_disjoint_item_causes_and_ownership():
    d=doc();tax=Taxonomy()
    r=next(protocol.requests_for('fixture',d['text'],tax,protocol.Protocol(core_chars=4,halo_chars=10)))
    cases=[({},'item_schema'),(item(category=[]),'invalid_category'),
           (item(category='unknown'),'invalid_category'),(item(text=''),'invalid_quote_field'),
           (item(occurrence=True),'invalid_occurrence_field'),(item('없는이름'),'quote_absent_from_target'),
           (item(occurrence=3),'occurrence_out_of_range'),(item(occurrence=2),'outside_owned_core'),
           (item(),'valid')]
    for i,expected in cases: assert item_outcome(i,r,d['text'],tax.categories)==expected


def test_gold_partition_detects_category_boundary_and_missing_without_repair():
    g=dict(start=1,end=4,category='person_name')
    assert gold_outcome(g,{(1,4,'address')},'nonempty_list',0)=='exact_boundary_wrong_category'
    assert gold_outcome(g,{(2,4,'person_name')},'nonempty_list',0)=='overlapping_boundary_same_category'
    assert gold_outcome(g,{(2,4,'address')},'nonempty_list',0)=='overlapping_boundary_wrong_category'
    assert gold_outcome(g,set(),'nonempty_list',3)=='unresolved_with_rejected_items'
    assert gold_outcome(g,set(),'nonempty_list',0)=='no_overlapping_prediction'
    assert gold_outcome(g,set(),'empty_list',0)=='empty_list'
    assert gold_outcome(g,set(),'invalid_json',0)=='invalid_json'
    assert gold_outcome(g,{(1,4,'person_name')},'nonempty_list',2)=='exact_hit'
    assert prf_sets({(1,4)},{(1,4)},2)['precision']==1/3


def test_replay_denominators_and_mixed_valid_invalid_items(tmp_path):
    gold,responses,ref,_=fixture_run(tmp_path)
    diagnose(gold,responses,ref,tmp_path/'diag')
    r=analyze(gold,responses,ref,tmp_path/'diag/analysis.json',tmp_path/'out')
    assert r['request_counts']['format_compliant']==1  # fabricated quote is grounding, not JSON.
    assert r['request_counts']['strict_rejected']==1
    assert r['item_outcomes']=={'valid':1,'quote_absent_from_target':1}
    assert r['gold_outcomes']=={'exact_hit':1,'unresolved_with_rejected_items':1}
    assert r['itemwise_exact']['tp']==1 and r['itemwise_exact']['fn']==1
    assert r['itemwise_exact']['fp']==1 and r['invalid_item_fp']==1
    assert r['strict_exact']['tp']==0
    with pytest.raises(ValueError,match='new'):
        analyze(gold,responses,ref,tmp_path/'diag/analysis.json',tmp_path/'out')
    d=json.loads((tmp_path/'diag/analysis.json').read_text());d['provenance']['inputs']['gold_sha256']='bad'
    (tmp_path/'diag/analysis.json').write_text(json.dumps(d))
    with pytest.raises(ValueError,match='provenance'):
        analyze(gold,responses,ref,tmp_path/'diag/analysis.json',tmp_path/'bad')


def test_export_keeps_denominators_and_rejects_inconsistent_partition(tmp_path):
    from src.analysis.export_failure_decomposition import export, rows_for
    gold,responses,ref,_=fixture_run(tmp_path)
    diagnose(gold,responses,ref,tmp_path/'diag')
    r=analyze(gold,responses,ref,tmp_path/'diag/analysis.json',tmp_path/'out')
    row,counts=rows_for(r,'fixture')
    assert row['format_compliance']==1 and row['detection_recall']==.5
    assert sum(v['count'] for v in counts if v['axis']=='gold_outcome')==2
    assert all(v['denominator']==2 for v in counts if v['axis']=='gold_outcome')
    assert export([tmp_path/'out/analysis.json'],tmp_path/'tables')==1
    r['request_counts']['total']=10
    with pytest.raises(ValueError,match='partition'):rows_for(r,'fixture')


def test_external_replay_retains_foreign_source_and_rechecks_outputs(tmp_path):
    from src.analysis.external_response_diagnostics import analyze as external_analyze
    gold,responses,ref,result=fixture_run(tmp_path)
    result['execution']['source_sha256']={'foreign.py':'recorded-foreign-source'}
    result['execution']['runner']='fixture external runner'
    ref.write_text(json.dumps(result))
    with pytest.raises(ValueError,match='scoring source'):
        diagnose(gold,responses,ref,tmp_path/'native')
    external_analyze(gold,responses,ref,tmp_path/'external')
    d=json.loads((tmp_path/'external/analysis.json').read_text())
    assert d['provenance']['original_runner_source_sha256']=={'foreign.py':'recorded-foreign-source'}
    assert d['provenance']['external_runner_replay'] is True
    r=analyze(gold,responses,ref,tmp_path/'external/analysis.json',tmp_path/'out')
    assert r['itemwise_exact']['tp']==1
    result['metrics']['exact_micro']['tp']=99;ref.write_text(json.dumps(result))
    with pytest.raises(ValueError,match='score replay'):
        external_analyze(gold,responses,ref,tmp_path/'tampered')
