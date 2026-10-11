# 0925-07-openmed-windows

- 담당: 은빈. 실행 지원: Claude Code.
- 상태: **전체 1,440문서 실행·채점 완료. LLM 공통 cohort 확정 전.**
- 모델: `OpenMed/privacy-filter-multilingual`, revision `f914f18d909d541d288dfda44a4d0b6bdb638d57`. native Transformers token classification (`OpenAIPrivacyFilterForTokenClassification`).
- 조건: overlapping_token_windows — 1,024토큰 창, 128토큰 겹침, 모든 창 처리. argmax + BIOES grouping (`decoder: argmax_bioes`). **OpenMed wrapper의 Viterbi decoding과 동일하다고 주장하지 않음.** 정확히 같은 스팬만 중복 제거, 경계 충돌·조각은 gold로 고치지 않음. 고정 label-map, benchmark 기반 튜닝 없음.
- 데이터: nmixx-fin/kiii-kiii content revision `2df0589d695c18665fd83d4ca5512e03ca0767f6`, test 전체 1,440문서. manifest.json은 실행에 사용한 `experiments/prepared/full_context_targeted` plan(data `d57b1cb0b8b67fe48a9b45ee985fb01e63b919147a8527f8231459a68b57456d`)이며 result.json의 manifest와 일치.
- 코드 commit: 실행 worktree HEAD `b4f76f4b3cd1542f50980144baa9e6874c9a7d6a` (브랜치 `feat/exp-eb`); source SHA와 dependencies는 run.json/result.json 참조 — 기존 LLM 실행과 source SHA 동일.
- 시각: 2026-09-30T07:11:47.115013+00:00 → 2026-09-30T07:23:31.061353+00:00 (UTC). 경과 시간 약 12분 8초(모델 로드 포함).
- 환경: Linux (GCP), Python 3.12.3, **torch 2.13.0+cu130, transformers 5.17.0** (`~/venvs/vllm` 환경; `requirements-eval-openmed.txt` 조건 충족). GPU: NVIDIA A100-SXM4-40GB × 1. dtype: 모델 로드 기본값(실행기 코드에서 명시적 변환 없음). 9/23 smoke 실행(문서 2개)은 torch 2.14.0 환경이었으며 그 환경은 현재 호스트에 없음 — smoke는 연결 점검용이고 결과로 쓰지 않음.
- 추론 API 호출·과금: 0.
- 처리: 1440/1440, 중단/누락 문서 0. result.json `predictions_sha256`이 예측 파일 해시와 일치함을 확인.
- 적용 설정: label-map.json = `experiments/label_maps/openmed.json` (SHA-256 `ef81b9b40c10737c55dabfb1ff1f7c18028a807e6265fdb6fa22d26ea79a0dc9`, run.json `mapping_sha256`과 동일). FIRST/MIDDLE/LASTNAME은 각각 person_name으로 매핑하고 gold 경계로 병합하지 않음. 세부 한계는 공용 label map README 참조.
- 공유 시 가린 메타데이터 필드: 없음. 키·서버 URL 없음.

## 전체 릴리스 점수 (최종 LLM 비교 집합 아님)

Strict category-and-boundary micro precision=0.07534071, recall=0.01210990, F1=0.02086592.
TP=2648, FP=32499, FN=216016. Category-aware character F1=0.03106932. non-PII character mask rate=0.001799.
식별자 F1=0.0413, 속성 F1=0.0000. 상위 카테고리: phone_no 0.23, bank_account_no 0.09, card_no 0.07, access_credential 0.03.
모든 36개 gold category가 분모에 포함되며 baseline이 지원하지 않는 category도 FN으로 남습니다. 이 값은 최종 비교군 순위나 카테고리 전체를 지원하는 NER 성능으로 해석하지 않습니다. 세부 분해는 result.json 참조.

## 재현 및 후속

1. manifest.json의 프로토콜로 고정 release의 전체 test를 준비합니다.
2. 기록된 코드/dependencies에서 `python -m src.eval.baselines --name openmed --revision f914f18d909d541d288dfda44a4d0b6bdb638d57 --device cuda --window 1024 --overlap 128 --directory <prepared-plan> --output <new-run>`으로 재현합니다. 기존 공유 run을 덮어쓰지 않습니다.
3. predictions.jsonl.gz에는 문서 ID, 고정 mapping 적용 spans, 원본 label/offset 예측이 들어 있습니다. 압축 및 원본 SHA-256은 ARTIFACTS.sha256에 기록했습니다.
4. LLM 공통 cohort가 확정되면 저장된 predictions에서 같은 문서 ID만 선택하여 **새 분석 artifact로 재채점**합니다(예: Kanana-1.5-8B의 1,438문서 집합). 탐지 재실행이나 mapping 수정은 필요하지 않습니다. 원본 1440문서 결과는 그대로 보존합니다.
5. 그 전에는 이 결과를 LLM과 합친 headline leaderboard로 export하지 않습니다.
