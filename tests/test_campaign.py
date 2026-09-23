import json
from dataclasses import asdict, replace

import pytest

from src.generate.campaign import prepare, prepare_repairs, run, usage_cost, export, MODEL
from src.generate.run import make_plans
from src.generate.taxonomy import Taxonomy


def setup_job(tmp_path, budget=1):
    p = replace(make_plans(Taxonomy(), 1, 0)[0], doc_type="kyc_form", num_subjects=1,
                context_len_bucket="1k", variation_level="T0", generator_slice="api-main")
    plan = tmp_path / "plan.jsonl"
    plan.write_text(json.dumps(asdict(p)) + "\n")
    directory = tmp_path / "job"
    prepare(plan, directory, budget)
    return directory


class FakeClient:
    calls = 0

    def __init__(self, *a, **kw):
        pass

    def complete(self, prompt, seed):
        FakeClient.calls += 1
        self.last_metadata = {"finish_reason": "stop", "usage": {"prompt_tokens": 10, "completion_tokens": 20}}
        return "고객 {{person_name:1}} 계좌개설 신청"


def test_budget_reservation_prevents_call(tmp_path):
    job = setup_job(tmp_path, .001)
    FakeClient.calls = 0
    state = run(job, client_factory=FakeClient)
    assert state["stop_reason"] == "budget" and FakeClient.calls == 0


def test_completed_request_never_called_twice(tmp_path):
    job = setup_job(tmp_path)
    FakeClient.calls = 0
    first = run(job, client_factory=FakeClient)
    second = run(job, client_factory=FakeClient)
    assert FakeClient.calls == 1
    assert next(iter(second["records"].values()))["status"] == "accepted"
    assert first["estimated_committed_usd"] == second["estimated_committed_usd"]
    assert len(list(job.glob("response.*.json"))) == 1
    assert export(job)["accepted"] == 1
    assert len((job / "docs.jsonl").read_text().splitlines()) == 1


def test_uncertain_request_and_tamper_block_calls(tmp_path):
    job = setup_job(tmp_path)
    path = job / "state.json"
    state = json.loads(path.read_text())
    state["records"]["test"] = {"status": "in_flight", "reserved_usd": .15}
    path.write_text(json.dumps(state))
    with pytest.raises(ValueError, match="uncertain"):
        run(job, client_factory=FakeClient)
    state["records"] = {}
    path.write_text(json.dumps(state))
    (job / "requests.json").write_text("[]")
    with pytest.raises(ValueError, match="inputs changed"):
        run(job, client_factory=FakeClient)


def test_quality_gate_retains_raw_and_cost(tmp_path):
    job = setup_job(tmp_path)

    class BadClient(FakeClient):
        def complete(self, prompt, seed):
            super().complete(prompt, seed)
            return "고객 {{person_name:1}} 담당자 staff1"

    state = run(job, client_factory=BadClient)
    assert state["stop_reason"] == "quality_gate"
    assert state["estimated_committed_usd"] > 0
    assert len(list(job.glob("response.*.json"))) == 1
    assert not list(job.glob("document.*.json"))
    assert usage_cost({"prompt_tokens": 10, "completion_tokens": 20, "reasoning_tokens": 15},
                      {"input": 1, "cached_input": .1, "output": 2}) == .00005


def test_server_error_keeps_reservation_and_never_retries_same_document(tmp_path):
    job = setup_job(tmp_path)
    calls = []

    class FailingClient(FakeClient):
        def complete(self, prompt, seed):
            calls.append(seed)
            raise TimeoutError("uncertain provider outcome")

    state = run(job, client_factory=FailingClient)
    assert state["stop_reason"] == "request_error"
    assert state["estimated_committed_usd"] > .1
    run(job, client_factory=FailingClient)
    assert len(calls) == 1
    assert export(job)["accepted"] == 0


def test_repairs_only_failed_complete_originals_and_preserve_lineage(tmp_path):
    job = setup_job(tmp_path)
    plan = json.loads((job / "requests.json").read_text())[0]["plan"]
    row = {"doc_id": plan["doc_id"], "plan": plan, "model": MODEL, "prompt_version": "compose_v5",
           "raw": "{{person_name:1}} [[gender:1]]여성[[/gender]]", "completion": {"finish_reason": "stop"}}
    path = tmp_path / "raw.jsonl"
    path.write_text(json.dumps(row) + "\n")
    directory = tmp_path / "repairs"
    assert prepare_repairs(path, directory, 1)["planned"] == 1
    request = json.loads((directory / "requests.json").read_text())[0]
    assert request["plan"] == plan and request["lineage"]["attempt"] == 1
    assert row["raw"] in request["prompt"] and request["lineage"]["parent_errors"]
    row["lineage"] = request["lineage"]
    path.write_text(json.dumps(row) + "\n")
    with pytest.raises(ValueError, match="no eligible"):
        prepare_repairs(path, tmp_path / "recursive", 1)
    row.pop("lineage")
    row["completion"]["finish_reason"] = "length"
    path.write_text(json.dumps(row) + "\n")
    with pytest.raises(ValueError, match="no eligible"):
        prepare_repairs(path, tmp_path / "truncated", 1)


def test_stream_limit_is_reserved_before_sending(tmp_path):
    job=setup_job(tmp_path,.2)
    plan=tmp_path/'plan.jsonl'
    streaming=tmp_path/'streaming'
    prepare(plan,streaming,.2,prompt_version='compose_v6',transport={'stream':True,'output_limit':65536})
    FakeClient.calls=0
    state=run(streaming,client_factory=FakeClient)
    assert state['stop_reason']=='budget'
    assert FakeClient.calls==0
