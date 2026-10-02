# Kiii-Kiii · Kiii²

> **2026-10-02 / SAC 2027 AIFT 제출 완료 #362:** [최종 원고](papers/sac2027/README.md)와 [검증된 접수 기록](docs/submissions/sac2027.json). 리뷰 관점의 마지막 수정과 AI 사용 고지를 반영한 8쪽 PDF·초록을 갱신했고, 제출본 재다운로드 검증을 완료했습니다. 기존 workshop #11과 독립된 제출이며 추가 추론은 없습니다.

> **2026-10-01 최종 범위 (ADR-0038): 추가 추론을 중단하고 완료 결과로 집필합니다.** LLM 12종·22조건 + baseline 3종 = **15시스템·25조건**. 성현의 Gemma 5종 양 조건과 은빈의 Qwen3-30B/EXAONE을 포함합니다. Qwen 2B local·4B full은 pilot-only라 제외합니다. [완료 결과/설정/통계](experiments/results/analyses/1001-completed-manuscript-v1/REPORT.md). 아래 과거 실행 계획은 새 실험 지시가 아닙니다.

**Korean Identifiers, Identifiability, and Ill-formed Inputs — A Regulation-Grounded Benchmark for Financial PII Detection.**

한국 금융 문서의 개인정보 탐지를 평가하는 연구 저장소입니다. 법령 기반 36개 카테고리, 표면형 변형 T0–T3, 다중 정보주체·긴 문서를 다룹니다. **데이터와 완료 실험의 검증을 마쳤고, 현재는 결과 기반 논문 집필 단계입니다. Native 계측 원본 부재 등 검증 한계는 공개하며 추가 실행은 하지 않습니다.**

