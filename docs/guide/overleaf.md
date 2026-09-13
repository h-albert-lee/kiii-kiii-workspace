# Overleaf 연동 가이드

논문 본문은 Overleaf에서 씁니다. Overleaf 프로젝트는 **GitHub 연동**(Overleaf ↔ `github.com/h-albert-lee/ICAIF-workshop`)이 걸려 있고,
이 레포는 그 GitHub 레포를 `paper/` **submodule**로 붙여 "이 커밋 시점의 본문이 어떤 버전인가"를 함께 기록합니다.

## 세 곳의 관계

```
Overleaf 프로젝트  ⇄ (Overleaf GitHub Sync: Menu → GitHub → Push/Pull)  ⇄  github.com/h-albert-lee/ICAIF-workshop  ⇄  kfinpii/paper (submodule)
```

- 본문 이력은 ICAIF-workshop 레포에, 연구 맥락 이력은 kfinpii에. 둘은 submodule 포인터로 연결.
- **Overleaf GitHub Sync는 자동이 아닙니다.** Overleaf 메뉴에서 "Push Overleaf changes to GitHub" / "Pull GitHub changes into Overleaf"를 눌러야 반영됩니다.

## 매일 쓰는 방법

**본문 편집 (권장 경로)**: Overleaf 웹에서 씁니다 → 작업 마무리에 Overleaf 메뉴 → GitHub → **Push** → 이 레포에서 포인터 갱신:

```bash
git submodule update --remote paper
git add paper && git commit -m "paper: Overleaf 포인터 갱신 (results 표 반영)"
```

**레포에서 본문 편집 (figure·bib·표 자동 반영 시)**: `paper/` 안에서 커밋·push → Overleaf 메뉴 → GitHub → **Pull**. 이때 Overleaf에 미push 변경이 있으면 충돌하므로, 항상 **Overleaf Push 먼저, 레포 Pull 다음**.

**figure·bib를 Overleaf로**:

```bash
scripts/sync_figures.sh        # figures/out/*.pdf → paper/figures/, literature/papers.bib → paper/references.bib, push
# 그 다음 Overleaf 메뉴 → GitHub → Pull
```

`paper/references.bib`는 복사본입니다. 원본은 `literature/papers.bib`. Overleaf에서 bib를 직접 고치지 마세요 — 다음 sync 때 덮어씁니다.

## 처음 clone한 사람

```bash
git clone --recurse-submodules <kfinpii-url>
# 이미 clone했다면
git submodule update --init
```

## 컴파일

`main.tex`가 `kotex`(한글 예시)을 쓰므로 Overleaf 컴파일러를 **XeLaTeX** 또는 LuaLaTeX로 설정하세요 (Menu → Compiler). 제출 모드는 `\documentclass[sigconf,anonymous,review]{acmart}`, 카메라레디는 `[sigconf]` + `\anonymousfalse`.

## 주의

- `paper/` 안에서 `git push`하면 GitHub로 바로 올라가고 Overleaf Pull 전까지는 Overleaf가 모릅니다.
- Overleaf GitHub Sync는 유료 플랜 기능입니다. 연동 계정(한울) 한 명은 유료 유지.
- 익명 심사: 초고에 레포 URL·소속·"Powered by …" 표기 금지. `\anonv{리뷰용}{카메라레디용}` 매크로 사용.
