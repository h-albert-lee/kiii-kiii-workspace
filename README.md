# kfinpii — K-Financial PII Benchmark (Kiii Kiii)

한국 금융 도메인 PII 벤치마크 논문 프로젝트의 **연구 맥락 저장소**입니다.
코드만이 아니라 자료조사, 결정사항, 회의록, 실험 결과, figure, 논문 본문(Overleaf 연동)까지
"이 연구에 대해 우리가 알고 있는 것 전부"를 이 레포 하나에서 찾을 수 있게 하는 것이 목표입니다.

> 처음 오셨다면 이 README → `STATUS.md` → `docs/decisions/` 순서로 읽으면 10분 안에 현재 상황을 파악할 수 있습니다.

## 연구 한 줄 요약

개인정보보호법 + 신용정보법 + 금융분야 가명·익명처리 안내서에 근거한 2-tier PII 택소노미(Legal / Identifiability)로,
long-context · multi-subject 합성 금융 문서에서 **(1) PII 스팬 추출**과 **(2) 비식별화**를 평가하는 벤치마크.
API 모델과 한국어 로컬 LLM을 함께 올린 리더보드 + 분석으로 4페이지 short paper를 씁니다.
자세한 포지셔닝은 [`docs/related_work.md`](docs/related_work.md), 채택 근거는 [`docs/decisions/0001-framing-a.md`](docs/decisions/0001-framing-a.md).

## 디렉토리 구조

```
kfinpii/
├── README.md            ← 지금 이 문서
├── STATUS.md            ← 현황 보드 (매주 갱신: 마일스톤, 이번 주 할 일, 막힌 것)
├── OWNERS.md            ← 누가 무엇을 맡는지
├── docs/                ← 사람이 읽는 문서
│   ├── related_work.md  ← 선행연구 조사 + 포지셔닝 (영어, 논문 related work 원천)
│   ├── decisions/       ← 결정 기록 (ADR). 번호 순, 한 결정 = 한 파일
│   ├── meetings/        ← 회의·논의 기록. 날짜 파일명
│   └── guide/           ← 협업 가이드 (git, Overleaf, 실험 수합, figure)
├── literature/          ← 논문 자료조사
│   ├── papers.bib       ← 공용 bib. Overleaf와 동일 파일 유지
│   └── notes/           ← 논문별 읽기 노트 (템플릿: _template.md)
├── taxonomy/            ← 택소노미 정의 (yaml이 원본, md는 설명)
├── experiments/         ← 실험 설정과 결과 수합
│   ├── configs/         ← 실험 설정 파일
│   └── results/         ← 결과 파일 + leaderboard.csv (마스터 표)
├── figures/             ← 논문 figure
│   ├── src/             ← figure 생성 스크립트 (재현 가능해야 함)
│   └── out/             ← 생성된 pdf/png (Overleaf로 복사되는 파일)
├── src/                 ← 데이터 생성·평가 코드
├── scripts/             ← 잡무 스크립트 (figure 동기화, 노트 생성 등)
└── paper/               ← Overleaf 프로젝트 (git submodule). 설정은 docs/guide/overleaf.md
```

## 무엇을 어디에 쓰나

| 이런 일이 생기면 | 여기에 남깁니다 |
|---|---|
| 카톡·회의에서 뭔가 논의했다 | `docs/meetings/YYYY-MM-DD-주제.md` |
| 방향이나 설계를 결정했다 | `docs/decisions/NNNN-제목.md` (회의록에는 "결정 → ADR 번호"만 링크) |
| 논문을 읽었다 | `literature/notes/저자-연도-키워드.md` + `papers.bib`에 항목 추가 |
| 실험을 돌렸다 | `experiments/results/`에 결과 파일, `leaderboard.csv`에 한 줄 |
| figure를 만들었다 | `figures/src/`에 스크립트, `figures/out/`에 산출물, `scripts/sync_figures.sh`로 Overleaf 반영 |
| 논문 본문을 썼다 | `paper/` (Overleaf)에서 직접. 이 레포에는 submodule 포인터만 갱신 |
| 진행 상황이 바뀌었다 | `STATUS.md` 갱신 |

## 시작하기

```bash
git clone <repo-url> kfinpii
cd kfinpii
git submodule update --init   # Overleaf 연동 후부터 필요
```

협업 규칙(브랜치, 커밋 메시지, PR)은 [`docs/guide/workflow.md`](docs/guide/workflow.md)에 있습니다. 짧습니다. 한 번만 읽어주세요.

## 원칙

- **미검증은 질문으로, 검증된 것만 문장으로.** 확인 안 된 수치·주장은 `[?]`를 붙여 남깁니다.
- **결정은 기록으로.** 카톡에서 정한 것도 ADR로 옮겨야 결정입니다.
- **결과는 재현 가능하게.** 결과 파일에는 반드시 config와 커밋 해시를 함께 남깁니다.
- **논문 본문의 원천은 이 레포.** related work, 수치, figure는 여기서 나가서 Overleaf로 들어갑니다. 반대 방향은 없습니다.

## 참여자

AIM Intelligence · 토스증권. 역할은 [`OWNERS.md`](OWNERS.md).
