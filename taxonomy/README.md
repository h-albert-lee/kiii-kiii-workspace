# taxonomy — PII 택소노미

## 파일

- `taxonomy.yaml` — **원본**. 코드(생성·평가)와 논문 표가 모두 이 파일에서 나옵니다.
- `taxonomy.md` — 설계 근거와 법령 매핑 (영어, 논문 §2 원천). 어긋나면 yaml이 맞음
- `mapping_prior_work.md` — Thunder-DeID·KDPII/Jang·ko-pii·Gretel·ai4privacy·TAB 대응표 (리뷰어 대응용)
- 근거 자료: `literature/notes/legal-sources-ko.md` (조문 원문), `literature/notes/prior-pii-schemas.md` (선행 레이블 체계), `literature/notes/stt-korean-numbers.md` (STT 숫자 출력 실태)

## 구조 (2 tier × 2 kind) — v1.2-draft: L-identifier 17, L-attribute 7, I-attribute 12 + 변형 축 (T0~T3, 25 ops) + STT 프로필

| Tier | 의미 | 근거 | 평가 |
|---|---|---|---|
| **L — Legal PII** | 법령상 개인정보·고유식별정보·개인신용정보로 명시된 식별자 | 개인정보보호법 §2·§23·§24, 신용정보법 §2, 금융분야 가명·익명처리 안내서 | 스팬 추출 필수, 비식별화 필수 |
| **I — Identifiability** | 법령상 직접 규제 대상은 아니나 결합 시 금융고객을 식별·프로파일링 가능하게 하는 준식별자·행동정보 | TAB의 quasi-identifier, Baroud et al. 간접식별자 개념 차용. **법적 판단 아님**을 명시 | 스팬 추출 평가, 비식별화는 선택(옵션 트랙) |

`kind`: identifier(단독 식별 스팬) / attribute(개인에 관한 정보). `span_policy`: must_mask / mask_if_linked(신용정보법 결합 조건) / detect_only. 자세한 정의는 yaml 상단 주석.

**변형 축 (`variation`)**: 정형 표기는 regex로 잡히므로 벤치마크 난이도는 표면형 변형에서 나옵니다. T0 canonical → T1 formatting → T2 lexical(한글 숫자·OCR·유니코드) → T3 structural(분할·상담사 되읽기·앵커 누락·대용 지칭). T4 encoded(인코딩·우회)는 공격 분포이므로 제외. 문서마다 레벨을 배정하고 스팬마다 적용 op를 기록합니다. 상담 전사는 `stt_profile`(실제 STT 출력 분포 조사 기반, `literature/notes/stt-korean-numbers.md`)을 따릅니다. hard negative 6종 포함. 설명은 `taxonomy.md` §8.

## 카테고리 작성 규칙

각 카테고리에 다음 필드를 채웁니다 (yaml 참고):
- `id` — 짧은 영문 snake_case, 변경 금지
- `tier` — L | I
- `name_ko`, `name_en`
- `legal_basis` — 조문 또는 안내서 항목. I tier는 `null`
- `format` — 정규식 / 체크섬 규칙 (있으면). 합성 데이터 생성과 규칙 베이스라인이 공유
- `examples` — 합성 예시 2~3개 (실제 데이터 금지)
- `notes` — 판단 기준, 경계 사례

## 버전

`taxonomy.yaml`의 `version` 필드를 올리고 변경 내용을 `CHANGELOG` 섹션에 적습니다. 실험 결과 파일의 `data_version`이 이 버전을 참조합니다.
