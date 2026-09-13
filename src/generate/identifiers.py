"""L-identifier 값 생성기. 실제 데이터 없음. 체크섬 규칙은 literature/notes/legal-sources-ko.md §6, ko-pii(MIT) 구현 참고.

모든 generate_* 함수는 (canonical: str, meta: dict) 를 반환한다. canonical 이 gold 정규형.
"""
from __future__ import annotations

import random
import string
from datetime import date, timedelta

# ---------------------------------------------------------------- checksums

def rrn_check_digit(d12: str) -> int:
    w = [2, 3, 4, 5, 6, 7, 8, 9, 2, 3, 4, 5]
    s = sum(int(c) * k for c, k in zip(d12, w))
    return (11 - s % 11) % 10


def rrn_valid(rrn: str) -> bool:
    d = rrn.replace("-", "")
    return len(d) == 13 and d.isdigit() and rrn_check_digit(d[:12]) == int(d[12])


def brn_check_digit(d9: str) -> int:
    w = [1, 3, 7, 1, 3, 7, 1, 3, 5]
    s = sum(int(c) * k for c, k in zip(d9, w)) + (int(d9[8]) * 5) // 10
    return (10 - s % 10) % 10


def brn_valid(brn: str) -> bool:
    d = brn.replace("-", "")
    return len(d) == 10 and d.isdigit() and brn_check_digit(d[:9]) == int(d[9])


def crn_check_digit(d12: str) -> int:
    s = sum(int(c) * (1 if i % 2 == 0 else 2) for i, c in enumerate(d12))
    return (10 - s % 10) % 10


def crn_valid(crn: str) -> bool:
    d = crn.replace("-", "")
    return len(d) == 13 and d.isdigit() and crn_check_digit(d[:12]) == int(d[12])


def luhn_check_digit(partial: str) -> int:
    total, alt = 0, True
    for ch in reversed(partial):
        n = int(ch)
        if alt:
            n *= 2
            if n > 9:
                n -= 9
        total += n
        alt = not alt
    return (10 - total % 10) % 10


def luhn_valid(num: str) -> bool:
    d = num.replace("-", "").replace(" ", "")
    return d.isdigit() and 13 <= len(d) <= 19 and luhn_check_digit(d[:-1]) == int(d[-1])


# ---------------------------------------------------------------- generators

def _rand_birth(rng: random.Random, lo=1950, hi=2004) -> date:
    start = date(lo, 1, 1)
    return start + timedelta(days=rng.randrange((date(hi, 12, 31) - start).days))


def generate_rrn(rng: random.Random, post2020_rate: float = 0.3) -> tuple[str, dict]:
    b = _rand_birth(rng)
    century_male = 1 if b.year < 2000 else 3
    sex = century_male + rng.randrange(2)          # 1/2 or 3/4
    front = b.strftime("%y%m%d")
    if rng.random() < post2020_rate:
        rear = f"{sex}{rng.randrange(10**6):06d}"
        meta = {"scheme": "post2020_random", "checksum_valid": None, "birth": b.isoformat(), "sex": "M" if sex % 2 else "F"}
    else:
        region = f"{rng.randrange(96):02d}{rng.randrange(100):02d}"   # legacy 지역코드 4자리 (00~95xx)
        serial = str(rng.randrange(10))
        d12 = front + str(sex) + region + serial
        rear = f"{sex}{region}{serial}{rrn_check_digit(d12)}"
        meta = {"scheme": "legacy_checksum", "checksum_valid": True, "birth": b.isoformat(), "sex": "M" if sex % 2 else "F"}
    return f"{front}-{rear}", meta


def generate_foreigner_reg_no(rng: random.Random) -> tuple[str, dict]:
    b = _rand_birth(rng)
    sex = (5 if b.year < 2000 else 7) + rng.randrange(2)
    front = b.strftime("%y%m%d")
    region = f"{rng.randrange(100):02d}{rng.randrange(100):02d}"
    serial = str(rng.randrange(10))
    d12 = front + str(sex) + region + serial
    return f"{front}-{sex}{region}{serial}{rrn_check_digit(d12)}", {"checksum_valid": True, "birth": b.isoformat()}


