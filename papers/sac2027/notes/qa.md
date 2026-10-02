# SAC draft QA — 2026-10-02

Status: internal anonymous draft, not submitted. Final hashes are recorded in
`draft-artifacts.json` and must be refreshed after substantive edits.

- Tectonic 0.17.0 (XeTeX) completed TeX/BibTeX/reruns; **8 total pages**,
  including references; US Letter, ACM sigconf. No text font/margin compression.
- All eight pages of the updated error-analysis draft rendered with Poppler and
  visually inspected. Four vector figures and two tables are readable with
  no clipping or overlap. Figure-label/footer collisions found during preview
  were corrected before final compilation.
- No overfull boxes, undefined references/citations, missing-character reports
  or TeX errors in the final console log. Font-request/underfull and bibliography
  warnings remain; this is not a claim of a warning-free build.
- PDF metadata has no named author. Body scan excludes author names,
  affiliations, identifying dataset/repository links and TODO placeholders.
  Ordinary third-person TWICE/NMIXX citations and bibliographic names remain.
- Figure inputs match pinned hashes. Builder checks 25 unique conditions,
  75 group scores against archived counts and ten original-cohort strict
  contrasts. Strict CIs are copied from the frozen paired table. D-F1
  differences are point estimates, with no invented CIs. Missing versus zero
  and baseline N/A are preserved; heatmap scales are shared.
- Error-atlas inputs conserve all gold and invalid-item penalties across 22
  completed LLM conditions. Five purposively stratified illustrations verify
  original raw/gold hashes, reconstructed request hashes, parsed-item outcomes
  and gold priority buckets. No new inference or score adjustment.
- All PDF fonts are embedded; no Type 3 fonts. Anonymous source bundle includes
  the four referenced figures, excluding the companion taxonomy heatmap.
- Original workshop source remains at `8d73e63` with a clean submodule;
  no Overleaf project/comment mutation was performed in this task.
- Anonymous source archive contains only referenced TeX/BibTeX, ACM
  class/style and PDF figures. Internal notes, local paths, operator records,
  data and credentials are excluded. ZIP integrity check passed.
- `python -m pytest tests -q`: **142 passed**. These are offline tests, not
  evidence of native API/GPU compatibility or new inference.

The source is an expanded manuscript starting point, not final coauthor signoff.
Sara's later workshop corrections, the final SAC author roster and the actual
EasyChair form/upload verification remain in `submission-checklist.md`.

## Official format / remote compile follow-up

See `format-verification.md`: official class and bibliography style match byte
for byte; bold captions are the class default. Abstract shortened to 172 words,
keywords to five. Recompiled and inspected all eight local and all eight
Overleaf pages; all 21 uploaded source files match the downloaded ZIP.
Overleaf XeLaTeX / TeX Live 2026: zero errors, 24 documented warnings.

## English-gloss follow-up — 2026-10-02

Added concise English glosses to the Korean dictated-digit example, statutory
name/address/telephone terms, mixed Korean numeral example and separator tokens;
Figure 1's caption spells out the Korean digit sequence in English. No data,
results or protocol changed. Native Overleaf review panel showed no comments
or suggestions before edits. All 21 exported sources were compared with the
intended files; native trailing blank lines were retained locally. The final
native XeLaTeX PDF has 8 pages, 0 errors and the same 24 warnings; all eight
pages were rendered and inspected. The stable delivered PDF/source ZIP now
use the native Overleaf exports, with updated artifact hashes.

Read the other session's shared `docs/authors.yaml` and author handoff. Preserve
its six-author order, equal-first roles and corresponding-author role in
submission metadata; author identities remain excluded from this anonymous
PDF/source bundle. That session's author/receipt files were not changed here.
