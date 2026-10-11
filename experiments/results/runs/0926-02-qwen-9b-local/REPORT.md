# Experiment report — 0926-02-qwen-9b-local

- 담당자 / GitHub ID: 은빈 / <REPLACE_GITHUB_ID>. 실행 지원: Claude Code.
- 상태: **완료** (전체 요청 실행·finalize 완료). ADR-0035 확장 실험(탐색적). 공통 cohort 재집계 전.
- 계획 모델 / 실제 served ID / 모델 revision: Qwen3.5-9B / `Qwen/Qwen3.5-9B` / `c202236235762e1c871ad0ccb60c8ee5ba337b9a` (tokenizer 동일 commit)
- 조건: local_window (짝 실행: `0926-01-qwen-9b-full`)
- 시작·종료 시각 / timezone: 2026-09-26T21:26:11Z → 2026-09-27T05:22:58Z (UTC). 짝 조건과 같은 서버에서 동시 실행
- 코드 commit / source SHA 위치: 실행 worktree HEAD `b4f76f4b3cd1542f50980144baa9e6874c9a7d6a` (브랜치 `feat/exp-eb`; `src/eval`은 `757d707`의 nullable usage 수정 포함). `source_sha256`은 run.json 참조 — **기존 Qwen/Kanana 핵심 6개 실행과 동일함을 확인**
- 데이터 repo / revision / 평가 문서 수 / data SHA: nmixx-fin/kiii-kiii / `2df0589d695c18665fd83d4ca5512e03ca0767f6` / **1440문서, 13723요청** / data `d57b1cb0b8b67fe48a9b45ee985fb01e63b919147a8527f8231459a68b57456d`, requests `b526cef377a0d4e42be1bdc7bfc881b05f8602d2f85847d8fa130bd5ecedfeed` (manifest.json)
- 공통 cohort ID / gate 링크: `cohort-q9.json` (Qwen3.5-2B/4B/9B + Kanana-2-3B × 두 조건, 1,440문서); run.json `cohort_sha256` `c8233d6a240b5a69c24d5bd55d3ed844bb53c90fdaae2a9f34501bbbd75408b8`. 원래의 5모델 확장 gate는 Kanana-1.5-8B 한도 초과로 실패(아래 한계 참조)하여 gate를 1,440(Qwen-9B)/1,438(Kanana-8B)로 분리. **핵심 run과 다른 gate이므로 현재 exporter로 합치지 않음**
- tokenizer / chat template / server revision: 모델과 같은 commit / `chat_template.jinja` SHA-256 `a4aee8afcf2e0711…` / vLLM 0.30.0 (Transformers 5.17.0, torch 2.13.0+cu130)
- core / halo / 최대 출력 / sampling / reasoning 설정: core 1,200자 / halo 1,200자 / output 4,096토큰 (핵심 실행과 동일, pilot 보정 전 초안값) / `chat_template_kwargs.enable_thinking=false` (generation·tokenize 동일); temperature/top_p 미지정 → vLLM 기본값(1.0/1.0), 모델 generation_config 없음; 구조화 출력 없음. ADR-0035에 따라 **프롬프트·JSON 강제 디코딩·토큰 예산을 추가 모델에만 바꾸지 않음**
- 실행 환경 / dependency inventory / GPU(해당 시): Linux, Python 3.12, 평가 실행기 `.venv`; dependencies는 run.json. A100-SXM4-40GB × 6 (GPU 3–8), data parallel 6. concurrency 8, timeout 900초(두 값은 config 해시에서 제외되는 운영 항목)
- 실제 dtype / 양자화 여부 / tensor parallel / 서버 실행 명령(키 제외): **BF16** / 양자화 없음 / TP 1 (data parallel 사용) / `vllm serve Qwen/Qwen3.5-9B --revision c202236235762e1c871ad0ccb60c8ee5ba337b9a --dtype bfloat16 --max-model-len 262144 --data-parallel-size 6 --port 8021`
- 권장 FP16 대신 다른 설정을 사용했다면 사유: 공식 가중치가 BF16. 배포 정밀도를 따름. 양자화·자동 dtype 아님
- 배정 예산 / 단가·확인일 / 사용·예약 비용 / 실제 청구 차이: 로컬 GPU, 유료 API 0 / 0 USD / 0 / 없음. 토큰 사용: 입력 87,652,458, 출력 4,734,934, 지연 합계 21.3시간(요청 합산)
- 완료 요청 또는 문서 수 / 전체 수 / 실패·uncertain 수: 13,723 / 13,723 요청 (status {'ok': 13639, 'failed': 84}, finish_reason {'stop': 13639, 'length': 84}). **실패 요청 10,273 (74.9%)**; 오류 항목 합계: JSON/스키마 2,272, 잘림/실패 84, TARGET 밖 인용 45,511, core 밖 23,079, 라벨 4,466, 스키마 항목 2,872, occurrence 131. 실패 요청은 빈 예측·gold FN으로 유지
- 장애·중단·한계와 처리: 전송 오류·중단 없음. 호환성 pilot(별도 합성 30요청)에서 응답 원문 저장·계측 토큰 일치·thinking 미출력 확인. 설정이 pilot 보정 전 기본값(temperature 1.0, 구조화 출력 없음)이라 형식 실패가 많음 — `docs/reviews/2026-09-26-issue-*.md` 참조. 정규화 예외 시 원문이 남지 않는 경로가 있으나 이번 실행에서는 발생하지 않음(전 요청 수신·저장). Kanana 1.5 8B와 Kanana 2 3B는 세대가 달라 크기 효과로 해석하지 않음
- result.json 링크(전체 완료 후에만): `result.json` (이 폴더). Strict micro exact P=0.62655728, R=0.01885999, F1=0.03661774 (TP=4124, FP=2458, FN=214540). 공개·통합 리더보드용 최종 수치 아님
- 계측 / raw 응답·예측 / 비용 저널 artifact 링크와 SHA-256: 응답 원문 `responses.jsonl`, 예약 저널 `events.jsonl` (이 폴더; 20MiB 초과 파일은 결과 공유 규칙상 gzip/Release asset 대상). 계측 파일은 실행 worktree `experiments/runs/counts/` 보관
  - `events.jsonl` `e7357d05e8010326c18b4510376f86bcb69a0423aff47499fa6f1301f4fb97fc`
  - `manifest.json` `04430b66fb1d61e344dc141dfafc72f80e83ed65f7b6fdad5e1734e1a813bcf0`
  - `progress.json` `415b930733f0d99dc8a37bac990b474406bb27d4d3d333a87ca73e608b3eb33d`
  - `responses.jsonl` `0b3daef0e938f0dd16f49bc2e747d1f5f746c55b5d76dabb715d5d75509c1e25`
  - `result.json` `32b91f366181bf00cb6a88ea8dfbbd3e6f96a2973e577e9e1a416cac882c1c17`
  - `run.json` `cea64021c6799662527fe8b8b8ee121081f8a02bac07e889bcd1f69aa1698250`
- 제외 문서/사유 및 설정 기록 위치: 없음. 1,440문서 전체
- 공유 시 가린 메타데이터 필드(없으면 없음): 없음. base_url은 `127.0.0.1` 로컬 주소, 키 없음
- 다음 담당자에게 필요한 작업: 공통 cohort 재집계 절차(서로 다른 gate의 provenance 보존) 검토 전까지 핵심 결과와 **별도 표**로 보고. Kanana 중복 키 채점 이슈 결정 시 저장 응답으로 재채점

진행 중에는 부분 성능을 적지 않습니다. 최종 수치는 finalized result.json을 참조하고 추정하지 않습니다. 실패/불확실 요청과 과거 실행을 제거하지 않습니다.
