"""Offline Batch lifecycle regressions, including ambiguous submission failures."""
import json
from copy import deepcopy
from types import SimpleNamespace

import pytest

from src.generate import batch, run
from src.generate.compose import completion_options, plan_to_dict
from src.generate.taxonomy import Taxonomy


def obj(value):
    return SimpleNamespace(**value, model_dump=lambda: deepcopy(value))


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


@pytest.fixture
def job(tmp_path, monkeypatch):
    monkeypatch.setattr(batch, "_client", lambda: pytest.fail("unexpected API initialization"))
    plans = run.make_plans(Taxonomy(), 5, 0)
    plan = tmp_path / "plan.jsonl"
    plan.write_text(batch._jsonl(plan_to_dict(p) for p in plans))
    directory = tmp_path / "job"
    run.main(["batch-prepare", "--plan", str(plan), "--model", "gpt-6-astra",
              "--prompt-version", "compose_v2", "--batch-dir", str(directory)])
    return directory


class FakeAPI:
    def __init__(self, directory):
        self.uploads = self.creates = self.downloads = 0
        self.timeout = False
        manifest, _, _ = batch._load(directory)
        self.remote = {"id": "batch_test", "input_file_id": "file_input", "endpoint": batch.ENDPOINT,
                       "metadata": {"kiii_job_id": manifest["job_id"]}, "status": "in_progress",
                       "output_file_id": None, "error_file_id": None, "errors": None}
        self.contents = {}
        self.files = SimpleNamespace(create=self.upload, content=self.download)
        self.batches = SimpleNamespace(create=self.create, retrieve=self.retrieve)

    def upload(self, file, purpose):
        assert purpose == "batch"
        assert file.read()
        self.uploads += 1
        return obj({"id": "file_input"})

    def create(self, **kwargs):
        self.creates += 1
        assert kwargs == {"input_file_id": "file_input", "endpoint": batch.ENDPOINT,
                          "completion_window": "24h", "metadata": self.remote["metadata"]}
        if self.timeout:
            raise TimeoutError("response lost after remote creation")
        return obj(self.remote)

    def retrieve(self, batch_id):
        assert batch_id == "batch_test"
        return obj(self.remote)

    def download(self, file_id):
        self.downloads += 1
        return SimpleNamespace(text=self.contents[file_id])


def api_for(job, monkeypatch):
    client = FakeAPI(job)
    monkeypatch.setattr(batch, "_client", lambda: client)
    return client


def response(did, finish="stop", content="고객 {{person_name:1}}", status_code=200):
    return {"id": "batch_req_" + did, "custom_id": did, "error": None,
            "response": {"status_code": status_code, "request_id": "req_" + did,
                         "body": {"id": "response_" + did, "model": "gpt-6-astra",
                                  "choices": [{"message": {"content": content}, "finish_reason": finish}],
                                  "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30,
                                            "completion_tokens_details": {"reasoning_tokens": 3}}}}}


def test_prepare_offline_routing_and_frozen_settings(job):
    manifest, state, requests = batch._load(job)
    assert len(requests) == 4  # local-check is never uploaded
    assert state["phase"] == "prepared"
    for request in requests:
        record = manifest["records"][request["custom_id"]]
        assert record["plan"]["generator_slice"] == "api-main"
        assert "{{person_name:1}}" in request["body"]["messages"][0]["content"]
        options = {k: v for k, v in request["body"].items() if k not in ("model", "messages")}
        assert options == completion_options("gpt-6-astra", seed=record["plan"]["seed"])
    assert batch.status(job)["phase"] == "prepared"


def test_prepare_rejects_overwrite_empty_slice_duplicates_and_limits(job, tmp_path, monkeypatch):
    plan = tmp_path / "plan.jsonl"
    before = (job / "manifest.json").read_bytes()
    with pytest.raises(FileExistsError):
        batch.prepare(plan, job, "gpt-6-astra", "compose_v2")
    assert (job / "manifest.json").read_bytes() == before
    rows = read_rows(plan)
    for contents, message in (([r for r in rows if r["generator_slice"] == "local-check"], "no api-main"),
                              ([rows[0], rows[0]], "duplicate")):
        other = tmp_path / "other.jsonl"
        other.write_text(batch._jsonl(contents))
        with pytest.raises(ValueError, match=message):
            batch.prepare(other, tmp_path / "bad", "gpt-6-astra", "compose_v2")
    monkeypatch.setattr(batch, "MAX_REQUESTS", 1)
    with pytest.raises(ValueError, match="requests"):
        batch.prepare(plan, tmp_path / "oversized", "gpt-6-astra", "compose_v2")
    monkeypatch.setattr(batch, "MAX_REQUESTS", 50_000)
    monkeypatch.setattr(batch, "MAX_BYTES", 1)
    with pytest.raises(ValueError, match="200 MB"):
        batch.prepare(plan, tmp_path / "oversized", "gpt-6-astra", "compose_v2")


