# 응답 분해 및 부분점수 — 사후 보조 분석

2026-09-27, [ADR-0036](../decisions/0036-posthoc-response-diagnostics.md). 추가 모델 호출 없이 저장된 완료 응답을 분석합니다. 공식 strict 점수는 그대로 유지합니다. 이미 오류 양상을 확인한 뒤 정한 분석이므로 탐색적 결과로 표기합니다.

## 어떤 점수를 보나

| 단계 | 허용하는 처리 | 잘못된 출력 처리 |
|---|---|---|
| `strict` | 기존 평가기 그대로 | 항목 하나라도 잘못되면 요청 전체가 빈 예측 |
| `itemwise` | 올바른 최상위 JSON 안의 항목을 각각 기존 규칙으로 검사 | 유효한 항목만 유지, 거절한 항목마다 exact FP 1개 |
| `fence_itemwise` | 응답 전체를 감싼 단일 JSON/무언어 코드펜스 제거 후 위와 동일 | 설명문 추출·JSON 완성·인용문 수정 없음 |

**세 단계 모두 전체 gold가 분모에 남습니다.** 실패 요청·잘린 출력은 빈 예측입니다. 최상위 JSON을 해석할 수 없으면 항목 개수를 알 수 없으므로 FP 수를 추정하지 않습니다. 해석 가능한 항목의 잘못된 occurrence, 없는 quote, core 밖 시작점, 잘못된 category/schema 등은 각각 FP를 부과합니다. 라벨을 알 수 없으면 `__unassigned_invalid_item__` 버킷을 사용합니다. 이를 정식 택소노미의 37번째 라벨로 취급하지 않습니다.

각 단계의 exact 지표는 `TP = category/start/end 완전 일치`, `FP = 앵커된 오탐 + 거절 항목 수`, `FN = 전체 gold − TP`입니다. 유효한 중복 스팬은 기존 규칙대로 제거하지만 거절 항목은 항목마다 벌점이 있습니다. `strict`의 invalid FP는 0이며, 이는 잘못된 항목이 없다는 뜻이 아니라 공식 점수에 항목 단위 벌점을 추가하지 않았다는 뜻입니다. `anchored_exact_micro`는 벌점 전 값이며 보조 점수 표에는 벌점을 포함한 `exact_micro`를 사용합니다.

**부분점수는 카테고리별 문자 겹침 precision/recall/F1**입니다. 각 `(category, Unicode 문자 위치)`의 집합을 G/P라고 하면 TP=`|G∩P|`, FP=`|P−G|`, FN=`|G−P|`입니다. 같은 범위를 여러 번 예측해도 합집합으로 한 번만 셉니다. UTF-8 바이트 길이와 다르며 이모지도 Python Unicode 위치 규칙을 따릅니다.

예를 들어 gold 이름 `김민수`를 같은 카테고리의 `민수`로 추출하면 exact 일치는 0이지만 문자 TP 2 / FN 1입니다. `주소` 카테고리로 추출하면 겹침 TP도 0입니다. 너무 넓게 추출한 문자는 FP가 됩니다. 긴 상담내용 스팬은 짧은 이름보다 더 많은 문자 가중치를 가지므로 **mention F1 또는 entity recall과 동등한 척도가 아닙니다.**

앵커할 수 없는 거절 항목은 문자 범위를 정할 수 없어 문자 FP에 포함하지 못합니다. 따라서 문자 precision은 **유효하게 앵커된 출력 기준**이며, 거절 항목까지 계산하는 exact precision·거절 수·요청 오류율을 함께 봐야 합니다. 임의의 항목→문자 환산이나 종합 가중점수를 만들지 않습니다.

## 실행

별도 분석 checkout에서 실행할 것을 권장합니다. 이 모듈은 `src/eval/`의 실행 소스 해시를 바꾸지 않지만, 작업 중인 추론 환경의 버전/의존성을 갱신하면 안 됩니다. 표준 라이브러리와 기존 taxonomy 의존성만 사용합니다.

