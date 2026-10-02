# ADR-0039 — Prepare a separate SAC 2027 AIFT manuscript

- Date: 2026-10-02.
- Status: accepted for manuscript/submission preparation by the operator.
- Related: ADR-0003, ADR-0036–0038.

## Decision and authorization

Prepare Kiii² for SAC 2027's AI for Intelligent Financial Technologies (AIFT)
track alongside the ICAIF workshop manuscript. The operator reports that
Prof. Yongjae Lee confirmed that submitting to both is acceptable. This is
an operator-reported confirmation, not a written policy exception independently
verified in this repository. Do not reopen this resolved planning question or
contact anyone without authorization. Preserve the overlap disclosure for any
relevant submission-system question; do not invent wording or a receipt from
the chair. Preparation does not mean a submission has been made.

Collection remains closed under ADR-0038: 15 systems / 25 completed conditions,
with original cohorts, strict scores and post-hoc diagnostics unchanged. No
new inference, missing-pair completion, common-gate reconstruction or test-set
tuning. The SAC version expands methods, diagnostics and interpretation rather
than inventing additional experiments. D-F1 is an observable proxy, not latent
format-independent ability. Native capacity and foreign-runner equivalence
remain unverified.

## Independent source and coordination

Use `papers/sac2027/` in the workspace repository for a standalone anonymous
draft based on workshop commit `8d73e63`. `notes/source-snapshot.json` records
the exact source hashes. The original `paper/` submodule and its live Overleaf
project remain the workshop source; Sara is polishing that manuscript.
Do not sync this SAC folder into the existing workshop project. Git does not
contain native Overleaf comments; snapshotting source does not copy comments.
Existing threads remain in the original project.

When Sara's polished version is exported through native Overleaf → GitHub,
review that specific commit and selectively incorporate applicable wording or
corrections into SAC. Never replace the expanded manuscript wholesale. A new
SAC Overleaf project, if created, must be distinct; subsequent edits there use
native editing and outbound GitHub sync with comments preserved.

## Venue constraints, checked 2026-10-02

- Official main-site extension: **2026-10-16 (EST as printed)**. Exact cutoff
  hour is not stated; do not infer a KST or AoE cutoff. Internal target: Oct 14 KST.
- Anonymous ACM sigconf regular paper, EasyChair, AIFT track.
- Default full-paper limit: 8 pages; author kit mentions up to 2 extra pages.
  This draft targets **8 total including references**, without assuming an
  exclusion or authorizing extra-page charges.
- Notification Nov 20; camera-ready Dec 11; conference Apr 5–9, 2027, Gwangju.
- AIFT's page still lists Oct 2; the dated main-site extension takes precedence.

Sources: [main dates](https://sigapp.org/sac/sac2027/index.php),
[regular submission](https://sigapp.org/sac/sac2027/submission.php),
[author kit](https://sigapp.org/sac/sac2027/authorkit.php),
[AIFT](https://academicworkshops.github.io/AIFT/).

## Completion criteria

Prepare a compiled, visually checked draft, reproducible figure/table inputs,
an evidence/claim ledger and a submission checklist. Keep actual submission,
author-list confirmation and eventual publication charges separate from local
preparation. NMIXX's already-submitted AIFT paper is a separate contribution;
its author roster or EasyChair number must not be reused for Kiii².
