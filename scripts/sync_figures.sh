#!/usr/bin/env bash
# figures/out/*.pdf 와 literature/papers.bib 를 Overleaf submodule(paper/)로 복사하고 push.
# 사용: scripts/sync_figures.sh [-n]   (-n: 복사만 하고 push 안 함)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PAPER="$ROOT/paper"
DRY=0
[[ "${1:-}" == "-n" ]] && DRY=1

if [[ ! -f "$PAPER/.git" && ! -d "$PAPER/.git" ]]; then
  echo "paper/ 가 submodule로 연결되어 있지 않습니다. docs/guide/overleaf.md 를 보세요." >&2
  exit 1
fi

echo "▶ Overleaf 최신 상태로 맞추기"
git -C "$PAPER" pull --ff-only

echo "▶ figure 복사"
mkdir -p "$PAPER/figures"
cp "$ROOT"/figures/out/*.pdf "$PAPER/figures/" 2>/dev/null || echo "  (복사할 pdf 없음)"

echo "▶ bib 복사"
cp "$ROOT/literature/papers.bib" "$PAPER/references.bib"

if [[ $DRY -eq 1 ]]; then
  echo "dry-run: push 생략"; exit 0
fi

if git -C "$PAPER" diff --quiet && git -C "$PAPER" diff --cached --quiet && [[ -z "$(git -C "$PAPER" ls-files --others --exclude-standard)" ]]; then
  echo "변경 없음"; exit 0
fi

git -C "$PAPER" add figures references.bib
git -C "$PAPER" commit -m "sync figures/bib from kfinpii $(git -C "$ROOT" rev-parse --short HEAD)"
git -C "$PAPER" push
echo "▶ 레포의 submodule 포인터 갱신"
git -C "$ROOT" add paper
echo "완료. 'git commit -m \"paper: figure/bib 동기화\"' 로 마무리하세요."
