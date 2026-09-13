"""표면형 변형 연산. taxonomy.yaml: variation.ops 의 id 와 1:1. 순수 함수 canonical -> surface.

T3 구조 op(chunk_split, agent_readback, coref_reference, multi_subject_interleave, negation_hypothetical, table_cell)는
텍스트 구조가 필요하므로 여기서는 값 조각화만 담당하고 배치는 compose/fill 이 한다.
"""
from __future__ import annotations

import random
import re
from collections.abc import Callable

Op = Callable[[str, random.Random], str]

HANGUL_DIGIT = {"0": "공", "1": "일", "2": "이", "3": "삼", "4": "사", "5": "오", "6": "육", "7": "칠", "8": "팔", "9": "구"}
HANJA_DIGIT = {"0": "〇", "1": "一", "2": "二", "3": "三", "4": "四", "5": "五", "6": "六", "7": "七", "8": "八", "9": "九"}
FULLWIDTH = {d: chr(ord("０") + int(d)) for d in "0123456789"}
CIRCLED = {"0": "⓪", "1": "①", "2": "②", "3": "③", "4": "④", "5": "⑤", "6": "⑥", "7": "⑦", "8": "⑧", "9": "⑨"}
OCR_CONFUSE = {"0": "O", "1": "l", "5": "S", "8": "B", "2": "Z", "6": "b"}
STT_CONFUSE = {"1": "2", "2": "1", "3": "4", "4": "3", "6": "9", "9": "6"}   # 이↔일, 삼↔사, 육↔구(유사음 근사)


def _digits_only(s: str) -> str:
    return re.sub(r"\D", "", s)


# ---------------- T1 formatting ----------------

def sep_drop(v: str, rng: random.Random) -> str:
    return re.sub(r"[-\s.]", "", v)


def sep_swap(v: str, rng: random.Random) -> str:
    return v.replace("-", rng.choice([" ", ".", "/", "·", " - "]))


def regroup(v: str, rng: random.Random) -> str:
    d = _digits_only(v)
    if len(d) < 6:
        return v
    n = len(d); cuts = sorted(rng.sample(range(2, n - 1), k=min(rng.choice([1, 2, 3]), n - 3)))
    parts, prev = [], 0
    for c in cuts:
        parts.append(d[prev:c]); prev = c
    parts.append(d[prev:])
    return rng.choice(["-", " "]).join(parts)


