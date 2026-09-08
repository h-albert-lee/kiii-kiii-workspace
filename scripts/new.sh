#!/usr/bin/env bash
# 템플릿에서 새 문서 만들기.
#   scripts/new.sh adr "generator-model"        → docs/decisions/0002-generator-model.md
#   scripts/new.sh meeting "taxonomy-review"    → docs/meetings/2026-09-15-taxonomy-review.md
#   scripts/new.sh note hahm2025thunderdeid     → literature/notes/hahm2025thunderdeid.md
#   scripts/new.sh run                          → experiments/configs/0915-01.yaml
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
kind="${1:-}"; name="${2:-}"
today="$(date +%F)"

case "$kind" in
  adr)
    [[ -n "$name" ]] || { echo "제목 필요"; exit 1; }
    last=$(ls "$ROOT/docs/decisions" | grep -E '^[0-9]{4}-' | sort | tail -1 | cut -c1-4)
    next=$(printf "%04d" $((10#$last + 1)))
    out="$ROOT/docs/decisions/$next-$name.md"
    sed "s/ADR-NNNN/ADR-$next/; s/YYYY-MM-DD/$today/" "$ROOT/docs/decisions/0000-template.md" > "$out" ;;
  meeting)
    [[ -n "$name" ]] || { echo "주제 필요"; exit 1; }
    out="$ROOT/docs/meetings/$today-$name.md"
    sed "s/YYYY-MM-DD/$today/" "$ROOT/docs/meetings/_template.md" > "$out" ;;
  note)
    [[ -n "$name" ]] || { echo "bib key 필요"; exit 1; }
    out="$ROOT/literature/notes/$name.md"
    sed "s/author2025keyword/$name/" "$ROOT/literature/notes/_template.md" > "$out" ;;
  run)
    d="$(date +%m%d)"
    n=$(ls "$ROOT/experiments/configs" 2>/dev/null | grep -c "^$d-" || true)
    id="$d-$(printf "%02d" $((n + 1)))"
    out="$ROOT/experiments/configs/$id.yaml"
    sed "s/MMDD-NN/$id/" "$ROOT/experiments/configs/_template.yaml" > "$out" ;;
  *)
    echo "사용: scripts/new.sh {adr|meeting|note|run} [이름]"; exit 1 ;;
esac
echo "만들었습니다: ${out#$ROOT/}"