@pytest.mark.parametrize("name", ["requests.jsonl", "manifest.json"])
def test_tampering_rejected_before_network(job, name):
    with (job / name).open("a") as f:
        f.write(" ")
    with pytest.raises(ValueError, match="hash mismatch"):
        batch.submit(job)


def test_submit_only_once_and_status(job, monkeypatch):
    api = api_for(job, monkeypatch)
    batch.submit(job)
    assert batch.submit(job)["already_submitted"]
    assert api.uploads == api.creates == 1
    assert batch.status(job)["status"] == "in_progress"
    assert batch.collect(job)["collected"] is False
    assert not (job / "raw.jsonl").exists()
    with batch._locked(job), pytest.raises(ValueError, match="another batch command"):
        batch.submit(job)


def test_unknown_submission_not_repeated_and_recoverable(job, monkeypatch):
    api = api_for(job, monkeypatch)
    api.timeout = True
    with pytest.raises(TimeoutError):
        batch.submit(job)
    with pytest.raises(ValueError, match="outcome is uncertain"):
        batch.submit(job)
    assert api.creates == 1
    batch.submit(job, recover_batch_id="batch_test")
    assert batch.submit(job)["already_submitted"]
    assert api.creates == api.uploads == 1


def test_remote_mismatch_rejected(job, monkeypatch):
    api = api_for(job, monkeypatch)
    batch.submit(job)
    api.remote["metadata"]["kiii_job_id"] = "unrelated-job"
    with pytest.raises(ValueError, match="does not match"):
        batch.collect(job)


def test_unordered_partial_results_usage_retry_and_idempotent_collection(job, tmp_path, monkeypatch):
    api = api_for(job, monkeypatch)
    batch.submit(job)
    manifest, _, requests = batch._load(job)
    ids = [r["custom_id"] for r in requests]
    api.remote.update(status="expired", output_file_id="out", error_file_id="err")
    api.contents["out"] = batch._jsonl([response(ids[2], finish="length"), response(ids[0])])
    api.contents["err"] = batch._jsonl([{"custom_id": ids[1], "response": None,
                                         "error": {"code": "batch_expired", "message": "expired"}}])
    summary = batch.collect(job)
    assert summary["succeeded"] == 1 and summary["failed"] == 3
    assert summary["usage"]["completion_tokens"] == 40  # includes truncated billable output
    raw = read_rows(job / "raw.jsonl")
    assert [r["doc_id"] for r in raw] == [ids[0], ids[2]]
    assert raw[0]["plan"] == manifest["records"][ids[0]]["plan"]
    assert raw[0]["completion"]["transport"] == "batch"
    assert raw[1]["completion"]["finish_reason"] == "length"
    assert raw[0]["completion"]["usage"]["completion_tokens_details"]["reasoning_tokens"] == 3
    errors = read_rows(job / "errors.jsonl")
    assert {r["reason"] for r in errors} == {"request_error", "incomplete_or_empty_response", "missing_result"}
    monkeypatch.setattr(batch, "_client", lambda: pytest.fail("collection should be cached"))
    before = (job / "raw.jsonl").read_bytes()
    assert batch.collect(job) == summary
    assert (job / "raw.jsonl").read_bytes() == before
    child = tmp_path / "retry"
    batch.retry(job, child)
    m2, _, req2 = batch._load(child)
    assert req2 == requests[1:]
    assert m2["parent_batch_id"] == "batch_test"
    assert m2["job_id"] != manifest["job_id"]
    assert set(m2["records"]) == set(ids[1:])


@pytest.mark.parametrize("status", ["completed", "failed", "cancelled"])
def test_terminal_batch_without_outputs_marks_all_missing(job, monkeypatch, status):
    api = api_for(job, monkeypatch)
    batch.submit(job)
    api.remote.update(status=status, errors={"data": [{"code": "invalid_request"}]})
    summary = batch.collect(job)
    assert summary["failed"] == 4 and summary["succeeded"] == 0
    assert summary["batch_errors"]["data"][0]["code"] == "invalid_request"


@pytest.mark.parametrize("mutation", ["duplicate", "unknown", "empty", "http", "refusal", "malformed"])
def test_bad_result_handling(job, mutation):
    manifest, _, requests = batch._load(job)
    rows = [response(r["custom_id"]) for r in requests]
    remote = {"id": "batch_test", "status": "completed"}
    if mutation == "duplicate":
        rows.append(rows[0])
    elif mutation == "unknown":
        rows[0]["custom_id"] = "unknown"
    elif mutation == "empty":
        rows[0]["response"]["body"]["choices"][0]["message"]["content"] = " "
    elif mutation == "http":
        rows[0]["response"]["status_code"] = 429
    elif mutation == "refusal":
        rows[0]["response"]["body"]["choices"][0]["message"]["refusal"] = "refused"
    else:
        rows[0]["response"]["body"]["choices"] = []
    if mutation in ("duplicate", "unknown"):
        with pytest.raises(ValueError, match="unknown or duplicate"):
            batch.normalize_results(manifest, requests, remote, rows)
    else:
        raw, errors, summary = batch.normalize_results(manifest, requests, remote, rows)
        assert summary["succeeded"] == 3 and summary["failed"] == 1
        assert len(errors) == 1
        if mutation == "refusal":
            assert raw[0]["completion"]["finish_reason"] == "refusal"


