"""Audit the matched MangoInference pilot and retain reproducible reports."""
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.generate.audit import audit_records
from src.generate.compose import Plan
from src.generate.run import fill_one
from src.generate.taxonomy import Taxonomy


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def estimate(records, prices):
    cost = 0
    for r in records:
        u = r.get("completion", {}).get("usage") or {}
        detail = u.get("prompt_tokens_details") or {}
        cached = detail.get("cached_tokens", 0) or 0
        written = detail.get("cache_write_tokens", 0) or 0
        cost += (max(0, u.get("prompt_tokens", 0) - cached - written) * prices["input"]
                 + cached * prices["cached_input"]
                 + written * prices.get("cache_write", prices["input"])
                 + u.get("completion_tokens", 0) * prices["output"]) / 1e6
    return round(cost, 6)


def main(directory):
    directory = Path(directory)
    config = json.loads((directory / "run-config.json").read_text())
    plans = {p["doc_id"]: p for p in map(json.loads, (directory / "plan.jsonl").read_text().splitlines())}
    tax = Taxonomy()
    provenance = {k: config[k] for k in ("run_id", "git_commit", "git_dirty", "data_version", "prompt_version", "provenance_note")}
    summary = {**provenance, "purpose": config["purpose"], "planned_per_model": len(plans), "models": {}}
    for name in config.get("sources", ("astra-reference", "deepseek", "glm")):
        path = directory / f"raw.{name}.jsonl"
        if not path.exists():
            continue
        records = [json.loads(line) for line in path.read_text().splitlines()]
        expected_prompt = config.get("source_prompt_versions", {}).get(name, config["prompt_version"])
        seen = set()
        for r in records:
            if r["doc_id"] in seen or r["plan"] != plans.get(r["doc_id"]):
                raise ValueError("duplicate ID or changed comparison plan")
            if r["prompt_version"] != expected_prompt:
                raise ValueError("comparison prompt version mismatch")
            seen.add(r["doc_id"])
        audit = audit_records(records, tax)
        audit.update(provenance)
        audit["prompt_version"] = expected_prompt
        write_json(directory / f"audit.{name}.json", audit)
        docs, rejected = [], []
        for r in records:
            doc, errors = fill_one(tax, Plan(**r["plan"]), r["raw"], r["model"], r["prompt_version"])
            if r.get("completion", {}).get("finish_reason") != "stop" or not r["raw"].strip():
                errors.append("incomplete/empty model response")
            if doc and not errors:
                docs.append(doc.to_json())
            else:
                rejected.append({"doc_id": r["doc_id"], "errors": errors})
        for target, rows in ((f"docs.{name}.jsonl", docs), (f"docs.{name}.rejects.jsonl", rejected)):
            (directory / target).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
        model = records[0]["model"] if records else None
        prices = ({"input": 10, "cached_input": 1, "cache_write": 12.5, "output": 50}
                  if name == "astra-reference" else config["price_usd_per_million"].get(model))
        flags = Counter(flag for row in audit["rows"] for flag in row["review_flags"])
        summary["models"][name] = {
            "model": model, "prompt_version": expected_prompt,
            "saved_responses": len(records), "missing_ids": sorted(set(plans) - seen),
            "finish_reasons": dict(Counter(r["completion"].get("finish_reason") for r in records)),
            "validator_passed": audit["validator_passed"],
            "documents_with_review_flags": audit["documents_with_review_flags"],
            "review_flags": dict(flags), "usage": audit["usage"],
            "estimated_usd": estimate(records, prices) if prices else None,
            "estimated_price_source": "2026-09-15 Astra price record" if name == "astra-reference" else config["price_source"],
            "response_models": sorted({r["completion"].get("response_model", "") for r in records}),
            "serving_metadata": [r["completion"].get("serving_metadata") for r in records],
            "raw_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    summary["limits"] = [
        "Matched plans; prompt versions are recorded per source. Generation dates, tokenizers and reasoning settings may differ.",
        "Structural checks are not semantic quality approval or human IAA.",
        "Estimates use saved response tokens and stated prices, not account billing; missing responses/retries may cost extra.",
        f"{len(plans)} documents per source were planned; missing IDs are reported. This is screening, not a leaderboard or final generator decision.",
    ]
    write_json(directory / "comparison-summary.json", summary)
    print(json.dumps({k: {x: v[x] for x in ("saved_responses", "validator_passed", "documents_with_review_flags", "estimated_usd", "missing_ids")}
                      for k, v in summary["models"].items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--directory", required=True)
    main(p.parse_args().directory)
