"""문서 계획 → 프롬프트 → LLM 호출. LLM 클라이언트는 OpenAI 호환 API(로컬 vLLM 포함) 하나로 통일."""
from __future__ import annotations

import os
import random
from dataclasses import asdict, dataclass
from pathlib import Path

from .taxonomy import Taxonomy

PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"

STYLE_HINTS = {
    "kyc_form": "계좌개설 신청서·고객확인(KYC) 서식. 항목: 값 형태의 필드 나열 + 하단 확인 문구. 표 형태 허용.",
    "bank_statement": "입출금 거래명세서. 헤더(예금주·계좌) + 날짜/적요/출금/입금/잔액 행 다수. 상대방 이름·계좌가 적요에 등장.",
    "card_statement": "카드 이용대금 명세서. 카드번호 마스킹 관행 반영 가능(masked). 가맹점·금액·승인번호 행.",
    "loan_contract": "대출 약정서. 계약 당사자 인적사항, 대출 조건(금액·금리·만기·상환), 담보·보증인(제3자) 인적사항, 조항 나열.",
    "insurance_claim": "보험금 청구서 + 심사 메모. 피보험자·수익자·병원·진단명(민감정보) + 지급 계좌.",
    "cs_transcript": "콜센터 상담 녹취 STT 전사. '상담사:'/'고객:' 화자 라벨. 구어체, 간투어, 본인확인 절차, 되읽기.",
    "complaint_case": "민원 접수·처리 기록. 접수번호, 민원인 인적사항, 민원 내용, 처리 경과, 담당자.",
    "securities_trade_report": "증권 거래내역·잔고 보고서. 계좌번호(8-2), 종목·수량·단가, 투자성향 등급, 담당 PB.",
    "internal_memo": "내부 심사·검토 메모. 여러 고객을 한 문서에서 비교·언급(연체·신용점수·한도). 표 또는 항목 나열.",
    "phishing_report": "사기·피싱 피해 신고 접수 기록. 피해자 진술(OTP·비밀번호 알려준 경위), 가해 계좌·전화, 송금 내역.",
}

STT_BLOCK = """- **STT 전사 규약**: 화자 라벨 '상담사:' / '고객:'. 고객이 번호를 말하는 발화에는 슬롯을 그대로 두세요(표기 변형은 시스템이 적용). 되읽기 위치에는 |readback 슬롯. 간투어(어, 음, 그) 와 자기수정을 자연스럽게 넣으세요. 숫자가 아닌 부분도 구어체로.
"""


@dataclass
class Plan:
    doc_id: str
    doc_type: str
    variation_level: str
    num_subjects: int
    context_len_bucket: str
    generator_slice: str            # api-main | local-check
    seed: int
    structure_directives: list[str]
    required: list[str]
    optional: list[str]
    neg_count: int


TARGET_TOKENS = {"1k": 1000, "4k": 4000, "16k": 14000}


def make_plan(tax: Taxonomy, rng: random.Random, doc_type: str, level: str, n_subj: int, bucket: str, slice_: str, idx: int) -> Plan:
    dom = tax.document_types[doc_type]["dominant"]
    required = [d.split(":")[-1].split(".")[0].strip() for d in dom if not d.startswith("multi-subject")]
    required = [r for r in required if r in tax.categories]
    pool = [c for c in tax.ids() if c not in required]
    optional = rng.sample(pool, k=min(6, len(pool)))
    directives = []
    if level == "T3":
        directives.append("계좌·전화 중 하나는 두 발화/두 줄로 나눠 말하게 하고(split=2), 상담사가 되읽는 위치(readback)를 두세요." if doc_type in ("cs_transcript", "phishing_report")
                          else "식별자 하나는 문서에서 한 번만 나오고 이후에는 '해당 고객', '위 계좌' 등으로만 지칭하세요(|coref 슬롯 1회).")
        if n_subj >= 3:
            directives.append("서로 다른 고객의 식별자가 같은 문단·표에 교차 등장하는 구간을 최소 1곳 만드세요.")
        directives.append("한 곳에는 키워드 없이 번호만 등장하게 하고(예: '거기로 보내주세요. {{bank_account_no:2}}'), 한 곳에는 잘못된 키워드 옆에 번호를 두세요(예: '연락처는 {{bank_account_no:1}}').")
    neg = rng.randint(2, 5)
    return Plan(f"kf-{idx:05d}", doc_type, level, n_subj, bucket, slice_, rng.randrange(2**31), directives, required, optional, neg)


def build_prompt(tax: Taxonomy, plan: Plan) -> str:
    tpl = (PROMPT_DIR / "compose_v1.txt").read_text(encoding="utf-8")
    ident = "\n".join(f"- {c.id} — {c.raw['name_ko']}" for c in tax.categories.values() if c.kind == "identifier")
    attr = "\n".join(f"- {c.id} — {c.raw['name_ko']}" + (f" (subtype: {', '.join(c.subtypes)})" if c.subtypes else "")
                     for c in tax.categories.values() if c.kind == "attribute")
    stt = STT_BLOCK if plan.doc_type in ("cs_transcript", "phishing_report") else ""
    return tpl.format(
        neg_count=plan.neg_count, doc_type_name=tax.document_types[plan.doc_type]["name_ko"], doc_type_id=plan.doc_type,
        style_hint=STYLE_HINTS[plan.doc_type], num_subjects=plan.num_subjects,
        interleave_hint="최소 1곳 만드세요." if plan.num_subjects > 1 else "만들 필요 없습니다.",
        staff_hint="상담사·담당자 1~2명 (staff1, staff2) 이름이 등장" if plan.doc_type in ("cs_transcript", "complaint_case", "internal_memo", "phishing_report", "securities_trade_report") else "필요 시 담당자 1명 (staff1)",
        target_tokens=TARGET_TOKENS[plan.context_len_bucket], target_chars=int(TARGET_TOKENS[plan.context_len_bucket] * 1.6),
        required_categories=", ".join(plan.required), optional_categories=", ".join(plan.optional),
        structure_directives=" ".join(plan.structure_directives) or "없음", stt_block=stt,
        identifier_list=ident, attribute_list=attr,
    )


class LLMClient:
    """OpenAI 호환 chat.completions. base_url 로 로컬 vLLM 도 동일하게."""

    def __init__(self, model: str, base_url: str | None = None, api_key: str | None = None, temperature: float = 0.8):
        from openai import OpenAI  # lazy import
        self.model, self.temperature = model, temperature
        self.client = OpenAI(base_url=base_url or os.getenv("OPENAI_BASE_URL"), api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def complete(self, prompt: str, seed: int | None = None, max_tokens: int = 16000) -> str:
        r = self.client.chat.completions.create(
            model=self.model, temperature=self.temperature, max_tokens=max_tokens, seed=seed,
            messages=[{"role": "user", "content": prompt}],
        )
        return r.choices[0].message.content or ""


def plan_to_dict(p: Plan) -> dict:
    return asdict(p)
