# Kiii-Kiii — arXiv preprint

**Prepared 2026-10-04; not yet submitted to arXiv.** Nine pages, based on the
reference- and layout-corrected SAC #362 source at `bd2547b`. The SAC submission
and Sara's workshop project remain unchanged.

[Separate Overleaf project](https://www.overleaf.com/project/6ac1bc35b1b29fb31b8139fc)
— main file `main.tex`, **XeLaTeX / TeX Live 2025**. Edit natively and export
outbound to preserve this project's comments. Do not sync into either venue project.

## Public author presentation

1. Eunbin Shin — LG AI Research; Band Foundation (equal first)
2. Sara Yu — KT; Band Foundation (equal first)
3. Seonghyun Kim — Toss Securities; Band Foundation
4. MinKyeong Shin — Shinhan Securities; Band Foundation
5. Yewon Hwang — kakao mobility; Band Foundation
6. Hanwool Lee — Seoul National University; AIM Intelligence; Band Foundation (corresponding)

Public contact: **www.instagram.com/band_foundation**. No personal email
addresses in the manuscript. Institutional spellings and roles follow the
operator's author record. Postal addresses and ORCIDs have not been inferred.
The author block disables ACM's mandatory postal-field check for this non-ACM
preprint; it does not suppress citation or compilation checks.

The paper links the public dataset only. **Do not add the project code repository
link to this manuscript** (operator preference, 2026-10-04). Dataset CC BY-NC 4.0
is distinct from the paper license; select the paper license separately at upload.
AI writing-assistance disclosure and the Kanana attribution are retained.

## Artifacts and validation

- PDF: `output/pdf/kiii-arxiv-preprint.pdf` from the workspace root.
- Upload source: `output/pdf/kiii-arxiv-source.zip` (22 files).
- Native export: `output/pdf/kiii-arxiv-overleaf-export.zip` (21 files).
- [Hashes and QA record](notes/preparation.json).

The upload archive contains the native source plus compiled `main.bbl`; it omits
this README, internal notes, logs, PDFs of the full manuscript and credentials.
All four figure PDFs, the bibliography and scientific sections are unchanged
from SAC except the conclusion's public data/attribution statements. Only
`main.tex` and `sections/07_conclusion.tex` differ in the native source.

Compiled successfully in Overleaf with TeX Live 2025: zero errors, no missing
glyphs, undefined references or overfull boxes. Eleven UI warnings remain:
ten missing bibliography publication-field warnings and the intentional
figure-only page 6. All nine pages were rendered and inspected. Figures are
on pages 2, 5 and 6; Table 2 is on page 7; references are uninterrupted on pages
8–9. The arXiv server itself has not yet compiled or accepted this source.

## Rebuild and package

From this directory with a TeX Live 2025 installation including ko.TeX and
UnBatang, run XeLaTeX → BibTeX → XeLaTeX → XeLaTeX on `main.tex`.
Fonts are addressed by file name. The checked-in `main.bbl` is the compiled
bibliography from the verified Overleaf build; regenerate it after citation edits.

From the workspace root, this packages only the pinned source files:

```sh
python3 - <<'PY'
import json, zipfile
from pathlib import Path
root = Path('papers/arxiv')
names = json.loads((root / 'notes/preparation.json').read_text())['source_files']
with zipfile.ZipFile('output/pdf/kiii-arxiv-source.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for name in sorted(names):
        z.write(root / name, name)
PY
```

Regenerate the QA record after any change; old hashes do not certify a new build.
Before actual arXiv publication, inspect the server-generated PDF and complete
its metadata, category and license fields. This preparation record is not a
submission receipt or an arXiv identifier.
