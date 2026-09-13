# 합성 코퍼스 생성 설계

> 결정 근거는 ADR-0002. 이 문서는 "어떻게"를 적습니다. 코드는 `src/generate/`.

## 1. 파이프라인 한눈에

```
taxonomy.yaml ──┐
                ▼
 (1) plan      층화 샘플링: doc_type × T-level × num_subjects × len_bucket → 문서 계획(plan.json)
                ▼
 (2) compose   LLM이 계획대로 문서 작성. 식별자는 {{슬롯}}, 속성·I 스팬은 [[태그]]…[[/태그]]
                ▼
 (3) fill      슬롯마다 코드가 값 생성(체크섬 유효) → 변형 op 적용 → 텍스트 삽입, 오프셋 기록
                ▼
 (4) negatives hard negative 삽입 (gold 수의 ~30%)
                ▼
 (5) validate  오프셋=surface 일치, 카테고리 존재, 체크섬, 태그 균형, 길이 버킷 → 실패 문서는 재생성
                ▼
 (6) emit      data/corpus/vX.Y/{train,dev,test}.jsonl + manifest.json
```

## 2. 문서 계획 (plan)

| 변수 | 값 | 비고 |
|---|---|---|
| `doc_type` | `taxonomy.yaml: document_types` 10종 | 유형별 dominant 카테고리를 필수 슬롯으로 |
| `variation_level` | T0 25% / T1 30% / T2 25% / T3 20% | 문서 단위. cs_transcript·phishing_report는 `stt_profile` 추가 적용 |
| `num_subjects` | 1 / 3 / 8 | 고객 수. internal_memo·complaint_case는 3·8 가중 |
| `context_len_bucket` | 1k / 4k / 16k 토큰 | LLM에 목표 길이 지시 → 생성 후 실측으로 버킷 재배정 |
| `generator` | api-main / local-check | 80 / 20 |

층화: 10 × 4 × 3 × 3 = 360 셀. 파일럿은 셀당 0~1건으로 100건, 본 코퍼스는 셀당 n건(총 2~3k 문서 목표; 4페이지 논문·API 비용 기준).

## 3. LLM 출력 규약 (compose)

LLM은 한국어 문서 본문만 출력한다. 두 종류의 표시만 허용:

**슬롯** — L-identifier. 값을 쓰지 않는다.
```
{{category:subject_idx[:param=value,...][|directive,...]}}
{{person_name:1}}                      고객 1의 이름
{{person_name:1|given}}                같은 사람, 이름만 ("민지 씨")
{{person_name:staff1}}                 상담사
{{bank_account_no:1:bank=신한}}         고객 1의 신한 계좌
{{bank_account_no:1|split=2}}          같은 계좌, 이 위치에 두 조각 중 첫 조각 (T3 chunk_split)
{{bank_account_no:1|split=2,part=2}}   두 번째 조각
{{phone_no:1|readback}}                상담사 되읽기 위치 (아라비아 숫자 강제; 고객 발화 쪽은 hangul_digits 적용)
{{rrn:1|masked}}                       부분 마스킹형 강제
```
동일 `category:subject_idx`는 문서 내 같은 값(entity_id 공유) → 일관성 채점 근거.

**태그** — L-attribute·I-attribute. LLM이 자연어로 쓰고 감싼다.
```
[[credit_transaction:1]]마이너스 통장 한도 5천만 원, 금리 연 5.2%[[/credit_transaction]]
[[consultation_content:1]]퇴직금 수령 후 예금 만기 연장 대신 해지를 원하심[[/consultation_content]]
[[life_event:1]]지난달 퇴직[[/life_event]]
[[sensitive_info:1:health]]고혈압 진단[[/sensitive_info]]
```
태그 안의 `:1`은 subject. 중첩 금지. 태그 안에 슬롯 가능(예: 거래내역 행 안의 계좌).

**금지**: 실제 기관 대표번호 외 실제 인물·실존 계좌 형식의 값 직접 기재, 슬롯 없는 숫자 식별자. 위반 시 validate에서 문서 폐기.

