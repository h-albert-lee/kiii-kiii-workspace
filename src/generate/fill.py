"""LLM 출력(슬롯 {{…}} + 태그 [[…]]…[[/…]])을 파싱해 값을 채우고 gold 스팬을 만든다.

슬롯 문법:  {{category:subject[:k=v,...][|directive,...]}}
  subject    1,2,… = 고객 / staff1,… = 상담사 / tp1,… = 제3자
  params     bank=신한  subtype=mobile  등 생성기 kwargs
  directives given (이름만) | masked | split=N[,part=K] | readback | coref | canonical(변형 금지)
태그 문법:  [[category:subject[:subtype]]]텍스트[[/category]]
"""
from __future__ import annotations

import random
import re
from dataclasses import dataclass

from . import identifiers as ids
from . import variation as var
from .schema import Fragment, Span, Subject
from .taxonomy import Taxonomy

SLOT_RE = re.compile(r"\{\{([a-z_]+):([a-z0-9]+)((?::[a-z_]+=[^:|}]+)*)(?:\|([^}]+))?\}\}")
TAG_OPEN_RE = re.compile(r"\[\[([a-z_]+):([a-z0-9]+)(?::([a-z_]+))?\]\]")
TAG_CLOSE_RE = re.compile(r"\[\[/([a-z_]+)\]\]")


@dataclass
class EntityState:
    entity_id: str
    canonical: str
    meta: dict
    fragments: dict[str, list[str]]


def _role(subject: str) -> str:
    if subject.startswith("staff"):
        return "staff"
    if subject.startswith("tp"):
        return "third_party"
    return "customer"


