# CLAUDE.md — kfinpii (Kiii-Kiii / Kiii²)

이 레포는 논문 프로젝트 **"Kiii-Kiii: Korean Identifiers, Identifiability, and Ill-formed Inputs — A Regulation-Grounded Benchmark for Financial PII Detection"**의 연구 맥락 저장소입니다. 코드·문서·결정·논문이 전부 여기 있습니다. 처음이면 이 파일 → `STATUS.md` → `docs/HANDOFF.md` 순서로 읽으세요.

## 한 줄 요약
한국 금융 PII 벤치마크. 법령 조문에 근거한 2-tier 택소노미(Legal 24 / Identifiability 12 = 36 카테고리) × 표면형 변형 축(T0 canonical ~ T3 structural; 정형 표기는 regex로 풀리므로 난이도는 변형에서 나옴) × long-context multi-subject 합성 문서. 과업은 스팬 추출 + 비식별화. 4페이지 short paper, **ICAIF'26 Financial AI Security/Privacy/Safety 워크샵, 마감 2026-10-08**.

## 사용자
한울(Hanwool Albert Lee, AIM Intelligence). 캐주얼 한국어 + 영어 기술 용어. 직설적 피드백 선호. 연구 의사결정은 위임받아 Claude가 근거 있게 내리되 ADR로 기록. 공저자 김성현(토스증권)은 콜센터 지식 없음 — 도메인 판단은 자체 조사로.

## 절대 규칙
- **결정은 ADR로** (`docs/decisions/NNNN-*.md`). 카톡·대화에서 정한 것도 ADR에 적어야 결정. 기존 ADR은 수정하지 않고 새 ADR로 대체.
- **택소노미 원본은 `taxonomy/taxonomy.yaml`**. 카테고리·op를 코드에 하드코딩하지 말 것. 바꾸면 `version`·`changelog` 갱신, `taxonomy.md`·`mapping_prior_work.md` 동기화.
- **LLM은 식별자 값을 절대 쓰지 않는다** (ADR-0002). `{{슬롯}}`만 쓰고 값은 `src/generate/identifiers.py`가 체크섬 유효하게 생성. 이게 gold 정확성의 근간.
- **논문 수치는 `experiments/results/leaderboard.csv`에서만**. 결과 json엔 `git_commit`·`data_version`·`prompt_version` 필수. 실행 ID `MMDD-NN`.
- **figure는 스크립트로 재생성 가능**해야 함 (`figures/src/`, 숫자 하드코딩 금지).
- **실제 고객 데이터 금지**. 합성만.
- **논문 초고는 익명**: 소속·레포 URL·"Powered by …" 표기는 `\anonv{리뷰용}{카메라레디}` 매크로로 숨김.
- 미검증 주장은 `[?]` 표시. "미검증은 질문으로, 검증된 것만 문장으로."
- 커밋 메시지 `영역: 내용` (영역: taxonomy/lit/exp/fig/docs/status/src/paper/generate/models). `docs/guide/workflow.md`.

## 디렉토리
```
taxonomy/        taxonomy.yaml(원본) · taxonomy.md(영어, 논문 §3 원천) · mapping_prior_work.md
src/generate/    슬롯 채우기 파이프라인 (taxonomy·identifiers·variation·compose·fill·negatives·validate·run)
src/prompts/     compose_v1.txt (LLM 문서 작성 프롬프트). 버전 바꾸면 새 파일
src/eval/        비어 있음 — metrics.py 작성 필요
tests/           pytest 9개 (python -m pytest tests -q)
docs/            related_work.md · generation_design.md · models.md · decisions/ · meetings/ · guide/ · HANDOFF.md
literature/      papers.bib(원본 bib) · notes/ (legal-sources-ko, prior-pii-schemas, stt-korean-numbers, evaluated-models)
experiments/     configs/ · results/leaderboard.csv
figures/         src/_style.py(공용 스타일) · out/
paper/           submodule → github.com/h-albert-lee/ICAIF-workshop (Overleaf GitHub Sync, acmart sigconf, XeLaTeX)
scripts/         new.sh (adr|meeting|note|run 템플릿) · sync_figures.sh (figures+bib → paper/)
```

## 자주 쓰는 명령
```bash
python -m pytest tests -q
python -m src.generate.run dryrun --text sample.txt --doc-type cs_transcript --level T2   # LLM 없이 fill+validate
python -m src.generate.run plan --n 100 --out data/corpus/pilot-0.1/plan.jsonl
python -m src.generate.run compose --plan … --model gpt-5.6-sol --out …/raw.jsonl        # OPENAI_API_KEY / OPENAI_BASE_URL
python -m src.generate.run fill --raw …/raw.jsonl --out …/docs.jsonl
scripts/new.sh adr "제목"
git submodule update --remote paper && git add paper   # Overleaf Push 후 포인터 갱신
```

## 지금 상태 (2026-09-13)
완료: 선행연구·포지셔닝(ADR-0001) → 택소노미 v1.2 accepted(ADR-0004) → 생성 방식(ADR-0002) + 파이프라인 스캐폴드(테스트 통과) → 리더보드 14+4(ADR-0005) → venue(ADR-0003) → 논문 골격(paper/main.tex, 컴파일 확인).
**다음 (우선순위):** ① 파일럿 100건 생성 (API 키 필요) + 한울 검수 + 프롬프트 튜닝 ② 이름·주소 사전 확장 (현재 시드 수준) ③ `src/eval/metrics.py` — (tier×kind)×T-level 격자, op별 recall, 조각 partial-overlap, TAB식 de-id 지표, 일관성 ④ 규칙 베이스라인 어댑터 (Presidio ko recognizer 활성, ko-pii) ⑤ 실험 → figure → 논문. 역산 일정은 ADR-0003.

## 알아둘 함정
- `paper/`는 submodule. 본문은 Overleaf에서 쓰고 **Overleaf Push → 레포 포인터 갱신**; 레포에서 figure/bib 넣었으면 **paper push → Overleaf Pull**. 순서 지키기 (`docs/guide/overleaf.md`).
- `paper/main.tex`는 kotex 사용 → XeLaTeX. acmart가 `\anon`을 이미 정의하므로 우리 매크로는 `\anonv`.
- 한국어 모델은 **가입·심사 필요한 API 제외** (HCX-007 제외). OpenRouter 가능(Solar Pro 4) 또는 HF 공개 가중치만.
- T4(encoded 우회)는 의도적으로 제외 — 공격 분포지 DLP 입력 분포가 아님.
- 생성기 모델은 리더보드에 `model_type: generator`로 표기하고 헤드라인 순위 제외.
- 금융분야 가명·익명처리 안내서 PDF는 자동 파싱 실패 — 본문 표를 사람이 확인해야 함 (STATUS 할 일).