def test_successful_batch_raw_can_fill_and_retry_cannot_repeat_success(job, tmp_path, monkeypatch):
    api = api_for(job, monkeypatch)
    batch.submit(job)
    _, _, requests = batch._load(job)
    api.remote.update(status="completed", output_file_id="out")
    api.contents["out"] = batch._jsonl(response(r["custom_id"]) for r in requests)
    assert batch.collect(job)["succeeded"] == 4
    with pytest.raises(ValueError, match="no failed"):
        batch.retry(job, tmp_path / "retry")
    # Existing fill accepts the raw schema and reports document validation normally.
    docs = tmp_path / "docs.jsonl"
    run.main(["fill", "--raw", str(job / "raw.jsonl"), "--out", str(docs)])
    assert len(read_rows(docs)) + len(read_rows(tmp_path / "docs.jsonl.rejects.jsonl")) == 4
    with (job / "raw.jsonl").open("a") as f:
        f.write(" ")
    with pytest.raises(ValueError, match="collected file hash mismatch"):
        batch.collect(job)


def test_batch_client_ignores_local_base_url_and_disables_retries(monkeypatch):
    import openai
    called = []
    monkeypatch.setenv("OPENAI_BASE_URL", "http://localhost:8000/v1")
    monkeypatch.setattr(openai, "OpenAI", lambda **kw: called.append(kw))
    batch._client()
    assert called == [{"base_url": "https://api.openai.com/v1", "max_retries": 0}]


def test_retry_merge_requires_coverage_and_excludes_truncated_responses(job, tmp_path, monkeypatch):
    api = api_for(job, monkeypatch)
    batch.submit(job)
    _, _, requests = batch._load(job)
    ids = [r["custom_id"] for r in requests]
    api.remote.update(status="completed", output_file_id="out")
    api.contents["out"] = batch._jsonl([response(ids[0], finish="length")]
                                       + [response(did) for did in ids[1:]])
    batch.collect(job)
    merged = tmp_path / "merged.jsonl"
    with pytest.raises(ValueError, match="missing successful"):
        batch.merge([job], merged)
    assert not merged.exists()
    child = tmp_path / "retry"
    batch.retry(job, child)
    api2 = api_for(child, monkeypatch)
    batch.submit(child)
    api2.remote.update(status="completed", output_file_id="out")
    api2.contents["out"] = batch._jsonl([response(ids[0], content="재생성 {{person_name:1}}")])
    batch.collect(child)
    monkeypatch.setattr(batch, "_client", lambda: pytest.fail("merge should be offline"))
    assert batch.merge([job, child], merged)["documents"] == 4
    rows = read_rows(merged)
    assert [r["doc_id"] for r in rows] == ids
    assert all(r["completion"]["finish_reason"] == "stop" for r in rows)
    assert rows[0]["raw"].startswith("재생성")
    with pytest.raises(FileExistsError):
        batch.merge([job, child], merged)


def test_batch_to_fill_preserves_a_valid_document(tmp_path, monkeypatch):
    import random
    from src.generate.compose import make_plan
    tax = Taxonomy()
    plan = make_plan(tax, random.Random(0), "internal_memo", "T0", 1, "1k", "api-main", 1)
    plan_path = tmp_path / "one.jsonl"
    plan_path.write_text(batch._jsonl([plan_to_dict(plan)]))
    job = tmp_path / "one"
    batch.prepare(plan_path, job, "gpt-6-astra", "compose_v2")
    api = api_for(job, monkeypatch)
    batch.submit(job)
    raw_text = "검토 고객 {{person_name:1}}의 신청 건입니다."
    api.remote.update(status="completed", output_file_id="out")
    api.contents["out"] = batch._jsonl([response(plan.doc_id, content=raw_text)])
    batch.collect(job)
    docs = tmp_path / "docs.jsonl"
    run.main(["fill", "--raw", str(job / "raw.jsonl"), "--out", str(docs)])
    expected, errors = run.fill_one(tax, plan, raw_text, "gpt-6-astra", "compose_v2")
    assert errors == []
    assert read_rows(docs) == [expected.to_json()]
    assert not (tmp_path / "docs.jsonl.rejects.jsonl").read_text()