class Filler:
    def __init__(self, tax: Taxonomy, level: str, rng: random.Random, doc_type: str, stt: bool = False,
                 profiles=None, profile_seed: int | None = None):
        self.tax, self.level, self.rng, self.doc_type, self.stt = tax, level, rng, doc_type, stt
        self.profiles, self.profile_seed = profiles, profile_seed
        self.entities: dict[tuple[str, str], EntityState] = {}
        self.subjects: dict[str, Subject] = {}
        self._eid = 0
        self._sid = 0
        self.level_of = {o.id: o.level for o in tax.ops.values()}

    # ------------------------------------------------------------ entities
    def entity(self, category: str, subject: str, params: dict) -> EntityState:
        key = (category, subject)
        if key not in self.entities:
            self._eid += 1
            kw = dict(params)
            if category in ("email", "online_handle"):
                name = self.entities.get(("person_name", subject))
                kw["name_meta"] = name.meta if name else None
            entity_rng = self.rng
            if self.profiles is not None:
                from .profiles import profile_rng
                if subject not in self.profiles:
                    raise ValueError(f"unknown profile subject: {subject}")
                profile = self.profiles[subject]
                if category in ("rrn", "foreigner_reg_no"):
                    if (category == "rrn") != (profile.nationality == "대한민국"):
                        raise ValueError(f"identifier nationality mismatch: {category}:{subject}")
                    kw.update(birth=profile.birth, sex=profile.sex)
                if category == "passport_no" and profile.nationality != "대한민국":
                    raise ValueError(f"Korean passport generator used for foreign profile: {subject}")
                if category in ("rrn", "foreigner_reg_no", "address"):
                    group = profile.household if category == "address" else subject
                    entity_rng = profile_rng(self.profile_seed, f"{category}:{group}")
            canonical, meta = ids.generate(category, entity_rng, **kw)
            self.entities[key] = EntityState(f"e{self._eid}", canonical, meta, {})
        if subject not in self.subjects:
            self.subjects[subject] = Subject(id=subject, role=_role(subject))
        return self.entities[key]

    # ------------------------------------------------------------ ops sampling
    def sample_ops(self, category: str, directives: dict) -> list[str]:
        cat = self.tax[category]
        if self.level == "T0" or "canonical" in directives or "readback" in directives:
            return []
        candidates = [o.id for o in self.tax.ops_for(cat, self.level) if o.id in var.OPS]
        if not candidates:
            return []
        k = self.rng.choice([1, 1, 2])
        chosen: list[str] = []
        for c in self.rng.sample(candidates, k=len(candidates)):
            if len(chosen) >= k:
                break
            if any(c in g and any(x in g for x in chosen) for g in var.EXCLUSIVE_GROUPS):
                continue
            chosen.append(c)
        if "masked" in directives and "partial_mask" not in chosen:
            chosen = [c for c in chosen if not any(c in g and "partial_mask" in g for g in var.EXCLUSIVE_GROUPS)] + ["partial_mask"]
        # STT 프로필: 전사 문서에서 숫자 식별자는 한글 표기 확률 상향
        if self.stt and category in var.NUMERIC_ONLY | {"phone_no", "bank_account_no"} and self.level in ("T2", "T3"):
            p = self.tax.stt_profile.get("digit_rendering", {}).get("hangul_phonetic", 0.2)
            if self.rng.random() < p and "hangul_digits" in [o.id for o in self.tax.ops_for(cat, self.level)]:
                chosen = ["hangul_digits"] + [c for c in chosen if not any(c in g and "hangul_digits" in g for g in var.EXCLUSIVE_GROUPS)]
        return var.order_ops(chosen)

    # ------------------------------------------------------------ main
    def fill(self, llm_text: str) -> tuple[str, list[Span], list[Subject]]:
        out: list[str] = []
        spans: list[Span] = []
        pos = 0            # output cursor
        i = 0
        open_tags: list[tuple[str, str, str | None, int]] = []   # (category, subject, subtype, start)
        sid = 0

        while i < len(llm_text):
            if open_tags and llm_text.startswith("{{NEG}}", i):
                raise ValueError("hard negative inside attribute tag: place {{NEG}} outside all tags")
            m_slot = SLOT_RE.match(llm_text, i)
            m_open = TAG_OPEN_RE.match(llm_text, i)
            m_close = TAG_CLOSE_RE.match(llm_text, i)
            if m_slot:
                category, subject, params_s, directives_s = m_slot.groups()
                if category not in self.tax.categories:
                    raise ValueError(f"unknown category in slot: {category}")
                params = dict(p.split("=", 1) for p in params_s.strip(":").split(":") if p) if params_s else {}
                directives = {}
                for d in (directives_s or "").split(","):
                    if not d:
                        continue
                    k, _, v = d.partition("="); directives[k.strip()] = v.strip() or True
                ent = self.entity(category, subject, params)
                lookahead = llm_text[m_slot.end():m_slot.end() + 6]
                directives["_subject"] = subject
                surface, applied, fragment = self._render(category, ent, directives, lookahead)
                sid += 1
                spans.append(Span(
                    id=f"s{sid}", start=pos, end=pos + len(surface), surface=surface, canonical=ent.canonical,
                    category=category, tier=self.tax[category].tier, kind=self.tax[category].kind,
                    span_policy=self.tax[category].span_policy, entity_id=ent.entity_id, subject_id=subject,
                    subject_role=_role(subject), subtype=params.get("subtype") or ent.meta.get("subtype"),
                    applied_ops=applied, regex_catchable=var.regex_catchable(applied, self.level_of), fragment=fragment,
                ))
                out.append(surface); pos += len(surface); i = m_slot.end()
            elif m_open:
                category, subject, subtype = m_open.groups()
                if category not in self.tax.categories or self.tax[category].kind != "attribute":
                    raise ValueError(f"tag must be an attribute category: {category}")
                if open_tags:
                    raise ValueError("nested attribute tags are not allowed")
                open_tags.append((category, subject, subtype, pos)); i = m_open.end()
            elif m_close:
                category = m_close.group(1)
                if not open_tags or open_tags[-1][0] != category:
                    raise ValueError(f"unbalanced tag close: {category}")
                cat, subject, subtype, start = open_tags.pop()
                surface = "".join(out)[start:pos]
                if subject not in self.subjects:
                    self.subjects[subject] = Subject(id=subject, role=_role(subject))
                self._eid += 1
                sid += 1
                spans.append(Span(
                    id=f"s{sid}", start=start, end=pos, surface=surface, canonical=surface, category=cat,
                    tier=self.tax[cat].tier, kind="attribute", span_policy=self.tax[cat].span_policy,
                    entity_id=f"e{self._eid}", subject_id=subject, subject_role=_role(subject), subtype=subtype,
                    applied_ops=[], regex_catchable=False, fragment=None,
                ))
                i = m_close.end()
            else:
                out.append(llm_text[i]); pos += 1; i += 1
        if open_tags:
            raise ValueError(f"unclosed tags: {[t[0] for t in open_tags]}")
        text = "".join(out)
        for s in spans:
            assert text[s.start:s.end] == s.surface, (s.id, s.category)
        return text, spans, list(self.subjects.values())

    HONORIFIC_NEXT = re.compile(r"^\s*(고객님|님|씨|선생님|부장|대리|과장|팀장|차장|사장|씨가|님이)")

    def _render(self, category: str, ent: EntityState, directives: dict, lookahead: str = "") -> tuple[str, list[str], Fragment | None]:
        canonical = ent.canonical
        if "split" in directives:
            n = int(directives["split"]); part = int(directives.get("part", 1))
            key = f"split{n}"
            if key not in ent.fragments:
                ent.fragments[key] = var.chunk_split(canonical, self.rng, parts=n)
            piece = ent.fragments[key][part - 1]
            applied = ["chunk_split"] + (["hangul_digits"] if self.stt and self.rng.random() < 0.5 else [])
            surface = var.apply_ops(piece, applied, self.rng)
            return surface, applied, Fragment(group=f"{ent.entity_id}-{key}", index=part, of=n)
        if "given" in directives and category == "person_name":
            return ent.meta["given"], ["given_name_only"], None
        if "readback" in directives:
            return canonical, ["agent_readback"], None
        applied = self.sample_ops(category, directives)
        if "honorific_wrap" in applied and self.HONORIFIC_NEXT.match(lookahead):
            applied = [a for a in applied if a != "honorific_wrap"]
        kw = {}
        if category == "person_name":
            kw["romanized"] = ent.meta.get("romanized")
            kw["role"] = _role(directives.get("_subject", ""))
        surface = var.apply_ops(canonical, applied, self.rng, **kw)
        if "coref" in directives:
            applied = applied + ["coref_reference"]
        return surface, applied, None
