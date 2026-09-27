# 은빈 추가 결과 검토 — ac25513

2026-09-27. 원격 `feat/exp-eb`의 `ac25513b9bfc9b08daab86b378ec67305e456cea`를 가져와 검토했습니다. 직전 검토 `b4f76f4` 이후 새 결과는 **Qwen3.5-4B / local_window**입니다. 중간 merge는 기존 main 문서 반영이며 새 추론 실험이 아닙니다. 원격 실행 브랜치·원본 결과·진행 중 평가 코드는 수정하지 않았습니다. 추가 추론은 없습니다.

## 완료 및 무결성 확인

- 본 실험 **1,440문서 / 13,723요청 / gold 218,664스팬**. manifest는 benchmark, accounting과 progress는 완료입니다.
- 응답 SHA, 고유 request ID, 요청별 모델·request SHA, 재구성된 전체 요청 SHA, 데이터·택소노미·scorer SHA가 일치합니다. 모든 strict 지표·세부 집계·문서별 결과·실패 기록이 기존 평가기로 재현됩니다.
- 예약/완료 이벤트가 각각 13,723개이며 누락·중복·응답 불일치가 없습니다. 모든 수신 응답에 provider JSON과 completion 전문이 있고 두 본문이 일치합니다.
- 결과에 기록된 data/request/cohort 해시는 기존 local 조건과 같습니다. **실제 native 계측과 cohort gate 원본은 업로드/링크가 없어 공통 capacity의 적정성은 별도로 검증하지 못했습니다.**
- 기록된 모델/토크나이저 revision은 `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`. 생성과 계측 모두 `enable_thinking: false`. 이는 설정 기록 확인이며 실제 서버 배포를 독립 검증했다는 뜻이 아닙니다. 코드 commit은 `757d707`이고 source SHA는 브랜치 파일과 일치합니다.

## 점수와 오류

F1은 0–100 척도입니다. 아래 보조 지표는 [ADR-0036](../../../../docs/decisions/0036-posthoc-response-diagnostics.md)을 그대로 적용했습니다. 규칙을 이번 결과에 맞춰 변경하지 않았습니다.

| 처리 단계 | Exact F1 | 문자 겹침 F1 | 거절 항목 exact FP |
|---|---:|---:|---:|
| 공식 strict | 0.9696 | 0.4144 | 추가 벌점 없음 |
| 항목별 검사 | 5.9165 | 3.2735 | 47,672 |
| 전체 JSON 코드펜스 제거 + 항목별 검사 | 8.5869 | 5.4645 | 83,370 |

공식 exact TP/FP/FN은 **1,070 / 984 / 217,594**입니다. Strict 실패는 **12,348 / 13,723 (89.9803%)**입니다. 이는 평가 규칙상 실패율이며 서버 장애율이 아닙니다. 업로드된 응답에서 131건은 출력 길이 종료, 나머지는 정상 stop이며 transport 실패는 관측되지 않았습니다.

오류 유형별 요청 수는 서로 중복될 수 있습니다: invalid JSON/최상위 schema 6,812, quote_not_found 4,242, core 밖 시작점 2,520, label_or_quote 1,268, 항목 schema 159, occurrence 100, 종료/잘림 131. `quote_not_found`는 정확한 인용문 부재와 occurrence 범위 초과를 함께 포함하며 모두 환각으로 해석하지 않습니다.

두 보조 처리를 적용하면 기존 strict 실패 요청 중 6,826개에서 유효 항목을 회수합니다. 이때 exact precision **12.59%**, recall **6.52%**이며 TP/FP/FN은 **14,249 / 98,965 / 204,415**입니다. 형식 처리의 영향이 크지만 이 결과만으로 누락을 형식 문제만 탓할 수 없습니다. 앵커할 수 없는 거절 항목은 문자 FP를 계산할 수 없으므로 문자 점수는 위 벌점 포함 exact precision·거절 수와 함께 해석합니다. 모든 단계의 gold 분모와 카테고리/문서 축 합계 일치를 확인했습니다.

이전 Kanana local의 보조 F1 4.0934보다 높지만, 공식 strict F1은 Kanana local 1.6156보다 낮습니다. 보조 결과를 공식 순위로 바꾸지 않습니다. Qwen 4B full 업로드는 아직 10문서 pilot이므로 **4B의 full/local 문맥 효과를 아직 비교할 수 없습니다.**

## 제출 보완 사항

1. Qwen 4B full과 Qwen 2B local의 현재 업로드는 10문서 pilot입니다. 본 실험 결과가 별도로 있다면 해당 아티팩트를 공유해야 합니다. 누락된 파일만으로 재추론을 시작하지 않습니다.
2. native count 파일, 원본 cohort gate, artifact 해시/링크가 필요합니다. REPORT는 아직 `준비`, 환경/시각/GPU/서버/template/실제 한도 등의 필드는 미기입입니다. evaluator 의존성 목록은 있으나 서버 환경 증빙을 대체하지 않습니다.
3. 디렉토리는 `0925-06-qwen-4b-local`이지만 frozen config의 run_id는 `0925-05`입니다. 과거 config/해시를 고쳐 덮어쓰지 말고 디렉토리와 run ID 대응을 REPORT에 설명해야 합니다.
4. responses 약 46.5 MB, events 약 50.4 MB가 git에 직접 올라왔습니다. 향후 공유는 기존 정책대로 압축 Release asset + SHA를 권장합니다. 이번 검토에서 공동 작업 이력을 재작성하지 않았습니다.
5. OpenMed 완료 결과와 Qwen 9B / Kanana 8B 결과는 이 브랜치 snapshot에 없습니다. 결과 미업로드를 실제 미실행으로 단정하지 않습니다.

이제 검토된 본 실험 업로드는 LLM 4조건(Kanana full/local, Qwen 2B full, Qwen 4B local)과 기존 CPU baseline 2개입니다. 전체 핵심 9조건의 실험이 완료됐다는 뜻은 아닙니다.

## 자료 및 재현

- [단계별 CSV](0925-06-qwen-4b-local/summary.csv), [430행 세부 점수 CSV](tables/breakdowns.csv).
- [분석 JSON](0925-06-qwen-4b-local/analysis.json), [요청별 진단](0925-06-qwen-4b-local/per_request.jsonl.gz), [원본/저널 감사](audit.json).
- [원본 고정 commit 링크와 입력 해시](INPUTS.json), [무결성 목록](ARTIFACTS.sha256).
- 코드 변경 없이 `src.analysis.response_diagnostics`와 `src.analysis.export_diagnostics`로 생성했습니다. [실행 가이드](../../../../docs/guide/response-diagnostics.md)의 입력에 위 고정 commit의 result/responses와 같은 SHA의 gold JSONL을 지정하면 재현할 수 있습니다. 분석 소스와 입력 SHA는 analysis.json에 있습니다.

이전 3조건 진단은 [원본 보고서](../0927-response-diagnostics-v1/REPORT.md)에 보존합니다. 이번 검토는 저장된 응답의 오프라인 검증이며 새 native API/GPU 테스트는 수행하지 않았습니다.