def generate_business_reg_no(rng: random.Random, corporate: bool | None = None) -> tuple[str, dict]:
    office = f"{rng.randrange(101, 1000):03d}"
    if corporate is None:
        corporate = rng.random() < 0.35
    kind = rng.choice(["81", "86", "87", "88"]) if corporate else f"{rng.randrange(1, 80):02d}"
    serial = f"{rng.randrange(1, 10000):04d}"
    d9 = office + kind + serial
    return f"{office}-{kind}-{serial}{brn_check_digit(d9)}", {"corporate": corporate, "checksum_valid": True}


def generate_corp_reg_no(rng: random.Random, new_scheme_rate: float = 0.3) -> tuple[str, dict]:
    registry = f"{rng.randrange(1100, 3000):04d}"
    kind = rng.choice(["11", "12", "13", "14", "15", "21", "22"])
    if rng.random() < new_scheme_rate:
        serial = f"{rng.randrange(10**7):07d}"
        return f"{registry}{kind}-{serial}", {"scheme": "2025_no_check", "checksum_valid": None}
    serial = f"{rng.randrange(10**6):06d}"
    d12 = registry + kind + serial
    return f"{registry}{kind}-{serial}{crn_check_digit(d12)}", {"scheme": "legacy_checksum", "checksum_valid": True}


def generate_card_no(rng: random.Random) -> tuple[str, dict]:
    if rng.random() < 0.05:                                    # Amex 15
        partial = rng.choice(["34", "37"]) + "".join(rng.choice(string.digits) for _ in range(12))
        num = partial + str(luhn_check_digit(partial))
        return f"{num[:4]}-{num[4:10]}-{num[10:]}", {"network": "amex", "checksum_valid": True}
    first = rng.choices(["4", "5", "9"], weights=[45, 35, 20])[0]     # 9 = 국내 전용 BIN (BC 등)
    partial = first + "".join(rng.choice(string.digits) for _ in range(14))
    num = partial + str(luhn_check_digit(partial))
    return "-".join(num[i:i + 4] for i in range(0, 16, 4)), {"network": {"4": "visa", "5": "master", "9": "domestic"}[first], "checksum_valid": True}


BANK_TEMPLATES = {
    "국민": [6, 2, 6], "신한": [3, 3, 6], "우리": [4, 3, 6], "하나": [3, 6, 5], "농협": [3, 4, 4, 2],
    "기업": [3, 6, 2, 3], "카카오뱅크": [4, 2, 7], "토스뱅크": [4, 4, 4], "케이뱅크": [3, 3, 6], "SC제일": [3, 2, 6],
}
BANK_PREFIX = {"신한": "110", "우리": "1002", "카카오뱅크": "3333", "토스뱅크": "1000", "농협": "3"}


def generate_bank_account_no(rng: random.Random, bank: str | None = None) -> tuple[str, dict]:
    bank = bank or rng.choice(list(BANK_TEMPLATES))
    groups = BANK_TEMPLATES[bank]
    digits = "".join(rng.choice(string.digits) for _ in range(sum(groups)))
    if bank in BANK_PREFIX:
        p = BANK_PREFIX[bank]
        digits = p + digits[len(p):]
    parts, i = [], 0
    for g in groups:
        parts.append(digits[i:i + g]); i += g
    return "-".join(parts), {"bank": bank, "checksum_valid": None}


def generate_securities_account_no(rng: random.Random) -> tuple[str, dict]:
    if rng.random() < 0.6:
        return f"{rng.randrange(10**8):08d}-{rng.choice(['01','02','03','05','11'])}", {"format": "8-2"}
    n = rng.choice([10, 11])
    return "".join(rng.choice(string.digits) for _ in range(n)), {"format": f"{n}"}


