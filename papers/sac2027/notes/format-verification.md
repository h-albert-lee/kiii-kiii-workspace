# SAC submission-format and Overleaf check — 2026-10-02

Status: anonymous review draft checked and uploaded; **not submitted** and not
camera-ready certified. Workshop project/comments were not edited.

## Live project

[Kiii-Kiii — SAC 2027 AIFT](https://www.overleaf.com/project/6abf20099c6d0b7f48e49e71)
was newly created from the anonymous source ZIP. Main document `main.tex`,
**XeLaTeX**, TeX Live **2026**. The initial default pdfLaTeX compile was
superseded by the verified XeLaTeX compile. Downloaded source contains exactly
21 files, all byte-identical to the upload. Downloaded PDF: 8 pages, US Letter,
searchable and unencrypted, all fonts embedded, no Type 3 fonts. All eight
remote PDF pages were rendered and visually checked. It is a separate project
with no automatic GitHub connection configured. Future edits should be native
Overleaf edits followed by outbound source export/sync; preserve any new
comments. Do not reimport a replacement project to synchronize later edits.

## Official evidence checked

- [Regular-paper submission](https://sigapp.org/sac/sac2027/submission.php):
  double-blind review; EasyChair; regular-paper initial submission.
- [Author Kit](https://sigapp.org/sac/sac2027/authorkit.php): full papers 8 pages,
  with an option for 2 additional pages. This draft stays at 8 total including
  references and authorizes no extra-page fee.
- [Author Kit PDF](https://sigapp.org/sac/sac2027/authorkit/author-kit-2027-July11.pdf):
  explicitly a **camera-ready** guide. It specifies searchable, unencrypted
  US Letter PDF, embedded fonts, 0.75-inch side margins / 1-inch top-bottom,
  abstract 100–200 words, and no more than five keywords. We adopt the abstract
  and keyword limits conservatively for this review draft. Camera-ready author,
  rights/DOI and registration instructions are not initial-upload requirements.
  Its legacy START wording is superseded by the live EasyChair submission link.
- [SAC LaTeX ZIP](https://sigapp.org/sac/sac2027/authorkit/ACM_SAC_2027_Article_Template.zip):
  `acmart.cls` and `ACM-Reference-Format.bst` are byte-identical to our files.
  The supplied document uses `sigconf`. Its generic ACM comments also mention
  manuscript/review modes; no SAC-specific mandatory line-number option was
  found on the checked live submission page. We retain anonymous `sigconf`,
  without inventing a requirement to use generic single-column review mode.
- [AIFT](https://academicworkshops.github.io/AIFT/) delegates formatting,
  anonymity and page limits to SAC. Its old dates lag the
  [main site's Sept 30 notice](https://sigapp.org/sac/sac2027/index.php), which
  extends submission to October 16, 2026 (EST as printed; exact hour unknown).

## Caption question and corrections

The official, unchanged class sets both `labelfont={bf}` and `textfont={bf}`
for conference captions (`acmart.cls`, lines 885–886). **Whole bold captions
are the template default**, not an accidental global bold command. We did not
add a caption override. Tables have captions above; figures below. Every figure
has an accessibility description.

The former abstract had approximately 222 whitespace-delimited words; it is
now **172**, preserving dataset/scope/results and proxy limitations. Keywords
were reduced from 7 to **5**. These are the only manuscript-content changes in
this format pass. No results, figures, evaluator or bibliography facts changed.
Body type size, margins and line spacing retain the official class defaults.
Local and Overleaf PDFs both remain eight pages. Anonymous author metadata and
body checks pass; third-person prior-work citations stay intact.

## Remaining pre-submission / camera-ready work

The Overleaf compile reports **0 errors, 24 warnings**, plus 28 informational
underfull-box messages. Warnings: 22 BibTeX metadata omissions, one suppressed
ACM reference-strip warning, one automatic column-balance warning. No overfull
box, undefined reference/citation or missing-character message was found in
the captured log headings. These are not all equivalent to submission failure:

- Bibliography metadata (volumes/pages/publishers/addresses) still needs a
  source-verified completeness pass; no values were invented to silence it.
- ACM reference strip, actual authors, rights text and DOI are intentionally
  absent from this anonymous draft. Restore verified publishing metadata if
  accepted; do not present this file as camera-ready compliant.
- Automatic last-page balancing warns because references start in the second
  column. Visual inspection found no clipping; final layout may change after
  bibliographic or coauthor edits and must be checked again.
- Final coauthor review, workshop corrections, submission form requirements
  and final PDF upload/download verification remain outstanding.

Hashes of official downloads and delivered local/Overleaf artifacts are in
`format-verification.json` and `draft-artifacts.json`. No new inference was run.
