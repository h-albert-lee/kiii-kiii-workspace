import hashlib
import json
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from package_dataset import split_plans, collect
from src.eval.dataset import verify_release, resolve_release
from upload_dataset import upload


def test_single_evaluation_set_preserves_all_documents():
    plans=[dict(doc_id=str(i),doc_type='a',variation_level='T0',num_subjects=1,context_len_bucket='1k') for i in range(4)]
    a=split_plans(plans)
    assert a==split_plans(list(reversed(plans)))
    assert set(a.values())=={'test'}
    assert len(a)==4
    with pytest.raises(ValueError):split_plans(plans+[plans[0]])


def fixture_release(tmp_path):
    (tmp_path/'README.md').write_text('synthetic test')
    m={'version':'test','documents':4,'files':{'README.md':hashlib.sha256(b'synthetic test').hexdigest()}}
    (tmp_path/'release-manifest.json').write_text(json.dumps(m))
    return tmp_path


def test_upload_preview_requires_no_credentials_or_network(tmp_path,monkeypatch):
    monkeypatch.delenv('HF_TOKEN',raising=False)
    result=upload(fixture_release(tmp_path),'owner/repo')
    assert not result['upload']
    assert result['files']==['README.md','release-manifest.json']
    with pytest.raises(ValueError,match='HF_TOKEN'):upload(tmp_path,'owner/repo',True)


def test_tampered_release_fails_before_upload(tmp_path):
    fixture_release(tmp_path);(tmp_path/'README.md').write_text('modified')
    with pytest.raises(ValueError,match='checksum'):verify_release(tmp_path)


def test_hub_revision_must_be_pinned():
    with pytest.raises(ValueError,match='commit SHA'):resolve_release(repo='owner/repo',revision='main')


def test_recovery_reads_accepted_states_not_stale_summary(tmp_path,monkeypatch):
    import package_dataset as release
    monkeypatch.setattr(release,'ROOT',tmp_path)
    root=tmp_path/'run';root.mkdir()
    (root/'state.json').write_text(json.dumps({'records':{'ok':{'status':'accepted'},'bad':{'status':'rejected'}}}))
    (root/'document.ok.json').write_text(json.dumps({'doc_id':'ok','text':'kept'}))
    docs,_=collect({'sources':[{'kind':'accepted_states','path':'run'}]})
    assert set(docs)=={'ok'}


def test_release_to_evaluation_roundtrip(tmp_path):
    pytest.importorskip('datasets')
    from src.eval.dataset import prepare_dataset
    from src.eval.protocol import Protocol
    (tmp_path/'data').mkdir()
    doc={'doc_id':'synthetic-smoke','text':'김민수입니다.','generator':{'reference_date':'2026-09-01'},
         'spans':[{'start':0,'end':3,'category':'person_name'}]}
    content=json.dumps(doc,ensure_ascii=False)+'\n'
    (tmp_path/'data/test.jsonl').write_text(content)
    (tmp_path/'release-manifest.json').write_text(json.dumps({'version':'test','files':{
        'data/test.jsonl':hashlib.sha256(content.encode()).hexdigest()}}))
    from src.generate.taxonomy import DEFAULT_PATH
    (tmp_path/'taxonomy.yaml').write_bytes(DEFAULT_PATH.read_bytes())
    result=prepare_dataset(tmp_path,'test',tmp_path/'eval',Protocol(),limit=1)
    assert result['documents']==1 and result['unrepresentable_spans']==0
    request=json.loads((tmp_path/'eval/requests.jsonl').read_text())
    assert request['doc_id']=='synthetic-smoke'
    assert json.loads((tmp_path/'eval/gold.jsonl').read_text())['generator']['reference_date']=='2026-09-01'
    assert json.loads((tmp_path/'eval/manifest.json').read_text())['purpose']=='plumbing_smoke_only'