def generate_phone_no(rng: random.Random, subtype: str | None = None) -> tuple[str, dict]:
    r = rng.random() if subtype is None else {"mobile": 0.0, "landline": 0.9, "voip": 0.97}[subtype]
    if r < 0.85:
        return f"010-{rng.randrange(1000, 10000)}-{rng.randrange(10**4):04d}", {"subtype": "mobile"}
    if r < 0.95:
        area = rng.choice(["02", "031", "032", "051", "053", "042", "062", "064"])
        mid = rng.randrange(200, 1000) if area == "02" and rng.random() < 0.5 else rng.randrange(1000, 10000)
        return f"{area}-{mid}-{rng.randrange(10**4):04d}", {"subtype": "landline"}
    return f"070-{rng.randrange(4000, 9000)}-{rng.randrange(10**4):04d}", {"subtype": "voip"}


def generate_passport_no(rng: random.Random) -> tuple[str, dict]:
    if rng.random() < 0.4:
        return "M" + "".join(rng.choice(string.digits) for _ in range(8)), {"scheme": "legacy"}
    return f"M{rng.randrange(1000):03d}{rng.choice(string.ascii_uppercase)}{rng.randrange(10**4):04d}", {"scheme": "2021"}


def generate_driver_license_no(rng: random.Random) -> tuple[str, dict]:
    region = rng.choice([11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 28])
    return f"{region}-{rng.randrange(0, 26):02d}-{rng.randrange(10**6):06d}-{rng.randrange(100):02d}", {"region": region}


def generate_customer_id(rng: random.Random) -> tuple[str, dict]:
    style = rng.choice(["digits", "prefixed", "member"])
    if style == "digits":
        return "".join(rng.choice(string.digits) for _ in range(rng.choice([8, 10, 12]))), {"subtype": "customer_no"}
    if style == "prefixed":
        return f"{rng.choice(['C', 'CU', 'KB', 'SH'])}{rng.randrange(10**8):08d}", {"subtype": "customer_no"}
    return f"{rng.randrange(10**7):07d}", {"subtype": "member_no"}


def generate_contract_no(rng: random.Random, subtype: str | None = None) -> tuple[str, dict]:
    subtype = subtype or rng.choice(["insurance_policy_no", "loan_contract_no", "approval_no", "receipt_no"])
    if subtype == "insurance_policy_no":
        return "".join(rng.choice(string.digits) for _ in range(rng.choice([12, 13, 14]))), {"subtype": subtype}
    if subtype == "loan_contract_no":
        return f"{rng.choice(['L', 'LN', 'DL'])}{rng.randrange(10**10):010d}", {"subtype": subtype}
    if subtype == "approval_no":
        return f"{rng.randrange(10**8):08d}", {"subtype": subtype}
    return f"{date.today().year}-{rng.randrange(10**6):06d}", {"subtype": subtype}


def generate_access_credential(rng: random.Random, subtype: str | None = None) -> tuple[str, dict]:
    subtype = subtype or rng.choice(["password_pin", "otp", "security_card"])
    if subtype == "otp":
        return f"{rng.randrange(10**6):06d}", {"subtype": subtype}
    if subtype == "security_card":
        return f"{rng.randrange(1, 36):02d}번 {rng.randrange(10**4):04d}", {"subtype": subtype}
    return f"{rng.randrange(10**rng.choice([4, 6])):0{rng.choice([4, 6])}d}"[:6], {"subtype": subtype}


