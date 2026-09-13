# ADR-0005: 리더보드 모델 선정

- 상태: accepted
- 날짜: 2026-09-13
- 결정자: 한울
- 관련: `docs/models.md`, `literature/notes/evaluated-models.md`, ADR-0002

## 배경

선행 PII 벤치마크 12편의 평가 모델을 조사한 결과 국제 표준 세트는 {GPT-4급 API, Claude, Llama-3.1-8B, Qwen2.5-7B, DeepSeek, Presidio, GLiNER, OpenAI Privacy Filter}이며, 한국어로 평가된 것은 Thunder-DeID의 EXAONE-3.5·Polyglot-Ko 베이스라인이 유일하다.

## 결정

14 모델 + 4 베이스라인 (`docs/models.md` §2). 구성 원칙:
1. **연속성 앵커** — GPT/Claude/Gemini API, Llama-3.1-8B, Qwen3.5, Presidio, OPF: 리뷰어가 아는 행.
2. **한국어 우선 모델 4+1** — HCX-007(API), Kanana-2-30B-A3B, HyperCLOVAX-SEED-Think-14B, EXAONE-4.0-32B, A.X Light 쌍. "한국어 네이티브 학습이 한국형 식별자·한글 숫자에 도움 되는가"가 논문의 finding 하나.
3. **토크나이저 ablation** — A.X-3.1-Light(자체) vs A.X-4.0-Light(Qwen 파생), 같은 회사·같은 크기.
4. **규칙 상한선** — Presidio(ko recognizer 활성) + ko-pii. T-level 곡선의 기준선.
5. **in-domain 상한선** — KLUE-RoBERTa-large fine-tune.
6. 80GB GPU 1장에서 돌아가지 않는 모델(Solar Open, A.X K2, K-EXAONE, Motif-3)은 제외; 후속 연구에서 hosted API.
7. 생성기 모델은 `model_type: generator`로 표기, 헤드라인 순위 제외 (ADR-0002).

## 이유

- 4페이지에 18행이 한계. 그 안에서 "국제 표준과 비교 가능"과 "한국어 모델 finding" 두 목표를 모두 만족하는 최소 구성.
- EXAONE NC 라이선스는 연구 평가에는 문제없으나 논문에 명시.

## 검토한 대안

- 한국어 모델만 — 국제 비교 불가, 리뷰어 설득력 약함.
- 30+ 모델 대규모 — 4페이지·비용·시간 초과. 부록/후속.

## 영향

- `experiments/configs/`에 모델별 템플릿 18개 생성 예정. `leaderboard.csv` 컬럼에 `model_group` (api/open_large/korean_open/open_small/rule) 추가.
- 실험 전 모델 ID·라이선스·컨텍스트 길이 재확인 ([?] 항목).
