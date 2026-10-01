# Completed manuscript — 2026-10-01

Paper commit `8d73e63` was created by Overleaf's official outbound GitHub integration. Six sections now report completed results, discussion and conclusion: 12 LLM models / 22 conditions plus 3 baselines. Incomplete Qwen pairs are omitted without numeric imputation. The main table presents strict exact F1 beside the post-hoc observable detection proxy; appendix tables report format/empty outputs, penalized detection P/R/F1, taxonomy groups and ten paired bootstrap contrasts. Original cohorts and execution differences remain explicit. No new inference.

## Research interpretation

D-F1 is a closer observable proxy for PII detection than request-atomic strict F1 in the presence of format failures, not format-independent latent ability. All gold and invalid-item exact-FP penalties remain. Local D-F1 is higher in all ten pairs; strict favors local in nine. Recorded native counts, foreign-runner deployment equivalence and representative pilot calibration are not independently established. These limitations and the post-hoc expansion are disclosed. No score or result source stamp was changed. TWICE/NMIXX citations remain, and anonymous rendering is preserved.

## Editing and QA

Backed up ten source files and all five native Overleaf threads before editing. A native append/revert probe passed. Changes preserve each comment's original text range; no thread was deleted, replied to or resolved. Source readback and document IDs were checked after editing. Local paper was then fast-forwarded from the Overleaf-generated commit, never blindly pushed into Overleaf.

XeLaTeX: zero errors, no overfull boxes, no undefined citations/references. All six PDF pages were rendered and inspected. Main text ends on page 4; references and appendix occupy the remainder (six total). Default margins/fonts were preserved. Twenty-seven template/bibliography/caption warnings remain; no missing results/TODO cells remain. Appendix placement should follow the venue's final submission rules; six total pages must not be described as a four-page PDF.

Local PDF: `output/pdf/kiii-completed-results.pdf`. Ignored native-source/comment/QA backup: `data/paper-review/2026-10-01-final/`. Analysis provenance: `experiments/results/analyses/1001-completed-manuscript-v1/`. Live src/eval code unchanged. 136 tests passed; archived response replay establishes scoring compatibility, not native server/GPU compatibility.
