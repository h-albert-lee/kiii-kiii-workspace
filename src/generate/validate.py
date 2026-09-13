"""문서 검증 (docs/generation_design.md §8). 실패 이유 리스트를 반환; 빈 리스트면 통과."""
from __future__ import annotations

import re

from . import identifiers as ids
from .schema import Document
from .taxonomy import Taxonomy

# LLM 이 슬롯 없이 직접 써버린 숫자 식별자 탐지용 (보수적)
LEAK_PATTERNS = {
    "rrn_like": re.compile(r"\b\d{6}-[1-8]\d{6}\b"),
    "card_like": re.compile(r"\b\d{4}-\d{4}-\d{4}-\d{4}\b"),
    "mobile_like": re.compile(r"\b01[016789]-\d{3,4}-\d{4}\b"),
    "brn_like": re.compile(r"\b\d{3}-\d{2}-\d{5}\b"),
}

LEN_BUCKETS = [("1k", 0, 2500), ("4k", 2500, 9000), ("16k", 9000, 10**9)]


def bucket_for(n_tokens: int) -> str:
    for name, lo, hi in LEN_BUCKETS:
        if lo <= n_tokens < hi:
            return name
    return "16k"


def validate(doc: Document, tax: Taxonomy) -> list[str]:
    errors: list[str] = []
    text = doc.text

    # 1. offsets
    for s in doc.spans:
        if text[s.start:s.end] != s.surface:
            errors.append(f"offset mismatch {s.id}: {text[s.start:s.end]!r} != {s.surface!r}")

    # 2. category consistency
    for s in doc.spans:
        if s.category not in tax.categories:
            errors.append(f"unknown category {s.category}"); continue
        c = tax[s.category]
        if (s.tier, s.kind, s.span_policy) != (c.tier, c.kind, c.span_policy):
            errors.append(f"tier/kind/policy mismatch for {s.id} ({s.category})")

    # 3. checksums
    for s in doc.spans:
        v = ids.VALIDATORS.get(s.category)
        if v and s.kind == "identifier" and not s.fragment:
            meta_ok = True
            if s.category == "rrn" and not v(s.canonical):
                # post-2020 랜덤 주민번호는 체크섬 없음 — canonical 앞자리 형식만 확인
                meta_ok = bool(re.fullmatch(r"\d{6}-[1-4]\d{6}", s.canonical))
            elif s.category == "corp_reg_no" and not v(s.canonical):
                meta_ok = bool(re.fullmatch(r"\d{6}-\d{7}", s.canonical))
            elif not v(s.canonical):
                meta_ok = False
            if not meta_ok:
                errors.append(f"checksum/format invalid {s.id} {s.category} {s.canonical}")

    # 4. leaked identifiers outside spans
    covered = [(s.start, s.end) for s in doc.spans] + [(h.start, h.end) for h in doc.hard_negatives]
    for name, pat in LEAK_PATTERNS.items():
        for m in pat.finditer(text):
            if not any(a <= m.start() and m.end() <= b for a, b in covered):
                errors.append(f"leaked {name} outside spans at {m.start()}: {m.group()}")

    # 5. attribute spans length
    for s in doc.spans:
        if s.kind == "attribute" and len(s.surface.split()) < 2:
            errors.append(f"attribute span too short {s.id}: {s.surface!r}")

    # 6. dominant categories present
    dom = tax.document_types.get(doc.doc_type, {}).get("dominant", [])
    dom_ids = {d.split(".")[0].split(":")[-1].strip() for d in dom if not d.startswith("multi-subject")}
    dom_ids = {d for d in dom_ids if d in tax.categories}
    present = {s.category for s in doc.spans}
    if dom_ids and not (dom_ids & present):
        errors.append(f"no dominant category present for {doc.doc_type}: need one of {sorted(dom_ids)}")

    # 7. length bucket
    if bucket_for(doc.n_tokens) != doc.context_len_bucket:
        errors.append(f"length bucket mismatch: planned {doc.context_len_bucket}, actual {bucket_for(doc.n_tokens)} ({doc.n_tokens} tok)")

    # 8. entity consistency
    canon: dict[str, str] = {}
    for s in doc.spans:
        if s.kind == "identifier":
            if s.entity_id in canon and canon[s.entity_id] != s.canonical:
                errors.append(f"entity {s.entity_id} has divergent canonical values")
            canon.setdefault(s.entity_id, s.canonical)

    # 9. subjects declared
    declared = {sub.id for sub in doc.subjects}
    for s in doc.spans:
        if s.subject_id not in declared:
            errors.append(f"span {s.id} references undeclared subject {s.subject_id}")
    if doc.num_subjects != len([sub for sub in doc.subjects if sub.role == "customer"]):
        errors.append(f"num_subjects {doc.num_subjects} != customers declared")

    return errors
