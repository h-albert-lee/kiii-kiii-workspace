"""문서·스팬 스키마 (docs/generation_design.md §7). dataclass + JSON 직렬화."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Fragment:
    group: str
    index: int
    of: int


@dataclass
class Span:
    id: str
    start: int
    end: int
    surface: str
    canonical: str
    category: str
    tier: str
    kind: str
    span_policy: str
    entity_id: str
    subject_id: str
    subject_role: str                      # customer | staff | third_party
    subtype: str | None = None
    applied_ops: list[str] = field(default_factory=list)
    regex_catchable: bool = True
    fragment: Fragment | None = None


@dataclass
class HardNegative:
    start: int
    end: int
    surface: str
    type: str


@dataclass
class Subject:
    id: str
    role: str


@dataclass
class Document:
    doc_id: str
    doc_type: str
    variation_level: str
    num_subjects: int
    context_len_bucket: str
    n_tokens: int
    generator: dict[str, Any]
    taxonomy_version: str
    text: str
    spans: list[Span] = field(default_factory=list)
    hard_negatives: list[HardNegative] = field(default_factory=list)
    subjects: list[Subject] = field(default_factory=list)
    pre_masked: bool = False

    def to_json(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_json(d: dict) -> "Document":
        spans = [Span(**{**s, "fragment": Fragment(**s["fragment"]) if s.get("fragment") else None}) for s in d["spans"]]
        return Document(
            **{k: v for k, v in d.items() if k not in ("spans", "hard_negatives", "subjects")},
            spans=spans,
            hard_negatives=[HardNegative(**h) for h in d.get("hard_negatives", [])],
            subjects=[Subject(**s) for s in d.get("subjects", [])],
        )
