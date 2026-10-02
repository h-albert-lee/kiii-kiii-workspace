# SAC draft QA — 2026-10-02

Status: internal anonymous draft, not submitted. Final hashes are recorded in
`draft-artifacts.json` and must be refreshed after substantive edits.

- Tectonic 0.17.0 (XeTeX) completed TeX/BibTeX/reruns; **8 total pages**,
  including references; US Letter, ACM sigconf. No text font/margin compression.
- All eight pages rendered with Poppler and visually inspected. Five result/
  taxonomy tables and two figures are readable with no clipping or overlap.
  The context figure's height was adjusted to remove a float-page overflow;
  the final affected page was rendered and inspected again.
- No overfull boxes, undefined references/citations, missing-character reports
  or TeX errors in the final console log. Font-request/underfull and bibliography
  warnings remain; this is not a claim of a warning-free build.
- PDF metadata has no named author. Body scan excludes author names,
  affiliations, identifying dataset/repository links and TODO placeholders.
  Ordinary third-person TWICE/NMIXX citations and bibliographic names remain.
- Figure inputs match pinned hashes. The new figure contains ten original-cohort
  pairs; strict CIs are copied from the frozen paired table. D-F1 differences
  are point estimates, with no invented CIs.
- Original workshop source remains at `8d73e63` with a clean submodule;
  no Overleaf project/comment mutation was performed in this task.
- Anonymous source archive contains 18 files: referenced TeX/BibTeX, ACM
  class/style and PDF figures. Internal notes, local paths, operator records,
  data and credentials are excluded. ZIP integrity check passed.
- `python -m pytest tests -q`: **136 passed**. These are offline tests, not
  evidence of native API/GPU compatibility or new inference.

The source is an expanded manuscript starting point, not final coauthor signoff.
Sara's later workshop corrections, the final SAC author roster and the actual
EasyChair form/upload verification remain in `submission-checklist.md`.
