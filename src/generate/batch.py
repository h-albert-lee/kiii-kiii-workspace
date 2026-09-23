"""Durable OpenAI Batch lifecycle; prepare/retry are entirely offline.

Each job freezes requests and plans. Only explicit submit creates billable work.
Results are joined by custom_id and converted to the existing compose raw schema.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import uuid
from collections import Counter
from contextlib import contextmanager
from pathlib import Path

from .compose import Plan, build_prompt, completion_options, plan_to_dict
from .taxonomy import Taxonomy

ENDPOINT = "/v1/chat/completions"
TERMINAL = {"completed", "failed", "expired", "cancelled"}
MAX_REQUESTS = 50_000
MAX_BYTES = 200_000_000


def _json(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def _jsonl(rows):
    return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _read_jsonl(text):
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def _atomic(path, text):
    temp = path.with_name(path.name + ".tmp")
    with temp.open("w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    temp.replace(path)


@contextmanager
def _locked(directory):
    # A process crash releases flock; don't delete a lock file held by another process.
    with (directory / ".lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError("another batch command is using this job directory") from None
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def _client():
    from openai import OpenAI
    # Local Qwen's OPENAI_BASE_URL must never redirect a Batch upload.
    # No implicit retries of batch creation after an ambiguous network failure.
    return OpenAI(base_url="https://api.openai.com/v1", max_retries=0)


def _new_job(directory, manifest, requests):
    payload = _jsonl(requests)
    if not requests or len(requests) > MAX_REQUESTS:
        raise ValueError(f"batch must contain 1..{MAX_REQUESTS} requests")
    if len(payload.encode()) > MAX_BYTES:
        raise ValueError("batch input exceeds 200 MB; split the plan")
    ids = [r["custom_id"] for r in requests]
    if len(set(ids)) != len(ids) or set(ids) != set(manifest["records"]):
        raise ValueError("duplicate or mismatched request IDs")
    manifest = dict(manifest, job_id=uuid.uuid4().hex, endpoint=ENDPOINT,
                    completion_window="24h", requests_sha256=_sha(payload.encode()))
    frozen = _json(manifest)
    directory.mkdir(parents=True, exist_ok=False)
    _atomic(directory / "requests.jsonl", payload)
    _atomic(directory / "manifest.json", frozen)
    _atomic(directory / "state.json", _json({"manifest_sha256": _sha(frozen.encode()),
                                            "phase": "prepared"}))
    return {"job_dir": str(directory), "requests": len(requests), "phase": "prepared"}


def _load(directory):
    frozen = (directory / "manifest.json").read_bytes()
    state = json.loads((directory / "state.json").read_text(encoding="utf-8"))
    if _sha(frozen) != state["manifest_sha256"]:
        raise ValueError("frozen manifest hash mismatch")
    manifest = json.loads(frozen)
    payload = (directory / "requests.jsonl").read_bytes()
    if _sha(payload) != manifest["requests_sha256"]:
        raise ValueError("frozen requests hash mismatch")
    requests = _read_jsonl(payload.decode("utf-8"))
    return manifest, state, requests


def prepare(plan_path, directory, model, prompt_version):
    source = Path(plan_path).read_bytes()
    plans = [Plan(**row) for row in _read_jsonl(source.decode("utf-8"))]
    if len({p.doc_id for p in plans}) != len(plans):
        raise ValueError("duplicate doc_id in plan")
    plans = [p for p in plans if p.generator_slice == "api-main"]
    if not plans:
        raise ValueError("no api-main plans; local-check uses synchronous compose")
    tax = Taxonomy()
    requests = [{"custom_id": p.doc_id, "method": "POST", "url": ENDPOINT,
                 "body": {"model": model,
                          "messages": [{"role": "user", "content": build_prompt(tax, p, prompt_version)}],
                          **completion_options(model, seed=p.seed)}} for p in plans]
    manifest = {"schema_version": 1, "model": model, "prompt_version": prompt_version,
                "generator_slice": "api-main", "taxonomy_version": tax.version,
                "plan_sha256": _sha(source),
                "records": {p.doc_id: {"doc_id": p.doc_id, "plan": plan_to_dict(p),
                                       "model": model, "prompt_version": prompt_version} for p in plans}}
    return _new_job(Path(directory), manifest, requests)


def _verify_remote(remote, manifest, state):
    if (remote.get("input_file_id") != state.get("input_file_id")
            or remote.get("endpoint") != ENDPOINT
            or (remote.get("metadata") or {}).get("kiii_job_id") != manifest["job_id"]
            or (state.get("batch_id") and remote.get("id") != state["batch_id"])):
        raise ValueError("remote batch does not match this local job")


def _save_remote(directory, manifest, state, remote):
    _verify_remote(remote, manifest, state)
    state.update(batch_id=remote["id"], phase="submitted", remote=remote)
    _atomic(directory / "state.json", _json(state))


def submit(directory, recover_batch_id=None):
    directory = Path(directory)
    with _locked(directory):
        manifest, state, _ = _load(directory)
        if state.get("batch_id") and not recover_batch_id:
            return {"batch_id": state["batch_id"], "already_submitted": True}
        if recover_batch_id:
            remote = _client().batches.retrieve(recover_batch_id).model_dump()
            _save_remote(directory, manifest, state, remote)
            return remote
        if state.get("create_attempted"):
            raise ValueError("prior submission outcome is uncertain; locate the batch with metadata "
                             f"kiii_job_id={manifest['job_id']} and use --recover-batch-id; do not resubmit")
        client = _client()
        if not state.get("input_file_id"):
            with (directory / "requests.jsonl").open("rb") as f:
                uploaded = client.files.create(file=f, purpose="batch")
            state.update(input_file_id=uploaded.id, phase="uploaded")
            _atomic(directory / "state.json", _json(state))
        # Persist intent BEFORE sending a potentially billable request.
        state.update(create_attempted=True, phase="submitting")
        _atomic(directory / "state.json", _json(state))
        remote = client.batches.create(input_file_id=state["input_file_id"], endpoint=ENDPOINT,
                                       completion_window="24h",
                                       metadata={"kiii_job_id": manifest["job_id"]}).model_dump()
        _save_remote(directory, manifest, state, remote)
        return remote


def status(directory):
    directory = Path(directory)
    with _locked(directory):
        manifest, state, _ = _load(directory)
        if not state.get("batch_id"):
            return {"phase": state["phase"], "job_id": manifest["job_id"],
                    "requests": len(manifest["records"])}
        remote = _client().batches.retrieve(state["batch_id"]).model_dump()
        _save_remote(directory, manifest, state, remote)
        return remote


def normalize_results(manifest, requests, remote, rows):
    """Terminal results only; keep every returned response, even incomplete ones."""
    if remote["status"] not in TERMINAL:
        raise ValueError("cannot normalize an active batch")
    expected = manifest["records"]
    results = {}
    for row in rows:
        did = row.get("custom_id")
        if did not in expected or did in results:
            raise ValueError(f"unknown or duplicate result custom_id: {did}")
        results[did] = row
    raw, errors, retry_ids = [], [], []
    usage = Counter()
    for request in requests:
        did = request["custom_id"]
        row = results.get(did)
        problem = None
        if row is None:
            problem = "missing_result"
        elif row.get("error"):
            problem = "request_error"
        else:
            response = row.get("response") or {}
            body = response.get("body") or {}
            if response.get("status_code") != 200 or body.get("error"):
                problem = "http_error"
            else:
                choices = body.get("choices") or []
                choice = choices[0] if len(choices) == 1 else {}
                message = choice.get("message") or {}
                content = message.get("content")
                finish = choice.get("finish_reason")
                tokens = body.get("usage") or {}
                for field in ("prompt_tokens", "completion_tokens", "total_tokens"):
                    usage[field] += tokens.get(field, 0)
                completion = {
                    "response_id": body.get("id"), "response_model": body.get("model"),
                    "finish_reason": finish, "usage": tokens,
                    "request_parameters": {k: v for k, v in request["body"].items()
                                           if k not in ("model", "messages")},
                    "transport": "batch", "batch_id": remote["id"],
                    "batch_request_id": row.get("id"), "request_id": response.get("request_id"),
                    "prompt_sha256": _sha(request["body"]["messages"][0]["content"].encode()),
                }
                raw.append({**expected[did], "raw": content if isinstance(content, str) else "",
                            "completion": completion})
                if finish != "stop" or not isinstance(content, str) or not content.strip() or message.get("refusal"):
                    problem = "incomplete_or_empty_response"
                    if message.get("refusal"):
                        raw[-1]["completion"]["finish_reason"] = "refusal"
        if problem:
            retry_ids.append(did)
            errors.append({"doc_id": did, "reason": problem, "result": row})
    summary = {"batch_id": remote["id"], "status": remote["status"],
               "requested": len(requests), "responses_saved": len(raw),
               "succeeded": len(requests) - len(retry_ids), "failed": len(retry_ids),
               "retry_ids": retry_ids, "usage": dict(usage), "batch_errors": remote.get("errors"),
               "note": "Success means complete API response, not corpus validation or human approval."}
    return raw, errors, summary


def _collected(directory, state):
    for name, digest in state["collected_files"].items():
        if _sha((directory / name).read_bytes()) != digest:
            raise ValueError(f"collected file hash mismatch: {name}")
    return json.loads((directory / "summary.json").read_text(encoding="utf-8"))


def collect(directory):
    directory = Path(directory)
    with _locked(directory):
        manifest, state, requests = _load(directory)
        if state.get("collected_files"):
            return _collected(directory, state)
        if not state.get("batch_id"):
            raise ValueError("batch has not been submitted or recovered")
        client = _client()
        remote = client.batches.retrieve(state["batch_id"]).model_dump()
        _save_remote(directory, manifest, state, remote)
        if remote["status"] not in TERMINAL:
            return {"batch_id": remote["id"], "status": remote["status"], "collected": False}
        downloads = {}
        rows = []
        for field, name in (("output_file_id", "batch-output.jsonl"), ("error_file_id", "batch-errors.jsonl")):
            downloads[name] = client.files.content(remote[field]).text if remote.get(field) else ""
            # Preserve original server output even if its records cannot be normalized.
            _atomic(directory / name, downloads[name])
            rows.extend(_read_jsonl(downloads[name]))
        raw, errors, summary = normalize_results(manifest, requests, remote, rows)
        files = {**downloads, "raw.jsonl": _jsonl(raw), "errors.jsonl": _jsonl(errors),
                 "retry-plan.jsonl": _jsonl(manifest["records"][did]["plan"] for did in summary["retry_ids"]),
                 "summary.json": _json(summary)}
        for name, content in files.items():
            _atomic(directory / name, content)
        state["collected_files"] = {name: _sha(content.encode()) for name, content in files.items()}
        _atomic(directory / "state.json", _json(state))
        return summary


def retry(directory, out_dir):
    directory = Path(directory)
    with _locked(directory):
        manifest, state, requests = _load(directory)
        if not state.get("collected_files"):
            raise ValueError("collect the terminal batch before preparing a retry")
        summary = _collected(directory, state)
        ids = set(summary["retry_ids"])
        if not ids:
            raise ValueError("no failed requests to retry")
        child = {**manifest, "parent_batch_id": state["batch_id"],
                 "parent_job_id": manifest["job_id"],
                 "records": {did: record for did, record in manifest["records"].items() if did in ids}}
        return _new_job(Path(out_dir), child, [r for r in requests if r["custom_id"] in ids])


def merge(directories, out):
    """Combine a collected root job and its retries, requiring complete coverage."""
    base, bodies, successful, job_ids = None, {}, {}, set()
    for path in directories:
        directory = Path(path)
        with _locked(directory):
            manifest, state, requests = _load(directory)
            if not state.get("collected_files"):
                raise ValueError("collect each batch before merging")
            _collected(directory, state)
            if base is None:
                base = manifest
                bodies = {r["custom_id"]: r["body"] for r in requests}
            elif manifest.get("parent_job_id") not in job_ids:
                raise ValueError("jobs must be a root followed by its retries")
            job_ids.add(manifest["job_id"])
            for r in requests:
                did = r["custom_id"]
                if (manifest["records"][did] != base["records"].get(did)
                        or r["body"] != bodies.get(did)):
                    raise ValueError("retry metadata/request mismatch")
            for row in _read_jsonl((directory / "raw.jsonl").read_text(encoding="utf-8")):
                if row["completion"]["finish_reason"] != "stop" or not row["raw"].strip():
                    continue
                did = row["doc_id"]
                if did in successful and successful[did] != row:
                    raise ValueError(f"multiple successful responses for {did}; choose explicitly")
                successful[did] = row
    if base is None or set(successful) != set(base["records"]):
        raise ValueError("missing successful responses; finish retries before merging")
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x", encoding="utf-8") as f:
        f.write(_jsonl(successful[did] for did in base["records"]))
    return {"documents": len(successful), "out": str(out)}


def register_commands(sub):
    p = sub.add_parser("batch-prepare", help="freeze api-main requests locally (no API call)")
    p.add_argument("--plan", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--prompt-version", required=True)
    p.add_argument("--batch-dir", required=True)
    p.set_defaults(fn=lambda a: _print(prepare(a.plan, a.batch_dir, a.model, a.prompt_version)))
    p = sub.add_parser("batch-submit", help="upload and submit a prepared job")
    p.add_argument("--batch-dir", required=True)
    p.add_argument("--recover-batch-id")
    p.set_defaults(fn=lambda a: _print(submit(a.batch_dir, a.recover_batch_id)))
    for name, fn in (("batch-status", status), ("batch-collect", collect)):
        p = sub.add_parser(name)
        p.add_argument("--batch-dir", required=True)
        p.set_defaults(fn=lambda a, fn=fn: _print(fn(a.batch_dir)))
    p = sub.add_parser("batch-retry", help="prepare failed requests only; does not submit")
    p.add_argument("--batch-dir", required=True)
    p.add_argument("--out-dir", required=True)
    p.set_defaults(fn=lambda a: _print(retry(a.batch_dir, a.out_dir)))
    p = sub.add_parser("batch-merge", help="combine a completed job and its retries offline")
    p.add_argument("--batch-dirs", nargs="+", required=True)
    p.add_argument("--out", required=True)
    p.set_defaults(fn=lambda a: _print(merge(a.batch_dirs, a.out)))


def _print(value):
    print(_json(value), end="")
