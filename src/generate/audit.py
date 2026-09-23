"""Offline pilot audit: python -m src.generate.audit --raw FILE --out REPORT.json."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from .compose import Plan
from .run import fill_one
from .taxonomy import Taxonomy


def audit_records(records: list[dict], tax: Taxonomy) -> dict:
    rows = []
    usage = Counter()
    for record in records:
        plan = Plan(**record["plan"])
        raw = record["raw"]
        completion = record.get("completion", {})
        tokens = completion.get("usage") or {}
        for field in ("prompt_tokens", "completion_tokens", "total_tokens"):
            usage[field] += tokens.get(field, 0)
        nested_reasoning = (tokens.get("completion_tokens_details") or {}).get("reasoning_tokens")
        usage["reasoning_tokens"] += (nested_reasoning if nested_reasoning is not None
                                      else tokens.get("reasoning_tokens", 0)) or 0
        doc, errors = fill_one(tax, plan, raw, record["model"], record["prompt_version"])
        if completion.get("finish_reason", "stop") != "stop" or not raw.strip():
            errors.append("incomplete/empty model response")
        flags = []
        if "```" in raw:
            flags.append("code_fence_in_output")
        if doc:
            present = {s.category for s in doc.spans}
            missing = sorted(set(plan.required) - present)
            if missing:
                flags.append("missing_required:" + ",".join(missing))
            if re.search(r"\{\{|\}\}|\[\[|\]\]", doc.text):
                flags.append("unresolved_markup")
            for negative in doc.hard_negatives:
                if doc.text[negative.start:negative.end] != negative.surface:
                    flags.append("hard_negative_offset")
                if any(s.start < negative.end and negative.start < s.end for s in doc.spans):
                    flags.append("hard_negative_overlaps_gold")
            if doc.context_len_bucket != plan.context_len_bucket:
                flags.append(f"length_bucket:{plan.context_len_bucket}->{doc.context_len_bucket}")
            higher = sorted({op for s in doc.spans for op in s.applied_ops
                             if op in tax.ops and tax.levels.index(tax.ops[op].level) > tax.levels.index(plan.variation_level)})
            if higher:
                flags.append("ops_above_planned_level:" + ",".join(higher))
            fragments = defaultdict(list)
            for span in doc.spans:
                if span.fragment:
                    fragments[span.fragment.group].append(span.fragment)
            for group, parts in fragments.items():
                if {p.index for p in parts} != set(range(1, parts[0].of + 1)):
                    flags.append("incomplete_fragments:" + group)
        rows.append({
            "doc_id": plan.doc_id, "doc_type": plan.doc_type,
            "level": plan.variation_level, "num_subjects": plan.num_subjects,
            "planned_bucket": plan.context_len_bucket,
            "actual_bucket": doc.context_len_bucket if doc else None,
            "approx_tokens": doc.n_tokens if doc else None,
            "spans": len(doc.spans) if doc else 0,
            "finish_reason": completion.get("finish_reason"),
            "validation_errors": errors, "review_flags": flags,
        })
    return {
        "documents": len(rows), "validator_passed": sum(not row["validation_errors"] for row in rows),
        "documents_with_review_flags": sum(bool(row["review_flags"]) for row in rows),
        "usage": dict(usage), "rows": rows,
        "note": "Validator passes and review flags are automated checks, not human quality approval. Token buckets are character-count approximations.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    records = [json.loads(line) for line in Path(args.raw).read_text(encoding="utf-8").splitlines()]
    report = audit_records(records, Taxonomy())
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "rows"}, ensure_ascii=False))
    for row in report["rows"]:
        print(row["doc_id"], "errors=", row["validation_errors"], "flags=", row["review_flags"])


if __name__ == "__main__":
    main()
