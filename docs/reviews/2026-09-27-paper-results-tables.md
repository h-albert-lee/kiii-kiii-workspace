# Result-table preparation — 2026-09-27

Paper commit: `d876752` (Overleaf → GitHub). Scope: `sections/06_results.tex` and `sections/A_appendix.tex` only. No inference, metric changes, live evaluator edits or unverified headline ranking.

## Prepared layout

- Main Table 2: full/local strict F1, document-level baseline F1 and LLM request failure rates. Core and exploratory extension rows are separated. All entries await completed common-cohort/provenance review, explicitly marked P; inapplicable entries are dashes.
- Appendix Table 3: category-group precision/recall/F1 for L-identifiers, L-attributes and I-attributes across all 13 planned conditions. Pending values are not zeros.
- Appendix Table 4: paired full−local ΔF1 and 95% document-bootstrap CI for the five LLMs. No unverified effect estimates or illustrative numeric results inserted.
- Appendix Table 5: actual archived-response diagnostics for four completed conditions, with strict/itemwise/fence/character F1, invalid-item exact-FP penalties, penalized precision/recall and strict request failure rate. All rows match the hashes and values in [table input provenance](2026-09-27-paper-table-inputs.json). Clearly provisional: original native count/cohort artifacts still need independent review. No pilot scores included.

The result narrative now explains the comparison and secondary metrics instead of a red leaderboard TODO. The original `main leaderboard` comment anchor is retained verbatim in its new sentence. The overview figure, taxonomy table, TWICE/NMIXX citations and prior framing remain unchanged. [Contributor handoff](../guide/paper-results-handoff.md) maps each future table cell to its source field and aggregation rule.

## Preservation and verification

Read and backed up all five Overleaf threads, message bodies, document sources and anchor ranges before editing. All nine initially inspected sources matched local paper HEAD, and GitHub integration reported no newer incoming commits. Backed up the appendix after verifying its actual document ID. A small append-and-revert probe established native editor readback before substantial edits.

Edits used native CodeMirror transactions; the results replacement was split around the existing anchor, and appendix additions preserved the original prefix. A delayed/stale document-range state during tab switching was detected before the appendix write, then resolved by reloading and checking the document ID and exact source. No comment was replied to, resolved or removed.

After Overleaf's official outbound GitHub sync and local fast-forward, reloaded each commented file and verified all five original thread IDs, full message bodies, document IDs and anchored substrings. The only shifted anchor is the expected new position of `main leaderboard`. Both changed sources exactly match the verified proposals.

## PDF and remaining work

XeLaTeX completed with **0 errors, 0 overfull boxes and no undefined references/citations**. All six PDF pages were rendered and visually checked. Main text ends on page 4; references continue on page 5 and the final appendix tables occupy page 6. Margins, base fonts and line spacing were not compressed. A nonfloating paired table avoids a lost float/blank-page issue in the draft's two-column end matter. Existing bibliography/template warnings and caption/spacing informational warnings remain (27 warnings total); there are no unresolved table references or clipped cells.

Anonymous PDF header verified; no identity-bearing organization or dataset/repository URL appears in the body. Third-person bibliography author names remain. The PDF is a preparation draft: Tables 2–4 are pending, existing appendix A–C TODOs remain, and final comparative findings/conclusion still require verified results. It is not ready for submission.

Local PDF: `output/pdf/kiii-results-tables-draft.pdf` (not committed). Ignored preservation/QA backups: `data/paper-review/2026-09-27-results/`. No new runtime code was changed, so validation consisted of input hash/value checks, source diffs, Overleaf compilation, complete PDF visual inspection and comment-preservation checks rather than another detector test run.
