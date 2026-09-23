"""Two sequential lanes with disjoint budgets, durable attempts, and quality gates.

Every call is a frozen campaign. Completed rejections get at most one repair;
uncertain calls retain their full reservation and are never retried automatically.
"""
from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .batch import _atomic, _json, _locked, _sha
from .campaign import prepare, prepare_repairs, run, MODEL


def committed(lane):
    return sum(json.loads(p.read_text())["estimated_committed_usd"]
               for p in lane.glob("*/state.json"))


def eligible_repair(job, doc_id):
    state = json.loads((job / "state.json").read_text())
    record = state["records"].get(doc_id, {})
    response = job / f"response.{doc_id}.json"
    return (record.get("status") == "rejected" and response.exists()
            and json.loads(response.read_text())["completion"].get("finish_reason") == "stop")


def init(plan_path, directory, budget=150.0):
    plans = [json.loads(s) for s in Path(plan_path).read_text().splitlines() if s.strip()]
    if not plans or len({p["doc_id"] for p in plans}) != len(plans):
        raise ValueError("unique nonempty plans required")
    if not 0 < budget <= 150 or any(p["generator_slice"] != "api-main" for p in plans):
        raise ValueError("all API plans and budget in (0,150] required")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    # Freeze a complete offline campaign before sending any requests.
    prepare(plan_path, directory / "frozen", budget, prompt_version="compose_v6")
    manifest = {"target": len(plans), "budget_usd": budget, "lanes": 2,
                "lane_budget_usd": budget / 2, "model": MODEL,
                "prompt_version": "compose_v6", "max_repairs_per_document": 1,
                "quality_gate": "pause a lane if final acceptance <70% after 10 documents",
                "error_gate": "pause a lane after 3 consecutive uncertain calls",
                "frozen_manifest_sha256": _sha((directory / "frozen/manifest.json").read_bytes())}
    _atomic(directory / "manifest.json", _json(manifest))
    for i in range(2):
        lane = directory / f"lane-{i}"
        lane.mkdir()
        _atomic(lane / "plan.json", _json(plans[i::2]))
        _atomic(lane / "progress.json", _json({"completed": [], "stop_reason": "prepared"}))
    return manifest


def verify(directory):
    manifest = json.loads((directory / "manifest.json").read_text())
    frozen_bytes = (directory / "frozen/manifest.json").read_bytes()
    frozen = json.loads(frozen_bytes)
    if _sha(frozen_bytes) != manifest["frozen_manifest_sha256"]:
        raise ValueError("frozen manifest changed")
    for path, digest in frozen["source_hashes"].items():
        if _sha(Path(path).read_bytes()) != digest:
            raise ValueError("production sources changed")
    payload = (directory / "frozen/requests.json").read_bytes()
    if _sha(payload) != frozen["requests_sha256"]:
        raise ValueError("frozen requests changed")
    plans = [r["plan"] for r in json.loads(payload)]
    if manifest["budget_usd"] != frozen["budget_usd"] or manifest["lane_budget_usd"] * 2 != frozen["budget_usd"]:
        raise ValueError("budget changed")
    for i in range(2):
        if json.loads((directory / f"lane-{i}/plan.json").read_text()) != plans[i::2]:
            raise ValueError("lane plans changed")
    return manifest


