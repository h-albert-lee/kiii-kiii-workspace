# Experiment report — 0928-03-gemma4-12b-local

- 담당자 / GitHub ID: 김성현 / MrBananaHuman. 실행 지원: Claude Code.
- 상태: **완료** (전체 요청 실행·채점 완료). Gemma 4 instruct 확장 실험. 은빈 실행과 별도 cohort gate.
- 계획 모델 / 실제 served ID / 모델 revision: gemma-4-12B-it / `google/gemma-4-12B-it` / `707f0a3b8a3c7ad586ed01e27eafbad8a27dd0f7` (tokenizer 동일 commit)
- 조건: local_window (짝 실행: `0928-03-gemma4-12b-full`)
- 시작·종료 시각 / timezone: 2026-09-28T17:45:53Z → 2026-09-28T21:47:00Z (UTC). 짝 조건과 같은 서버에서 동시 실행
- 코드 commit / source SHA 위치: 레포 `f5ffc9fc5b3c7a150c3a1d01701423ea885527a0`는 **읽기 전용**(프롬프트·분할·채점 규칙의 출처). 요청 생성·실행·채점은 레포 규칙을 그대로 옮긴 `gemma_runner/`(prepare.py, runner.py, repo_format.py)로 수행 — 레포 실행기 자체는 실행하지 않음. 파일 SHA는 run.json `source_sha256`
- 데이터 repo / revision / 평가 문서 수 / data SHA: nmixx-fin/kiii-kiii / `2df0589d695c18665fd83d4ca5512e03ca0767f6` / **1440문서, 13723요청** / data `d57b1cb0b8b67fe48a9b45ee985fb01e63b919147a8527f8231459a68b57456d`, requests `b526cef377a0d4e42be1bdc7bfc881b05f8602d2f85847d8fa130bd5ecedfeed` — **은빈 실행과 동일 해시**
- 공통 cohort ID / gate 링크: [`cohort-gemma4`](../../cohorts/cohort-gemma4/cohort.json) (Gemma 4 5종 × 두 조건, 1,440문서, 65,536토큰 한도 초과 0건); run.json `cohort_sha256` `3ca4201edaa6047399bd8d052fec95af0074df21e1919dc15b6f2caa14a277f4`. 은빈 gate와 다르므로 **현재 exporter로 합치지 않음**
- tokenizer / chat template / server revision: 모델과 같은 commit / `chat_template.jinja` SHA-256 `ae53464bf3be2580…` / vLLM 0.30.0 (Gemma4Unified 구조를 0.19.0이 지원하지 않아 별도 venv, Transformers 5.17.0, torch 2.13.0+cu130)
- core / halo / 최대 출력 / sampling / reasoning 설정: core 1,200자 / halo 1,200자 / output 4,096토큰 / `chat_template_kwargs.enable_thinking=false` (generation·tokenize 동일); sampling 미지정 → 서버가 모델 generation_config 적용(temperature 1.0, top_p 0.95, top_k 64, 서버 로그 확인); 구조화 출력 없음. 프롬프트·토큰 예산 변경 없음
- 실행 환경 / dependency inventory / GPU(해당 시): Linux, Python 3.11; dependencies는 run.json. NVIDIA H100 80GB HBM3 × 1. concurrency 16(조건당), timeout 900초
- 실제 dtype / 양자화 여부 / tensor parallel / 서버 실행 명령(키 제외): **BF16** / 양자화 없음 / TP 1 / `vllm serve google/gemma-4-12B-it --revision 707f0a3b8a3c7ad586ed01e27eafbad8a27dd0f7 --tokenizer-revision 707f0a3b8a3c7ad586ed01e27eafbad8a27dd0f7 --served-model-name google/gemma-4-12B-it --dtype bfloat16 --max-model-len 65536 --gpu-memory-utilization 0.9 --enable-prefix-caching --limit-mm-per-prompt '{"image":0,"audio":0,"video":0}' --host 127.0.0.1 --port 8100`
- 권장 FP16 대신 다른 설정을 사용했다면 사유: 공식 가중치가 BF16. 배포 정밀도를 따름. 양자화·자동 dtype 아님
- 배정 예산 / 단가·확인일 / 사용·예약 비용 / 실제 청구 차이: 로컬 GPU, 유료 API 0 / 0 USD / 0 / 없음. 토큰 사용: 입력 94,838,149, 출력 7,308,010, 지연 합계 64.2시간(요청 합산)
- 완료 요청 또는 문서 수 / 전체 수 / 실패·uncertain 수: 13,723 / 13,723 요청 (status {'ok': 13700, 'failed': 23}, finish_reason {'stop': 13700, 'length': 23}). **실패 요청 13,037 (95.0%)**; 오류 항목 합계: JSON/스키마 12,938, 잘림/실패 23, TARGET 밖 인용 332, core 밖 173, 라벨 0, 스키마 항목 0, occurrence 0. 실패 요청은 빈 예측·gold FN으로 유지
- 장애·중단·한계와 처리: 전송 오류·중단 없음, 재전송 없음. 2문서 smoke에서 응답 원문 저장·계측 토큰 일치(요청마다 정확히 동일)·thinking/채널 토큰 미출력 확인. 응답 12,955건이 ```json 코드블록으로 감싸져 strict에서 JSON/스키마 오류 처리(런북대로 수정하지 않음)
- result.json 링크(전체 완료 후에만): `result.json` (이 폴더). Strict micro exact P=0.48076923, R=0.00022866, F1=0.00045711 (TP=50, FP=54, FN=218614). 공개·통합 리더보드용 최종 수치 아님
- 계측 / raw 응답·예측 / 비용 저널 artifact 링크와 SHA-256: 응답 원문 `responses.jsonl.gz`, 예약 저널 `events.jsonl.gz` (이 폴더). 계측 파일은 `gemma_runner/counts/gemma4-12b-local_window.jsonl` (실행 서버 보관, 이 폴더 미포함; SHA는 cohort.json `measurements_sha256`)
  - `events.jsonl.gz` `5ff6f6c6f0b8207283228d1e5cf03130ef198b4aaded564e1a3a3a88748e3c9a`
  - `manifest.json` `42b20686c650240ac3ba8bd6427b1cb6525c4b16da4d28d1540a8b9486b6a709`
  - `progress.json` `5956a20a4362f6549a5e9dacfa1777b370d09155538183eadc6ce4ac7750ea39`
  - `responses.jsonl.gz` `7d44f8da1278ea208701a305308f49f2c15cd25db42273e4313481257d1ba649`
  - `result.json` `56aa855de3f269c26e87abc6a984abb345ea2c2c36a6bc225d5b37a2d11916c0`
  - `run.json` `ec92eccfe76c63a0c883cd34a90ca4c4dc9e446e45a8640cb49a211cb832ab58`
- 제외 문서/사유 및 설정 기록 위치: 없음. 1,440문서 전체
- 공유 시 가린 메타데이터 필드(없으면 없음): 없음. base_url은 `127.0.0.1` 로컬 주소, 키 없음
- 다음 담당자에게 필요한 작업: 은빈 결과와 **별도 표**로 보고(cohort gate 다름). 응답 형식 보조 분석(ADR-0036)은 레포 `src.analysis.response_diagnostics` 형식으로 아직 만들지 않음

- 공유본 검증(2026-09-30): 응답·저널은 원본 JSONL과 바이트 일치 확인 후 공유용으로 다시 gzip(`-9`, mtime 0) — 위 `.gz` SHA는 실행 서버 원본 압축본 값이라 이 폴더의 `.gz`와 다름. 압축 해제한 원본 SHA: `responses.jsonl` `0f73025ab1351794ef45281af22d5354366c103fa12e0c7b4cc2506653a99984` (= result.json `response_sha256`), `events.jsonl` `37baf0622de271f5f527677eda5433046509ea6da166b29babe2589617a4ff46`. 이 폴더 파일 SHA는 `ARTIFACTS.sha256`
- 재채점 확인: 레포 `f5ffc9f`의 `python -m src.eval.run score`로 저장 응답을 다시 채점한 결과가 result.json의 metrics·세부 집계·문서별 결과·실패 목록·usage와 완전히 일치(manifest의 생성 시각·요청 생성기 표기만 다름). ADR-0036 `response_diagnostics`는 이 run의 소스 해시가 `gemma_runner`라서 거부하므로 보조 진단은 아직 없음
- 참고: run.json `dependencies`는 실행기(runner) 환경 목록이라 vLLM 0.30.0 등으로 표시됨. 서버 버전은 run.json `server`와 위 서버 실행 명령을 기준으로 봄

진행 중에는 부분 성능을 적지 않습니다. 최종 수치는 finalized result.json을 참조하고 추정하지 않습니다. 실패/불확실 요청과 과거 실행을 제거하지 않습니다.
