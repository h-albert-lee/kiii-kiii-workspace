# Kiii² — SAC 2027 AIFT submission workspace

**Independent anonymous draft; not submitted.** Workshop polishing remains in
the existing `paper/` / Overleaf project. This folder starts from workshop
commit `8d73e63`, not an uninspected copy of Sara's later live edits.

## Start here

1. Read root `AGENTS.md`, ADR-0038 and [ADR-0039](../../docs/decisions/0039-sac2027-submission-preparation.md).
2. Read [the frozen completed-run report](../../experiments/results/analyses/1001-completed-manuscript-v1/REPORT.md).
3. Edit this standalone `main.tex` and `sections/`. Do not redirect the workshop
   sync script or push this folder into its Overleaf project.
4. Read [ADR-0040](../../docs/decisions/0040-sac-error-analysis.md) and the
   [error-analysis report](../../experiments/results/analyses/1002-sac-error-analysis-v1/REPORT.md)
   for conserved all-gold partitions and five hash-verified illustrative cases.
5. Use [submission checklist](notes/submission-checklist.md) and
   [claim/evidence ledger](notes/claim-evidence.md). No new inference.

Target: SAC 2027 **AIFT**, anonymous ACM sigconf, **8 total pages including
references**. Official extended deadline **Oct 16, 2026 (EST as printed)**;
exact hour is not established. Internal target Oct 14 KST. The operator reports
Prof. Yongjae Lee's confirmation that workshop/SAC parallel submission is okay.
This does not mean either submission has been performed here.

## What differs from the workshop snapshot

- The fixed core/halo ownership and exact quotation protocol are explained
  formally, including unrepresentable spans and all-gold denominators.
- Strict extraction, structural compliance, grounding and D-F1 receive their
  own methods section. No claim of latent format-independent ability.
- Four coordinated vector figures cover the benchmark design, strict/D score
  comparison with format compliance, ten paired context contrasts and all-gold
  error partitions. A fifth taxonomy coverage figure remains a companion asset. The full diagnostic table stays in the body; numerical source
  tables retain group P/R/F1 and exact paired intervals.
- Discussion separates empirical observations from speculative mechanisms
  and describes which conclusions the execution evidence cannot support.
- TWICE/NMIXX references are retained using ordinary third-person citations.

## Rebuild

From the workspace root, with matplotlib installed:

```sh
MPLCONFIGDIR=/tmp/kiii-mpl .venv/bin/python papers/sac2027/scripts/build_publication_figures.py
mkdir -p output/pdf/sac2027-build
tectonic -X compile papers/sac2027/main.tex --outdir output/pdf/sac2027-build --keep-logs
cp output/pdf/sac2027-build/main.pdf output/pdf/kiii-sac2027-draft.pdf
```

Or compile `main.tex` with XeLaTeX → BibTeX → XeLaTeX twice from this folder.
The source requires ko.TeX and UnBatang fonts, available in the Tectonic/TeX
Live bundle. The bundled `acmart.cls`/bibliography style are copied unchanged
from the existing source; use the venue's current template requirements for
the final preflight. No margins, font sizes or line spacing are compressed to
meet the page budget.

`notes/source-snapshot.json` pins the workshop starting point.
`notes/analysis-inputs.json` pins completed analysis inputs; the figure builder
refuses changed input hashes. `notes/error-analysis-inputs.json` pins the offline error partitions. The builder only visualizes existing statistics. It does
not recalculate CIs or bypass any cohort/export gate. Kanana-1.5-8B retains
1,438 documents, all others 1,440. D-F1 contrasts have no plotted CIs.

[Figure design and reading guide](notes/figure-design.md). The five figures
are exported as embedded-font PDF, editable SVG and PNG previews. The overview
needs an installed Korean font (Arial Unicode MS or Noto Sans CJK); fonts are
not redistributed. The other figures use Matplotlib's bundled DejaVu Sans.
The original workshop `fig1_overview.pdf` remains a historical reference and
is excluded from the current anonymous source archive because it is unused.

The local PDF is `output/pdf/kiii-sac2027-draft.pdf` in the workspace root;
build products are excluded from version control. The anonymous source bundle
contains only TeX/BibTeX, the ACM class/style and referenced PDF figures, not
internal notes, operator identities or raw artifacts.

## Coordination with Sara

Sara owns workshop polishing. When she finishes, export through native
Overleaf → GitHub, record the new commit, inspect the diff against `8d73e63`
and port relevant corrections selectively. Native comments live in Overleaf;
Git source copies do not preserve comment threads in the new draft. The
existing five threads remain untouched in the workshop project. A SAC
Overleaf project has not yet been created. Create a distinct project when
moving this draft into collaborative editing; use native edits and outbound
sync there as well.
