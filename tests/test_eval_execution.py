import json
from pathlib import Path
import pytest
from src.eval.protocol import Protocol
from src.eval.run import prepare, load_plan, write_jsonl
from src.eval.execute import count, execute, finalize, load_config, config_hash
from src.eval.providers import Provider, normalize
from src.eval.baselines import Rules, mapped, decode_bioes
from src.eval.cohort import freeze
from src.eval.export import export


def doc():
    return dict(doc_id='fixture',text='😀 연락처 010-1234-5678 이메일 test@example.com',doc_type='fixture',
                variation_level='T0',context_len_bucket='1k',num_subjects=1,generator={'model':'fixture'},
                spans=[dict(start=6,end=19,category='phone_no',entity_id='p',subject_role='customer')],hard_negatives=[])


def config():
    return dict(model='fixture',model_revision='r1',tokenizer_revision='r1',operator='tester',run_id='0923-01',
                price_date='2026-09-23',provider='openai_compatible',base_url='http://localhost:8000/v1',
                input_limit=10000,output_limit=4096,total_limit=20000,input_usd_per_million=1,
                output_usd_per_million=1,budget_usd=1,settings_frozen=True,concurrency=2)


class Fake:
    def __init__(self): self.calls=0
    def count(self,r): return 100
    def generate(self,r):
        self.calls+=1
        return dict(status='ok',finish_reason='stop',text='{"spans":[]}',usage={'input_tokens':100,'output_tokens':5})


def plan(tmp_path, mode='full_context_targeted'):
    corpus=tmp_path/'corpus.jsonl'
    if not corpus.exists():write_jsonl(corpus,[doc()])
    root=tmp_path/mode;prepare(corpus,root,Protocol(mode=mode,core_chars=20,halo_chars=20))
    return root


def test_resume_budget_and_finalize(tmp_path):
    root=plan(tmp_path);c=config();provider=Fake();counts=tmp_path/'counts.jsonl';out=tmp_path/'run'
    count(root,c,counts,provider)
    report=execute(root,{**c,'budget_usd':0},counts,out,provider)
    assert report['stop_reason']=='budget_exhausted' and provider.calls==0
    assert not execute(root,c,counts,out,provider,max_new=1)['complete']
    assert execute(root,c,counts,out,provider)['complete']
    calls=provider.calls
    assert execute(root,c,counts,out,provider)['complete'] and calls==provider.calls
    assert finalize(root,c,out)['f1_micro']==0
    with pytest.raises(ValueError,match='pilot/smoke'):
        export([out/'result.json'],tmp_path/'leaderboard.csv')


def test_interrupted_reservation_is_not_resent(tmp_path):
    from src.eval.execute import append
    root=plan(tmp_path);c=config();provider=Fake();counts=tmp_path/'counts';out=tmp_path/'run'
    count(root,c,counts,provider);execute(root,{**c,'budget_usd':0},counts,out,provider)
    r=load_plan(root)[2][0]
    append(out/'events.jsonl',dict(event='reserved',request_id=r['request_id'],request_sha256=r['request_sha256'],reserved_usd=.1))
    report=execute(root,c,counts,out,provider)
    assert provider.calls==len(load_plan(root)[2])-1
    first=json.loads((out/'responses.jsonl').read_text().splitlines()[0])
    assert first['status']=='uncertain' and report['spent_or_reserved_usd']>=.1


def test_benchmark_requires_both_condition_gate(tmp_path):
    entries=[];c=config();cfg=tmp_path/'config.json';cfg.write_text(json.dumps(c))
    for mode in ['full_context_targeted','local_window']:
        root=plan(tmp_path,mode);mp=root/'manifest.json';m=json.loads(mp.read_text());m['purpose']='benchmark';mp.write_text(json.dumps(m))
        counts=tmp_path/f'{mode}.counts';count(root,c,counts,Fake())
        entries.append(dict(config=str(cfg),directory=str(root),measurements=str(counts)))
    with pytest.raises(ValueError,match='cohort'):
        execute(root,c,counts,tmp_path/'run',Fake())
    matrix=tmp_path/'matrix';matrix.write_text(json.dumps({'entries':entries}));gate=tmp_path/'gate'
    freeze(matrix,gate)
    execute(root,c,counts,tmp_path/'run',Fake(),cohort=gate)
    finalize(root,c,tmp_path/'run')
    assert export([tmp_path/'run/result.json'],tmp_path/'leaderboard.csv')==1


