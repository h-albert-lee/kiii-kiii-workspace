# Experiment report — 0925-07-openmed-windows

- 담당자 / GitHub ID: 은빈 / <REPLACE_GITHUB_ID>
- 상태: **준비** (준비 / 계측 완료 / 실행 중 / 중단 / 완료)
- 계획 모델 / 실제 served ID / 모델 revision: OpenMed/privacy-filter-multilingual / <미확인> / <미확인>
- 조건: overlapping_token_windows
- 시작·종료 시각 / timezone:
- 코드 commit / source SHA 위치: (실행 시 run.json 참조)
- 데이터 repo / revision / 평가 문서 수 / data SHA: nmixx-fin/kiii-kiii / `2df0589d695c18665fd83d4ca5512e03ca0767f6` / <cohort 확정 후> / manifest.json 참조
- 공통 cohort ID / gate 링크: **미확정 — 취합 담당자 미정**
- tokenizer / chat template / server revision: 해당 없음 (token-classification, Transformers 경로)
- 가중치 revision: `f914f18d909d541d288dfda44a4d0b6bdb638d57`
- 창 크기 / overlap: <pilot에서 확정; 초안 --window 1024 --overlap 128>
- device / dtype: <예: cuda, 미확정>
- 디코딩: 토큰 logits argmax + BIOES grouping (OpenMed wrapper의 Viterbi와 동일하다고 주장하지 않음)
- FP16 vLLM 서빙 지침: 해당 없음 (chat 모델 아님)
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
