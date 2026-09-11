# ADR-0004: 택소노미 v1 설계 — 2 tier × 2 kind, 법령 조문 단위 근거, 표면형 변형 축

- 상태: proposed (한울 결정으로 accepted 전환 예정; 성현 리뷰 불필요 — 콜센터 실태는 자체 조사로 대체)
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
2. 각 카테고리에 **kind** (identifier / attribute)를 둔다. L-identifier 17, L-attribute 7, I-attribute 12 = 36개. 근거 약한 `crypto_wallet`(특금법은 사업자 의무 규정), `lifestyle_indicator`(법령·선행 근거 없음)는 제외하고 사유를 `exclusions`에 기록.
3. **span_policy** 3종: `must_mask` (L-identifier, 민감정보) / `mask_if_linked` (L-attribute: 신용정보법 결합 조건 반영) / `detect_only` (I).
4. 채점은 **카테고리 단위**. subtype은 어노테이션에만 기록.
5. **제외**: 생체정보(텍스트 스팬 불가), 금융기관·상품명(공개 정보), 금액 단독.
6. 체크섬이 있는 5개(rrn, 외국인번호, 사업자, 법인, 카드)는 합성 시 항상 유효값 생성. rrn은 2020.10 전후 두 집단 모두 생성하고 태그.
7. 직원(상담사) 이름은 person_name + `subject_role: staff`로 기록해 분석에서 분리 가능하게.
8. **표면형 변형 축 (DLP 축)**: 정형 숫자 식별자는 regex로 풀리므로, 문서 단위 변형 레벨 T0(canonical)~T3(structural) 4단계와 25개 변형 연산(한글 숫자 받아쓰기, STT 오류, 분할 발화, 상담사 되읽기, 부분 마스킹, OCR 혼동, 앵커 누락 등)을 정의한다. **T4(encoded: base64·역순·계산식·유사 글리프)는 제외** — 공격 분포이지 DLP 입력 분포가 아님; adversarial 트랙 후보. 스팬마다 `applied_ops`를 기록하고, F1을 (tier×kind)×(T-level) 격자로 보고한다. hard negative 6종을 gold의 ~30% 비율로 삽입해 precision을 의미 있게 만든다.
9. **STT 프로필은 실태 조사로 고정** (`literature/notes/stt-korean-numbers.md`): 상용 한국어 STT는 ITN 기본(리턴제로 `use_itn` true, CLOVA·Google 숫자 고정) → 아라비아 70% / 한글 발음 20% (KsponSpeech·AI Hub directText 형태) / 혼합 10% (Whisper 토큰 분할). 0은 공 80%·영 20%, 구어 구분자 에 55%·다시 35%. STT 단 한국어 PII 마스킹 상용 엔진 부재(AWS Transcribe ko-KR redaction 미지원) → regex 마스킹 후 한글 숫자·분할 발화가 남는 pre-masked 전사 20%.

## 이유

- 조문 단위 인용이 Thunder-DeID·KDPII와의 결정적 차별점이고, 리뷰어가 "왜 이게 PII냐"를 물을 때 답이 된다.
- identifier/attribute 분리가 없으면 "대출 잔액 3,200만 원"을 계좌번호와 같은 잣대로 채점하게 되어 리더보드가 왜곡된다.
- `mask_if_linked`는 법 조문(결합 시 신용정보)을 그대로 과업 정의로 옮긴 것. long-context multi-subject 설계와 자연스럽게 맞물린다.
- 변형 축이 없으면 리더보드는 regex 상한선 근처에서 포화하고 "누가 잘 막나"가 측정되지 않는다. AI DLP의 실제 입력(STT 녹취, OCR, 표, 우회)이 바로 T2~T4다. 이것이 NER 벤치마크가 아니라 DLP 벤치마크인 이유.

## 검토한 대안

- **Thunder-DeID 레이블 재사용 + 금융 확장** — 판결문 중심 위계(사건관계인/기타)가 금융 문서와 맞지 않고, 공개 기관·상품명이 대량 포함되어 채점 노이즈. 대신 매핑표로 호환성만 확보.
- **flat 33-tag (Jang/KDPII) 확장** — 법령 근거·tier 구조가 없어 기여가 약함.
- **I tier를 문서 단위 속성으로** — 과업이 둘로 갈라져 4페이지에 안 맞음. v1은 전부 스팬. 문서 속성은 후속.

## 열린 질문 (리뷰 요청)

1. `dob_age`를 L로 올릴지 (PIPA 개인정보 vs 신용정보법 미열거). v1: I.
2. `device_network`(IP)를 L로 올릴지. 개인정보위 결정례 인용 가능하면 L.
3. `consultation_content` 경계 — 100건 파일럿 IAA 후 가이드라인 확정.
4. 직원 이름을 de-id 과업에서 must_mask로 볼지.
5. 변형 레벨 기본 분포(T0 25/T1 30/T2 25/T3 20%)와 hard negative 비율(30%)의 적정성 — 파일럿 후 조정.

해결됨: T4 제외 (2026-09-11, 한울). STT 프로필 수치는 자체 조사로 확정 (결정 9).

## 영향

- `src/generate`는 `taxonomy.yaml`의 `format`·`document_types`·`variation`을 읽어 생성. 변형 연산은 값 생성 후 후처리 단계로 구현 (op별 함수 1개). 체크섬 유틸은 ko-pii 구현(MIT) 인용·재사용.
- `src/eval/metrics.py`는 (tier×kind)×(T-level) 격자와 op별 recall, hard-negative precision을 내야 함. chunk_split은 불연속 스팬 partial-overlap 채점.
- 논문 §2 표는 `taxonomy.md` §3·§4에서 생성.
- 다음 단계: 한울 결정(열린 질문 1~4) → accepted → 어노테이션 가이드라인 초안 → 생성 파이프라인.
