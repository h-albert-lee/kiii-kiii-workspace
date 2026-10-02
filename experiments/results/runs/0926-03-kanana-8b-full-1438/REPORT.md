# Experiment report — 0926-03-kanana-8b-full-1438

- 담당자 / GitHub ID: 은빈 / <REPLACE_GITHUB_ID>. 실행 지원: Claude Code.
- 상태: **완료** (전체 요청 실행·finalize 완료). ADR-0035 확장 실험(탐색적). 공통 cohort 재집계 전.
- 계획 모델 / 실제 served ID / 모델 revision: Kanana-1.5-8B-Instruct-2505 / `kakaocorp/kanana-1.5-8b-instruct-2505` / `c963a5f4f6496c749f94064a20b33028b0db9f19` (tokenizer 동일 commit)
- 조건: full_context_targeted (짝 실행: `0926-04-kanana-8b-local-1438`)
- 시작·종료 시각 / timezone: 2026-09-26T21:49:51Z → 2026-09-27T19:28:28Z (UTC). 짝 조건과 같은 서버에서 동시 실행
- 코드 commit / source SHA 위치: 실행 worktree HEAD `b4f76f4b3cd1542f50980144baa9e6874c9a7d6a` (브랜치 `feat/exp-eb`; `src/eval`은 `757d707`의 nullable usage 수정 포함). `source_sha256`은 run.json 참조 — **기존 Qwen/Kanana 핵심 6개 실행과 동일함을 확인**
- 데이터 repo / revision / 평가 문서 수 / data SHA: nmixx-fin/kiii-kiii / `2df0589d695c18665fd83d4ca5512e03ca0767f6` / **1438문서, 13653요청** / data `f3062c1637dd2df7240cdd1b009482f8623d9fe5de320e459a4fcd2b58949139`, requests `3a5973ff136aae034911745a140969aa67821399c5c9df5b6a19fb772a761030` (manifest.json)
- 공통 cohort ID / gate 링크: `cohort-1438.json` (5모델 × 두 조건, 1,438문서, 전 모델 재계측); run.json `cohort_sha256` `d7077277a19e345a0cfd6aa0dc9b42c1fe38cb7ffe8f72f3c5f49e32e1db5a0b`. 원래의 5모델 확장 gate는 Kanana-1.5-8B 한도 초과로 실패(아래 한계 참조)하여 gate를 1,440(Qwen-9B)/1,438(Kanana-8B)로 분리. **핵심 run과 다른 gate이므로 현재 exporter로 합치지 않음**
- tokenizer / chat template / server revision: 모델과 같은 commit / `tokenizer_config.json` chat_template SHA-256 `42745fb34df3e367…` / vLLM 0.30.0 (Transformers 5.17.0, torch 2.13.0+cu130)
- core / halo / 최대 출력 / sampling / reasoning 설정: core 1,200자 / halo 1,200자 / output 4,096토큰 (핵심 실행과 동일, pilot 보정 전 초안값) / generation 설정 없음(`{}`, Kanana-2-3B와 동일); temperature/top_p 미지정 → vLLM 기본값(1.0/1.0), 모델 generation_config에 샘플링 값 없음; 구조화 출력 없음. ADR-0035에 따라 **프롬프트·JSON 강제 디코딩·토큰 예산을 추가 모델에만 바꾸지 않음**
- 실행 환경 / dependency inventory / GPU(해당 시): Linux, Python 3.12, 평가 실행기 `.venv`; dependencies는 run.json. A100-SXM4-40GB × 4 (GPU 9–12), data parallel 4. concurrency 8, timeout 900초(두 값은 config 해시에서 제외되는 운영 항목)
- 실제 dtype / 양자화 여부 / tensor parallel / 서버 실행 명령(키 제외): **BF16** / 양자화 없음 / TP 1 (data parallel 사용) / `vllm serve kakaocorp/kanana-1.5-8b-instruct-2505 --revision c963a5f4f6496c749f94064a20b33028b0db9f19 --dtype bfloat16 --max-model-len 32768 --data-parallel-size 4 --port 8022`
- 권장 FP16 대신 다른 설정을 사용했다면 사유: 공식 가중치가 BF16. 배포 정밀도를 따름. 양자화·자동 dtype 아님
- 배정 예산 / 단가·확인일 / 사용·예약 비용 / 실제 청구 차이: 로컬 GPU, 유료 API 0 / 0 USD / 0 / 없음. 토큰 사용: 입력 226,880,524, 출력 16,217,724, 지연 합계 74.8시간(요청 합산)
- 완료 요청 또는 문서 수 / 전체 수 / 실패·uncertain 수: 13,653 / 13,653 요청 (status {'ok': 12780, 'failed': 873}, finish_reason {'stop': 12780, 'length': 873}). **실패 요청 13,476 (98.7%)**; 오류 항목 합계: JSON/스키마 5,732, 잘림/실패 873, TARGET 밖 인용 195,238, core 밖 15,354, 라벨 12,925, 스키마 항목 8,509, occurrence 3,012. 실패 요청은 빈 예측·gold FN으로 유지
- 장애·중단·한계와 처리: 전송 오류·중단 없음. 호환성 pilot(별도 합성 30요청)에서 응답 원문 저장·계측 토큰 일치·thinking 미출력 확인. 설정이 pilot 보정 전 기본값(temperature 1.0, 구조화 출력 없음)이라 형식 실패가 많음 — `docs/reviews/2026-09-26-issue-*.md` 참조. 정규화 예외 시 원문이 남지 않는 경로가 있으나 이번 실행에서는 발생하지 않음(전 요청 수신·저장). Kanana 1.5 8B와 Kanana 2 3B는 세대가 달라 크기 효과로 해석하지 않음
- result.json 링크(전체 완료 후에만): `result.json` (이 폴더). Strict micro exact P=0.64260563, R=0.00167280, F1=0.00333691 (TP=365, FP=203, FN=217832). 공개·통합 리더보드용 최종 수치 아님
- 계측 / raw 응답·예측 / 비용 저널 artifact 링크와 SHA-256: 응답 원문 `responses.jsonl`, 예약 저널 `events.jsonl` (이 폴더; 20MiB 초과 파일은 결과 공유 규칙상 gzip/Release asset 대상). 계측 파일은 실행 worktree `experiments/runs/counts/` 보관
  - `capacity-all5-full_context_targeted.json` `2c42d945d50368262353f7fffc4d8d6704232f73801db09f774537726764c461`
  - `capacity-all5-local_window.json` `22c0d95a027125aeecf074a28c45d3b5203c21d89d3dc0fb91b76765ae7a3cb0`
  - `eligible-1438.json` `4f6545bdf5e76f452a9372c268096f3bd52a4d9dc75629ba16f8a19203886765`
  - `events.jsonl.gz` `ea14ce6730aab57ece5f27c0f87a68392fd7e2e9731e81e65fd5eb59705da6ac` (압축 전 `events.jsonl` `59f7b748d304b6dd9401444c14f11fa2cd9ee769f938773b3ec30950763e2861`; 원본 133MB/130MB가 GitHub 100MB 한도를 넘어 gzip -n -9)
  - `manifest.json` `6f1f786016c23c4bd44f3d675680d9f853069c94cfa414e07c4b5a179b9001a2`
  - `progress.json` `fac104f3b3345c64341dcc590e9b31518ebffff0ab693e2051c1c25bd33bfba0`
  - `responses.jsonl.gz` `2c7b16e1cb0103fd4b368ffc8601330a3695854a159df587107f9690004de271` (압축 전 `responses.jsonl` `1c21762737edea9fe8453ff6d65ff2bc17bc2e03aa8811c5bf39bafbb1bce901`; 원본 133MB/130MB가 GitHub 100MB 한도를 넘어 gzip -n -9)
  - `result.json` `f53688ed6e986a72a21258c3352cadef5e3a8e6a940755528c323fb2b510e206`
  - `run.json` `5e7119a41cffea5e31768fde3978df12d3cf9aca3d2e78024211bbb5bac881c6`
- 제외 문서/사유 및 설정 기록 위치: **2문서 제외**: `kiii-main-v2-00311`(loan_contract, 38,899자), `kiii-main-v2-01050`(kyc_form, 43,576자). Kanana-1.5-8B 토크나이저로 full 조건 68요청이 입력+출력 4,096 > 32,768. 5모델 preflight 결과 `capacity-all5-*.json`, 제외 후 ID 목록 `eligible-1438.json`(이 폴더). YaRN 등 문맥 확장·잘라내기 없이 두 조건 모두 같은 1,438문서로 새 plan 준비
- 공유 시 가린 메타데이터 필드(없으면 없음): 없음. base_url은 `127.0.0.1` 로컬 주소, 키 없음
- 다음 담당자에게 필요한 작업: 공통 cohort 재집계 절차(서로 다른 gate의 provenance 보존) 검토 전까지 핵심 결과와 **별도 표**로 보고. Kanana 중복 키 채점 이슈 결정 시 저장 응답으로 재채점

진행 중에는 부분 성능을 적지 않습니다. 최종 수치는 finalized result.json을 참조하고 추정하지 않습니다. 실패/불확실 요청과 과거 실행을 제거하지 않습니다.