프롬프트는 `src/prompts/compose_v1.txt`. 입력 = 문서 계획 + 허용 슬롯/태그 목록 + 문서유형별 스타일 힌트 + 목표 길이.

## 4. 값 생성 (identifiers.py)

| category | 생성 규칙 | 체크섬 |
|---|---|---|
| rrn | 생년월일 유효 + 성별자리 + (2020.10 이전 70%: 검증번호 유효 / 이후 30%: 임의 6자리) | 유효 |
| foreigner_reg_no | rrn 규칙, 성별자리 5~8 | 유효(구 체계) |
| business_reg_no | 세무서 3 + 구분 2(개인 01~79 / 법인 81·86·87·88) + 일련 4 + 검증 | 유효 |
| corp_reg_no | 4-2-6 + 검증(구) 70% / 4-2-7 무검증(2025.1.31~) 30% | 유효(구) |
| card_no | BIN 4/5/9 시작, 16자리 Luhn; Amex 15자리 5% | Luhn |
| bank_account_no | 은행 템플릿(국민 6-2-6, 신한 3-3-6, 우리 4-3-6, 하나 3-6-5, 농협 3-4-4-2, 카카오 3333-2-7, 토스 1000-4-4, 케이 12) | 없음 |
| securities_account_no | 8-2 (60%) / 10~11 연속 (40%) | 없음 |
| phone_no | 010-XXXX-XXXX 85%, 지역번호 10%, 070 5% | 없음 |
| passport_no | M + 8 (40%) / M+3+A+4 (60%) | 없음 |
| driver_license_no | 지역 11~28 + 발급연도 2 + 6 + 2 | 없음 |
| customer_id | 기관 스타일 8~12자리 또는 접두+숫자 | 없음 |
| contract_no | 보험증권 12~14 / 대출계약 접두+10 / 승인번호 8 | 없음 |
| access_credential | PIN 4~6 / OTP 6 / 보안카드 2자리 좌표 | 없음 |
| person_name | 성 사전(빈도 가중) × 이름 음절 사전; 로마자 변환기 | — |
| address | 시도·시군구·도로명 사전 + 가짜 번지·동호 | — |
| email / online_handle | 이름 로마자 기반 로컬파트 + 도메인 사전 | — |

모든 생성기는 `(canonical: str, meta: dict)`를 반환. `canonical`이 gold의 정규형.

## 5. 변형 적용 (variation.py)

- 문서 레벨 T에서 각 슬롯에 `ops = sample(ops where level ≤ T and applies_to matches)`; T0은 빈 리스트.
- op는 순수 함수 `canonical → surface`. 여러 op 합성 가능(예: sep_drop ∘ ocr_confusable). `applied_ops` 순서 기록.
- `regex_catchable` 판정은 op 정의에서 계산: 적용된 op 중 하나라도 `level ≥ T2`면 false.
- T3 구조 op(chunk_split, agent_readback, coref_reference, multi_subject_interleave)는 슬롯 지시자로 LLM이 배치 → fill 단계에서 조각 값 생성.
- STT 프로필: `doc_type ∈ {cs_transcript, phishing_report}`이면 `stt_profile` 확률로 digit_rendering·zero_word·separator·error_injection 적용, `pre_masked_subset` 20%는 fill 후 마스킹 패스(아라비아 숫자 PII만 `*`/`[전화번호]`로 치환, 한글 숫자·분할 조각은 남김).

## 6. Hard negatives (negatives.py)

gold 스팬 수 × 0.3 ± 0.1 개를 문서에 삽입. 삽입 위치는 LLM이 남긴 `{{NEG}}` 슬롯(프롬프트에서 2~5개 요구) 또는 문단 끝. 6종 균등. `hard_negatives[]`에 기록(스팬 채점의 FP 집계용).

## 7. 데이터 스키마 (JSONL, 1행 = 1문서)

