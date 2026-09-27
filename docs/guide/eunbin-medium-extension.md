# 은빈 / 에이전트 — 중간 크기 모델 추가 실험

2026-09-26, [ADR-0035](../decisions/0035-medium-model-extension.md). **기존 소형 모델 실험을 보존하고 아래 두 모델을 추가합니다.** 담당은 은빈이며, 실제 착수 시 새 run ID·서버 자원·revision·상태를 [배정표](../../experiments/ASSIGNMENTS.md)에 기록합니다. 이 문서는 추가 배정이며 실행 완료 보고가 아닙니다.

## 배정과 순서

| 우선순위 | 정확한 모델 ID | 비교 목적 | 조건 |
|---|---|---|---|
| 1 | `Qwen/Qwen3.5-9B` | 기존 Qwen3.5 2B/4B와 같은 계열의 큰 모델 비교 | full_context_targeted + local_window |
| 2 | `kakaocorp/kanana-1.5-8b-instruct-2505` | 더 큰 한국어·영어 모델 기준점 | full_context_targeted + local_window |

[Qwen 공식 카드](https://huggingface.co/Qwen/Qwen3.5-9B)는 네이티브 문맥 262,144와 vLLM 지원을 명시합니다. [Kanana 공식 카드](https://huggingface.co/kakaocorp/kanana-1.5-8b-instruct-2505)는 한국어·영어 모델이며 32,768 초과는 별도 문맥 확장 설정이 필요합니다. 실제 서버 한도는 모델 카드가 아니라 배포 환경에서 확인합니다. 이번 비교에 YaRN 같은 문맥 확장이나 양자화를 임의로 추가하지 않습니다. Kanana 1.5 8B와 Kanana 2 3B는 세대가 달라 **크기만의 효과라고 해석할 수 없습니다.** 형식 오류가 줄어들지는 실제 결과로 판단합니다.

## 진행 중인 fork/브랜치 보호

9/26 확인한 `origin/feat/exp-eb`에는 `c1c7c48`의 실행 폴더·checkpoint 기록과 `757d707`의 nullable usage 처리 수정이 있습니다. [브랜치 결과 기록](https://github.com/h-albert-lee/kiii-kiii-workspace/tree/feat/exp-eb/experiments/results/runs)을 근거로 삼되, 최신 실행 상태는 은빈이 갱신합니다. 사용자 보고상 실험 진행 중이며 이 레포에서 GPU 실행 완료나 오류율을 확인한 것은 아닙니다.

- 실행 중인 checkout에 main을 통째로 합치거나 서버·prompt·parser를 교체하지 않습니다. 이 배정 문서와 템플릿은 별도 checkout에서 확인하고 추가 실행을 준비합니다. 기존 source hash와 재개 디렉토리를 유지합니다.
- 브랜치에는 BF16 사용 사유가 기록돼 있습니다. 기존 run을 FP16으로 바꾸지 않습니다. 추가 모델도 실제 지원 여부를 확인한 명시적 dtype을 기록합니다. FP16 기본 권장에 대한 BF16 선택은 모델별 근거를 남기며, 자동 dtype/양자화는 피합니다.
- 실제 모델·tokenizer commit, chat template hash, vLLM/Transformers 버전, GPU·TP·dtype·서버 한도를 기록합니다. 동일 기계에서 동시에 서빙할 수 있다고 가정하지 않습니다. Qwen 9B 양 조건을 먼저 마친 뒤 Kanana 8B로 넘어가도 됩니다.

## 설정·계측·cohort

1. [runbook](experiment-runbook.md)을 따릅니다. `qwen-9b.example.json`, `kanana-8b.example.json`을 각 `.local.json`으로 복사하고 실제 endpoint·revision·한도·자원 배정을 채웁니다. 예제 포트는 배포 사실이 아닙니다. 새 run ID와 디렉토리를 사용합니다.
2. 기존 동결된 요청, core/halo/output cap, 추출 prompt, 채점 기준을 사용합니다. 모델별 reasoning/template 설정은 별도 pilot에서 호환성을 확인하고 명시하며 두 조건에서 동일하게 사용합니다. 본 데이터에서 본 형식 오류를 근거로 prompt·JSON 강제 디코딩·토큰 예산을 추가 모델에만 개선하지 않습니다. 그런 변경은 별도 프로토콜 결정이 필요합니다.
3. 기존 `matrix.example.json`은 3모델×2조건 그대로 둡니다. `matrix.extended.example.json`은 5모델×2조건의 **추가 계측/공통 집합 검토용**입니다. 기존 counts는 config/source/data가 정확히 일치할 때만 재사용합니다. 새 모델은 실제 chat framing을 포함하는 네이티브 계측을 수행합니다.
4. gate 생성 전에 runbook의 preflight 절차로 모든 모델·양 조건의 eligible 문서 ID 교집합을 확인합니다. 한도 초과 시 제외 내역을 기록하고, 별도 준비 경로에 같은 교집합을 두 조건 모두 적용한 뒤 모든 모델을 다시 계측합니다. 기존 gate·plan·result·해시를 덮어쓰지 않습니다. 전 항목이 통과한 뒤 별도 경로에 확장 gate를 생성합니다. gate는 ID 목록을 직접 담지 않으므로 원래/새 plan의 문서 목록·해시와 제외 보고서도 함께 비교·보관합니다. 검토된 확장 gate로 새 모델 실행을 시작합니다.
5. **현재 exporter는 서로 다른 gate 해시의 LLM 결과를 합치지 않습니다.** 문서가 같더라도 기존 run에 새 gate를 끼워 넣지 않습니다. 확장 결과는 먼저 별도 표로 공유합니다. 통합표는 원본 provenance를 보존하는 별도 공통 cohort 재집계 절차를 검토한 뒤 만듭니다. 필요하면 기존 저장 예측을 교집합으로 재채점하되 원본 결과·게이트는 보존하고, 이 절차가 아직 구현·검증되었다고 가정하지 않습니다. 기존 추론을 자동 재실행하지 않습니다.
6. `src.eval.execute`로 실행하고 모델/조건별 완료 결과를 GitHub에 공유합니다. 새 유료 서비스·GPU 임대가 필요하면 실제 자원/예산은 운영자가 배정합니다. 과거 생성 예산을 쓰지 않습니다.

## 형식 오류와 응답 전문 보존

사용자 요청대로 **성공·실패 모두 수신한 응답 전문**을 보존합니다. JSON 추출/정리 이전의 completion 텍스트와 공급자 응답 JSON(content, 제공되는 reasoning 필드, finish_reason, usage 포함)을 request ID·조건·run ID와 연결합니다. 설명문·코드펜스·잘린 JSON을 삭제하거나 성공한 응답만 보관하지 않습니다. HTTP 실패는 수신한 오류 본문과 상태도 안전하게 보관하고, timeout 등 수신하지 못한 내용은 '미수신'으로 기록합니다. 비밀키·인증 헤더는 저장/공유하지 않습니다.

현재 main 실행기는 정상적으로 공급자 응답을 정규화하면 raw/text를 보존하지만, 정규화 예외에서는 원문이 남지 않을 수 있습니다. 브랜치의 nullable usage 수정도 이와 관련된 어댑터 문제입니다. **전체 수신 응답이 이미 보존된다고 단정하지 말고**, 실행 중인 버전과 서버 로그에서 보존 여부를 확인합니다. 원문이 없으면 같은 요청을 다시 보내 복원하지 않습니다. 추가 로깅 패치가 필요하면 별도 버전·새 run 또는 명시적 인계 절차로 처리하고 진행 중인 source hash를 바꾸지 않습니다.

사라에게 전달할 진단에서는 다음을 구분합니다. 이는 새 채점 규칙이 아니라 원인 분류입니다.

- 모델 출력: JSON 문법/설명문·펜스, schema, category, 인용/occurrence/core 범위 위반.
- 출력 잘림: finish reason, 실제 출력 토큰, reasoning이 출력 예산을 사용했는지.
- 인프라/어댑터: HTTP/timeout, 응답 정규화 오류, 수신 여부 불명.

실패 요청은 본 strict 평가에서 빈 예측으로 남겨 gold FN을 유지합니다. 오류 분류의 분모는 전체 예정 요청이며 제외·실패·미수신 건수를 함께 보고합니다. 성공한 요청만의 성능을 본 성능으로 대체하지 않습니다. 부분 점수는 푸시하지 않으며 중간에는 진행·장애 기록만 올립니다. 원문/저널은 [결과 공유 규칙](../../experiments/results/README.md)에 따라 압축·해시·Release asset 링크로 공유합니다.

## 분석 범위

핵심 6시스템·9조건은 유지하고 확장 완료 시 총 8시스템·13조건입니다. 소형 모델의 오류 보고를 들은 뒤 추가했다는 시점을 기록합니다. 사라는 실패율과 full/local 차이를 함께 해석하고, 소형 모델을 나쁜 결과 때문에 빼지 않습니다. 4페이지 본문은 간결한 비교표와 문맥 효과 그림에 집중하고 모델별 응답 사례·오류 세부표는 저장소에 둡니다.
