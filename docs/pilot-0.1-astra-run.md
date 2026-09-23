# Astra 파일럿 실행 결과 — 2026-09-15

**API 배정 80건 생성 완료. 자동 검증 80/80 통과, 추가 자동 검수 경고 0건. 사람 검수는 미완료이며 로컬 20건은 엔드포인트 대기 중입니다.**

## 실행 설정

- 모델: `gpt-6-astra`, OpenAI 공식 API. 사용자가 선택하고 키를 설정했습니다.
- 프롬프트: `compose_v2`, 택소노미 1.2, 계획 seed 0.
- Astra 설정: `reasoning_effort=low`, `max_completion_tokens=32000`. `temperature`와 API `seed`는 생략합니다. 값·변형 생성에는 계획 seed를 사용합니다.
- 사전 10건은 최대 4건, 나머지 70건은 최대 8건 동시 호출했습니다. 사전 10건은 본 80건에 포함하며 중복 호출하지 않았습니다.
- 출력 모델 ID·응답 ID·종료 사유·토큰 사용량·호출 설정은 원문 JSONL의 `completion`에 저장했습니다.

## 산출물

| 항목 | 결과 |
|---|---:|
| 실제 생성 / 자동 검증 통과 | 80 / 80 |
| 추가 자동 검수 경고 | 0 |
| 스팬 수 | 12,167 |
| 문서 내 고유 식별자 엔터티 합계 | 1,747 |
| Hard negatives | 276 |
| 등장 카테고리 | 36 / 36 |
| 독립 검수 자료 | 30건, 문서유형별 3건 |

T-level: T0 28 / T1 23 / T2 16 / T3 13. 길이 버킷은 여전히 문자 수 기반 근삿값입니다. 원래 계획의 80/20 슬라이스 배정을 유지했습니다.

로컬 파일 (`data/`는 gitignore 대상):

- `data/corpus/pilot-0.1/raw.astra-v2-api.jsonl`: 원문 80건과 API 메타데이터.
- `data/corpus/pilot-0.1/docs.astra-v2-api.jsonl`: 검증을 통과한 값·스팬 포함 문서.
- `data/corpus/pilot-0.1/docs.astra-v2-api.jsonl.rejects.jsonl`: 자동 검증 실패 기록.
- `data/corpus/pilot-0.1/audit.astra-v2-api.json`: 문서별 오류·필수 카테고리·길이·레벨·hard negative 점검.
- `data/corpus/pilot-0.1/manifest.astra-v2-api.json`: 분포·사용량·코드 및 파일 SHA-256·설치 버전.
- `data/corpus/pilot-0.1/review/consultation-iaa30.md` / `.jsonl`: 기존 모델 주석을 숨긴 독립 검수 30건.
- `data/corpus/pilot-0.1/review/README.md`: 검수 기준.
- `data/corpus/pilot-0.1/prompts.v2/`: 계획별 실제 프롬프트 재현본.

## 파일럿에서 발견하고 수정한 문제

초안 v1은 완료 응답 2건을 받은 뒤 중단했습니다. T1 문서에 T3 `readback` 지시가 들어갔고, 속성 태그 안의 `{{NEG}}` 치환으로 스팬 오프셋이 어긋났습니다. 이 당시 진행 중이던 장문 요청 하나는 중단돼 응답과 사용량이 저장되지 않았습니다.

v2에서는 레벨별 구조 지시를 명시하고 hard negative를 태그 밖 독립 줄로 배치했습니다. 파서는 태그 중첩과 태그 내부 hard negative를 거부합니다. 서로 겹치는 개인정보/비개인정보 라벨을 허용하지 않는 처리입니다. 기존 v1 원문·진단 보고서는 별도 파일로 보존했습니다.

관련 테스트는 **21개 통과**했습니다. 잘린 응답을 저장하되 코퍼스에서는 거부하고, 재개 시 계획·모델·프롬프트 불일치를 검사합니다.

## 비용 기록

v2의 저장된 완료 응답 기준 입력 138,346토큰, 출력 593,864토큰입니다. 출력에는 추론 11,206토큰이 포함됩니다. 캐시 읽기·쓰기를 반영한 공식 Standard 단가 환산은 **약 $31.42**입니다. [공식 단가](https://developers.openai.com/api/docs/models/gpt-6-astra)

이는 실제 계정 청구액이 아닙니다. v1 진단·중단한 요청·저장되지 않은 재시도·세금·계정 할인은 제외했습니다. 사전 v2 10건은 80건에 포함돼 비용도 한 번만 집계합니다.

## 남은 검수와 제한

- 모델의 속성 태그는 검수 전 임시 주석입니다. 일부 응답은 일반 절차 안내까지 `consultation_content`로 감싸므로 택소노미의 제외 규칙에 따라 사람 검수가 필요합니다.
- 두 검수자가 공통 판정 단위를 사전에 확정하고 독립 검수해야 합니다. IAA 30건 자료는 준비했지만 κ나 사람 간 일치도는 아직 계산하지 않았습니다.
- 은행명과 생성된 계좌 형식의 일치, T3 대용 지칭·앵커·분할의 의미, 문체 현실성은 자동 검사만으로 확정할 수 없습니다.
- `공통 참고정보:`라는 일정한 표제가 hard negative의 위치를 알려 주는 단서가 될 수 있습니다. 본 코퍼스에서는 문맥을 다양화하고 유형에 맞게 자연스럽게 배치해야 합니다.
- T3 구조 연산의 실제 효과·STT 프로필 분포·토큰 수 실측은 별도 점검 대상입니다. `pre_masked_subset` 문서 단위 후처리는 아직 구현되지 않아 이번 파일럿은 해당 20% 비율을 충족한다고 주장할 수 없습니다.
- 로컬 Qwen 20건과 생성기 간 순위 상관, 베이스라인 평가, 논문 결과는 아직 실행하지 않았습니다.

## 재검증

```bash
.venv/bin/python -m src.generate.run fill --raw data/corpus/pilot-0.1/raw.astra-v2-api.jsonl --out data/corpus/pilot-0.1/docs.astra-v2-api.jsonl
.venv/bin/python -m src.generate.audit --raw data/corpus/pilot-0.1/raw.astra-v2-api.jsonl --out data/corpus/pilot-0.1/audit.astra-v2-api.json
```
