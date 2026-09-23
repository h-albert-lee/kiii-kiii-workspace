# ADR-0030 — Experiment ownership and GitHub result sharing

Date: 2026-09-23. Status: accepted.

The user requested an explicit model/assignee roster and that experiment results be accumulated and pushed to GitHub for sharing.

- Keep the existing four LLMs × two conditions plus three frozen baselines (11 condition runs). Record owner, status, run IDs and result links in experiments/ASSIGNMENTS.md. Names remain unassigned until provided; API/GPU/baseline/aggregation groupings are suggestions, not fabricated assignments.
- Every operator commits and pushes each completed model/condition's finalized results and reproducibility metadata to experiments/results/runs/<run-id>/, and updates the roster. Share progress/failure reports during interruptions without publishing partial or pilot scores.
- Retain ignored experiments/runs/ for live resumable state; it is not the sharing destination. Small results are git-tracked. Large compressed raw/count/journal bundles go to GitHub Release assets in the same repository with links and SHA-256 in the run report.
- Do not commit credentials or private local configs. Preserve original execution hashes and disclose any metadata redaction. Do not overwrite others' runs, force-push shared history or silently delete failed experiments.
- This changes sharing/ownership procedures, not scoring, model selection, paid inference authorization or the common-cohort requirement.
