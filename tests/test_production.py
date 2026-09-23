import json
from dataclasses import asdict, replace

import pytest

from src.generate.campaign import run
from src.generate.production import init, verify, run_lane, report
from src.generate.run import make_plans
from src.generate.taxonomy import Taxonomy


def setup(tmp_path, budget=1):
    plans = [asdict(replace(p, generator_slice="api-main", num_subjects=1,
                          doc_type="kyc_form", context_len_bucket="1k", variation_level="T0"))
             for p in make_plans(Taxonomy(), 2, 0)]
    source = tmp_path / "plan.jsonl"
    source.write_text("".join(json.dumps(p) + "\n" for p in plans))
    directory = tmp_path / "production"
    init(source, directory, budget)
    return directory


class Fake:
    calls = 0

    def __init__(self, *a, **kw):
        pass

    def complete(self, prompt, seed):
        type(self).calls += 1
        self.last_metadata = {"finish_reason": "stop", "usage": {"prompt_tokens": 10, "completion_tokens": 20}}
        if "rejected_document" not in prompt:
            return "고객 {{person_name:1}} 담당자 staff1"
        return "고객 {{person_name:1}} 계좌 개설 신청"


def test_repair_shared_budget_and_resume_no_duplicate(tmp_path):
    directory = setup(tmp_path)
    Fake.calls = 0
    runner = lambda job: run(job, client_factory=Fake)
    for i in range(2):
        run_lane(directory, i, .5, runner)
        run_lane(directory, i, .5, runner)
    result = report(directory)
    assert Fake.calls == 4 and result["accepted"] == 2
    assert result["estimated_committed_usd"] == pytest.approx(4 * .000097)
    docs = [json.loads(s) for s in (directory / "docs.jsonl").read_text().splitlines()]
    assert all(d["generator"]["lineage"]["attempt"] == 1 for d in docs)
    assert all(d["generator"]["prompt_version"] == "compose_v6" for d in docs)


def test_disjoint_budgets_block_calls_and_tampered_plans(tmp_path):
    directory = setup(tmp_path, .1)
    Fake.calls = 0
    for i in range(2):
        run_lane(directory, i, .05, lambda job: run(job, client_factory=Fake))
    assert Fake.calls == 0 and report(directory)["estimated_committed_usd"] == 0
    verify(directory)
    (directory / "lane-0/plan.json").write_text("[]")
    with pytest.raises(ValueError, match="lane plans changed"):
        verify(directory)


def test_uncertain_error_keeps_reservation_without_repair(tmp_path):
    directory = setup(tmp_path)
    class Broken(Fake):
        calls = 0
        def complete(self, prompt, seed):
            type(self).calls += 1
            raise TimeoutError()
    for _ in range(2):
        run_lane(directory, 0, .5, lambda job: run(job, client_factory=Broken))
    result = report(directory)
    assert Broken.calls == 1 and result["accepted"] == 0
    assert .1 < result["estimated_committed_usd"] < .5
    assert not list((directory / "lane-0").glob("*-repair"))
