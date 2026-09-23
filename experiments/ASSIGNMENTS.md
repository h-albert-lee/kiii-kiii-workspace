# 실험 담당 배정표

2026-09-23. **사용자 확정 배정: API는 성현, GPU 실험은 은빈, GPU 불필요 규칙 베이스라인은 한울, 문맥 효과 연구는 사라.** GitHub ID는 각 담당자가 기입합니다. 담당자는 착수 전에 상태와 run ID를 커밋·푸시합니다. 취합 담당자는 별도 지정 전까지 미정입니다.

| 묶음 | 계획 모델 | 실행 조건 | 담당자 / GitHub ID | 상태 | run ID / 결과 링크 |
|---|---|---|---|---|---|
| A · API | Claude Sonnet 5 | full_context_targeted + local_window | 성현 | 미착수 | — |
| A · API | Gemini 3.8 Flash | full_context_targeted + local_window | 성현 | 미착수 | — |
| B · GPU LLM | Qwen3.6-35B-A3B | full_context_targeted + local_window | 은빈 | 미착수 | — |
| B · GPU LLM | Kanana2-30B-A3B-Instruct2601 | full_context_targeted + local_window | 은빈 | 미착수 | — |
| C · CPU 베이스라인 | Presidio 한국형 규칙 + 계좌·카드 규칙 | 동일 평가 문서 전체, 1회 | 한울 | 미착수 | — |
| C · CPU 베이스라인 | ko-pii 1.16.0 | 동일 평가 문서 전체, 1회 | 한울 | 미착수 | — |
| B · GPU 베이스라인 | OpenMed/privacy-filter-multilingual | 동일 평가 문서, 겹침 토큰 창, 1회 | 은빈 | 미착수 | — |
| D · 취합 | 공통 설정·평가 집합 확정 / 결과 통합 | 전체 모델 계측 취합, cohort gate, CSV·bootstrap | 미정 | 미착수 | — |
| E · 연구 분석 | 전체 문맥 대 지역 문맥 효과 | 가설·통계·오류 분석·표/그림·결과/논의 집필 | 사라 | 배정 완료·착수 전 | [시작 문서](../docs/research/sara-context-analysis.md) |

총 **7개 시스템, 11개 실행 조건**입니다(LLM 4×2 + baseline 3×1). 이름은 계획 모델명이며 served model ID·revision·접근 가능 여부는 각 담당자가 확인합니다. 임의로 다른 모델로 바꾸지 않습니다. GLM/Astra는 생성기이므로 헤드라인 탐지 실험에서 제외합니다. 본 데이터로 학습하는 baseline도 없습니다.

사라는 [문맥 효과 연구 작업 문서](../docs/research/sara-context-analysis.md)를 따라 결과가 없어도 분석 계획·코드부터 시작합니다. 기존 11개 조건을 활용하며 새 모델 실행을 추가하지 않습니다. 운영 취합 담당과 별도의 연구 책임입니다.

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
