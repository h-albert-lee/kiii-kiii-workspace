# Experiment execution readiness validation — 2026-09-23

- Python 3.12 environment, complete suite: **106 passed**, 7.65 seconds.
- Fixture coverage: native provider/count request shapes, finish-reason normalization (including reasoning tokens), unknown/malformed predictions, Unicode offsets, common-capacity gate, per-run budget denial, safe resume, interrupted reservations, transport-error stop, no duplicate dispatch, finalized-only leaderboard export.
- Verified local release checksums and exact taxonomy match; loaded two released documents through the dataset loader; eight extraction requests prepared as `plumbing_smoke_only`.
- Installed/exercised Presidio 2.2.364 and ko-pii 1.16.0. Both completed detection and scoring on the two-document plumbing sample. No quality tuning performed from these outcomes and no smoke metrics published to the leaderboard.
- Handoff Markdown links checked; evaluation modules compile; CLI help checked. Staged file secret-pattern scan found no credentials. Runtime config, raw outputs and keys are ignored by git.
- No paid detector calls made. Claude/Gemini actual access, native counter consistency and Qwen/Kanana deployment remain live pilot requirements. OpenMed BIOES grouping is fixture-tested, but its GPU/model initialization has not been run here. Confirm the installed Transformers native architecture and hardware compatibility before full execution.

Current implementation decisions: ADR-0029. Operator commands: docs/guide/experiment-runbook.md. Tests establish software behavior under fixtures, not detector accuracy or endpoint availability.
