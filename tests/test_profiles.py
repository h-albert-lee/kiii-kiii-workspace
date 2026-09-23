import pytest
import random
from dataclasses import replace

from src.generate.compose import build_prompt
from src.generate.fill import Filler
from src.generate.identifiers import rrn_valid
from src.generate.profiles import make_profiles, REFERENCE_DATE
from src.generate.run import fill_one, make_plans
from src.generate.taxonomy import Taxonomy


def test_profile_bound_identifiers_survive_slot_order_and_share_household():
    tax = Taxonomy()
    profiles = make_profiles(42, 3)
    a = Filler(tax, "T0", random.Random(1), "kyc_form", profiles=profiles, profile_seed=42)
    b = Filler(tax, "T0", random.Random(99), "kyc_form", profiles=profiles, profile_seed=42)
    a.fill("{{phone_no:1}} {{address:2}} {{rrn:1}} {{address:1}}")
    b.fill("{{rrn:1}} {{address:1}} {{address:2}}")
    for key in (("rrn", "1"), ("address", "1"), ("address", "2")):
        assert a.entities[key].canonical == b.entities[key].canonical
    assert a.entities[("address", "1")].canonical == a.entities[("address", "2")].canonical
    rrn = a.entities[("rrn", "1")]
    assert rrn.meta["birth"] == profiles["1"].birth
    assert rrn.meta["sex"] == profiles["1"].sex
    assert rrn.meta["scheme"] == "post2020_random" or rrn_valid(rrn.canonical)


def test_v4_rejects_semantic_inconsistency_but_preserves_legacy_behavior():
    tax = Taxonomy()
    plan = replace(make_plans(tax, 1, 0)[0], doc_type="kyc_form", num_subjects=1,
                   context_len_bucket="1k", variation_level="T0")
    raw = "{{person_name:1}} [[dob_age:1:age]]현재 만 99세[[/dob_age]]"
    _, legacy = fill_one(tax, plan, raw, "test", "compose_v3")
    _, current = fill_one(tax, plan, raw, "test", "compose_v4")
    assert not legacy
    assert any("age differs" in x for x in current)
    for raw, expected in [
        ("{{person_name:1}} [[consultation_content:staff1:agent_note]]고객 청구 승인[[/consultation_content]]", "assigned to staff"),
        ("{{person_name:1}} 담당자 staff1", "internal subject ID"),
        ("{{person_name:1}} {{foreigner_reg_no:1}}", "nationality mismatch"),
        ("{{person_name:1}} [[gender:1:invented]]성별 정보[[/gender]]", "unknown attribute subtype"),
    ]:
        _, errors = fill_one(tax, plan, raw, "test", "compose_v4")
        assert any(expected in e for e in errors), errors


@pytest.mark.parametrize("version", ["compose_v4", "compose_v5"])
def test_v4_matching_profile_and_prompt(version):
    tax = Taxonomy()
    plan = replace(make_plans(tax, 1, 0)[0], doc_type="kyc_form", num_subjects=1,
                   context_len_bucket="1k", variation_level="T0")
    profile = make_profiles(plan.seed, 1)["1"]
    raw = ("{{person_name:1}} {{rrn:1}} "
           f"[[dob_age:1:full_dob]]생년월일 {profile.birth}[[/dob_age]] "
           f"[[dob_age:1:age]]현재 만 {profile.age}세[[/dob_age]] "
           f"[[gender:1]]성별 {'남성' if profile.sex == 'M' else '여성'}[[/gender]]")
    doc, errors = fill_one(tax, plan, raw, "test", version)
    assert doc and not errors
    assert doc.generator["profile_version"] == "profiles_v1"
    prompt = build_prompt(tax, plan, version)
    assert profile.birth in prompt and REFERENCE_DATE.isoformat() in prompt
    assert "{subject_profiles}" not in prompt and "{example_birth}" not in prompt


def test_v7_long_plan_rejects_one_bucket_shortfall():
    from dataclasses import replace
    from src.generate.run import make_plans, fill_one
    from src.generate.taxonomy import Taxonomy
    tax=Taxonomy()
    plan=replace(make_plans(tax,1,0)[0],doc_type='loan_contract',num_subjects=1,
                 variation_level='T0',context_len_bucket='16k')
    raw='고객 {{person_name:1}}\n' + '약정에 따라 상환 방법과 일정 및 거래 조건을 안내합니다. ' * 180
    old, old_errors=fill_one(tax,plan,raw,'test','compose_v6')
    new, new_errors=fill_one(tax,plan,raw,'test','compose_v7')
    assert old.context_len_bucket=='4k'
    assert not any('long-document minimum' in e for e in old_errors)
    assert any('long-document minimum' in e for e in new_errors)
