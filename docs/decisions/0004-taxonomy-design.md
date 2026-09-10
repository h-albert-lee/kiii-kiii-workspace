# ADR-0004: 택소노미 v1 설계 — 2 tier × 2 kind, 법령 조문 단위 근거

- 상태: proposed (한울·성현 리뷰 후 accepted 예정)
- 날짜: 2026-09-10
- 결정자: 한울
- 관련: ADR-0001, `taxonomy/taxonomy.yaml`, `taxonomy/taxonomy.md`, `literature/notes/legal-sources-ko.md`

## 배경

ADR-0001에서 "Legal / Identifiability 2-tier"를 정했지만 카테고리 단위 설계는 없었다.
law.go.kr 원문 조사 결과 신용정보법 시행령 §2가 식별정보를 상세히 열거하고(전자우편·SNS·**고객번호**·CI/DI·사업자/법인번호),
§2 1호 가목이 "식별정보는 거래정보 등과 **결합될 때만** 신용정보"라고 정의함을 확인했다.
Thunder-DeID는 계좌·카드번호를 `고유번호` 버킷에 두고 금액·거래·신용정보 속성은 다루지 않는다.

## 결정

1. **Tier L** = 법령이 열거한 것만. 카테고리마다 조문을 적는다. **Tier I** = 미열거 준식별자·행동정보. 법적 주장이 아님을 명시한다.
2. 각 카테고리에 **kind** (identifier / attribute)를 둔다. L-identifier 18, L-attribute 7, I-attribute 13 = 38개.
3. **span_policy** 3종: `must_mask` (L-identifier, 민감정보) / `mask_if_linked` (L-attribute: 신용정보법 결합 조건 반영) / `detect_only` (I).
4. 채점은 **카테고리 단위**. subtype은 어노테이션에만 기록.
5. **제외**: 생체정보(텍스트 스팬 불가), 금융기관·상품명(공개 정보), 금액 단독.
6. 체크섬이 있는 6개(rrn, 외국인번호, 사업자, 법인, 카드, 지갑)는 합성 시 항상 유효값 생성. rrn은 2020.10 전후 두 집단 모두 생성하고 태그.
7. 직원(상담사) 이름은 person_name + `subject_role: staff`로 기록해 분석에서 분리 가능하게.

## 이유

- 조문 단위 인용이 Thunder-DeID·KDPII와의 결정적 차별점이고, 리뷰어가 "왜 이게 PII냐"를 물을 때 답이 된다.
- identifier/attribute 분리가 없으면 "대출 잔액 3,200만 원"을 계좌번호와 같은 잣대로 채점하게 되어 리더보드가 왜곡된다.
- `mask_if_linked`는 법 조문(결합 시 신용정보)을 그대로 과업 정의로 옮긴 것. long-context multi-subject 설계와 자연스럽게 맞물린다.

## 검토한 대안

- **Thunder-DeID 레이블 재사용 + 금융 확장** — 판결문 중심 위계(사건관계인/기타)가 금융 문서와 맞지 않고, 공개 기관·상품명이 대량 포함되어 채점 노이즈. 대신 매핑표로 호환성만 확보.
- **flat 33-tag (Jang/KDPII) 확장** — 법령 근거·tier 구조가 없어 기여가 약함.
- **I tier를 문서 단위 속성으로** — 과업이 둘로 갈라져 4페이지에 안 맞음. v1은 전부 스팬. 문서 속성은 후속.

## 열린 질문 (리뷰 요청)

1. `dob_age`를 L로 올릴지 (PIPA 개인정보 vs 신용정보법 미열거). v1: I.
2. `device_network`(IP)를 L로 올릴지. 개인정보위 결정례 인용 가능하면 L.
3. `crypto_wallet` 근거가 약함(특금법). L 유지 vs I 이동.
4. `consultation_content` 경계 — 100건 파일럿 IAA 후 가이드라인 확정.
5. 직원 이름을 de-id 과업에서 must_mask로 볼지.

## 영향

- `src/generate`는 `taxonomy.yaml`의 `format`·`document_types`를 읽어 생성. 체크섬 유틸은 ko-pii 구현(MIT) 인용·재사용.
- `src/eval/metrics.py`는 tier×kind 계층으로 stratified F1을 내야 함.
- 논문 §2 표는 `taxonomy.md` §3·§4에서 생성.
- 다음 단계: 성현 리뷰(금융 현실성) → v1.0 accepted → 어노테이션 가이드라인 초안 → 생성 파이프라인.