# ---- text identifiers (사전은 최소 시드; 본 코퍼스 전 확장) ----
SURNAMES = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임", "한", "오", "서", "신", "권", "황", "안", "송", "류", "전"]
SURNAME_W = [21, 15, 8.5, 4.7, 4.3, 2.4, 2.1, 2.1, 2.0, 1.7, 1.5, 1.4, 1.4, 1.3, 1.3, 1.3, 1.3, 1.2, 1.1, 1.0]
GIVEN_SYL = list("민서준우현지영수진하윤도연아은성재원호경")
ROMAN = {"김": "Kim", "이": "Lee", "박": "Park", "최": "Choi", "정": "Jung", "강": "Kang", "조": "Cho", "윤": "Yoon", "장": "Jang",
         "임": "Lim", "한": "Han", "오": "Oh", "서": "Seo", "신": "Shin", "권": "Kwon", "황": "Hwang", "안": "Ahn", "송": "Song", "류": "Ryu", "전": "Jeon"}


def generate_person_name(rng: random.Random) -> tuple[str, dict]:
    sur = rng.choices(SURNAMES, weights=SURNAME_W)[0]
    given = "".join(rng.choice(GIVEN_SYL) for _ in range(2 if rng.random() < 0.95 else 1))
    return sur + given, {"surname": sur, "given": given, "romanized": f"{ROMAN.get(sur, sur)} {given}"}


SIDO = ["서울특별시", "부산광역시", "대구광역시", "인천광역시", "경기도", "대전광역시", "광주광역시"]
GU = {"서울특별시": ["강남구", "서초구", "마포구", "송파구", "영등포구"], "부산광역시": ["해운대구", "부산진구"], "대구광역시": ["수성구"],
      "인천광역시": ["연수구", "남동구"], "경기도": ["성남시 분당구", "수원시 영통구", "고양시 일산동구"], "대전광역시": ["유성구"], "광주광역시": ["북구"]}
ROADS = ["테헤란로", "올림픽로", "월드컵북로", "중앙대로", "판교역로", "송도과학로", "대학로", "번영로"]


def generate_address(rng: random.Random) -> tuple[str, dict]:
    sido = rng.choice(SIDO); gu = rng.choice(GU[sido]); road = rng.choice(ROADS)
    num = rng.randrange(1, 500)
    detail = f", {rng.randrange(101, 2500)}호" if rng.random() < 0.6 else ""
    return f"{sido} {gu} {road} {num}{detail}", {"sido": sido, "sigungu": gu}


DOMAINS = ["gmail.com", "naver.com", "kakao.com", "daum.net", "hanmail.net", "outlook.com"]


def generate_email(rng: random.Random, name_meta: dict | None = None) -> tuple[str, dict]:
    if name_meta:
        local = (name_meta["romanized"].lower().replace(" ", ".") + str(rng.randrange(10, 99)))
    else:
        local = "".join(rng.choice(string.ascii_lowercase) for _ in range(rng.randrange(5, 10)))
    return f"{local}@{rng.choice(DOMAINS)}", {}


def generate_online_handle(rng: random.Random, name_meta: dict | None = None) -> tuple[str, dict]:
    base = (name_meta["romanized"].split()[-1].lower() if name_meta else "".join(rng.choice(string.ascii_lowercase) for _ in range(6)))
    return f"@{base}_{rng.randrange(100, 9999)}", {"subtype": "sns_url"}


GENERATORS = {
    "rrn": generate_rrn, "foreigner_reg_no": generate_foreigner_reg_no, "business_reg_no": generate_business_reg_no,
    "corp_reg_no": generate_corp_reg_no, "card_no": generate_card_no, "bank_account_no": generate_bank_account_no,
    "securities_account_no": generate_securities_account_no, "phone_no": generate_phone_no, "passport_no": generate_passport_no,
    "driver_license_no": generate_driver_license_no, "customer_id": generate_customer_id, "contract_no": generate_contract_no,
    "access_credential": generate_access_credential, "person_name": generate_person_name, "address": generate_address,
    "email": generate_email, "online_handle": generate_online_handle,
}

VALIDATORS = {"rrn": rrn_valid, "foreigner_reg_no": rrn_valid, "business_reg_no": brn_valid, "corp_reg_no": crn_valid, "card_no": luhn_valid}


def generate(category: str, rng: random.Random, **kw) -> tuple[str, dict]:
    return GENERATORS[category](rng, **kw)
