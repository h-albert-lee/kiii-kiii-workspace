"""Apply explicit, source-pinned boundary decisions; never rewrite the source corpus.

Run from the repository root with .venv/bin/python scripts/apply_consultation_review.py.
Outputs are calibration annotations, not independently verified gold labels.
"""
from __future__ import annotations

import copy
import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.generate.schema import Document
from src.generate.taxonomy import Taxonomy
from src.generate.validate import validate


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jsonl(rows):
    return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)


def main():
    review_path = ROOT / "docs/reviews/consultation-calibration-v1.json"
    review = json.loads(review_path.read_text())
    source = ROOT / review["source"]
    if digest(source) != review["source_sha256"]:
        raise ValueError("Source corpus differs from the reviewed version")
    originals = [json.loads(line) for line in source.read_text().splitlines()]
    by_id = {d["doc_id"]: d for d in originals}
    selected = review["selected_doc_ids"]
    decisions = {(r["doc_id"], r["span_id"]): r for r in review["decisions"]}
    assert len(decisions) == len(review["decisions"])
    corrected = []
    tax = Taxonomy()
    for did in selected:
        doc = copy.deepcopy(by_id[did])
        spans = []
        for span in doc["spans"]:
            if span["category"] != "consultation_content":
                spans.append(span)
                continue
            decision = decisions.pop((did, span["id"]))
            assert (decision["start"], decision["end"], decision["original"]) == (
                span["start"], span["end"], span["surface"])
            parts = decision["parts"]
            if decision["action"] == "keep":
                assert parts == [span["surface"]]
                spans.append(span)
                continue
            assert decision["action"] == ("replace" if parts else "drop")
            cursor = 0
            for i, surface in enumerate(parts, 1):
                start = span["surface"].find(surface, cursor)
                assert surface and start >= cursor, (did, span["id"], surface)
                assert span["surface"].count(surface) == 1, "Ambiguous substring"
                cursor = start + len(surface)
                updated = dict(span, start=span["start"] + start,
                               end=span["start"] + cursor,
                               surface=surface, canonical=surface)
                if len(parts) > 1:
                    updated["id"] += f".review{i}"
                    updated["entity_id"] += f".review{i}"
                spans.append(updated)
        doc["spans"] = sorted(spans, key=lambda s: (s["start"], s["end"], s["id"]))
        assert len({s["id"] for s in spans}) == len(spans)
        # All document fields, other categories, and identifier annotations survive.
        assert {k: v for k, v in doc.items() if k != "spans"} == {
            k: v for k, v in by_id[did].items() if k != "spans"}
        other = lambda d: {s["id"]: s for s in d["spans"] if s["category"] != "consultation_content"}
        assert other(doc) == other(by_id[did])
        errors = validate(Document.from_json(doc), tax)
        assert not errors, (did, errors)
        corrected.append(doc)
    assert not decisions

    # Preserve the old blind sample; replace only calibration overlaps within type.
    old_blind = source.parent / "review/consultation-iaa30.jsonl"
    old_rows = [json.loads(line) for line in old_blind.read_text().splitlines()]
    old_ids = {r["doc_id"] for r in old_rows}
    reserved = old_ids | set(selected)
    rng = random.Random(0)
    replacements = {}
    for did in sorted(old_ids & set(selected)):
        candidates = sorted(d["doc_id"] for d in originals
                            if d["doc_id"] not in reserved
                            and d["doc_type"] == by_id[did]["doc_type"])
        replacement = rng.choice(candidates)
        replacements[did] = replacement
        reserved.add(replacement)
    blind = [{"doc_id": replacements.get(r["doc_id"], r["doc_id"]),
              "text": by_id[replacements.get(r["doc_id"], r["doc_id"])]["text"]}
             for r in old_rows]
    assert len(blind) == len({r["doc_id"] for r in blind}) == 30
    assert not ({r["doc_id"] for r in blind} & set(selected))
    assert set(Counter(by_id[r["doc_id"]]["doc_type"] for r in blind).values()) == {3}

    counts = Counter(r["action"] for r in review["decisions"])
    after = sum(s["category"] == "consultation_content" for d in corrected for s in d["spans"])
    manifest = {
        "data_version": "pilot-0.1-consultation-calibration-v1",
        "status": review["status"], "reviewer": review["reviewer"],
        "scope": review["scope"], "source_sha256": digest(source),
        "review_sha256": digest(review_path), "script_sha256": digest(Path(__file__)),
        "selected_doc_ids": selected, "reviewed_existing_spans": len(review["decisions"]),
        "actions": dict(counts), "resulting_consultation_spans": after,
        "validation_passed": len(corrected),
        "human_iaa_performed": False, "blind_sample_replacements": replacements,
        "old_blind_sample_sha256": digest(old_blind),
        "blind_sample_note": "3 per type; excludes calibration; not an estimate over the original full sampling frame",
    }
    report = ["# 상담내용 경계 보정 사례", "", "Codex 단독 검토 · 임시 주석 · 사람 IAA 아님",
              "", f"10개 문서의 기존 태그 64개: 유지 {counts['keep']}, 경계 조정 {counts['replace']}, 제외 {counts['drop']}.",
              "문서 유형별 가장 짧은 문서이므로 전체 코퍼스 오류율로 해석하지 않습니다.", ""]
    for r in review["decisions"]:
        report.extend([f"## {r['doc_id']} / {r['span_id']} — {r['action']}", "",
                       f"원래: {r['original']}", "",
                       "보정: " + (" / ".join(r['parts']) or "상담내용 태그 제외"), "", r['reason'], ""])
    contents = {
        "docs.calibration10.jsonl": jsonl(corrected),
        "consultation-iaa30.v2.jsonl": jsonl(blind),
        "consultation-iaa30.v2.md": "# 독립 검수용 30건 v2\n\n" + "\n\n".join(f"## {r['doc_id']}\n\n{r['text']}" for r in blind),
        "boundary-review.md": "\n".join(report),
    }
    manifest["output_sha256"] = {k: hashlib.sha256(v.encode()).hexdigest() for k, v in contents.items()}
    contents["manifest.json"] = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    out = source.parent / "review/consultation-calibration-v1"
    # Fail before writing if any output would replace different existing content.
    for name, content in contents.items():
        target = out / name
        if target.exists() and target.read_text() != content:
            raise FileExistsError(f"Different output already exists: {target}")
    out.mkdir(parents=True, exist_ok=True)
    for name, content in contents.items():
        (out / name).write_text(content)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