def test_changed_config_and_counts_refused(tmp_path):
    root=plan(tmp_path);counts=tmp_path/'counts';c=config();count(root,c,counts,Fake())
    with pytest.raises(ValueError,match='do not match'):
        execute(root,{**c,'model_revision':'changed'},counts,tmp_path/'run',Fake())
    path=tmp_path/'config';path.write_text(json.dumps({**c,'api_key':'secret'}))
    with pytest.raises(ValueError,match='unknown config'):load_config(path)
    assert config_hash(c)==config_hash({**c,'budget_usd':99})


@pytest.mark.parametrize('kind,raw,reason,tokens',[
 ('anthropic',{'content':[{'type':'text','text':'{}'}],'stop_reason':'end_turn','usage':{'input_tokens':2,'cache_read_input_tokens':3,'output_tokens':4}},'stop',4),
 ('gemini',{'candidates':[{'content':{'parts':[{'text':'secret thought','thought':True},{'text':'{}'}]},'finishReason':'STOP'}],'usageMetadata':{'promptTokenCount':2,'candidatesTokenCount':3,'thoughtsTokenCount':4}},'stop',7),
 ('openai_compatible',{'choices':[{'message':{'content':'{}'},'finish_reason':'length'}],'usage':{'prompt_tokens':2,'completion_tokens':8}},'length',8),
 ('openai_compatible',{'choices':[{'message':{'content':'{}'},'finish_reason':'stop'}],'usage':{'prompt_tokens':2,'completion_tokens':5,'completion_tokens_details':None}},'stop',5)])
def test_normalization(kind,raw,reason,tokens):
    text,finish,usage=normalize(kind,raw)
    assert text=='{}' and finish==reason and usage['output_tokens']==tokens


@pytest.mark.parametrize('kind,suffix,key', [('anthropic','/messages/count_tokens','input_tokens'),('gemini',':countTokens','totalTokens'),('openai_compatible','/tokenize','count')])
def test_native_counter(kind,suffix,key):
    seen=[]
    def transport(url,payload,headers,timeout):seen.append((url,payload));return {key:42}
    p=Provider({**config(),'provider':kind},transport)
    assert p.count({'messages':[{'role':'system','content':'rules'},{'role':'user','content':'text'}],'max_output_tokens':99})==42
    assert seen[0][0].endswith(suffix)
    assert 'text' in json.dumps(seen[0][1]) and 'rules' in json.dumps(seen[0][1])


@pytest.mark.parametrize('name',['ko-pii','presidio'])
def test_real_rules_unicode_offsets(name):
    pytest.importorskip('ko_pii' if name=='ko-pii' else 'presidio_analyzer')
    text=doc()['text'];raw=Rules(name)(text)
    mapping=json.loads(Path(f'experiments/label_maps/{name}.json').read_text())['mapping']
    spans=mapped(raw,mapping)
    assert any(text[s['start']:s['end']]=='010-1234-5678' and s['category']=='phone_no' for s in spans)
    assert any(text[s['start']:s['end']]=='test@example.com' and s['category']=='email' for s in spans)


def test_bioes_and_unmapped():
    spans=decode_bioes(['O','B-FIRSTNAME','E-FIRSTNAME','S-PHONE'],[(0,0),(1,2),(2,3),(4,8)])
    assert spans==[dict(start=1,end=3,label='FIRSTNAME'),dict(start=4,end=8,label='PHONE')]
    assert mapped(spans,{'FIRSTNAME':None,'PHONE':'phone_no'})==[dict(start=4,end=8,category='phone_no')]
    with pytest.raises(ValueError,match='unknown source'):mapped(spans,{'PHONE':'phone_no'})


def test_transport_error_stops_dispatch_and_keeps_reservation(tmp_path):
    class Broken(Fake):
        def generate(self,r):
            self.calls+=1
            raise TimeoutError('private transport detail')
    root=plan(tmp_path);c={**config(),'concurrency':1};counts=tmp_path/'counts';provider=Broken()
    count(root,c,counts,provider)
    report=execute(root,c,counts,tmp_path/'run',provider)
    assert report['stop_reason']=='transport_error' and not report['complete']
    assert provider.calls==1 and report['spent_or_reserved_usd']>0
    assert 'private transport detail' not in (tmp_path/'run/events.jsonl').read_text()


def test_capacity_cannot_be_silently_truncated(tmp_path):
    root=plan(tmp_path);c={**config(),'input_limit':99};counts=tmp_path/'counts'
    count(root,c,counts,Fake())
    with pytest.raises(ValueError,match='capacity exclusion'):
        execute(root,c,counts,tmp_path/'run',Fake())
