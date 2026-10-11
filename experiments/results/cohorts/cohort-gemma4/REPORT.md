# Cohort report — cohort-gemma4

- 담당자: 김성현 / MrBananaHuman
- 대상: Gemma 4 instruct 5종(`google/gemma-4-E2B-it`, `-E4B-it`, `-12B-it`, `-26B-A4B-it`, `-31B-it`) × full_context_targeted / local_window, 10개 조건
- 데이터: nmixx-fin/kiii-kiii `2df0589d695c18665fd83d4ca5512e03ca0767f6`, data `d57b1cb0b8b67fe48a9b45ee985fb01e63b919147a8527f8231459a68b57456d`. requests SHA(full `3542d46e…`, local `b526cef3…`)는 은빈 실행과 동일
- 한도: 전체 65,536토큰(입력 + 출력 예약), 출력 4,096토큰. 모델별 native tokenizer 계측 최대 입력은 full 31,765–31,769 / local 9,062–9,066토큰이며 초과 0건 → 1,440문서 전체 eligible, 제외 문서 없음
- `cohort.json` SHA-256 `3ca4201edaa6047399bd8d052fec95af0074df21e1919dc15b6f2caa14a277f4` = 10개 run.json의 `cohort_sha256`
- 계측 파일(`gemma_runner/counts/*.jsonl`)은 실행 서버 보관, 이 폴더 미포함. 각 파일 SHA는 `cohort.json` `entries[].measurements_sha256`
- 은빈 실행(cohort-q9 등)과 다른 gate이므로 현재 exporter로 합치지 않고 별도 표로 보고합니다
