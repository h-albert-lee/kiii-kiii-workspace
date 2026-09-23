# ADR-0032 — Sara owns the context-effect research contribution

Date: 2026-09-23. Status: accepted assignment; analysis plan not yet frozen.

The user assigned 사라 the research contribution on full-context versus local-context extraction, after agreeing to constrain it to existing experiments and a four-page main paper.

- 사라 owns hypotheses, the pre-result analysis plan, statistical interpretation, error analysis, reproducible analysis/figures and the results/discussion draft.
- Use the existing four LLMs × two context conditions. Baselines remain reference systems. No additional models, paid calls or experimental conditions are authorized by this assignment.
- Immediate work is possible without detector results: freeze the analysis plan, implement analysis against the existing result schema and synthetic fixtures, prepare figure code, and push artifacts. No fabricated findings.
- Primary contrast is model-specific paired Δ strict micro F1 (full minus local), preserving failures and shared document eligibility. Existing document bootstrap is the starting implementation; multiplicity, subgroup and qualitative-sampling details must be settled in the analysis plan before outcomes are inspected.
- Main-paper space: one shared performance table, at most one analysis figure and short results/discussion text. Detailed planned analyses live in GitHub; do not assume an unlimited appendix.
- Execution ownership is unchanged. 사라 is not automatically assigned operational cohort coordination; that owner remains unspecified.
- Entry document: docs/research/sara-context-analysis.md. Model IDs, scoring rules, frozen data and GitHub sharing procedures remain unchanged.
