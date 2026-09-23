"""Offline regressions for the plan → prompt → compose boundary."""
import json
from collections import Counter
from types import SimpleNamespace

import pytest

from src.generate import run
from src.generate.compose import LLMClient, build_prompt, plan_to_dict
from src.generate.taxonomy import Taxonomy


def test_internal_memo_dominant_mapping_fills_without_crash():
    tax = Taxonomy()
    assert tax.dominant_ids("internal_memo") == ["person_name", "customer_id", "credit_score", "delinquency_info"]
    plan = next(p for p in run.make_plans(tax, 360, 0)
                if p.doc_type == "internal_memo" and p.num_subjects == 1
                and p.variation_level == "T0" and p.context_len_bucket == "1k")
    doc, errors = run.fill_one(tax, plan, "대상 고객 {{person_name:1}}", "test", "compose_v1")
    assert doc is not None and not errors


def test_prompt_preserves_fillable_slots():
    tax = Taxonomy()
    for plan in run.make_plans(tax, 100, 0):
        prompt = build_prompt(tax, plan)
        assert "{{person_name:1}}" in prompt
        assert "{{bank_account_no:1:bank=신한|split=2}}" in prompt
        assert "{{NEG}}" in prompt
        assert "{num_subjects}" not in prompt
        assert "{identifier_list}" not in prompt
        assert f"고객 수: {plan.num_subjects}명" in prompt


@pytest.mark.parametrize("version", ["compose_v2", "compose_v3"])
def test_v2_stt_prompt_does_not_instruct_t3_ops_at_lower_levels(version):
    tax = Taxonomy()
    for plan in run.make_plans(tax, 100, 0):
        prompt = build_prompt(tax, plan, version)
        assert f"현재 변형 레벨은 {plan.variation_level}" in prompt
        assert "태그 바깥의 독립된 줄" in prompt
        if plan.variation_level != "T3":
            assert "되읽기 위치에는 |readback 슬롯." not in prompt
            assert "split, part, readback, coref 지시자는 사용하지 마세요" in prompt


def test_v3_prompt_bank_and_subtype_examples_match_filler():
    from src.generate.identifiers import BANK_TEMPLATES
    from src.generate.fill import Filler
    import random
    tax = Taxonomy()
    plan = run.make_plans(tax, 1, 0)[0]
    prompt = build_prompt(tax, plan, "compose_v3")
    assert ", ".join(BANK_TEMPLATES) in prompt
    assert "{supported_banks}" not in prompt
    samples = [
        "{{bank_account_no:1:bank=토스뱅크}}",
        "[[consultation_content:1:complaint_reason]]이체 지연으로 생활비 사용이 곤란하다는 민원[[/consultation_content]]",
        "[[financial_capacity:1:debts]]담보인정비율 60% 적용[[/financial_capacity]]",
    ]
    for sample in samples:
        assert sample in prompt
        text, spans, _ = Filler(tax, "T0", random.Random(1), plan.doc_type).fill(sample)
        assert spans and "[[" not in text and "{{" not in text


@pytest.mark.parametrize("raw", [
    "[[consultation_content:1]]참고 번호 {{NEG}}를 받았어요[[/consultation_content]]",
    "[[consultation_content:1]]지난달 [[life_event:1]]직장을 옮김[[/life_event]][[/consultation_content]]",
])
def test_invalid_attribute_markup_rejected_before_emitting_gold(raw):
    tax = Taxonomy()
    plan = run.make_plans(tax, 1, 0)[0]
    doc, errors = run.fill_one(tax, plan, raw, "test", "compose_v2")
    assert doc is None and errors and errors[0].startswith("fill error:")


def test_pilot_cells_balanced_unique_reproducible():
    tax = Taxonomy()
    plans = run.make_plans(tax, 100, 0)
    assert plans == run.make_plans(tax, 100, 0)
    assert plans != run.make_plans(tax, 100, 1)
    cells = [(p.doc_type, p.variation_level, p.num_subjects, p.context_len_bucket) for p in plans]
    assert len(set(cells)) == 100
    assert set(Counter(p.doc_type for p in plans).values()) == {10}
    assert Counter(p.generator_slice for p in plans) == {"api-main": 80, "local-check": 20}


def test_complete_cell_round_and_invalid_size():
    tax = Taxonomy()
    plans = run.make_plans(tax, 720, 3)
    cells = Counter((p.doc_type, p.variation_level, p.num_subjects, p.context_len_bucket) for p in plans)
    assert len(cells) == 360
    assert set(cells.values()) == {2}
    with pytest.raises(ValueError, match="positive"):
        run.make_plans(tax, 0, 0)


def test_plan_refuses_overwrite(tmp_path):
    path = tmp_path / "plan.jsonl"
    args = ["plan", "--n", "100", "--out", str(path)]
    run.main(args)
    original = path.read_bytes()
    with pytest.raises(FileExistsError):
        run.main(args)
    assert path.read_bytes() == original


