# Manuscript layout audit — 2026-09-16

Reviewed all four pages of the Overleaf XeLaTeX manuscript after inserting Figure 1.

## Fixes

- Table 1 used three non-wrapping columns inside a single-column float; category lists and the policy column ran off the page. Rebuilt it with wrapping columns and moved policies below the table. All 36 categories remain: 17 Legal identifiers, 7 Legal attributes, and 12 Identifiability attributes.
- Enabled breaks in long schema labels, operation names, URLs, and the appendix specification path. Shortened the illustrative slot to a valid minimal example.
- Replaced manual subtitle formatting with ACM's native subtitle and supplied a short running title.
- Removed unsupported small-cap styling from the dataset macro; mapped Hangul emphasis to available upright font faces and used supported circled statutory clause glyphs.
- Added a last-pass line-breaking allowance without changing ACM margins, font sizes, line spacing, or paragraph spacing.

## Validation and publication

- Paper commits: `90cd071` (table and typography), `0aef4b2` (Hangul font shapes).
- Pushed to the manuscript repository and pulled into [Overleaf](https://www.overleaf.com/project/6a9fd3f13552b8aca9a09304).
- Final XeLaTeX build: 4 pages, 0 errors, no overfull boxes, no font-shape fallback or undefined-reference warnings in the displayed compiler log.
- Rendered and inspected all four pages; Table 1, Figure 1, headers, Korean examples, and body columns remain readable and unclipped.
- Final local preview: `output/pdf/kiii-paper-layout-fixed.pdf`.

## Still pending

The manuscript is a research draft. Experimental results and appendix TODOs remain. The compiler still reports 32 warnings, primarily incomplete bibliography metadata and the existing ACM-reference-format setting, plus 24 underfull-box informational entries. These are not unresolved citations or clipped content. No experimental results or missing bibliographic facts were invented during this layout pass.
