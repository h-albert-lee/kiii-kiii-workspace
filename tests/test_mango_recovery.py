import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location('resume_mango', Path(__file__).resolve().parents[1] / 'scripts/resume_mango.py')
recovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recovery)


def test_cost_deduplicates_roots_and_keeps_uncertain_reservations(tmp_path):
    p=tmp_path/'job';p.mkdir()
    (p/'state.json').write_text(json.dumps({'estimated_committed_usd':.3,'records':{'a':{'status':'request_error'}}}))
    assert recovery.cost([tmp_path,p]) == .3
    assert recovery.accepted([tmp_path]) == {}


def test_only_explicit_transient_status_retries_and_respects_retry_after():
    assert recovery.transient({'http_status':502})
    assert recovery.transient({'http_status':429})
    assert not recovery.transient({'http_status':400})
    assert not recovery.transient({'error_type':'APIConnectionError'})
    assert recovery.pause_seconds({'retry_after':'120'}) == 120
    assert recovery.pause_seconds({'retry_after':'600'}) == 600


def test_resume_skips_existing_docs_and_deducts_all_prior_costs(tmp_path, monkeypatch):
    prior=tmp_path/'prior';prior.mkdir()
    old_state={'estimated_committed_usd':1.7,'records':{'old':{'status':'accepted'}}}
    (prior/'state.json').write_text(json.dumps(old_state))
    (prior/'document.old.json').write_text(json.dumps({'doc_id':'old','context_len_bucket':'4k'}))
    root=tmp_path/'resume';root.mkdir();(root/'frozen').mkdir()
    frozen=json.dumps({'source_hashes':{}}).encode()
    (root/'frozen/manifest.json').write_bytes(frozen)
    plans=[{'doc_id':k,'context_len_bucket':'4k'} for k in ('old','new1','new2')]
    manifest={'plans':plans,'budget_usd':150,'prior_roots':[str(prior)],
              'script_sha256':recovery._sha(Path(recovery.__file__).read_bytes()),
              'frozen_sha256':recovery._sha(frozen),
              'prior_states_sha256':{str(prior/'state.json'):recovery._sha((prior/'state.json').read_bytes())}}
    (root/'manifest.json').write_text(json.dumps(manifest))
    (root/'progress.json').write_text(json.dumps({'processed':[],'stop_reason':'prepared'}))
    budgets=[]
    def prepare(plan_path, job, budget, **kwargs):
        budgets.append(budget)
        job.mkdir(parents=True)
        (job/'plan.json').write_text(plan_path.read_text())
        (job/'state.json').write_text(json.dumps({'estimated_committed_usd':0,'records':{}}))
    def run(job):
        plan=json.loads((job/'plan.json').read_text())
        state={'estimated_committed_usd':.1,'records':{plan['doc_id']:{'status':'accepted'}},'stop_reason':'all_attempted'}
        (job/'state.json').write_text(json.dumps(state))
        (job/f"document.{plan['doc_id']}.json").write_text(json.dumps(plan))
        return state
    monkeypatch.setattr(recovery,'prepare',prepare)
    monkeypatch.setattr(recovery,'run',run)
    result=recovery.execute(root)
    assert result['accepted']==3
    assert round(result['estimated_committed_usd'],8)==1.9
    assert [round(x,8) for x in budgets]==[148.3,148.2]
    recovery.execute(root)
    assert len(budgets)==2


def test_short_prior_response_is_not_counted_as_long_document(monkeypatch):
    monkeypatch.setattr(recovery,'accepted',lambda roots:{'short':{'context_len_bucket':'4k'},'long':{'context_len_bucket':'16k'}})
    plans=[{'doc_id':k,'context_len_bucket':'16k'} for k in ('short','long')]
    assert set(recovery.selected_docs({'plans':plans},[]))=={'long'}


def test_quarantined_source_is_excluded_without_discarding_later_replacement(monkeypatch):
    manifest={'plans':[{'doc_id':'a','context_len_bucket':'16k'}],'excluded_source_runs':['canary']}
    doc={'context_len_bucket':'16k','generator':{'run_id':'canary'}}
    monkeypatch.setattr(recovery,'accepted',lambda roots:{'a':doc})
    assert recovery.selected_docs(manifest,[])=={}
    doc['generator']['run_id']='replacement'
    assert set(recovery.selected_docs(manifest,[]))=={'a'}
