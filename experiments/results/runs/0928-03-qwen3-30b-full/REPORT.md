# Experiment report — 0928-03-qwen3-30b-full

- 담당자 / GitHub ID: 은빈 / <REPLACE_GITHUB_ID>. 실행 지원: Claude Code.
- 상태: **완료** (전체 요청 실행·finalize 완료). **배정표·ADR에 없는 추가 모델**(운영자 요청, 2026-09-28). ADR-0034는 "대형 MoE는 현 범위에서 제외"로 정하고 있으므로 공유·논문 사용 전 범위 결정(ADR·배정표) 필요. 공통 cohort 재집계 전.
- 계획 모델 / 실제 served ID / 모델 revision: Qwen3-30B-A3B (MoE, 128 experts) / `Qwen/Qwen3-30B-A3B` / `ad44e777bcd18fa416d9da3bd8f70d33ebb85d39` (tokenizer 동일 commit). 라이선스 apache-2.0
- 조건: full_context_targeted (짝 실행: `0928-04-qwen3-30b-local`)
- 시작·종료 시각 / timezone: 2026-09-28T16:02:46Z → 2026-09-29T04:28:15Z (UTC). 짝 조건과 같은 서버에서 동시 실행
- 코드 commit / source SHA 위치: 실행 worktree HEAD `b4f76f4b3cd1542f50980144baa9e6874c9a7d6a` (브랜치 `feat/exp-eb`). `source_sha256`은 run.json 참조 — **기존 Qwen/Kanana 핵심 실행과 동일함을 확인**
- 데이터 repo / revision / 평가 문서 수 / data SHA: nmixx-fin/kiii-kiii / `2df0589d695c18665fd83d4ca5512e03ca0767f6` / **1440문서, 13723요청** / data `d57b1cb0b8b67fe48a9b45ee985fb01e63b919147a8527f8231459a68b57456d`, requests `3542d46ed09a04f3ef09f2d6b368b756cf0bfe5746444fe3927aea39022e454f` (manifest.json)
- 공통 cohort ID / gate 링크: `cohort-qwen3-30b.json` (Qwen3.5-2B/4B + Kanana-2-3B + Qwen3-30B-A3B × 두 조건, 1,440문서, 제외 없음); run.json `cohort_sha256` `aa82fe0f98d8d2758fa9be39a5bb5a25df45cd349659a6cf0bbb2acb2abc0c8b`. **핵심 run과 다른 gate이므로 현재 exporter로 합치지 않음**
- tokenizer / chat template / server revision: 모델과 같은 commit / `tokenizer_config.json` chat_template SHA-256 `a55ee1b1660128b7…` / vLLM 0.30.0 (Transformers 5.17.0, torch 2.13.0+cu130)
- core / halo / 최대 출력 / sampling / reasoning 설정: core 1,200자 / halo 1,200자 / output 4,096토큰 (핵심 실행과 동일) / `chat_template_kwargs.enable_thinking=false` (generation·tokenize 동일, reasoning 토큰 0). **샘플링: 모델 generation_config(temperature 0.6, top_p 0.95, top_k 20)를 `--generation-config vllm`으로 끄고 vLLM 기본값 temperature 1.0 / top_p 1.0 사용** — 이전 LLM 전부와 같은 실효 샘플링을 맞추기 위한 의도적 선택이며 모델 권장값과 다름. 구조화 출력 없음
- 실행 환경 / dependency inventory / GPU(해당 시): Linux, Python 3.12, 평가 실행기 `.venv`; dependencies는 run.json. A100-SXM4-40GB × 4 (GPU 8–11), tensor parallel 2 × data parallel 2. concurrency 8, timeout 900초(config 해시 제외 운영 항목)
- 실제 dtype / 양자화 여부 / tensor parallel / 서버 실행 명령(키 제외): **BF16** / 양자화 없음 / TP 2 × DP 2 / `vllm serve Qwen/Qwen3-30B-A3B --revision ad44e777bcd18fa416d9da3bd8f70d33ebb85d39 --dtype bfloat16 --max-model-len 40960 --tensor-parallel-size 2 --data-parallel-size 2 --generation-config vllm --port 8032`
- 권장 FP16 대신 다른 설정을 사용했다면 사유: 공식 가중치가 BF16. 배포 정밀도를 따름. 양자화·자동 dtype 아님. `--max-model-len 40960`은 모델 config 기본값(`max_position_embeddings`), YaRN 등 문맥 확장 없음. 이 조건 최대 입력 35,726토큰 + 출력 4,096 ≤ 40,960
- 배정 예산 / 단가·확인일 / 사용·예약 비용 / 실제 청구 차이: 로컬 GPU, 유료 API 0 / 0 USD / 0 / 없음. 토큰 사용: 입력 263,310,176, 출력 8,689,641
- 완료 요청 또는 문서 수 / 전체 수 / 실패·uncertain 수: 13,723 / 13,723 요청 (status {'ok': 12596, 'failed': 1127}, finish_reason {'stop': 12596, 'length': 1127}; `failed`는 전부 출력 4,096토큰 도달). **실패 요청 6,239 (45.5%)**; 오류 항목 합계: JSON/스키마 157, 잘림 1,127, TARGET 밖 인용 110,650, core 밖 10,038, 라벨 3,003, 스키마 항목 33, occurrence 0. 실패 요청은 빈 예측·gold FN으로 유지
- **빈 응답 주의:** 채점을 통과한 요청 7,484개 중 **7,282개(97.3%)가 `{"spans":[]}`(예측 없음)**, 스팬을 낸 요청은 202개. 실패율이 낮게 보이는 것은 형식을 잘 지켜서가 아니라 빈 답이 규칙 위반 없이 통과하기 때문이므로, 실패율을 다른 모델과 비교할 때 함께 보고할 것
- 장애·중단·한계와 처리: 전송 오류·중단 없음. 호환성 pilot(별도 합성 30요청): 전송 오류 0, 계측 토큰 30/30 일치, thinking 0, 잘림 1. 설정이 pilot 보정 전 기본값이라 형식 실패가 많음 — `docs/reviews/2026-09-26-issue-*.md` 참조
- result.json 링크(전체 완료 후에만): `result.json` (이 폴더). Strict micro exact P=0.66824085, R=0.00258845, F1=0.00515692 (TP=566, FP=281, FN=218098). 공개·통합 리더보드용 최종 수치 아님
- 계측 / raw 응답·예측 / 비용 저널 artifact 링크와 SHA-256: 응답 원문 `responses.jsonl`, 예약 저널 `events.jsonl` (이 폴더; 20MiB 초과 파일은 결과 공유 규칙상 gzip/Release asset 대상). 계측 파일은 실행 worktree `experiments/runs/counts/qwen3-30b-*.jsonl` 보관
  - `events.jsonl` `dcc564f0990d974ee2dd2b39c2bd07a20c077cd1b1b0754675b56db7e9c7e445`
  - `manifest.json` `60823b68b860f6bc1ffd5d806c17ebeb860cb732c6f56a057e03795c2dc091e3`
  - `progress.json` `dc9627e0f758cd5a3dc94165891efd6d9d0c876ea74aaa055fb8e76fc01e6323`
  - `responses.jsonl` `9091165c53f99cd0febb876da356830420b901844aff6506050ea6bbaeeccc5b`
  - `result.json` `81bd7b428cf7b919b474419afcedf5fd3bf9946e598c70d20346c15d7c533ab0`
  - `run.json` `0db7f51e82d3eb809e81a46e84b6c3a3e3ac48f25b20c9474b86ad8fa4af8704`
- 제외 문서/사유 및 설정 기록 위치: 없음. 1,440문서 전체
- 공유 시 가린 메타데이터 필드(없으면 없음): 없음. base_url은 `127.0.0.1` 로컬 주소, 키 없음
- 다음 담당자에게 필요한 작업: 범위 결정(ADR·배정표) 후 공유 여부 확정. 공통 cohort 재집계 절차 검토 전까지 핵심 결과와 **별도 표**로 보고

진행 중에는 부분 성능을 적지 않습니다. 최종 수치는 finalized result.json을 참조하고 추정하지 않습니다. 실패/불확실 요청과 과거 실행을 제거하지 않습니다.