```bash
python -m src.analysis.response_diagnostics \
  --gold experiments/prepared/full_context_targeted/gold.jsonl \
  --responses path/to/completed-run/responses.jsonl \
  --strict-result path/to/completed-run/result.json \
  --output experiments/results/analyses/response-v1/run-id
```

`--gold`는 result manifest의 data SHA와 정확히 일치하는 JSONL입니다. 동일한 데이터라도 재직렬화해 SHA를 바꾸면 거절합니다. frozen protocol로 요청을 재구성하므로 수백 MB의 requests 파일을 메모리에 읽을 필요는 없습니다. gold와 raw responses는 메모리에 읽습니다. 출력 경로는 새 디렉토리여야 합니다.

다음 조건이 맞지 않으면 결과를 쓰지 않습니다: 완료 accounting, 전체 응답 수/고유 ID, benchmark gate 기록, 원본 protocol/metrics 소스 SHA, data/taxonomy/raw SHA, served model, 각 request SHA와 전체 요청 SHA, 원본 strict 점수·세부 집계·문서별 결과·실패 목록 재현. 현재 checkout의 scorer가 다르면 원본 버전을 준비하며 해시를 고쳐 통과시키지 않습니다. 단위 테스트 통과는 native API/GPU 검증을 의미하지 않습니다.

pilot/smoke는 기본 거절합니다. 개발자가 로컬에서 명시적으로 `--allow-pilot`을 쓰더라도 benchmark 경로에 그 점수를 공개하지 않습니다. 이 분석은 underlying native count/cohort gate를 직접 검증하지 않으므로 `capacity_eligibility_independently_verified: false`를 기록합니다. 별도 cohort 감사가 필요합니다.

## 산출물과 연구 인계

- `summary.csv`: 3단계별 exact 및 character P/R/F1, invalid-item FP, 요청 오류 수. 값의 범위는 0–1입니다. REPORT 표는 100배 표시합니다.
- `analysis.json`: 전체 지표와 provenance. `stages.<stage>.by_category`, `by_axis`, `tier_kind_tlevel`에 exact, `character_coverage_breakdowns`에 문자 부분점수. 문서 축은 T-level·문서 유형·길이·subject 수·생성기입니다. 기존 op/subject-role recall과 entity all-mentions recall도 유지합니다.
- `per_request.jsonl.gz`: strict 거절 사유, 단계별 해석 경로·항목 수·유효/거절 수·거절 유형·카테고리. 원본 completion은 입력 raw에서 request ID로 찾습니다. 여러 오류가 같은 요청에 있을 수 있으므로 유형별 요청 수를 단순 합산하지 않습니다.
- `REPORT.md`, `ARTIFACTS.sha256`: 해석 주의점과 산출물 무결성.

실험 담당자는 원본 result/응답/계측/cohort/환경 기록을 계속 기존 공유 규칙대로 제출합니다. 보조 분석의 JSON은 `src.eval.export`용 result 형식이 아니며 공식 리더보드에 넣지 않습니다. 사라는 strict 결과와 함께 이 자료를 오류 해석에 활용할 수 있습니다. 세 단계 차이는 독립적인 요인 분해가 아니며, 일부 항목 복구와 FP 벌점 때문에 F1이 항상 오르지는 않습니다. 사후 선택한 분석임을 논문/부록에 밝히고, 4페이지 본문에는 필요한 보조 결과만 요약합니다.

완료 분석은 코드·입력의 고정 commit/link·해시와 함께 GitHub `experiments/results/analyses/`에 푸시합니다. 원본 실행 아티팩트는 수정하거나 재추론하지 않습니다.

JSON의 카테고리·문서 축·tier/kind/T 격자를 비교하기 쉬운 CSV로 펼칠 수도 있습니다. 재채점하거나 서로 다른 run을 합산하지 않고 각 run/stage의 값을 그대로 옮깁니다. `metric=exact_with_invalid_item_fp`와 `anchored_character_coverage`를 구별합니다.

