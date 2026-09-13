# HANDOFF — 2026-09-13, Cowork → Claude Code

이 문서는 다른 세션·도구가 이어받을 때 필요한 **전체 맥락**입니다. 결정의 근거는 각 ADR, 현황은 `STATUS.md`. 여기는 "왜 이렇게 되어 있고, 지금 어디까지 왔고, 무엇을 조심해야 하는가".

## 1. 프로젝트가 무엇인가

- **논문**: *Kiii-Kiii: Korean Identifiers, Identifiability, and Ill-formed Inputs — A Regulation-Grounded Benchmark for Financial PII Detection.* 제목의 "Kiii-Kiii"는 걸그룹 이름 오마주(K-I-I-I 순서 유지). 본문에서 데이터셋은 `\kiii` = **Kiii²**.
- **venue**: ICAIF'26 Workshop on Financial AI Security, Privacy, and Safety (Milan, 11/14–15). **마감 10/8 (AoE 가정 → KST 10/7 목표)**, 4p excl. refs, ACM sigconf, double-blind, non-archival. 백업 AI4F (10/7). ADR-0003.
- **기여 3개**: (1) 조문 인용 2-tier 택소노미 36개 (2) 체크섬 유효 식별자 + 변형 축 T0~T3의 합성 long-context multi-subject 코퍼스 (3) 14 모델 + 4 베이스라인 리더보드와 (tier×kind)×T-level 분석.
- **저자**: 한울(AIM Intelligence), 김성현(토스증권). 성현은 초개인화 피싱 문제제기를 냈고, 콜센터·STT 도메인 지식은 없음 → 관련 판단은 자체 조사(`literature/notes/stt-korean-numbers.md`)로 대체.

## 2. 결정 이력 (ADR 순서가 아니라 시간 순서)

| 날짜 | 결정 | 근거 위치 |
|---|---|---|
| 9/8 | 프레이밍 A: 규제 기반 택소노미 + long-context 벤치, 4p short paper. 생성·평가 모델 로컬 한정 안 함 | ADR-0001, `docs/related_work.md` |
| 9/10 | 택소노미 v1: 2 tier × 2 kind, 법령 조문 단위 근거. 신용정보법 시행령 §2③이 고객번호를 식별정보로 명시 — 핵심 발견 | ADR-0004, `taxonomy/taxonomy.md` |
| 9/10 | 근거 약한 crypto_wallet·lifestyle_indicator 제거. **변형 축(DLP 축)** 추가 — 정형 표기는 regex로 풀리니 난이도는 표면형 변형에서 | ADR-0004 결정 8 |
| 9/11 | T4(encoded 우회) 제외 — 공격 분포 ≠ DLP 입력 분포. STT 실태 조사로 프로필 고정(아라비아 70/한글 20/혼합 10, 공/영, 에/다시, pre-masked 20%) | ADR-0004 결정 9, `literature/notes/stt-korean-numbers.md` |
| 9/13 | 열린 질문 해소: dob_age·IP는 I 유지, consultation_content 운영 규칙, 상담사 이름 must_mask + subject_role 분리 → **v1.2 accepted** | ADR-0004 결정 10~13 |
| 9/13 | 생성 = 슬롯 채우기 (LLM은 값 안 씀), API 주생성 80% + 로컬 20% 슬라이스, 생성기 리더보드 표기 | ADR-0002, `docs/generation_design.md` |
| 9/13 | 리더보드 14+4. 표준 세트 ID 재검증(gpt-5.6-sol/luna, claude-sonnet-5/opus-5, gemini-3.8-flash, Qwen3.6-35B-A3B, Gemma 4). **가입·심사 필요한 한국 API 제외** (HCX-007 제외) → Solar Pro 4(OpenRouter)만 | ADR-0005, `docs/models.md` |
| 9/13 | venue ICAIF'26 Security/Privacy/Safety WS; `paper/` submodule 연결; 논문 골격 | ADR-0003 |

## 3. 지금 있는 것 (검증 상태)

| 산출물 | 상태 | 확인 방법 |
|---|---|---|
| `taxonomy/taxonomy.yaml` v1.2 | accepted. 36 카테고리, 25 ops, stt_profile, 10 문서유형, exclusions | `python -c "import yaml;yaml.safe_load(open('taxonomy/taxonomy.yaml'))"` |
| `src/generate/*` | 스캐폴드 동작. 체크섬·변형·슬롯 파싱·검증 전부 구현. LLM 호출(`compose`)만 미실행 | `python -m pytest tests -q` (9 passed) / `run.py dryrun` |
| `src/prompts/compose_v1.txt` | 초안. 파일럿 전 미검증 | — |
| `src/eval/` | **비어 있음** | — |
| `paper/` | acmart 골격 7 sections, xelatex 컴파일 4p, 인용 0 미해결. 결과·실험은 `\todo` | Overleaf XeLaTeX |
| `literature/papers.bib` | ~25 entries, venue 검증된 것 위주. `paper/references.bib`는 복사본 + 3개 추가 | — |
| `experiments/results/leaderboard.csv` | 헤더만 | — |
| `figures/src/_style.py` | 공용 스타일만 | — |

