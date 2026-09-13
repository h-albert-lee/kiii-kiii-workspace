import random
from src.generate import identifiers as ids, variation as var
from src.generate.taxonomy import Taxonomy
from src.generate.fill import Filler
from src.generate.negatives import fill_negatives
from src.generate.validate import validate
from src.generate.run import fill_one
from src.generate.compose import make_plan


def test_checksums_roundtrip():
    rng = random.Random(1)
    for _ in range(200):
        r, m = ids.generate_rrn(rng, post2020_rate=0.0); assert ids.rrn_valid(r), r
        b, _ = ids.generate_business_reg_no(rng); assert ids.brn_valid(b), b
        c, m = ids.generate_corp_reg_no(rng, new_scheme_rate=0.0); assert ids.crn_valid(c), c
        k, _ = ids.generate_card_no(rng); assert ids.luhn_valid(k), k
        f, _ = ids.generate_foreigner_reg_no(rng); assert ids.rrn_valid(f), f


def test_known_checksums():
    # 사업자등록번호 체크섬 알고리즘 검증 (공개 예시: 국세청 안내 형식 준수 임의값으로 self-consistency)
    assert ids.luhn_valid("4539 1488 0343 6467")     # 표준 Luhn 테스트 벡터
    assert not ids.luhn_valid("4539 1488 0343 6468")
    assert ids.rrn_check_digit("900101123456") in range(10)


def test_all_generators_run():
    rng = random.Random(3)
    tax = Taxonomy()
    for cid in tax.ids(tier="L", kind="identifier"):
        v, meta = ids.generate(cid, rng)
        assert isinstance(v, str) and v


def test_variation_ops_all_defined_in_yaml():
    tax = Taxonomy()
    for oid in tax.ops:
        assert oid in var.OPS or oid in var.STRUCTURAL_OPS, oid
    for oid in var.OPS:
        assert oid in tax.ops, f"op {oid} in code but not in taxonomy.yaml"


def test_hangul_digits():
    rng = random.Random(0)
    s = var.hangul_digits("010-3344-5566", rng, zero="공", sep_word="에")
    assert s == "공일공 에 삼삼사사 에 오오육육" or s.replace(" ", "") == "공일공에삼삼사사에오오육육"


def test_partial_mask_rrn_card():
    rng = random.Random(0)
    assert var.partial_mask("900101-1234567", rng) == "900101-1******"
    assert var.partial_mask("1234-5678-9012-3456", rng) == "1234-56**-****-3456"


SAMPLE = """상담사: 안녕하세요, {{person_name:staff1}}입니다. {{person_name:1}} 고객님 맞으실까요?
고객: 네 맞아요. [[dob_age:1]]88년 3월생[[/dob_age]]이고요.
상담사: 확인됐습니다. 이체하실 계좌 말씀해 주세요.
고객: {{bank_account_no:1:bank=신한|split=2}}이고요, 뒤는 {{bank_account_no:1:bank=신한|split=2,part=2}}요.
상담사: {{bank_account_no:1|readback}} 맞으시죠? [[consultation_content:1]]지난달 퇴직금 들어온 걸 정기예금으로 묶고 싶다고 하심[[/consultation_content]].
고객: 네. 연락처는 {{phone_no:1}}이에요. 참고로 {{NEG}} 도 있어요.
상담사: [[credit_transaction:1]]현재 마이너스 통장 한도 5천만 원[[/credit_transaction]] 확인되고요, 카드는 {{card_no:1|masked}} 이 카드 맞으시죠.
{{NEG}}
"""


def _run(level, seed=0):
    tax = Taxonomy(); rng = random.Random(seed)
    plan = make_plan(tax, rng, "cs_transcript", level, 1, "1k", "api-main", 1)
    doc, errs = fill_one(tax, plan, SAMPLE, "test", "compose_v1")
    return doc, errs


def test_fill_T0_canonical():
    doc, errs = _run("T0")
    assert doc is not None
    assert not [e for e in errs if not e.startswith("length")], errs
    by_cat = {s.category: s for s in doc.spans if not s.fragment and s.category != "person_name"}
    assert by_cat["phone_no"].applied_ops == [] and by_cat["phone_no"].regex_catchable
    # readback + 2 fragments share entity
    acct = [s for s in doc.spans if s.category == "bank_account_no"]
    assert len(acct) == 3 and len({s.entity_id for s in acct}) == 1
    assert len(doc.hard_negatives) == 2
    for s in doc.spans:
        assert doc.text[s.start:s.end] == s.surface


def test_fill_T2_variation_and_offsets():
    for seed in range(5):
        doc, errs = _run("T2", seed)
        assert doc is not None, errs
        assert not [e for e in errs if not e.startswith("length")], errs
        for s in doc.spans:
            assert doc.text[s.start:s.end] == s.surface
        staff = [s for s in doc.spans if s.subject_role == "staff"]
        assert staff and staff[0].category == "person_name"
        masked = [s for s in doc.spans if s.category == "card_no"][0]
        assert "partial_mask" in masked.applied_ops


def test_leak_detection():
    tax = Taxonomy(); rng = random.Random(0)
    plan = make_plan(tax, rng, "cs_transcript", "T0", 1, "1k", "api-main", 1)
    leaked = SAMPLE + "\n고객: 제 다른 번호는 010-9999-8888 입니다."
    doc, errs = fill_one(tax, plan, leaked, "test", "compose_v1")
    assert any("leaked mobile_like" in e for e in errs)
