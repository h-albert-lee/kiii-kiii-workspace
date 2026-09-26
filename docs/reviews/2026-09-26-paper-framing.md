# Manuscript framing revision — 2026-09-26

Editorial scope: sharpen the problem, contribution statements and interpretation of the existing experiment. No dataset, labels, prompts, scoring code or live experiment settings changed. The medium-model roster follows ADR-0035 rather than a new decision in the manuscript.

## Argument

The paper asks how wider document context affects recovery of identifiers and contextual attributes **under an explicit Korean financial detection policy and a fixed output task**, across input variations. Long input capacity alone does not establish that a model can enumerate all sensitive spans within a bounded response.

The three contributions now describe what the benchmark enables:

1. An auditable 36-category detection policy: statutory grounds and additional identifiability concerns, with detection targets distinguished from masking metadata and legal obligations.
2. A controlled financial testbed: 1,440 documents, 218,664 spans, ten types, multiple subjects and T0–T3 variation, with code-generated identifiers and provenance.
3. A matched full/local context evaluation: identical target regions and output budgets, common capacity checks and explicit failure accounting.

This is a benchmark and evaluation-design contribution; neither a new detector nor an established empirical superiority claim. Comparative findings remain pending. The four-page paper should ultimately use one compact main comparison and one context-effect figure; the current analysis-plan placeholder must be replaced with finalized results rather than accumulated alongside them.

## Manuscript edits

- Abstract/introduction lead with the evaluation problem and the context question, instead of leading with a catalogue of corpus features or model counts.
- Related work is organized around detection/anonymization, Korean PII and Korean financial evaluation. TWICE and NMIXX remain explicitly cited in third person. Removed unsupported exclusivity and the assertion that court judgments do not contain financial attributes.
- Construction distinguishes permitted T-level operations from paired rewrites and a design-based regex flag from measured detector performance. No causal T-level effect is claimed.
- Setup reflects the three core local LLMs and two exploratory medium models, plus three baselines. The extension follows qualitative format-failure reports; Kanana sizes also differ in model generation. Existing poor runs are retained.
- Results plan connects taxonomy coverage, full/local changes and output reliability. Adapter faults, model formatting and truncation require separate diagnosis. Full response retention is written as a protocol requirement, not as verified universal logging.
- Conclusion states the resource contribution and limits: synthetic representativeness, annotation uncertainty, common-capacity exclusions, generator/length confounding and the distinction between extraction and legal compliance/disclosure risk.

## Preservation and validation

Read all five existing Overleaf comment threads and backed up source, full message bodies and anchor ranges under ignored `data/paper-review/2026-09-26/`. Before editing, all nine inspected source files matched the local paper checkout, and Overleaf reported no new GitHub commits since its last merge. Edits use native CodeMirror change transactions, split around existing comment anchors. No thread was replied to or resolved. A file-switch state delay was handled by reloading and rechecking exact source and document ID before further edits.

Final compile, visual checks and sync receipt are recorded below after completion.

## Completion

- Paper commit: `1d96f32` — `Sharpen financial privacy motivation, contributions and matched context evaluation`, exported through Overleaf → GitHub. The local paper checkout fast-forwarded cleanly; all seven revised files match the verified proposed sources.
- After final sync, all five original thread IDs and full message bodies remain identical, and every anchor still points to the same original substring in the same document. No comments resolved or replied to.
- XeLaTeX: zero errors, zero overfull boxes, no undefined references/citations; 23 existing bibliography/template warnings and underfull-box informational messages remain.
- Five-page compiled PDF visually checked on every page. Main text ends on page 4; references and draft appendix account for the rest. The results section and appendix still contain explicit draft TODOs, so this is not a submission-ready final paper. The full result table/figure still needs a page-budget check when substituted for the analysis plan.
- TWICE/NMIXX render correctly. Anonymous header/author block verified; author names in third-person bibliography entries are preserved. No identifying affiliations or public dataset/repository links appear in the anonymous body.
- Final PDF and review backups: ignored `data/paper-review/2026-09-26/`. No detector calls or generation runs performed; executable evaluation code is unchanged.
