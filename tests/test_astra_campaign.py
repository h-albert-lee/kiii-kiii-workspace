import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from astra_campaign import reserve,response_cost


def test_reservation_includes_reasoning_limit_and_cache_write_input():
 r={'body':{'messages':[{'content':'가나다'}],'max_completion_tokens':32000}}
 assert reserve(r)>.8
 amount,known=response_cost({'prompt_tokens':1000,'completion_tokens':2000,'reasoning_tokens':1000},1)
 assert known and abs(amount-.05625)<1e-9
 assert response_cost(None,1)==(1,False)


def test_budget_stops_before_any_submission(tmp_path,monkeypatch):
 import json
 import astra_campaign as campaign
 from dataclasses import asdict,replace
 from src.generate.run import make_plans
 from src.generate.taxonomy import Taxonomy
 plan=replace(make_plans(Taxonomy(),1,0)[0],generator_slice='api-main')
 source=tmp_path/'plan.jsonl';source.write_text(json.dumps(asdict(plan))+'\n')
 root=tmp_path/'campaign'
 campaign.prepare(root,source,budget=47,data_version='main-1440-v1')
 state=json.loads((root/'state.json').read_text());state['estimated_committed_usd']=46.99
 (root/'state.json').write_text(json.dumps(state))
 monkeypatch.setattr(campaign.batch,'submit',lambda p: (_ for _ in ()).throw(AssertionError('must not submit')))
 result=campaign.run(root)
 assert result['status']=='budget' and result['submitted']==0
 assert result['estimated_committed_usd']==46.99
 assert result['budget_usd']==47