def run_lane(directory, number, budget, runner=run):
    lane = directory / f"lane-{number}"
    with _locked(lane):
        progress = json.loads((lane / "progress.json").read_text())
        if progress["stop_reason"] in {"quality_gate", "error_gate", "budget", "reservation_exceeded"}:
            return progress
        plans = json.loads((lane / "plan.json").read_text())
        done = {p["doc_id"] for p in progress["completed"]}
        uncertain_streak = 0
        for old in reversed(progress["completed"]):
            if not old["uncertain"]:
                break
            uncertain_streak += 1
        for plan in plans:
            doc_id = plan["doc_id"]
            if doc_id in done:
                continue
            initial = lane / f"{doc_id}-initial"
            plan_path = lane / "current-plan.jsonl"
            if not initial.exists():
                remaining = budget - committed(lane)
                if remaining <= 0:
                    progress["stop_reason"] = "budget"
                    break
                _atomic(plan_path, json.dumps(plan, ensure_ascii=False) + "\n")
                prepare(plan_path, initial, remaining, prompt_version="compose_v6")
            state = runner(initial)
            selected = initial
            if state["stop_reason"] in {"budget", "reservation_exceeded"}:
                progress["stop_reason"] = state["stop_reason"]
                break
            if eligible_repair(initial, doc_id):
                repair = lane / f"{doc_id}-repair"
                if not repair.exists():
                    remaining = budget - committed(lane)
                    if remaining <= 0:
                        progress["stop_reason"] = "budget"
                        break
                    response = json.loads((initial / f"response.{doc_id}.json").read_text())
                    raw_path = lane / "current-repair.jsonl"
                    _atomic(raw_path, json.dumps(response, ensure_ascii=False) + "\n")
                    prepare_repairs(raw_path, repair, remaining)
                state = runner(repair)
                selected = repair
                if state["stop_reason"] in {"budget", "reservation_exceeded"}:
                    progress["stop_reason"] = state["stop_reason"]
                    break
            entry = state["records"][doc_id]
            uncertain = entry["status"] in {"in_flight", "request_error", "usage_unknown"}
            uncertain_streak = uncertain_streak + 1 if uncertain else 0
            progress["completed"].append({"doc_id": doc_id, "status": entry["status"],
                                          "selected": selected.name, "uncertain": uncertain})
            n = len(progress["completed"])
            accepted = sum(r["status"] == "accepted" for r in progress["completed"])
            progress.update(stop_reason="running", estimated_committed_usd=committed(lane))
            if uncertain_streak >= 3:
                progress["stop_reason"] = "error_gate"
            elif n >= 10 and accepted / n < .7:
                progress["stop_reason"] = "quality_gate"
            _atomic(lane / "progress.json", _json(progress))
            print(json.dumps({"lane": number, "completed": n, "accepted": accepted,
                              "usd": progress["estimated_committed_usd"], "stop": progress["stop_reason"]}), flush=True)
            if progress["stop_reason"] != "running":
                break
        else:
            progress["stop_reason"] = "all_attempted"
        _atomic(lane / "progress.json", _json(progress))
        return progress


def report(directory):
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text())
    docs, raws, lanes = [], [], []
    for i in range(2):
        lane = directory / f"lane-{i}"
        progress = json.loads((lane / "progress.json").read_text())
        lanes.append({"lane": i, "completed": len(progress["completed"]),
                      "stop_reason": progress["stop_reason"], "estimated_committed_usd": committed(lane)})
        for row in progress["completed"]:
            if row["status"] == "accepted":
                docs.append(json.loads((lane / row["selected"] / f"document.{row['doc_id']}.json").read_text()))
        for path in sorted(lane.glob("*/response.*.json")):
            raws.append(json.loads(path.read_text()))
    summary = {"target": manifest["target"], "accepted": len(docs), "responses": len(raws),
               "estimated_committed_usd": sum(l["estimated_committed_usd"] for l in lanes),
               "budget_usd": manifest["budget_usd"], "lanes": lanes,
               "human_reviewed": False}
    for name, rows in (("docs.jsonl", docs), ("raw.jsonl", raws)):
        _atomic(directory / name, "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    _atomic(directory / "summary.json", _json(summary))
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["prepare", "run", "report"])
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--plan")
    parser.add_argument("--budget-usd", default=150.0, type=float)
    args = parser.parse_args()
    if args.command == "prepare":
        result = init(args.plan, args.directory, args.budget_usd)
    elif args.command == "report":
        result = report(args.directory)
    else:
        with _locked(args.directory):
            manifest = verify(args.directory)
            try:
                with ThreadPoolExecutor(max_workers=2) as pool:
                    futures = [pool.submit(run_lane, args.directory, i, manifest["lane_budget_usd"]) for i in range(2)]
                    for future in futures:
                        future.result()
            finally:
                result = report(args.directory)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
