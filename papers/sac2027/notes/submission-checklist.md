# SAC 2027 AIFT submission checklist

Status: preparation only, 2026-10-02. No Kiii² EasyChair record created.

## Venue facts

- [Main site](https://sigapp.org/sac/sac2027/index.php): Sept 30 extension to
  **Oct 16, 2026 (EST)**. No exact cutoff hour; internal target Oct 14 KST.
- [AIFT](https://academicworkshops.github.io/AIFT/): financial NLP, synthetic
  financial data, privacy, reliability and compliance are in scope. Its old
  Oct 2 deadline has not caught up with the main notice.
- [Submission](https://sigapp.org/sac/sac2027/submission.php): regular paper,
  double blind, EasyChair. Use the official link on this page.
- [Author kit](https://sigapp.org/sac/sac2027/authorkit.php): 8 pages normally,
  up to 2 additional; we target 8 total and do not authorize extra-page fees.
- Notification Nov 20, camera-ready Dec 11, meeting Apr 5–9 in Gwangju.

## Prepared locally

- [x] Separate SAC source based on a pinned workshop commit.
- [x] Completed-run scope fixed: 15 systems / 25 conditions; no new inference.
- [x] Expanded protocol, diagnostics, discussion and paired-context figure.
- [x] Original cohorts, primary scores and provenance limitations retained.
- [x] Operator-reported parallel-submission confirmation recorded in ADR-0039.
- [x] Title/abstract/keywords available in anonymous manuscript source.

## Before submission

- [ ] Selectively integrate relevant final workshop corrections after Sara's
  native Overleaf → GitHub export; record that exact commit.
- [ ] Coauthors review the SAC version and approve the final author list,
  order, affiliations and corresponding author. Do not infer the roster from
  the old two-author template or from NMIXX.
- [ ] Review category boundaries and substantive claims; current practitioner
  review is document-appropriateness only, not span annotation validation.
- [ ] Confirm factual deployment limits with existing records where available;
  unresolved native counts/pilot/source-equivalence gaps remain disclosed.
- [ ] Rerun local PDF/source preflight after final edits: <=8 total pages,
  citations resolved, no clipping, anonymous metadata and links, matching
  source/PDF hashes. See `qa.md` for current draft checks.
- [ ] If required by the submission form, accurately disclose the related
  non-archival workshop manuscript and the reported chair confirmation.
  Do not claim a new dataset or new inference relative to the workshop.
- [ ] Open a **new Kiii² AIFT regular-paper submission**, never replace NMIXX
  #185. Confirm track/title/abstract/keywords and operator-approved authors.
- [ ] Upload the final approved PDF; download it again and verify the file,
  page count and visible content; record the actual submission number/receipt.

The actual form has not been inspected in this task; these are preparation
items, not assertions about every required EasyChair field. Author names,
emails, conflicts and permissions must come from the operator. ORCID is
requested by ACM for the publishing process. Publication/registration charges
are not paid or authorized by this preparation task.

## Submission text

**Title:** Kiii-Kiii: Korean Identifiers, Identifiability, and Ill-formed Inputs
— A Regulation-Grounded Benchmark for Financial PII Detection.

**Abstract:** Use the compiled text of `sections/00_abstract.tex` after final
coauthor review; do not independently edit form text and let the PDF diverge.

**Keywords:** PII detection; Korean financial NLP; regulation-grounded benchmark;
long-context extraction; output reliability; data loss prevention.

**Internal overlap note:** This SAC manuscript uses the same frozen synthetic
benchmark and completed runs as the non-archival ICAIF workshop manuscript.
It expands the extraction/diagnostic methods, full result presentation and
interpretation. The operator reports Prof. Yongjae Lee confirmed both
submissions are acceptable. The workshop's actual submission/acceptance status
must be checked at submission time; this note does not establish either.
