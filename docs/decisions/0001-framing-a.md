# ADR-0001: 프레이밍 A 채택 — 규제 기반 택소노미 + long-context 벤치마크

- 상태: accepted
- 날짜: 2026-09-08
- 결정자: 한울
- 관련: `docs/related_work.md` §3, `docs/meetings/2026-09-08-kickoff.md`

## 배경

선행연구 조사 결과, 한국 금융 도메인 PII 벤치마크는 없으나 과업(스팬 추출·비식별화) 자체는 성숙했고,
Thunder-DeID(Findings EMNLP 2025)가 이미 계좌·카드·금융상품 레이블을 포함한 한국어 PII 택소노미를 냈다.
4페이지 short paper에서 novelty를 어디에 둘지 정해야 했다.

## 결정

프레이밍 A를 채택한다.

1. 개인정보보호법 + 신용정보법 + 금융분야 가명·익명처리 안내서에 근거한 **2-tier 택소노미** (Legal PII / Identifiability)
2. **long-context · multi-subject 합성 금융 문서 코퍼스** (포맷 유효 식별자 포함)
3. 과업 두 개: **스팬 추출** (tier별 F1) + **비식별화** (TAB식 risk-weighted recall, 정보손실, 교차 언급 일관성)
4. **API 모델 + 한국어 로컬 LLM**을 함께 올린 리더보드와 분석
5. 초개인화 피싱(행동정보 악용)은 motivation + 소규모 identifiability probe로만 다룬다

합성 데이터 생성과 스팬 추출 평가 대상은 **로컬 모델에 한정하지 않는다**.

## 이유

- domain × language × setting 갭은 명확하고 방어 가능하다. task 신규성을 주장하면 반박당한다.
- 두 과업 + 리더보드 + 분석 세 가지 finding이면 4페이지가 딱 찬다. adversarial 벤치까지 넣으면 넘친다.
- 한국 금융사가 외부 API에 PII를 못 보내는 현실에서 API-vs-로컬 격차 자체가 실무적으로 의미 있는 finding이다.

## 검토한 대안

- **B. Identifiability(법적으로는 괜찮지만 위험한 정보) 중심 adversarial 벤치** — 스토리는 강하지만 attacker 프로토콜·re-ID 평가가 추가로 필요해 2~3주·4페이지에 안 맞음. dual-use 리뷰 리스크. → 후속 long paper로.
- **C. 기존 PII 필터 감사(audit)만** — 가장 싸지만 택소노미 기여를 버리게 되어 Thunder-DeID 대비 차별점이 약함.

## 영향

- Thunder-DeID·KDPII와의 차별점(도메인, 코퍼스 성격, 법령 정렬, long-context, 일관성 지표)을 related work에서 명시적으로 side-by-side로 써야 함
- 후속 결정 필요: 생성 모델과 리더보드 제외 규칙(ADR-0002), 타겟 venue(ADR-0003), 리더보드 모델 리스트
- 길이·subject 수를 통제 변수로 설계해 degradation curve를 깨끗한 figure로 만들 것