@pytest.mark.parametrize("version", ["compose_v1", "compose_v3"])
def test_compose_routes_and_resumes(tmp_path, monkeypatch, version):
    calls = []

    class FakeClient:
        def __init__(self, model, base_url=None):
            self.model = model

        def complete(self, prompt, seed=None):
            calls.append(self.model)
            return "가상 문서 {{person_name:1}}"

    monkeypatch.setattr(run, "LLMClient", FakeClient)
    plan_path = tmp_path / "plan.jsonl"
    run.main(["plan", "--n", "100", "--out", str(plan_path)])
    for slice_name, count in [("api-main", 80), ("local-check", 20)]:
        output = tmp_path / slice_name / "raw.jsonl"
        args = ["compose", "--plan", str(plan_path), "--model", slice_name,
                "--generator-slice", slice_name, "--prompt-version", version, "--out", str(output)]
        run.main(args)
        records = [json.loads(line) for line in output.read_text().splitlines()]
        assert len(records) == count
        assert all(r["plan"]["generator_slice"] == slice_name for r in records)
        assert len([m for m in calls if m == slice_name]) == count
        run.main(args)
        assert len([m for m in calls if m == slice_name]) == count
        other_model = args.copy()
        other_model[other_model.index("--model") + 1] = "different-model"
        with pytest.raises(ValueError, match="metadata mismatch"):
            run.main(other_model)
    assert len(calls) == 100


def test_resume_rejects_changed_plan_before_api(tmp_path, monkeypatch):
    plan = run.make_plans(Taxonomy(), 1, 0)[0]
    output = tmp_path / "raw.jsonl"
    output.write_text(json.dumps({"doc_id": plan.doc_id, "plan": plan_to_dict(plan),
                                  "model": "test", "prompt_version": "compose_v1", "raw": "old"}) + "\n")
    plan.seed += 1
    plan_path = tmp_path / "plan.jsonl"
    plan_path.write_text(json.dumps(plan_to_dict(plan)) + "\n")
    def no_api(*args, **kwargs):
        pytest.fail("API initialized before checking resume metadata")
    monkeypatch.setattr(run, "LLMClient", no_api)
    with pytest.raises(ValueError, match="metadata mismatch"):
        run.main(["compose", "--plan", str(plan_path), "--model", "test",
                  "--generator-slice", "api-main", "--out", str(output)])


def test_astra_request_compatibility_and_usage(monkeypatch):
    import openai
    calls = []
    def create(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(id="response-test", model="gpt-6-astra",
            choices=[SimpleNamespace(finish_reason="stop", message=SimpleNamespace(content="가상 문서"))],
            usage=SimpleNamespace(model_dump=lambda: {"prompt_tokens": 10, "completion_tokens": 20}))
    monkeypatch.setattr(openai, "OpenAI", lambda **kwargs: SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))))
    client = LLMClient("gpt-6-astra", api_key="test")
    assert client.complete("본문", seed=42) == "가상 문서"
    assert "temperature" not in calls[0] and "seed" not in calls[0] and "max_tokens" not in calls[0]
    assert calls[0]["reasoning_effort"] == "low"
    assert calls[0]["max_completion_tokens"] == 32000
    assert client.last_metadata["usage"]["completion_tokens"] == 20
    assert client.last_metadata["finish_reason"] == "stop"
    local = LLMClient("local-test", api_key="test")
    local.complete("본문", seed=42)
    assert calls[1]["temperature"] == 0.8 and calls[1]["seed"] == 42


def test_truncated_response_saved_and_rejected(tmp_path, monkeypatch):
    class TruncatedClient:
        last_metadata = {"finish_reason": "length", "usage": {"completion_tokens": 32000}}
        def __init__(self, *args, **kwargs):
            pass
        def complete(self, *args, **kwargs):
            return "잘린 문서 {{person_name:1}}"
    monkeypatch.setattr(run, "LLMClient", TruncatedClient)
    plan_path = tmp_path / "plan.jsonl"
    raw_path = tmp_path / "raw.jsonl"
    docs_path = tmp_path / "docs.jsonl"
    run.main(["plan", "--n", "1", "--out", str(plan_path)])
    args = ["compose", "--plan", str(plan_path), "--generator-slice", "api-main",
            "--model", "test", "--out", str(raw_path)]
    with pytest.raises(ValueError, match="incomplete/empty"):
        run.main(args)
    record = json.loads(raw_path.read_text())
    assert record["raw"] == "잘린 문서 {{person_name:1}}"
    assert record["completion"]["finish_reason"] == "length"
    run.main(["fill", "--raw", str(raw_path), "--out", str(docs_path)])
    assert not docs_path.read_text()
    with pytest.raises(ValueError, match="incomplete response"):
        run.main(args)