```bash
python -m src.analysis.export_diagnostics \
  --analyses experiments/results/analyses/response-v1/*/analysis.json \
  --output experiments/results/analyses/response-v1/tables
```

## 형식 준수와 탐지 성능 분리 (10/1)

[ADR-0037](../decisions/0037-format-grounding-detection-decomposition.md)은 공식 점수를 바꾸지 않고 다음 축을 추가합니다. 기존 보조 분석을 입력으로 사용하며 모든 정답·실패 요청을 유지합니다.

- **형식 준수율:** 전체 요청 중 정상 종료하고 코드펜스 없는 JSON, 정확한 필드·자료형, 양의 정수 occurrence, 비어 있지 않은 인용문, 중복 키 없음 조건을 만족한 비율. 인용문이 실제 원문에 있는지와 문자열 category가 허용 목록에 있는지는 별도 검사입니다. `spans: []`도 형식은 준수할 수 있으므로 **빈 답 비율**을 함께 보여줍니다.
- **원문 위치 지정:** 파싱된 항목 기준으로 없는 인용문, occurrence 범위 초과, core 밖 시작점 등을 분리합니다. 없는 인용문이 곧 환각의 증거는 아니며 일부는 표기 변형·잘못된 반복 지정일 수 있습니다. 한 항목에 문제가 여러 개면 고정된 검사 순서의 첫 사유로 집계합니다.
- **관측된 탐지:** 기존 `fence_itemwise` P/R/F1을 전체 gold 기준으로 제시합니다. 위치만 일치하는 보조 점수는 유효한 알려진 category 항목만 대상으로 라벨을 무시하되, 거절 항목 FP는 유지합니다. 미지의 category를 고쳐 주거나 파싱 불가 답변에서 모델의 잠재적 인식을 추정하지 않습니다.
- **정답 누락 분해:** 정답 스팬을 정확 적중 / 소유 요청의 종료·JSON·빈 답 문제 / 위치 일치·라벨 오류 / 경계 겹침 / 거절 항목이 섞인 미해결 누락 / 그 외 겹치는 예측 없음으로 우선순위 분할합니다. 각 요청 소유권은 정답 시작점을 포함하는 기존 core로 정합니다. 이는 사후 설명용이며 정답을 프롬프트·복구에 사용하지 않습니다. `거절 항목이 섞인 미해결 누락`은 그 정답을 모델이 찾았다는 뜻이 아닙니다.

```bash
python -m src.analysis.failure_decomposition \
  --gold path/to/hash-matching-gold.jsonl \
  --responses path/to/responses.jsonl \
  --reference path/to/result.json \
  --diagnostics path/to/replay-verified/analysis.json \
  --output experiments/results/analyses/failure-decomposition/run-id
python -m src.analysis.export_failure_decomposition \
  --analyses experiments/results/analyses/failure-decomposition/*/analysis.json \
  --output experiments/results/analyses/failure-decomposition/tables
```

`summary.csv`는 strict F1, 형식·빈 답 비율, 항목별 탐지 P/R/F1, 위치·문자 지표와 각 분모를 제공합니다. `failure_types.csv`는 요청·항목·정답별 상호 배타적 분해와 분모를 담습니다. 축 간 비율은 분모가 다르므로 합산하지 않습니다. 문서/요청별 기록과 입력·소스 SHA도 보존합니다.

논문에는 **strict F1 / 형식 준수율 / 빈 답 비율 / 항목별 P·R·F1**을 병기하고 누락 분해 그림은 보조 자료로 둘 수 있습니다. 성공 요청만의 점수를 전체 능력으로 제시하거나, 증가한 보조 점수를 “형식 영향을 완전히 제거한 순수 탐지능력”이라고 부르지 않습니다. 규칙/토큰 분류 baseline의 형식 준수는 비교 가능한 생성 작업이 아니므로 100% 대신 N/A로 표시합니다. 새 기준 역시 사후 탐색적 분석임을 명시합니다.
