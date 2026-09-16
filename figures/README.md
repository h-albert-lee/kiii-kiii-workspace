# figures

`src/`에 스크립트, `out/`에 산출물. 규칙은 [`docs/guide/figures.md`](../docs/guide/figures.md).

한 줄 요약: **손으로 그린 그림 없음. 숫자는 `experiments/results/`에서만.**

Overleaf 반영: `scripts/sync_figures.sh`

## Main figure

`python figures/src/fig1_overview.py` builds the four-panel T0–T3 overview as
`out/fig1_overview.pdf`, `.svg`, and `.png`. The PDF has a fixed ACM two-column
width and embedded TrueType fonts; it is the manuscript asset. The SVG uses
outlined text for portable editing. Nanum Gothic and its OFL license are bundled
under `assets/fonts/`.

Illustrative text lives in `specs/fig1_overview.yaml`; category counts come from
`taxonomy/taxonomy.yaml`. The examples are synthetic, not measured results or
paired corpus records. T2 uses Korean digit names; T3 isolates structural
fragmentation with Arabic digits, two speakers, and an entity-link bracket.

`concepts/` contains the earlier image-generated layout explorations, not paper
assets. The final diagram is rebuilt from code and does not embed those images.

For figure-only updates, copy just the selected PDF into `paper/figures/` and
sync the relevant LaTeX files. The general sync script also replaces the
bibliography, so do not run it for a figure-only change without checking that diff.
