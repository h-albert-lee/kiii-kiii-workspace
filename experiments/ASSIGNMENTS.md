# 실험 담당 배정표

## 최종 집필 범위 — 2026-10-01 / ADR-0038

추가 실행 없이 완료 결과로 마감합니다. **15시스템·25조건**. 아래 기존 계획은 이 결정으로 대체됩니다. [전체 결과와 재현 근거](results/analyses/1001-completed-manuscript-v1/REPORT.md).

| 담당 | 완료하여 포함하는 결과 | 제외/특기 |
|---|---|---|
| 성현 | Gemma 4 E2B, E4B, 12B, 26B-A4B, 31B 각 full/local (10조건) | 31B FP8; 외부 runner·서버/decoding 차이 공개 |
| 은빈 | Kanana 3B/8B, Qwen 9B/30B, EXAONE 33B 각 full/local; Qwen 2B full·4B local; OpenMed (13조건) | Qwen 2B local·4B full pilot 제외; Kanana8B 1,438건 |
| 한울 | Presidio, ko-pii (2조건) | 각 1,440건 |
| 사라 | 완료 결과의 문맥 효과·해석·원고 검토 | 기존 연구 담당 유지; 중복 추론 없음 |

원본 결과/strict 점수는 보존합니다. 새 표는 기존 공통 gate exporter를 우회한 결과가 아니라, 실행 블록·검증 한계를 명시한 완료 결과 스냅샷입니다.

## 이전 배정 및 실행 기록

2026-10-01 (ADR-0034/0035/0036/0037). **사용자 확정 배정: API 실행은 보류(기존 담당 성현), GPU 실험은 은빈, GPU 불필요 규칙 베이스라인은 한울, 문맥 효과 연구는 사라.** GitHub ID는 각 담당자가 기입합니다. 담당자는 착수 전에 상태와 run ID를 커밋·푸시합니다. 취합 담당자는 별도 지정 전까지 미정입니다.

