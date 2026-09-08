# Overleaf 연동 가이드

논문 본문은 Overleaf에서 씁니다. 이 레포는 Overleaf 프로젝트를 `paper/` 아래 **git submodule**로 붙여
"이 커밋 시점의 본문은 어떤 버전이었나"를 함께 기록합니다.

## 왜 submodule인가

- Overleaf도 git 저장소입니다 (`https://git.overleaf.com/<project-id>`).
- 본문 이력은 Overleaf에, 연구 맥락 이력은 이 레포에 두고, 둘을 포인터로 연결하는 게 가장 덜 꼬입니다.
- subtree나 복사는 양쪽 편집이 충돌할 때 수습이 어렵습니다.

## 최초 설정 (한 명만 하면 됩니다)

1. Overleaf 프로젝트 → Menu → **Git** 에서 clone URL 복사. Overleaf 계정 설정에서 **Git authentication token** 발급.
2. 레포 루트에서:

```bash
git submodule add https://git.overleaf.com/<project-id> paper
git commit -m "paper: Overleaf submodule 연결"
git push
```

## 매일 쓰는 방법

**본문 편집**: Overleaf 웹에서 그냥 씁니다. 이 레포에서는 안 고칩니다.

**최신 본문을 레포에 기록** (수치·figure를 논문에 반영한 뒤, 또는 주 1회):

```bash
git submodule update --remote paper
git add paper
git commit -m "paper: Overleaf 포인터 갱신 (results 표 반영)"
```

**figure를 Overleaf로 보내기**:

```bash
scripts/sync_figures.sh        # figures/out/*.pdf → paper/figures/ 복사 후 push
```

**bib 동기화**: `literature/papers.bib`가 원본입니다. Overleaf의 `references.bib`는 `sync_figures.sh`가 함께 복사합니다. Overleaf에서 bib를 직접 고치지 마세요 (다음 동기화 때 덮어씁니다).

## 처음 clone한 사람

```bash
git clone <repo-url> kfinpii
cd kfinpii
git submodule update --init
```

Overleaf 토큰이 없으면 `paper/`는 비어 있어도 됩니다. 본문이 필요하면 Overleaf 웹으로 보세요.

## 주의

- `paper/` 안에서 `git commit`/`git push`를 하면 Overleaf로 바로 올라갑니다. 급할 때만.
- Overleaf 무료 플랜은 Git 연동이 안 됩니다. 계정 한 명은 유료여야 합니다 [?] 최신 정책 확인.
