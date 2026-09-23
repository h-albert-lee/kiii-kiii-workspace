"""Versioned synthetic subject facts shared by compose_v4 and identifier filling."""
from __future__ import annotations

import hashlib
import random
import re
from dataclasses import asdict, dataclass
from datetime import date, timedelta

VERSION = "profiles_v1"
REFERENCE_DATE = date(2026, 9, 1)


def profile_rng(seed: int, key: str) -> random.Random:
    digest = hashlib.sha256(f"{VERSION}:{seed}:{key}".encode()).digest()
    return random.Random(int.from_bytes(digest, "big"))


@dataclass(frozen=True)
class Profile:
    subject: str
    birth: str
    sex: str
    nationality: str
    household: str
    spouse: str | None = None

    @property
    def age(self) -> int:
        b = date.fromisoformat(self.birth)
        return REFERENCE_DATE.year - b.year - ((REFERENCE_DATE.month, REFERENCE_DATE.day) < (b.month, b.day))


def make_profiles(seed: int, num_subjects: int) -> dict[str, Profile]:
    subjects = [str(i) for i in range(1, num_subjects + 1)] + ["staff1", "staff2", "tp1", "tp2"]
    profiles = {}
    for subject in subjects:
        rng = profile_rng(seed, subject)
        birth = date(1960, 1, 1) + timedelta(days=rng.randrange(45 * 365))
        foreign = subject == "tp2" or (num_subjects == 8 and subject == "8")
        profiles[subject] = Profile(subject, birth.isoformat(), rng.choice(["M", "F"]),
                                    "미국" if foreign else "대한민국", subject)
    # Explicit spouse pair: customer 1 + customer 2 (or a third party for a single customer).
    partner = "2" if num_subjects > 1 else "tp1"
    first = profiles["1"]
    partner_birth = date.fromisoformat(first.birth) + timedelta(days=730)
    profiles["1"] = Profile(**{**asdict(first), "spouse": partner})
    profiles[partner] = Profile(partner, partner_birth.isoformat(), "F" if first.sex == "M" else "M",
                                "대한민국", "1", "1")
    return profiles


def prompt_profiles(seed: int, num_subjects: int) -> str:
    lines = [f"문서 기준일: {REFERENCE_DATE.isoformat()} (나이는 이 날짜 기준)"]
    for p in make_profiles(seed, num_subjects).values():
        lines.append(f"- 주체 {p.subject}: 생년월일 {p.birth}, 만 {p.age}세, "
                     f"성별 {'남성' if p.sex == 'M' else '여성'}, {p.nationality} 국적, "
                     f"동일 주소 그룹 {p.household}" + (f", 배우자 주체 {p.spouse}" if p.spouse else ", 정의된 가족관계 없음"))
    return "\n".join(lines)


def profile_identifier_permissions(seed: int, num_subjects: int) -> str:
    return "\n".join(
        f"- 주체 {p.subject}: " + ("rrn·passport_no 허용, foreigner_reg_no 금지"
                                    if p.nationality == "대한민국" else
                                    "foreigner_reg_no 허용, rrn·passport_no 금지")
        for p in make_profiles(seed, num_subjects).values())


def profile_errors(doc, profiles: dict[str, Profile], tax) -> list[str]:
    errors = []
    if re.search(r"\b(?:staff|tp)\d+\b", doc.text):
        errors.append("internal subject ID exposed in prose")
    if any(mark in doc.text for mark in ("{{", "}}", "[[", "]]")):
        errors.append("unresolved markup")
    for span in doc.spans:
        p = profiles.get(span.subject_id)
        if p is None:
            errors.append(f"unknown profile subject {span.subject_id}")
            continue
        if span.subtype and span.subtype not in tax[span.category].subtypes:
            # Generator metadata may carry implementation-specific identifier subtypes.
            if span.kind == "attribute":
                errors.append(f"unknown attribute subtype {span.category}:{span.subtype}")
        if span.category == "consultation_content" and span.subject_role == "staff":
            errors.append("customer case note assigned to staff rather than information subject")
        if span.category == "dob_age":
            surface = span.surface
            dates = re.findall(r"(\d{4})\s*(?:년|[-./])\s*(\d{1,2})\s*(?:월|[-./])\s*(\d{1,2})(?:일)?", surface)
            for y, m, d in dates:
                try:
                    actual = date(int(y), int(m), int(d)).isoformat()
                except ValueError:
                    actual = "invalid"
                if actual != p.birth:
                    errors.append(f"birth date differs from profile for {p.subject}")
            for value in re.findall(r"(?:만\s*)?(\d{1,3})\s*세", surface):
                if int(value) != p.age:
                    errors.append(f"age differs from profile for {p.subject}")
            for year in re.findall(r"(\d{4})\s*년생", surface):
                if int(year) != int(p.birth[:4]):
                    errors.append(f"birth year differs from profile for {p.subject}")
            if not dates and not re.search(r"\d+\s*세|\d{4}\s*년생", surface):
                errors.append(f"unverifiable dob_age format for {p.subject}")
        if span.category == "gender":
            expected, opposite = ("남성", "여성") if p.sex == "M" else ("여성", "남성")
            if expected not in span.surface or opposite in span.surface:
                errors.append(f"gender differs from profile for {p.subject}")
        if span.category == "nationality" and p.nationality not in span.surface:
            errors.append(f"nationality differs from profile for {p.subject}")
    return list(dict.fromkeys(errors))
