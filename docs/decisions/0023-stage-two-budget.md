# ADR-0023: Start the second 720 within new provider budgets

- Date: 2026-09-21
- Status: accepted, explicitly authorized by user

User requested the next 720 documents with $47 remaining OpenAI credit and $50 additional GLM budget. Treat these as new-stage ceilings of $47 and $50 respectively; do not reuse unused headroom from the old GLM $150 ceiling. GLM historical conservative costs/reservations are $74.5065897, so its new cumulative ceiling is $124.5065897. Historical unknown charges remain reserved.

Use existing stage-two plans with original document IDs and seeds. Offline assertions verify 720 unique IDs, disjoint from the previous hybrid allocations, and no seed overlap with those allocations. Allocation is deterministic (seed 20260921), per document type: Astra 18 short + 12 medium + 2 long, GLM 6 short + 12 medium + 22 long. Totals: Astra 320, GLM 400. All plans use the API generator slice. Source corpus plans are preserved; assigned copies record the actual provider route.

Astra uses existing low-reasoning Batch generation with 10-document canary then bounded waves, maximum new spending estimate $47. Current official model pricing was checked at https://developers.openai.com/api/docs/models/gpt-6-astra : Batch is 50% of standard rates. Existing conservative accounting charges input at $6.25 and output at $25 per million tokens. GLM uses eight disjoint lanes, each receiving $6.25 of new conservative allowance. No changes to generation prompts or validators.

Historical request averages imply approximately $44.41 Astra and $48.40 GLM for initial outputs. This is a planning estimate, not a guarantee; repairs, server errors, reservations and yield can exhaust the budget before 720 accepted documents. Automatic budget gates take precedence over the count target. Fixed per-lane budgets may strand some headroom until a later explicit redistribution.

Length distribution differs by generator to fit cost limits. Both generators include all lengths and document types, but report generator×length results and do not claim a balanced generator experiment. Aggregate stage-two coverage retains all planned cells. Headline model evaluation excludes generator models per earlier ADRs.

Active paths are `data/corpus/main-1440-v1/stage2-0921/astra` and sibling `glm`. First-stage status remains 719 accepted with one annotation failure; this new 720 does not replace that document. Execution remains local for GLM and Batch orchestration, with no recurring LLM monitoring. Output provenance uses `main-1440-v1` in campaign summaries; raw single-attempt GLM artifacts retain their run identifiers.