| 묶음 | 계획 모델 | 실행 조건 | 담당자 / GitHub ID | 상태 | run ID / 결과 링크 |
|---|---|---|---|---|---|
| B · GPU LLM | Qwen3.5-2B | full_context_targeted + local_window | 은빈 | full 1,440건 재현 검증; local 업로드는 10건 pilot | [feat/exp-eb 기록](https://github.com/h-albert-lee/kiii-kiii-workspace/tree/feat/exp-eb/experiments/results/runs) · 0925-03/04-qwen-2b-full/local |
| B · GPU LLM | Qwen3.5-4B | full_context_targeted + local_window | 은빈 | full 업로드는 10건 pilot; local 1,440건 재현 검증 | [feat/exp-eb 기록](https://github.com/h-albert-lee/kiii-kiii-workspace/tree/feat/exp-eb/experiments/results/runs) · 0925-05/06-qwen-4b-full/local |
| B · GPU LLM | Kanana-2-3B-Instruct | full_context_targeted + local_window | 은빈 | full/local 각 1,440건 재현 검증; native 계측/gate 원본 확인 대기 | [feat/exp-eb 기록](https://github.com/h-albert-lee/kiii-kiii-workspace/tree/feat/exp-eb/experiments/results/runs) · 0925-01/02-kanana-3b-full/local |
| C · CPU 베이스라인 | Presidio 한국형 규칙 + 계좌·카드 규칙 | 동일 평가 문서 전체, 1회 | 한울 | 1,440건 완료·공통 cohort 재집계 대기 | [0924-01-presidio-full1440](results/runs/0924-01-presidio-full1440/REPORT.md) |
| C · CPU 베이스라인 | ko-pii 1.16.0 | 동일 평가 문서 전체, 1회 | 한울 | 1,440건 완료·공통 cohort 재집계 대기 | [0924-01-ko-pii-full1440](results/runs/0924-01-ko-pii-full1440/REPORT.md) |
| B · GPU 베이스라인 | OpenMed/privacy-filter-multilingual | 동일 평가 문서, 겹침 토큰 창, 1회 | 은빈 | 1,440건 완료·예측/점수 재현 검증; 공통 cohort 재집계 대기 | [0925-07-openmed-windows](https://github.com/h-albert-lee/kiii-kiii-workspace/blob/feat/exp-eb/experiments/results/runs/0925-07-openmed-windows/REPORT.md) |
| B+ · GPU 확장 1순위 | Qwen3.5-9B | full_context_targeted + local_window | 은빈 | full/local 각 1,440건 재현 검증; native 계측/gate 대기 | 0926-01/02-qwen-9b-full/local · [검토](results/analyses/0928-response-diagnostics-v1-update-24a3595/REPORT.md) |
| B+ · GPU 확장 2순위 | Kanana-1.5-8B-Instruct-2505 | full_context_targeted + local_window | 은빈 | full/local 각 1,438건 재현 검증; 2건 길이 제외·별도 gate | 0926-03/04-kanana-8b-full/local-1438 · [검토](results/analyses/0928-response-diagnostics-v1-update-24a3595/REPORT.md) |
| B+ · GPU 확장 (Gemma) | Gemma 4 instruct 5종 (E2B / E4B / 12B / 26B-A4B / 31B-FP8) | full_context_targeted + local_window | 김성현 / MrBananaHuman | 5모델 × 2조건 각 1,440건 완료; 레포 scorer 재채점 일치; 별도 gate(`cohort-gemma4`) | 0928-01~04 · 0929-05-gemma4-*-full/local · [cohort](results/cohorts/cohort-gemma4/REPORT.md) · 브랜치 `feat/exp-gemma` |
| D · 취합 | 공통 설정·평가 집합 확정 / 결과 통합 | 전체 모델 계측 취합, cohort gate, CSV·bootstrap | 미정 | 미착수 | — |
| E · 연구 분석 | 전체 문맥 대 지역 문맥 효과 | 가설·통계·오류 분석·표/그림·결과/논의 집필 | 사라 | 배정 완료·착수 전 | [시작 문서](../docs/research/sara-context-analysis.md) |

기존 핵심은 **6개 시스템, 9개 실행 조건**입니다(LLM 3×2 + baseline 3×1). 이름은 계획 모델명이며 served model ID·revision·접근 가능 여부는 각 담당자가 확인합니다. 임의로 다른 모델로 바꾸지 않습니다. GLM/Astra는 생성기이므로 헤드라인 탐지 실험에서 제외합니다. 본 데이터로 학습하는 baseline도 없습니다.

ADR-0035 확장은 2개 LLM × 두 조건을 추가하여 완료 시 **총 8개 시스템, 13개 조건**입니다. 기존 run/gate를 교체하지 않습니다. 서로 다른 gate의 결과는 현재 exporter로 합칠 수 없으므로 확장 결과는 별도 공유하고 통합 cohort 분석은 별도 검토합니다. 상세 절차는 [은빈 인계 문서](../docs/guide/eunbin-medium-extension.md)를 따릅니다.

사라는 [문맥 효과 연구 작업 문서](../docs/research/sara-context-analysis.md)를 따라 결과가 없어도 분석 계획·코드부터 시작합니다. 핵심 9개 조건과 이번에 승인된 확장 4개 조건의 완료 결과를 활용합니다. 사라가 별도 추론을 중복 실행하지 않습니다. 운영 취합 담당과 별도의 연구 책임입니다.

**보류:** 성현 담당 Gemini는 선택 기준점으로 남기되 별도 범위·예산 승인 전에는 실행하지 않습니다. Claude 및 기존 대형 Qwen/Kanana는 이번 범위에서 제외합니다. 성현에게 다른 업무를 임의 배정하지 않습니다. 과거 실행이 있다면 삭제하지 않고 이전 조건으로 보존합니다.

## GPU 실행 권장 방식

- **은빈 — Qwen/Kanana:** FP16을 기본 권장 정밀도로 삼고, vLLM 등으로 모델을 서빙한 뒤 평가 실행기를 OpenAI-compatible API에 연결합니다. 현재 어댑터는 `/v1/chat/completions`와 실제 chat template을 적용하는 `/tokenize`를 사용합니다. 다른 서버도 이 계약을 충족하는지 먼저 확인합니다.
- 모델 아키텍처·GPU·서버 버전의 FP16 지원과 메모리 여유는 별도 pilot에서 검증합니다. 자동 dtype이나 양자화로 조용히 바꾸지 않습니다. FP16이 지원되지 않거나 안정성 문제가 있으면 BF16 등 대안과 사유를 공유·기록한 뒤 설정을 확정합니다.
- **은빈 — OpenMed:** GPU 베이스라인도 담당합니다. 현재 구현은 Transformers token-classification 경로이며 vLLM chat API에 그대로 연결하는 모델이 아닙니다. 해당 경로로 실행하고 dtype·가중치 revision·GPU·창 크기를 기록합니다. LLM의 FP16 서빙 권장을 OpenMed에 자동 적용하지 않습니다.
- **한울 — Presidio/ko-pii:** CPU에서 실행합니다.

## 역할과 전달 순서

1. **각 실행 담당자:** 모델 접근·배포 버전·한도·가격·배정 예산 확인, 별도 pilot에서 연결/출력 검증, 공유 설정으로 두 조건 계측. 설정/계측/진행 기록을 GitHub에 전달합니다. API 키는 전달하지 않습니다.
2. **취합 담당자:** 공동 pilot 설정 고정, 모든 LLM·두 조건의 계측 취합, 공통 eligible 문서와 cohort gate 확정. 확정된 데이터/요청 해시와 gate를 GitHub로 공유합니다. 각자 다른 집합으로 먼저 본 추론을 시작하지 않습니다.
3. **각 실행 담당자:** 승인된 예산으로 본 실행·재개·채점. 완료할 때마다 [결과 공유 규칙](results/README.md)에 따라 해당 run을 커밋·푸시하고 이 표의 링크를 갱신합니다. 진행 중이면 진행 상태만 공유하고 부분 점수를 최종 성능처럼 올리지 않습니다.
4. **취합 담당자:** 결과 해시·완료 상태·실패율·공통 집합 확인, 전체 CSV/paired bootstrap 생성 후 푸시. 담당자별 결과를 덮어쓰지 않습니다.

상태: 미착수 → 환경 준비 → pilot → 계측 완료 → 공통 집합 확정 → 본 실행 → 완료 / 중단(사유 기록).

모델별 담당자가 정해지면 이 표를 먼저 갱신합니다. 새로운 실행 ID는 날짜와 작업 식별자를 함께 쓰고(예: `0924-01-claude-full`), 다른 담당자의 경로를 재사용하지 않습니다.

9/27: 위 업로드 상태는 `feat/exp-eb@b4f76f4` 기준입니다. [완료 3조건의 응답 분해·부분점수](results/analyses/0927-response-diagnostics-v1/REPORT.md)를 공유했습니다. strict 원본은 그대로이며, native 계측/cohort 원본·담당자 환경 기록과 나머지 본 실험 결과의 제출은 계속 필요합니다. 파일럿 업로드를 본 실험 완료로 집계하지 않습니다.

추가 검토 `ac25513`: [Qwen 4B local 완료 및 보조 점수](results/analyses/0927-response-diagnostics-v1-update-ac25513/REPORT.md). 기존 9/27 `b4f76f4` snapshot 이후 이 조건이 추가됐습니다. 운영 상태표는 현재 업로드를 기준으로 하며 실제 실행 중인 미업로드 작업의 상태는 추정하지 않습니다.

9/28 `24a3595`: 확장 4조건 완료 응답·공식 점수를 재현했습니다. 위 표는 최신 업로드 기준입니다. native count/최종 gate 원본 및 남은 핵심 3조건 완료 자료는 계속 확인 대기이며, Qwen 9B와 Kanana 8B의 평가 문서 수와 gate 차이를 보존합니다. 중복 JSON 키 처리 한계는 새 검토 보고서에 기록했습니다.

10/1 `9e0570a`: OpenMed 전체 완료를 검증해 기존 계획은 11/13조건의 완료 업로드를 확인했습니다. Qwen3-30B-A3B와 EXAONE 4.5 33B full/local도 추가 업로드됐으나 기존 배정표 밖의 운영자 추가 실험으로 보존합니다. 논문 포함 범위를 자동 확대하지 않습니다. [형식·위치 지정·탐지 성능 분해](results/analyses/1001-failure-decomposition-v1/tables/REPORT.md)는 완료 LLM 12조건 전체의 사후 진단이며 사라의 연구 분석에 사용할 수 있습니다.
