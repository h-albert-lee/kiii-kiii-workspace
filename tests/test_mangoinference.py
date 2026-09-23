from types import SimpleNamespace
import pytest

from src.generate.compose import LLMClient
from src.generate.audit import audit_records
from src.generate.run import make_plans
from src.generate.compose import plan_to_dict
from src.generate.taxonomy import Taxonomy


def test_mango_uses_separate_key_and_documented_parameters(monkeypatch):
    import openai
    init, requests = [], []
    monkeypatch.setenv("OPENAI_API_KEY", "openai-test-do-not-send")
    monkeypatch.setenv("MANGOINFERENCE_API_KEY", "mango-test")

    def create(**kwargs):
        requests.append(kwargs)
        return SimpleNamespace(id="r1", model="zai-org/GLM-5.2-FP8",
            choices=[SimpleNamespace(finish_reason="stop", message=SimpleNamespace(content="가상 문서"))],
            usage=SimpleNamespace(model_dump=lambda: {"completion_tokens": 20, "reasoning_tokens": 5}),
            model_dump=lambda: {"metadata": {"weight_version": "test"}})

    def client(**kwargs):
        init.append(kwargs)
        return SimpleNamespace(base_url=kwargs["base_url"], chat=SimpleNamespace(
            completions=SimpleNamespace(create=create)))

    monkeypatch.setattr(openai, "OpenAI", client)
    c = LLMClient("zai-org/GLM-5.2-FP8", base_url="https://api.mangoboost.io/v1")
    assert c.complete("test", seed=42) == "가상 문서"
    assert init[0]["api_key"] == "mango-test" and init[0]["max_retries"] == 0
    assert requests[0]["max_tokens"] == 32000 and requests[0]["top_p"] == 1.0
    assert "seed" not in requests[0] and "reasoning_effort" not in requests[0]
    assert c.last_metadata["serving_metadata"] == {"weight_version": "test"}
    assert c.last_metadata["usage"]["reasoning_tokens"] == 5


def test_audit_accepts_top_level_reasoning_tokens_without_double_counting():
    tax = Taxonomy()
    plan = make_plans(tax, 1, 0)[0]
    r = {"plan": plan_to_dict(plan), "model": "test", "prompt_version": "compose_v2",
         "raw": "검토 대상 {{person_name:1}}", "completion": {"finish_reason": "stop",
         "usage": {"prompt_tokens": 10, "completion_tokens": 20, "reasoning_tokens": 7}}}
    assert audit_records([r], tax)["usage"]["reasoning_tokens"] == 7
    r["completion"]["usage"]["completion_tokens_details"] = {"reasoning_tokens": 7}
    assert audit_records([r], tax)["usage"]["reasoning_tokens"] == 7


def test_missing_mango_key_never_falls_back_to_openai_key(monkeypatch):
    import openai
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-be-sent")
    monkeypatch.delenv("MANGOINFERENCE_API_KEY", raising=False)
    monkeypatch.setattr(openai, "OpenAI", lambda **kw: pytest.fail("wrong key could be sent"))
    with pytest.raises(ValueError, match="MANGOINFERENCE_API_KEY"):
        LLMClient("test", base_url="https://api.mangoboost.io/v1")


def test_stream_retains_answer_usage_and_progress_not_reasoning(monkeypatch):
    from types import SimpleNamespace as NS
    import openai
    monkeypatch.setenv('MANGOINFERENCE_API_KEY', 'mango-test')
    class Stream:
        response = NS(headers={'x-request-id': 'req', 'x-trace-id': 'trace'})
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def __iter__(self):
            yield NS(id='r',model='glm',usage=None,choices=[NS(delta=NS(content=None,reasoning_content='private'),finish_reason=None)])
            yield NS(id='r',model='glm',usage=None,choices=[NS(delta=NS(content='본문'),finish_reason='stop')])
            yield NS(id='r',model='glm',choices=[],usage=NS(model_dump=lambda:{'prompt_tokens':10,'completion_tokens':30}))
    requests=[]
    def create(**kw): requests.append(kw); return Stream()
    monkeypatch.setattr(openai,'OpenAI',lambda **kw:NS(base_url=kw['base_url'],chat=NS(completions=NS(create=create))))
    c=LLMClient('glm',base_url='https://api.mangoboost.io/v1')
    progress=[]
    assert c.complete('prompt',stream=True,output_limit=65536,on_progress=lambda t,m:progress.append((t,dict(m))))=='본문'
    assert requests[0]['max_tokens']==65536
    assert c.last_metadata['usage']['completion_tokens']==30
    assert c.last_metadata['request_id']=='req'
    assert 'private' not in str(progress)
    assert progress[-1][0]=='본문'
