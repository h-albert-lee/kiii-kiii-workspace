"""Merge accepted one-shot repairs into a screening view without touching originals."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.generate.audit import audit_records
from src.generate.compose import Plan
from src.generate.run import fill_one
from src.generate.taxonomy import Taxonomy
from src.generate.campaign import usage_cost, PRICES


def main(directory):
    root = Path(directory)
    config = json.loads((root / "run-config.json").read_text())
    plans = {r["doc_id"]: r for r in map(json.loads, (root / "plan.jsonl").read_text().splitlines())}
    initial = [json.loads(l) for l in (root / "raw.glm.jsonl").read_text().splitlines()]
    selected = {r["doc_id"]: r for r in initial}
    if len(selected) != len(initial):
        raise ValueError("duplicate initial document ID")
    repair_dir = root / "repairs-first"
    state = json.loads((repair_dir / "state.json").read_text()) if repair_dir.exists() else {"records": {}}
    repair_responses = []
    for doc_id, entry in state["records"].items():
        response = repair_dir / f"response.{doc_id}.json"
        if not response.exists():
            continue
        row = json.loads(response.read_text())
        repair_responses.append(row)
        original = selected.get(doc_id)
        if not original or row["plan"] != original["plan"]:
            raise ValueError("repair plan mismatch")
        parent = hashlib.sha256((json.dumps(original, ensure_ascii=False, indent=2) + "\n").encode()).hexdigest()
        if row.get("lineage", {}).get("parent_raw_sha256") != parent:
            raise ValueError("repair parent mismatch")
        if entry["status"] == "accepted":
            selected[doc_id] = row
    rows = list(selected.values())
    tax = Taxonomy()
    docs, rejected = [], []
    for r in rows:
        if r["plan"] != plans[r["doc_id"]] or r["prompt_version"] != config["prompt_version"]:
            raise ValueError("screening plan/version mismatch")
        doc, errors = fill_one(tax, Plan(**r["plan"]), r["raw"], r["model"], r["prompt_version"])
        if r["completion"].get("finish_reason") != "stop" or not r["raw"].strip():
            errors.append("incomplete/empty response")
        if doc and not errors:
            doc.generator["generation_mode"] = r.get("lineage", {}).get("mode", "first_pass")
            if r.get("lineage"):
                doc.generator["lineage"] = r["lineage"]
            docs.append(doc.to_json())
        else:
            rejected.append({"doc_id": r["doc_id"], "errors": errors})
    for name, values in (("raw.final.jsonl", rows), ("docs.final.jsonl", docs), ("docs.final.rejects.jsonl", rejected)):
        (root / name).write_text("".join(json.dumps(v, ensure_ascii=False) + "\n" for v in values))
    summary = {k: config[k] for k in ("run_id", "git_commit", "git_dirty", "data_version", "prompt_version")}
    summary.update(planned=len(plans), initial_saved=len(initial),
                   first_pass_accepted=audit_records(initial, tax)["validator_passed"],
                   final_accepted=len(docs), repaired_accepted=sum(d["generator"]["generation_mode"] == "validation_repair" for d in docs),
                   missing_ids=sorted(set(plans) - set(selected)), final_rejected=rejected,
                   estimated_returned_usage_usd=sum(usage_cost(r["completion"]["usage"], PRICES) for r in initial + repair_responses),
                   uncertain_repair_reserved_usd=sum(e["reserved_usd"] for e in state["records"].values() if e["status"] in {"request_error", "usage_unknown", "in_flight"}),
                   note="Screening only. Cost includes returned initial and repair usage; no-response calls may incur additional charges. Acceptance is automated, not human gold.")
    (root / "final-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    lines = ["# compose_v5 시험 통과본", "", "합성 문서이며 자동 검증 통과본입니다. 사람 검수 완료본은 아닙니다.", ""]
    for d in docs:
        lines += [f"## {d['doc_id']} · {d['doc_type']} · {d['generator']['generation_mode']}", "", d["text"], ""]
    (root / "samples.final.md").write_text("\n".join(lines))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--directory", required=True)
    main(p.parse_args().directory)