## 4. 다음 할 일 (역산 일정: ADR-0003)

1. **파일럿 100건** (9/15): `run.py plan --n 100` → `compose --model gpt-5.6-sol` (또는 claude-sonnet-5; `OPENAI_BASE_URL`로 OpenAI 호환 아무 엔드포인트) → `fill`. reject 로그 보고 프롬프트 튜닝(슬롯 준수율·태그 경계). 한울 검수 + consultation_content IAA 30건.
2. **사전 확장**: `identifiers.py`의 SURNAMES 20·GIVEN_SYL 20·ROADS 8·GU 소수는 시드 수준. 성 100+·이름 음절 100+·시군구 전체·도로명 200+로. 외국인 이름·로마자 표기 추가.
3. **`src/eval/metrics.py`**: 스팬 F1 (카테고리 단위, 조각은 partial overlap, entity 단위 집계), (tier×kind)×T-level 격자, op별 recall, hard-negative precision, `subject_role` 분리, TAB식 risk-weighted recall, 정보손실, cross-mention consistency. 결과 json 스키마는 `docs/guide/experiments.md`.
4. **베이스라인 어댑터**: Presidio(ko recognizer 5종 활성 + 우리 계좌·카드 regex 추가), ko-pii, OpenMed/privacy-filter-multilingual, KLUE-RoBERTa fine-tune.
5. **LLM 추출 프롬프트** `src/prompts/span_p1.txt` (JSON 출력, 카테고리 목록 주입), de-id 프롬프트 `deid_p1.txt`.
6. 실험(API 4 → 로컬 10) → figure(`figures/src/fig2_tlevel_curve.py` 등) → `scripts/sync_figures.sh` → 논문 결과 섹션.
7. 남은 조사: 금융분야 가명·익명처리 안내서 PDF 본문 표(자동 파싱 실패), REDACT 25개 언어에 한국어 포함 여부, KDPII 평가 모델 목록.

## 5. 함정·주의

- **git 흐름**: `paper/`는 submodule. Overleaf ↔ GitHub는 수동 Sync. Overleaf에서 썼으면 Overleaf Push → `git submodule update --remote paper`; 레포에서 figure/bib 넣었으면 `paper/` push → Overleaf Pull. 충돌 방지 위해 항상 Overleaf Push 먼저.
- **LaTeX**: `main.tex` kotex → XeLaTeX. acmart가 `\anon` 정의하므로 우리 매크로는 `\anonv{리뷰}{카메라레디}`. 제출 `[sigconf,anonymous,review]`, 카메라레디 `[sigconf]` + `\anonymousfalse`.
- **익명화**: 초고에 AIM·토스·레포 URL·"Powered by …" 금지. 카메라레디에 SEED·Kanana 표기 의무.
- **모델 ID는 변동**: `docs/models.md`의 ID·가격은 9/13 기준. 실험 직전 재확인. OpenAI Sol 가격은 두 공식 페이지가 2배 불일치.
- **생성기 편향**: 문서 작성 모델은 `model_type: generator`로 리더보드 표기, 헤드라인 제외. 식별자 값·변형은 코드가 만들어 편향 제한적 — 논문에 명시.
- **validate가 문서를 버리는 이유 1순위**는 LLM이 슬롯 없이 숫자를 직접 쓴 것(`leaked *_like`). 프롬프트 규칙 1번이 이걸 막지만 파일럿에서 비율을 봐야 함.
- **T3 구조 op**(chunk_split·agent_readback·coref)는 슬롯 지시자로 LLM이 배치 → 프롬프트 준수율이 T3 문서 품질을 결정.
- 맥북 로컬 레포 `~/research/kfinpii`, 리모트 `github.com/h-albert-lee/kiii-kiii-workspace`. Cowork 세션에서는 .git lock 정리 이슈가 있었지만 Claude Code(로컬 터미널)에서는 무관.

## 6. 참고 문서 지도

- 포지셔닝·선행연구: `docs/related_work.md` (영어, 논문 §2 원천)
- 택소노미 근거: `taxonomy/taxonomy.md`, `literature/notes/legal-sources-ko.md`(조문 원문), `literature/notes/prior-pii-schemas.md`
- 생성: `docs/generation_design.md`, ADR-0002
- STT: `literature/notes/stt-korean-numbers.md`
- 모델: `docs/models.md`, `literature/notes/evaluated-models.md`
- 회의: `docs/meetings/2026-09-08-kickoff.md` (카톡 기반)
