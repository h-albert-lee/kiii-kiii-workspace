"""Hard negative 생성·삽입. fill 이후에 호출: {{NEG}} 자리에 텍스트를 넣고 뒤쪽 스팬 오프셋을 이동시킨다."""
from __future__ import annotations

import random

from . import identifiers as ids
from .schema import HardNegative, Span

NEG_TOKEN = "{{NEG}}"


def _lookalike_number(rng: random.Random) -> str:
    return rng.choice([
        f"주문번호 {rng.randrange(2020, 2027)}-{rng.randrange(10**4):04d}-{rng.randrange(10**4):04d}",
        f"운송장 {rng.randrange(10**12):012d}",
        f"상품코드 {rng.choice(['KR', 'FN'])}{rng.randrange(10**8):08d}",
        f"공시번호 {rng.randrange(10**8):08d}",
    ])


def _checksum_invalid(rng: random.Random) -> str:
    brn, _ = ids.generate_business_reg_no(rng)
    d = brn.replace("-", "")
    bad = d[:9] + str((int(d[9]) + rng.randrange(1, 10)) % 10)
    return f"사업자번호 {bad[:3]}-{bad[3:5]}-{bad[5:]}"


def _public_entity(rng: random.Random) -> str:
    return rng.choice(["고객센터 1588-8000", "1544-9999", "KB국민은행 강남역지점", "신한은행 여의도금융센터", "국민연금공단 1355", "금융감독원 1332"])


def _date_as_rrn_prefix(rng: random.Random) -> str:
    return rng.choice([f"계약일 {rng.randrange(20, 27):02d}{rng.randrange(1, 13):02d}{rng.randrange(1, 29):02d}",
                       f"기준일자 {rng.randrange(2020, 2027)}{rng.randrange(1, 13):02d}{rng.randrange(1, 29):02d}"])


def _example_placeholder(rng: random.Random) -> str:
    return rng.choice(["예: 010-0000-0000", "홍길동(예시)", "000-000-000000 형식으로", "예시 계좌 123-456-789012"])


def _generic_amount(rng: random.Random) -> str:
    return rng.choice([f"수수료 {rng.choice(['0.015%', '0.1%', '500원'])}", f"상품 한도 최대 {rng.choice([3, 5, 10])}천만원", f"기준금리 {rng.choice(['3.5%', '2.75%'])}"])


MAKERS = {
    "lookalike_number": _lookalike_number, "checksum_invalid": _checksum_invalid, "public_entity": _public_entity,
    "date_as_rrn_prefix": _date_as_rrn_prefix, "example_placeholder": _example_placeholder, "generic_amount": _generic_amount,
}


def fill_negatives(text: str, spans: list[Span], rng: random.Random, types: list[str]) -> tuple[str, list[HardNegative]]:
    negs: list[HardNegative] = []
    while True:
        i = text.find(NEG_TOKEN)
        if i < 0:
            break
        t = rng.choice(types)
        s = MAKERS[t](rng)
        delta = len(s) - len(NEG_TOKEN)
        text = text[:i] + s + text[i + len(NEG_TOKEN):]
        for sp in spans:
            if sp.start >= i + len(NEG_TOKEN):
                sp.start += delta; sp.end += delta
        for n in negs:
            if n.start >= i + len(NEG_TOKEN):
                n.start += delta; n.end += delta
        negs.append(HardNegative(start=i, end=i + len(s), surface=s, type=t))
    return text, negs