def partial_mask(v: str, rng: random.Random) -> str:
    """앞부분은 남기고 뒤를 *로. 주민번호는 '900101-1******' 형태, 카드는 '1234-56**-****-7890'."""
    if re.fullmatch(r"\d{6}-\d{7}", v):
        return v[:8] + "******"
    if re.fullmatch(r"(\d{4}-){3}\d{4}", v):
        return v[:7] + "**-****-" + v[-4:]
    d = re.sub(r"\D", "", v)
    keep = max(2, len(d) // 3)
    out, i = [], 0
    for ch in v:
        if ch.isdigit():
            out.append(ch if i < keep or i >= len(d) - 2 else "*"); i += 1
        else:
            out.append(ch)
    return "".join(out)


def prefix_suffix_noise(v: str, rng: random.Random) -> str:
    return rng.choice([f"#{v}", f"({v})", f"{v}.", f"[{v}]", f"*{v}", f"{v}번"])


def honorific_wrap(v: str, rng: random.Random, role: str | None = None) -> str:
    if role == "staff":
        return v + rng.choice([" 상담사", " 대리", " 주임", " 과장", " 팀장", " 님"])
    return v + rng.choice([" 고객님", " 씨", " 님", " 선생님", " 사장님", " 어머님"])


def address_granularity(v: str, rng: random.Random) -> str:
    v2 = v.replace("특별시", "").replace("광역시", "")
    if rng.random() < 0.5 and "," in v2:
        v2 = v2.split(",")[0]
    return re.sub(r"(\D)\s+(\d)", r"\1\2", v2) if rng.random() < 0.5 else v2


# ---------------- T2 lexical ----------------

def hangul_digits(v: str, rng: random.Random, zero: str | None = None, sep_word: str | None = None) -> str:
    """'010-3344-5566' -> '공일공 삼삼사사 오오육육' / '공일공 에 삼삼사사 에 오오육육' / 음절 사이 공백 변형."""
    zero = zero or ("공" if rng.random() < 0.8 else "영")
    table = dict(HANGUL_DIGIT); table["0"] = zero
    groups = [g for g in re.split(r"[-\s.]", v) if g]
    spaced = rng.random() < 0.3                       # KsponSpeech 발음전사식 음절 공백
    conv = [("" if not spaced else " ").join(table.get(c, c) for c in g) for g in groups]
    r = rng.random()
    if sep_word:
        joiner = f" {sep_word} "
    elif r < 0.55:
        joiner = " 에 "
    elif r < 0.90:
        joiner = " 다시 "
    else:
        joiner = " "
    return joiner.join(conv)


def mixed_digits(v: str, rng: random.Random) -> str:
    groups = re.split(r"(-)", v)
    out = []
    for g in groups:
        if g == "-" or not g.isdigit():
            out.append(g); continue
        mode = rng.choice(["arabic", "hangul", "hanja"])
        table = {"arabic": None, "hangul": HANGUL_DIGIT, "hanja": HANJA_DIGIT}[mode]
        out.append(g if table is None else "".join(table[c] for c in g))
    return "".join(out)


def unicode_variant(v: str, rng: random.Random) -> str:
    table = rng.choice([FULLWIDTH, CIRCLED])
    return "".join(table.get(c, c) for c in v)


def ocr_confusable(v: str, rng: random.Random) -> str:
    chars = list(v); idx = [i for i, c in enumerate(chars) if c in OCR_CONFUSE]
    for i in rng.sample(idx, k=min(len(idx), rng.choice([1, 2]))):
        chars[i] = OCR_CONFUSE[chars[i]]
    return "".join(chars)


def typo(v: str, rng: random.Random) -> str:
    if len(v) < 3:
        return v
    i = rng.randrange(1, len(v))
    return rng.choice([v[:i] + " " + v[i:], v[:i] + v[i - 1] + v[i:], v[:i - 1] + v[i:]])


def name_obfuscation(v: str, rng: random.Random, romanized: str | None = None) -> str:
    if len(v) < 2:
        return v
    forms = [v[0] + "O" + v[2:] if len(v) >= 3 else v[0] + "O", v[0] + "*" * (len(v) - 1), v[0] + "ㅁ" * (len(v) - 1)]
    if romanized:
        forms += [romanized, "".join(w[0] for w in romanized.split()).upper()]
    return rng.choice(forms)


def romanization_codeswitch(v: str, rng: random.Random) -> str:
    return v  # 주소·속성용. 사전 기반 변환은 compose 단계에서 LLM 지시로 처리 (placeholder)


def stt_digit_error(v: str, rng: random.Random) -> str:
    d_positions = [i for i, c in enumerate(v) if c.isdigit()]
    if not d_positions:
        return v
    chars = list(v)
    mode = rng.random()
    if mode < 0.5:                       # 유사 발음 치환 1자리
        i = rng.choice(d_positions); chars[i] = STT_CONFUSE.get(chars[i], chars[i])
    elif mode < 0.8:                     # 한 자리 탈락
        i = rng.choice(d_positions); del chars[i]
    else:                                # 앞 0 탈락
        if chars[0] == "0":
            del chars[0]
    return "".join(chars)


def separator_artifact(v: str, rng: random.Random) -> str:
    word = rng.choice(["에", "다시"])
    return v.replace("-", f" {word} ") if rng.random() < 0.7 else v.replace("-", f"-{word}-")


def verbal_amount(v: str, rng: random.Random) -> str:
    return v  # 속성 스팬은 LLM 이 자연어로 생성; 여기서는 no-op (호환용)


# ---------------- T3 (값 조각화만) ----------------

def chunk_split(v: str, rng: random.Random, parts: int = 2) -> list[str]:
    groups = [g for g in re.split(r"[-\s]", v) if g]
    if len(groups) >= parts:
        k = len(groups) // parts
        return [" ".join(groups[i * k:(i + 1) * k if i < parts - 1 else None]) for i in range(parts)]
    d = _digits_only(v); k = len(d) // parts
    return [d[i * k:(i + 1) * k if i < parts - 1 else None] for i in range(parts)]


def anchor_missing(v: str, rng: random.Random) -> str:
    return v  # 앵커(키워드) 제거는 compose 프롬프트 지시로 처리; 값은 그대로


def anchor_wrong(v: str, rng: random.Random) -> str:
    return v  # 동일


OPS: dict[str, Op] = {
    "sep_drop": sep_drop, "sep_swap": sep_swap, "regroup": regroup, "partial_mask": partial_mask,
    "prefix_suffix_noise": prefix_suffix_noise, "honorific_wrap": honorific_wrap, "address_granularity": address_granularity,
    "hangul_digits": hangul_digits, "mixed_digits": mixed_digits, "unicode_variant": unicode_variant, "ocr_confusable": ocr_confusable,
    "typo": typo, "name_obfuscation": name_obfuscation, "romanization_codeswitch": romanization_codeswitch,
    "stt_digit_error": stt_digit_error, "separator_artifact": separator_artifact, "verbal_amount": verbal_amount,
    "anchor_missing": anchor_missing, "anchor_wrong": anchor_wrong,
}
STRUCTURAL_OPS = {"chunk_split", "agent_readback", "coref_reference", "multi_subject_interleave", "table_cell", "negation_hypothetical"}
NUMERIC_ONLY = {"sep_drop", "sep_swap", "regroup", "partial_mask", "prefix_suffix_noise", "hangul_digits", "mixed_digits",
                "unicode_variant", "ocr_confusable", "stt_digit_error", "separator_artifact"}


def apply_ops(canonical: str, op_ids: list[str], rng: random.Random, **kw) -> str:
    v = canonical
    for oid in op_ids:
        if oid in STRUCTURAL_OPS:
            continue
        fn = OPS[oid]
        try:
            v = fn(v, rng, **{k: kw[k] for k in kw if k in fn.__code__.co_varnames})
        except TypeError:
            v = fn(v, rng)
    return v


# 표면형을 바꾸지 않는 구조 마커 — regex 판정에서 무시
SURFACE_NEUTRAL = {"agent_readback", "coref_reference", "given_name_only", "anchor_missing", "anchor_wrong"}
# 서로 합성하면 비현실적인 op 군 (한 값에 하나만)
EXCLUSIVE_GROUPS = [
    {"hangul_digits", "mixed_digits", "unicode_variant", "ocr_confusable", "partial_mask", "stt_digit_error"},
    {"sep_drop", "sep_swap", "regroup", "separator_artifact"},
]
# 합성 시 적용 순서 (앞이 먼저)
PRECEDENCE = ["partial_mask", "regroup", "sep_swap", "sep_drop", "separator_artifact", "stt_digit_error", "hangul_digits",
              "mixed_digits", "unicode_variant", "ocr_confusable", "typo", "name_obfuscation", "address_granularity",
              "honorific_wrap", "prefix_suffix_noise"]


def order_ops(op_ids: list[str]) -> list[str]:
    return sorted(op_ids, key=lambda o: PRECEDENCE.index(o) if o in PRECEDENCE else 99)


def regex_catchable(op_ids: list[str], levels: dict[str, str]) -> bool:
    """표면형을 바꾼 op 중 T2 이상이 하나라도 있으면 regex 로 못 잡는 것으로 본다. chunk_split 조각은 못 잡는 것으로."""
    for o in op_ids:
        if o in SURFACE_NEUTRAL:
            continue
        if o == "chunk_split" or levels.get(o, "T0") not in ("T0", "T1"):
            return False
    return True