- 공개 데이터: [nmixx-fin/kiii-kiii](https://huggingface.co/datasets/nmixx-fin/kiii-kiii), **1,440문서 / 218,664스팬**, 단일 `test`.
- 라이선스: **데이터 CC BY-NC 4.0**. Preview 버전이며 정식 버전은 추후 공개합니다. 코드·제3자 모델의 라이선스를 이 데이터 라이선스로 대체하지 않습니다.
- 실험 데이터 고정 revision: `2df0589d695c18665fd83d4ca5512e03ca0767f6`.
- 준비한 비교군: Qwen3.5-2B, Qwen3.5-4B, Kanana-2-3B-Instruct + Presidio, ko-pii, OpenMed. 이름은 계획이며 **실제 접근 가능한 모델 ID·revision은 실행 담당자가 확인**합니다.
- GLM/Astra는 데이터 생성기이므로 본 탐지 리더보드에서 제외합니다. 학습·validation 분할이나 이 데이터로 학습하는 베이스라인은 없습니다.

> **9/24 확정 (ADR-0034):** 소형 로컬 LLM 3개와 기존 baseline 3개로 실행합니다. [선정 근거](docs/research/small-model-roster-2026-09-24.md). Claude·대형 MoE는 현 범위에서 제외하고 Gemini는 별도 승인 전까지 보류합니다.

> **9/26 추가 배정 (ADR-0035):** 은빈에게 Qwen3.5-9B → Kanana 1.5 8B 양 조건을 추가 배정했습니다. 기존 핵심 9조건은 유지하고 확장 4조건은 별도 실행합니다(완료 시 총 8시스템·13조건). [추가 모델·응답 전문 보존·진행 중 브랜치 인계](docs/guide/eunbin-medium-extension.md).

## 모델별 담당자와 결과 공유

**핵심 LLM 3개 × 두 조건 + baseline 3개 = 9개 실행 조건**입니다. [담당 배정표](experiments/ASSIGNMENTS.md)에 모델별 담당자·상태·결과 링크를 관리합니다. **은빈: Qwen 2B·4B / Kanana 3B / OpenMed, 한울: Presidio·ko-pii**로 배정했습니다. 성현의 API 실행은 보류입니다. 사라는 **문맥 효과의 가설·통계 분석·오류 해석·결과/논의 집필**을 맡습니다. [사라/에이전트 시작 문서](docs/research/sara-context-analysis.md)에 즉시 할 작업과 4페이지 범위를 정리했습니다. 운영 취합 담당자는 미정입니다. Qwen·Kanana는 FP16 + vLLM 계열 서빙 후 API 연결을 권장하며, OpenMed는 별도 Transformers GPU 경로를 사용합니다.

**각 담당자는 모델·조건별 완료 결과를 이 GitHub 레포에 커밋·푸시합니다.** 위치와 제출 규칙은 [결과 공유 가이드](experiments/results/README.md)를 따릅니다. 중단 시에도 진행 기록과 장애를 푸시하며 부분 점수는 최종 결과로 공유하지 않습니다.

## 실험을 맡은 분 / 에이전트는 여기서 시작

1. [AGENTS.md](AGENTS.md): 연구 결정과 작업 규칙.
2. [실험 실행 가이드](docs/guide/experiment-runbook.md): 설치 → 데이터 → 별도 파일럿 → 토큰 계측 → 공통 평가 집합 고정 → 실행·재개 → 결과.
3. [현재 상태](STATUS.md), [인수인계](docs/HANDOFF.md): 완료된 것, 아직 확인할 것.
4. [프로토콜](docs/guide/evaluation.md), [모델별 설정 예시](experiments/configs/evaluation/), [베이스라인 매핑](experiments/label_maps/README.md).

담당자가 에이전트에게 그대로 전달할 요청:

> 이 레포의 AGENTS.md와 docs/guide/experiment-runbook.md를 읽고 실험 환경을 준비해줘. 공개된 고정 revision 데이터로 설치·오프라인 테스트·연결 점검을 수행하고, 별도 파일럿에서 설정을 고정해줘. 모델별 실제 ID, endpoint, revision, 토큰 한도, 단가와 배정 예산을 확인한 뒤 모든 모델·두 조건의 공통 평가 집합을 고정해줘. 키는 환경변수로만 받고, 기존 완료 요청은 다시 호출하지 마. 본 실행 전에 예상 비용과 확정 설정을 알려주고, 내가 승인한 예산 안에서 실행·재개·채점해줘. experiments/ASSIGNMENTS.md에서 내 담당 모델을 확인하고, 완료 결과와 재현 자료를 experiments/results/에 정리해 GitHub에 커밋·푸시해줘. 중단 시 진행 기록도 공유해줘. 논문 수치를 추정하거나 smoke 결과를 리더보드에 넣지 마.

## 빠른 로컬 검증

Python 3.12, Linux/macOS 기준입니다. API 실행기는 표준 라이브러리를 사용하며 GPU가 필요 없습니다. Qwen/Kanana는 별도 추론 서버, OpenMed는 별도 모델 실행 환경이 필요합니다.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-eval.txt
python -m pytest tests -q
```

기존 `.venv`가 uv로 만들어져 pip가 없다면 `uv pip install --python .venv/bin/python -r requirements.txt -r requirements-eval.txt`를 사용합니다. 이 검증은 유료 모델을 호출하지 않습니다. 코드 다운로드만 필요하면 paper submodule을 초기화하지 않아도 됩니다.

## 저장소 지도

| 경로 | 역할 |
|---|---|
| `src/analysis/` | 원본 strict를 보존하는 사후 응답 분해·문자 부분점수 |
| `src/eval/` | 데이터 로드, 고정 요청, 공급자 어댑터, 토큰 계측, 예산·재개, 베이스라인, 채점·CSV |
| `experiments/configs/evaluation/` | 키 없는 설정 템플릿, 핵심 3모델/확장 포함 5모델 × 2조건 capacity matrix |
| `experiments/label_maps/` | 소스 라벨 → 36개 택소노미, 제외 라벨 명시 |
| `taxonomy/taxonomy.yaml` | 카테고리·변형 정의의 원본 |
| `src/generate/` | 완료된 합성 생성 파이프라인; 실험 담당자는 재생성하지 않음 |
| `docs/decisions/` | ADR: 최근 결정이 이전 결정을 대체 |
| `literature/`, `docs/related_work.md` | 선행연구·BibTeX; TWICE/NMIXX 포함 |
| `paper/` | 별도 git submodule, Overleaf 연결 논문 |
| `experiments/results/` | 완료한 CPU baseline 결과·원본 예측; 통합 리더보드는 공통 cohort 확정 후 |

데이터 본문·키·개인 접속 설정은 git에 넣지 않습니다. `experiments/runs/`는 로컬 재개용으로 보존하고, 최종 결과·재현 메타데이터는 `experiments/results/`에 복사해 푸시합니다. 큰 raw 응답·저널은 같은 GitHub 레포의 Release asset으로 공유하고 결과 보고서에 링크·해시를 남깁니다. Overleaf 코멘트를 보존해야 하므로 논문 파일을 통째로 교체하거나 무조건 동기화하지 않습니다.

> **9/27 보조 분석 (ADR-0036):** [응답 분해·부분점수 가이드](docs/guide/response-diagnostics.md). 공식 strict 점수는 보존하며, 저장된 완료 응답만으로 항목별 유효 추출·코드펜스 처리·카테고리별 문자 겹침을 따로 평가합니다. 사후 탐색적 분석이며 추론 코드는 변경하지 않습니다. [완료 3조건 분석](experiments/results/analyses/0927-response-diagnostics-v1/REPORT.md)과 [세부 CSV](experiments/results/analyses/0927-response-diagnostics-v1/tables/breakdowns.csv)를 제공합니다.

> **추가 업로드 검토 (`ac25513`):** [Qwen 4B local 1,440건 결과·부분점수](experiments/results/analyses/0927-response-diagnostics-v1-update-ac25513/REPORT.md)를 확인했습니다. Qwen 4B full과 Qwen 2B local의 현재 업로드는 여전히 pilot이며 native count/cohort 자료 보완이 필요합니다.

> **논문 결과표 준비:** [표별 입력·검증·편집 안내](docs/guide/paper-results-handoff.md). 본문 비교표와 부록 L/I 분해·paired CI·보조 점수표를 Overleaf에 준비했습니다. 최종 비교는 공통 cohort 검증 후 채웁니다.

> **9/28 확장 4조건 검토 (`24a3595`):** [공식 점수 재현·부분점수·중복 JSON 키 진단](experiments/results/analyses/0928-response-diagnostics-v1-update-24a3595/REPORT.md). Qwen 9B는 1,440건, Kanana 8B는 길이 한도로 2건을 제외한 1,438건입니다. 서로 다른 gate 결과를 통합 순위로 합치지 않습니다.

> **10/1 실패 분해 (ADR-0037):** [12개 완료 LLM 조건의 형식 준수·빈 답·탐지 P/R/F1](experiments/results/analyses/1001-failure-decomposition-v1/tables/REPORT.md)과 [전체 정답 기준 누락 유형 그림](experiments/results/analyses/1001-failure-decomposition-v1/figures/gold-outcomes.png). 공식 strict와 기존 항목별 점수는 유지합니다. 추가 Qwen3-30B/EXAONE 결과도 별도 관측 자료로 포함하며 기존 배정 범위는 바꾸지 않습니다.
