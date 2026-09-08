# taxonomy — PII 택소노미

## 파일

- `taxonomy.yaml` — **원본**. 코드(생성·평가)와 논문 표가 모두 이 파일에서 나옵니다.
- `taxonomy.md` — 사람이 읽는 설명과 법령 근거 (yaml에서 생성하거나 손으로 유지, 어긋나면 yaml이 맞음)
- `mapping_thunder_deid.md` — Thunder-DeID 레이블과의 대응표 (리뷰어 대응용, 예정)

## 구조 (2-tier)

| Tier | 의미 | 근거 | 평가 |
|---|---|---|---|
| **L — Legal PII** | 법령상 개인정보·고유식별정보·개인신용정보로 명시된 식별자 | 개인정보보호법 §2·§23·§24, 신용정보법 §2, 금융분야 가명·익명처리 안내서 | 스팬 추출 필수, 비식별화 필수 |
| **I — Identifiability** | 법령상 직접 규제 대상은 아니나 결합 시 금융고객을 식별·프로파일링 가능하게 하는 준식별자·행동정보 | TAB의 quasi-identifier, Baroud et al. 간접식별자 개념 차용. **법적 판단 아님**을 명시 | 스팬 추출 평가, 비식별화는 선택(옵션 트랙) |

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
