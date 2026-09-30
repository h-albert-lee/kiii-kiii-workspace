# Experiment report — 0928-02-exaone-33b-local

- 담당자 / GitHub ID: 은빈 / <REPLACE_GITHUB_ID>. 실행 지원: Claude Code.
- 상태: **완료** (전체 요청 실행·finalize 완료). **배정표·ADR에 없는 추가 모델**(운영자 요청, 2026-09-28) — 공유·논문 사용 전 범위 결정(ADR·배정표) 필요. 공통 cohort 재집계 전.
- 계획 모델 / 실제 served ID / 모델 revision: EXAONE-4.5-33B (dense 33B, `Exaone4_5_ForConditionalGeneration` 멀티모달 checkpoint, 텍스트 입력만 사용) / `LGAI-EXAONE/EXAONE-4.5-33B` / `570aa4b15a4f45ba1133072b45f50198f6e3b4fd` (tokenizer 동일 commit). **라이선스 `other`(EXAONE 자체 라이선스) — 결과 공개 전 이용 조건 확인 필요**
- 조건: local_window (짝 실행: `0928-01-exaone-33b-full`)
- 시작·종료 시각 / timezone: 2026-09-28T16:03:31Z → 2026-09-29T15:15:43Z (UTC). 짝 조건과 같은 서버에서 동시 실행
- 코드 commit / source SHA 위치: 실행 worktree HEAD `b4f76f4b3cd1542f50980144baa9e6874c9a7d6a` (브랜치 `feat/exp-eb`). `source_sha256`은 run.json 참조 — 기존 핵심 실행과 동일
- 데이터 repo / revision / 평가 문서 수 / data SHA: nmixx-fin/kiii-kiii / `2df0589d695c18665fd83d4ca5512e03ca0767f6` / **1440문서, 13723요청** / data `d57b1cb0b8b67fe48a9b45ee985fb01e63b919147a8527f8231459a68b57456d`, requests `b526cef377a0d4e42be1bdc7bfc881b05f8602d2f85847d8fa130bd5ecedfeed` (manifest.json)
- 공통 cohort ID / gate 링크: `cohort-exaone-33b.json` (Qwen3.5-2B/4B + Kanana-2-3B + EXAONE-4.5-33B × 두 조건, 1,440문서, 제외 없음); run.json `cohort_sha256` `33c670c00de2006bcce594aa52aa29625e9f56d956bca595f5b1b787f1daad7a`. **핵심 run과 다른 gate이므로 현재 exporter로 합치지 않음**
- tokenizer / chat template / server revision: 모델과 같은 commit / `chat_template.jinja` SHA-256 `e4ece7acc79ba821…` / vLLM 0.30.0 (Transformers 5.17.0, torch 2.13.0+cu130)
- core / halo / 최대 출력 / sampling / reasoning 설정: core 1,200자 / halo 1,200자 / output 4,096토큰 (핵심 실행과 동일) / **reasoning off**: `chat_template_kwargs.enable_thinking=false`(generation·tokenize 동일; 모델 기본값은 True이며 false일 때 template이 빈 `<think></think>` 블록 삽입), reasoning 토큰 0. **샘플링: 모델 generation_config(temperature 1.0, top_p 0.95, presence_penalty 1.5)를 `--generation-config vllm`으로 끄고 temperature 1.0 / top_p 1.0 사용** — 이전 LLM 전부와 같은 실효 샘플링을 위한 의도적 선택. 모델 카드 권장값(텍스트: temperature 1.0 / top_p 0.95; 한국어·문서: temperature 0.6 / top_p 0.95 / top_k 20 / presence_penalty 1.5)과 다르며 이 모델에 불리할 수 있음. 구조화 출력 없음
- 모델 카드 권장 vLLM 명령과의 차이: TP 2 → **4**(A100 40GB), max-model-len 262,144 → **65,536**(최대 입력 7,929토큰으로 충분), `--reasoning-parser qwen3`·tool-call 옵션·`--limit-mm-per-prompt` 미사용(비추론·텍스트 전용), **`--speculative_config` MTP 미사용**(출력 분포 불변, 속도만 영향)
- 실행 환경 / dependency inventory / GPU(해당 시): Linux, Python 3.12, 평가 실행기 `.venv`; dependencies는 run.json. A100-SXM4-40GB × 4 (GPU 4–7), tensor parallel 4. concurrency 8, timeout 900초
- 실제 dtype / 양자화 여부 / tensor parallel / 서버 실행 명령(키 제외): **BF16** / 양자화 없음 / TP 4 / `vllm serve LGAI-EXAONE/EXAONE-4.5-33B --revision 570aa4b15a4f45ba1133072b45f50198f6e3b4fd --dtype bfloat16 --max-model-len 65536 --tensor-parallel-size 4 --generation-config vllm --port 8031`
- 권장 FP16 대신 다른 설정을 사용했다면 사유: 공식 가중치가 BF16. 배포 정밀도를 따름. 양자화·자동 dtype 아님
- 배정 예산 / 단가·확인일 / 사용·예약 비용 / 실제 청구 차이: 로컬 GPU, 유료 API 0 / 0 USD / 0 / 없음. 토큰 사용: 입력 78,367,760, 출력 8,636,621
- 완료 요청 또는 문서 수 / 전체 수 / 실패·uncertain 수: 13,723 / 13,723 요청 (status {'ok': 13541, 'failed': 182}, finish_reason {'stop': 13541, 'length': 182}; `failed`는 전부 출력 4,096토큰 도달). **실패 요청 8,791 (64.1%)**; 오류 항목 합계: JSON/스키마 1,521, 잘림 182, TARGET 밖 인용 92,201, core 밖 38,830, 라벨 10,120, 스키마 항목 2,851, occurrence 1,377. 실패 요청은 빈 예측·gold FN으로 유지
- **빈 응답:** 채점을 통과한 요청 4,932개 중 `{"spans":[]}`(예측 없음) 4,098개(83.1%)
- 장애·중단·한계와 처리: 전송 오류·중단 없음. 호환성 pilot(별도 합성 30요청): 전송 오류 0, 계측 토큰 30/30 일치, thinking 0. 응답 일부(약 0.1%)에 `</think>` 뒤 JSON을 반복 출력한 형식 오류 있음(추론 아님, JSON 오류로 실패 처리). 설정이 pilot 보정 전 기본값이라 형식 실패가 많음 — `docs/reviews/2026-09-26-issue-*.md` 참조
- result.json 링크(전체 완료 후에만): `result.json` (이 폴더). Strict micro exact P=0.61506276, R=0.00941170, F1=0.01853971 (TP=2058, FP=1288, FN=216606). 공개·통합 리더보드용 최종 수치 아님
- 계측 / raw 응답·예측 / 비용 저널 artifact 링크와 SHA-256: 응답 원문과 예약 저널(이 폴더). 계측 파일은 실행 worktree `experiments/runs/counts/exaone-33b-*.jsonl` 보관
  - `events.jsonl` `1fd8be0bb7c51bf0540e991ecbe25be9c51d8dfd31dad63c4aedd45ef7c818f8`
  - `manifest.json` `04430b66fb1d61e344dc141dfafc72f80e83ed65f7b6fdad5e1734e1a813bcf0`
  - `progress.json` `f083d3301d50912fa0d6eba9cfec0e1260cad651217aa031e163db38e90bfc78`
  - `responses.jsonl` `742d1905bbec2866a61770a1f83f9d022b527a8b30d279a345ec95ef66774728`
  - `result.json` `77bbe8a8f15e301c30034682ac0f4d0b08179a47e88ce0ee8a03bc2736aa6082`
  - `run.json` `ebe1f359eac83fbae6ffed896795dfe6e94ef3717958a483ab2bfb7a9f4acc18`
- 제외 문서/사유 및 설정 기록 위치: 없음. 1,440문서 전체
- 공유 시 가린 메타데이터 필드(없으면 없음): 없음. base_url은 `127.0.0.1` 로컬 주소, 키 없음
- 다음 담당자에게 필요한 작업: 범위·라이선스 결정 후 공유 여부 확정. `read_jsonl` U+2028 버그 수정 시 이 run을 수정된 코드로 재채점해 결과 동일성 확인. 공통 cohort 재집계 전까지 핵심 결과와 **별도 표**로 보고

진행 중에는 부분 성능을 적지 않습니다. 최종 수치는 finalized result.json을 참조하고 추정하지 않습니다. 실패/불확실 요청과 과거 실행을 제거하지 않습니다.