```json
{
  "doc_id": "kf-0001a2b3",
  "doc_type": "cs_transcript",
  "variation_level": "T2",
  "num_subjects": 3,
  "context_len_bucket": "4k",
  "n_tokens": 4120,
  "generator": {"model": "gpt-5.5", "prompt_version": "compose_v1", "slice": "api-main"},
  "taxonomy_version": "1.2",
  "text": "상담사: 안녕하세요 … ",
  "spans": [
    {
      "id": "s1",
      "start": 120, "end": 134,
      "surface": "공일공 삼삼사사 오오육육",
      "canonical": "010-3344-5566",
      "category": "phone_no", "subtype": "mobile",
      "tier": "L", "kind": "identifier", "span_policy": "must_mask",
      "entity_id": "e3", "subject_id": "c1", "subject_role": "customer",
      "applied_ops": ["hangul_digits"],
      "regex_catchable": false,
      "fragment": null
    },
    {
      "id": "s2", "start": 410, "end": 418, "surface": "신한 110", "canonical": "110-123-456789",
      "category": "bank_account_no", "entity_id": "e5", "subject_id": "c1", "subject_role": "customer",
      "applied_ops": ["chunk_split"], "regex_catchable": false,
      "fragment": {"group": "f1", "index": 1, "of": 2}
    }
  ],
  "hard_negatives": [
    {"start": 900, "end": 915, "surface": "주문번호 2024-0912-3456", "type": "lookalike_number"}
  ],
  "subjects": [
    {"id": "c1", "role": "customer"}, {"id": "c2", "role": "customer"}, {"id": "st1", "role": "staff"}
  ],
  "pre_masked": false
}
```

- `spans` 오프셋은 **문자(codepoint) 단위**, `text[start:end] == surface`를 validate가 강제.
- 태그 스팬(속성)은 `canonical == surface`, `applied_ops == []`.
- `fragment`가 있으면 같은 `group`의 조각들이 하나의 entity 언급. 채점은 조각 단위 partial overlap.
- 비식별화 gold는 별도 파일이 아니라 이 스키마에서 파생: must_mask 스팬 → surrogate 규칙(`deid_default`).

## 8. 검증 (validate.py) — 실패 시 문서 재생성, 3회 실패 시 폐기·로그

1. 모든 `text[start:end] == surface`
2. `category ∈ taxonomy`, `span_policy·tier·kind`가 yaml과 일치
3. 체크섬 카테고리는 `canonical` 검증 통과
4. 슬롯 없이 남은 숫자 식별자 패턴(정규식 스캔) → 생성 모델이 값을 직접 썼다는 뜻, 폐기
5. 태그 균형·중첩 없음, 속성 스팬 ≥ 2어절
6. `doc_type`의 dominant 카테고리 최소 1개 이상 존재
7. 실측 토큰 수로 `context_len_bucket` 재배정 (계획과 2버킷 이상 어긋나면 폐기)
8. 동일 `entity_id`의 `canonical` 동일

## 9. 파일럿 (100건)

- 셀 층화로 100건 → `data/corpus/pilot-0.1/`
- 한울 검수 체크리스트: 문체 현실성 / 슬롯 배치 자연스러움 / 속성 태그 경계 / consultation_content IAA(2인, 30건)
- 규칙 베이스라인(ko-pii, Presidio ko) 실행 → T-level별 F1이 단조 감소하는지 확인. 아니면 op 분포 조정.
- 산출: 분포 조정안 → `taxonomy.yaml: variation.generation_policy` 갱신, ADR-0004 후속 항목 닫기.

## 10. 비용·시간 추정 (참고)

2,500 문서 × 평균 5k 토큰 출력 ≈ 12.5M 출력 토큰. 재생성률 30% 가정 시 ~16M. frontier API 출력 단가 기준 수십만 원대 [?] 파일럿 후 실측. 로컬 20% 슬라이스는 80GB GPU 1장에서 Qwen3.5-35B-A3B로 수 시간.
