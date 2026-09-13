# ADR-0005: 리더보드 모델 선정

- 상태: accepted
- 날짜: 2026-09-13
- 결정자: 한울
- 관련: `docs/models.md`, `literature/notes/evaluated-models.md`, ADR-0002

## 배경

선행 PII 벤치마크 12편의 평가 모델을 조사한 결과 국제 표준 세트는 {GPT-4급 API, Claude, Llama-3.1-8B, Qwen2.5-7B, DeepSeek, Presidio, GLiNER, OpenAI Privacy Filter}이며, 한국어로 평가된 것은 Thunder-DeID의 EXAONE-3.5·Polyglot-Ko 베이스라인이 유일하다.

## 결정

15 모델 + 4 베이스라인 (`docs/models.md` §2; 2026-09-13 ID·접근성 재검증 반영). 구성 원칙:
1. **연속성 앵커** — GPT/Claude/Gemini API, Llama-3.1-8B, Qwen3.5, Presidio, OPF: 리뷰어가 아는 행.
2. **한국어 우선 모델 4+2** — HCX-007·Solar Pro 4(API), Kanana-2-30B-A3B, HyperCLOVAX-SEED-Think-14B, EXAONE-4.0-32B, A.X Light 쌍. Solar Pro 4는 HCX 한도·심사 리스크의 보험이자 OpenRouter에 있는 유일한 한국 모델. "한국어 네이티브 학습이 한국형 식별자·한글 숫자에 도움 되는가"가 논문의 finding 하나.
3. **토크나이저 ablation** — A.X-3.1-Light(자체) vs A.X-4.0-Light(Qwen 파생), 같은 회사·같은 크기.
4. **규칙 상한선** — Presidio(ko recognizer 활성) + ko-pii. T-level 곡선의 기준선.
5. **in-domain 상한선** — KLUE-RoBERTa-large fine-tune.
6. 80GB GPU 1장에서 돌아가지 않는 모델(Solar Open, A.X K2, K-EXAONE, Motif-3)은 제외; 후속 연구에서 hosted API.
7. 생성기 모델은 `model_type: generator`로 표기, 헤드라인 순위 제외 (ADR-0002).
8. **ID 갱신 (2026-09-13 검증)**: GPT-5.5→`gpt-5.6-sol`/`gpt-5.6-luna`; Gemini 3.5 Flash→`gemini-3.8-flash`(stable), 3.1 Pro는 preview 표기; Qwen3.5-35B-A3B→`Qwen3.6-35B-A3B`. Claude는 `claude-sonnet-5`/`claude-opus-5` 유지.
9. **접근성 확인**: HCX-007은 NCP 셀프서브 + OpenAI 호환 엔드포인트로 호출 가능, 테스트 키 60 QPM/60K TPM → 서비스 앱 심사 즉시 신청. A.X·Mi:dm은 외부 API 없음 → 로컬. EXAONE NC는 논문 발표 명시 허용(§2.1b).

## 이유

- 4페이지에 18행이 한계. 그 안에서 "국제 표준과 비교 가능"과 "한국어 모델 finding" 두 목표를 모두 만족하는 최소 구성.
- EXAONE NC 라이선스는 연구 평가에는 문제없으나 논문에 명시.

## 검토한 대안

- 한국어 모델만 — 국제 비교 불가, 리뷰어 설득력 약함.
- 30+ 모델 대규모 — 4페이지·비용·시간 초과. 부록/후속.

## 영향

- `experiments/configs/`에 모델별 템플릿 18개 생성 예정. `leaderboard.csv` 컬럼에 `model_group` (api/open_large/korean_open/open_small/rule) 추가.
- 실험 전 모델 ID·라이선스·컨텍스트 길이 재확인 ([?] 항목).
