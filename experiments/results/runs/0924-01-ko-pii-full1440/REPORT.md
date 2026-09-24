# 0924-01-ko-pii-full1440

- 담당: 한울. 실행 지원: Codex.
- 상태: **전체 1,440문서 실행·채점 완료. LLM 공통 cohort 확정 전.**
- 모델: ko-pii; 버전: 1.16.0.
- 조건: whole_document_rules, 고정 rule/label-map, benchmark 기반 튜닝 없음.
- 데이터: nmixx-fin/kiii-kiii content revision `2df0589d695c18665fd83d4ca5512e03ca0767f6`, test 전체.
- 실제 로드: 체크섬 확인된 로컬 release; 저장소 taxonomy와 일치 확인.
- 코드 commit: `0f24a4962aeb9298282d03e5790a55d80de2098c`; 실행 source SHA와 dependencies는 run.json/result.json 참조.
- 시각: 2026-09-24T06:34:00.569377+00:00 → 2026-09-24T06:35:46.045029+00:00 (UTC).
- 경과 시간: 105.48초. 같은 호스트에서 두 baseline을 병렬 실행했으므로 단독 성능 벤치마크 시간이 아님.
- 환경: macOS-26.5-arm64-arm-64bit; Python 3.12.13; CPU, GPU 없음.
- 추론 API 호출·과금: 0. 데이터 생성 비용은 이 실행에 포함하지 않음.
- 처리: 1440/1440, 중단/누락 문서 0, 문서 ID 및 예측 파일 해시 검증 완료.
- 적용 설정: Presidio는 ko recognizer 5개 + email/KR phone + custom account/card, threshold 0.3. ko-pii는 normalize=False. 상세는 공용 label map README와 이 폴더의 label-map.json.
- 공유 시 가린 메타데이터 필드: 없음. 키·서버 URL 없음.

## 전체 릴리스 점수 (최종 LLM 비교 집합 아님)

Strict category-and-boundary micro precision=0.07972873, recall=0.11527275, F1=0.09426134.
TP=25206, FP=290941, FN=193458.
모든 36개 gold category가 분모에 포함되며 baseline이 지원하지 않는 category도 FN으로 남습니다. 이 값은 최종 비교군 순위나 카테고리 전체를 지원하는 NER 성능으로 해석하지 않습니다. 세부 분해는 result.json 참조.

## 재현 및 후속

1. manifest.json의 프로토콜로 고정 release의 전체 test를 준비합니다.
2. 기록된 코드/dependencies에서 `python -m src.eval.baselines --name ko-pii --directory <prepared-plan> --output <new-run>`으로 재현 가능합니다. 기존 공유 run을 덮어쓰지 않습니다.
3. predictions.jsonl.gz에는 문서 ID, 고정 mapping 적용 spans, 원본 label/offset 예측이 들어 있습니다. 정답은 고정 HF release로 재현합니다. 압축 및 원본 SHA-256은 ARTIFACTS.sha256에 기록했습니다.
4. LLM 공통 cohort가 확정되면 저장된 predictions에서 같은 문서 ID만 선택하여 **새 분석 artifact로 재채점**합니다. 탐지 재실행이나 rule 수정은 필요하지 않습니다. 원본 1440문서 결과는 그대로 보존합니다.
5. 그 전에는 이 결과를 LLM과 합친 headline leaderboard로 export하지 않습니다. 공통 cohort에서 최종 성능을 확인한 뒤에만 본문/통합 표에 사용합니다.
