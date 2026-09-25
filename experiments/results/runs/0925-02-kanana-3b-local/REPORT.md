# Experiment report — 0925-02-kanana-3b-local

- 담당자 / GitHub ID: 은빈 / <REPLACE_GITHUB_ID>
- 상태: **준비** (준비 / 계측 완료 / 실행 중 / 중단 / 완료)
- 계획 모델 / 실제 served ID / 모델 revision: Kanana-2-3B-Instruct / `kakaocorp/kanana-2-3b-instruct` / `6a5d7889964c4c590299d16e309eabab1f73f8a9` (2026-07-29 기준 main; 서빙 시 이 revision을 명시적으로 고정)
- 조건: local_window
- 시작·종료 시각 / timezone:
- 코드 commit / source SHA 위치: (실행 시 run.json 참조)
- 데이터 repo / revision / 평가 문서 수 / data SHA: nmixx-fin/kiii-kiii / `2df0589d695c18665fd83d4ca5512e03ca0767f6` / <cohort 확정 후> / manifest.json 참조
- 공통 cohort ID / gate 링크: **미확정 — 취합 담당자 미정**
- tokenizer / chat template / server revision: 같은 repo commit `6a5d7889964c4c590299d16e309eabab1f73f8a9` / chat template SHA <서버에서 확인> / vLLM <버전 기입>
- core / halo / 최대 출력 / sampling / reasoning 설정: <pilot에서 확정; 초안 core=1200자 / halo=1200자 / output=4096토큰>
- 실제 dtype / 양자화 여부 / tensor parallel / 서버 실행 명령(키 제외): **BF16** / 양자화 없음 / TP <기입> / `vllm serve ... --dtype bfloat16 --max-model-len <기입>`
- 권장 FP16 대신 다른 설정을 사용했다면 사유: **모델 카드와 config.json의 `torch_dtype`이 `bfloat16`.** 런북의 FP16 기본 권장 대신 배포 정밀도를 따름. 양자화·자동 dtype 아님.
- 모델 사양(참고): dense 3.51B, Qwen3ForCausalLM, vocab 128,256, `max_position_embeddings` 32,768, `use_sliding_window: false` (MoE 아님)
- 실행 환경 / dependency inventory / GPU(해당 시):
- 배정 예산 / 단가·확인일 / 사용·예약 비용 / 실제 청구 차이:
- 완료 요청 또는 문서 수 / 전체 수 / 실패·uncertain 수:
- 장애·중단·한계와 처리:
- result.json 링크(전체 완료 후에만):
- 계측 / raw 응답·예측 / 비용 저널 artifact 링크와 SHA-256:
- 제외 문서/사유 및 설정 기록 위치:
- 공유 시 가린 메타데이터 필드(없으면 없음):
- 다음 담당자에게 필요한 작업:

진행 중에는 부분 성능을 적지 않습니다. 최종 수치는 finalized result.json을 참조하고 추정하지 않습니다. 실패/불확실 요청과 과거 실행을 제거하지 않습니다.
