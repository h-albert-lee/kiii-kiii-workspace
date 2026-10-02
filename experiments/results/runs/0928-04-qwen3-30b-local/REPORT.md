# Experiment report — 0928-04-qwen3-30b-local

- 담당자 / GitHub ID: 은빈 / <REPLACE_GITHUB_ID>. 실행 지원: Claude Code.
- 상태: **완료** (전체 요청 실행·finalize 완료). **배정표·ADR에 없는 추가 모델**(운영자 요청, 2026-09-28). ADR-0034는 "대형 MoE는 현 범위에서 제외"로 정하고 있으므로 공유·논문 사용 전 범위 결정(ADR·배정표) 필요. 공통 cohort 재집계 전.
- 계획 모델 / 실제 served ID / 모델 revision: Qwen3-30B-A3B (MoE, 128 experts) / `Qwen/Qwen3-30B-A3B` / `ad44e777bcd18fa416d9da3bd8f70d33ebb85d39` (tokenizer 동일 commit). 라이선스 apache-2.0
- 조건: local_window (짝 실행: `0928-03-qwen3-30b-full`)
- 시작·종료 시각 / timezone: 2026-09-28T16:02:46Z → 2026-09-29T03:04:02Z (UTC). 짝 조건과 같은 서버에서 동시 실행
- 코드 commit / source SHA 위치: 실행 worktree HEAD `b4f76f4b3cd1542f50980144baa9e6874c9a7d6a` (브랜치 `feat/exp-eb`). `source_sha256`은 run.json 참조 — **기존 Qwen/Kanana 핵심 실행과 동일함을 확인**
- 데이터 repo / revision / 평가 문서 수 / data SHA: nmixx-fin/kiii-kiii / `2df0589d695c18665fd83d4ca5512e03ca0767f6` / **1440문서, 13723요청** / data `d57b1cb0b8b67fe48a9b45ee985fb01e63b919147a8527f8231459a68b57456d`, requests `b526cef377a0d4e42be1bdc7bfc881b05f8602d2f85847d8fa130bd5ecedfeed` (manifest.json)
- 공통 cohort ID / gate 링크: `cohort-qwen3-30b.json` (Qwen3.5-2B/4B + Kanana-2-3B + Qwen3-30B-A3B × 두 조건, 1,440문서, 제외 없음); run.json `cohort_sha256` `aa82fe0f98d8d2758fa9be39a5bb5a25df45cd349659a6cf0bbb2acb2abc0c8b`. **핵심 run과 다른 gate이므로 현재 exporter로 합치지 않음**
- tokenizer / chat template / server revision: 모델과 같은 commit / `tokenizer_config.json` chat_template SHA-256 `a55ee1b1660128b7…` / vLLM 0.30.0 (Transformers 5.17.0, torch 2.13.0+cu130)
- core / halo / 최대 출력 / sampling / reasoning 설정: core 1,200자 / halo 1,200자 / output 4,096토큰 (핵심 실행과 동일) / `chat_template_kwargs.enable_thinking=false` (generation·tokenize 동일, reasoning 토큰 0). **샘플링: 모델 generation_config(temperature 0.6, top_p 0.95, top_k 20)를 `--generation-config vllm`으로 끄고 vLLM 기본값 temperature 1.0 / top_p 1.0 사용** — 이전 LLM 전부와 같은 실효 샘플링을 맞추기 위한 의도적 선택이며 모델 권장값과 다름. 구조화 출력 없음
- 실행 환경 / dependency inventory / GPU(해당 시): Linux, Python 3.12, 평가 실행기 `.venv`; dependencies는 run.json. A100-SXM4-40GB × 4 (GPU 8–11), tensor parallel 2 × data parallel 2. concurrency 8, timeout 900초(config 해시 제외 운영 항목)
- 실제 dtype / 양자화 여부 / tensor parallel / 서버 실행 명령(키 제외): **BF16** / 양자화 없음 / TP 2 × DP 2 / `vllm serve Qwen/Qwen3-30B-A3B --revision ad44e777bcd18fa416d9da3bd8f70d33ebb85d39 --dtype bfloat16 --max-model-len 40960 --tensor-parallel-size 2 --data-parallel-size 2 --generation-config vllm --port 8032`
- 권장 FP16 대신 다른 설정을 사용했다면 사유: 공식 가중치가 BF16. 배포 정밀도를 따름. 양자화·자동 dtype 아님. `--max-model-len 40960`은 모델 config 기본값(`max_position_embeddings`), YaRN 등 문맥 확장 없음. 이 조건 최대 입력 9,263토큰 + 출력 4,096 ≤ 40,960
- 배정 예산 / 단가·확인일 / 사용·예약 비용 / 실제 청구 차이: 로컬 GPU, 유료 API 0 / 0 USD / 0 / 없음. 토큰 사용: 입력 103,554,748, 출력 7,118,744
- 완료 요청 또는 문서 수 / 전체 수 / 실패·uncertain 수: 13,723 / 13,723 요청 (status {'ok': 13071, 'failed': 652}, finish_reason {'stop': 13071, 'length': 652}; `failed`는 전부 출력 4,096토큰 도달). **실패 요청 10,337 (75.3%)**; 오류 항목 합계: JSON/스키마 176, 잘림 652, TARGET 밖 인용 94,904, core 밖 25,063, 라벨 3,385, 스키마 항목 44, occurrence 0. 실패 요청은 빈 예측·gold FN으로 유지
- **빈 응답 주의:** 채점을 통과한 요청 3,386개 중 **2,417개(71.4%)가 `{"spans":[]}`(예측 없음)**, 스팬을 낸 요청은 969개. 실패율이 낮게 보이는 것은 형식을 잘 지켜서가 아니라 빈 답이 규칙 위반 없이 통과하기 때문이므로, 실패율을 다른 모델과 비교할 때 함께 보고할 것
- 장애·중단·한계와 처리: 전송 오류·중단 없음. 호환성 pilot(별도 합성 30요청): 전송 오류 0, 계측 토큰 30/30 일치, thinking 0, 잘림 1. 설정이 pilot 보정 전 기본값이라 형식 실패가 많음 — `docs/reviews/2026-09-26-issue-*.md` 참조
- result.json 링크(전체 완료 후에만): `result.json` (이 폴더). Strict micro exact P=0.61176847, R=0.00874858, F1=0.01725047 (TP=1913, FP=1214, FN=216751). 공개·통합 리더보드용 최종 수치 아님
- 계측 / raw 응답·예측 / 비용 저널 artifact 링크와 SHA-256: 응답 원문 `responses.jsonl`, 예약 저널 `events.jsonl` (이 폴더; 20MiB 초과 파일은 결과 공유 규칙상 gzip/Release asset 대상). 계측 파일은 실행 worktree `experiments/runs/counts/qwen3-30b-*.jsonl` 보관
  - `events.jsonl` `d648d8a0a3aad9c0369ad8e62a71878aee8908ee4a84257c8fd83210b26ecb45`
  - `manifest.json` `04430b66fb1d61e344dc141dfafc72f80e83ed65f7b6fdad5e1734e1a813bcf0`
  - `progress.json` `dc9627e0f758cd5a3dc94165891efd6d9d0c876ea74aaa055fb8e76fc01e6323`
  - `responses.jsonl` `e1baa396ba5bf42fddc2264f11749ef567c04db2a1cce7f0a30512897414fdbb`
  - `result.json` `92090f9ce39ceb0a07dcb79907aac0d0d9bfb9994c1ee3f3b044d5a9abb6f840`
  - `run.json` `7d73fb53fc3c77986f04919b33987823fbe6a7e530e6c246be635024465e88da`
- 제외 문서/사유 및 설정 기록 위치: 없음. 1,440문서 전체
- 공유 시 가린 메타데이터 필드(없으면 없음): 없음. base_url은 `127.0.0.1` 로컬 주소, 키 없음
- 다음 담당자에게 필요한 작업: 범위 결정(ADR·배정표) 후 공유 여부 확정. 공통 cohort 재집계 절차 검토 전까지 핵심 결과와 **별도 표**로 보고

진행 중에는 부분 성능을 적지 않습니다. 최종 수치는 finalized result.json을 참조하고 추정하지 않습니다. 실패/불확실 요청과 과거 실행을 제거하지 않습니다.
