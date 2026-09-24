# STATUS — 2026-09-23

## Current outcome

**Dataset complete and public; detector execution infrastructure prepared; actual detector experiments not yet run.** Experiment collaborators should begin with README.md → AGENTS.md → docs/guide/experiment-runbook.md.

| Item | Status |
|---|---|
| Taxonomy | v1.2 accepted, 36 categories, T0–T3 |
| Corpus | 1,440 documents / 218,664 spans; one test split, no benchmark training |
| Public release | nmixx-fin/kiii-kiii, CC BY-NC 4.0 preview, content pin `2df0589d695c18665fd83d4ca5512e03ca0767f6` |
| Practitioner review | Five financial-sector-experienced reviewers, each a different 10% sample, broad appropriateness only; not span validation/IAA |
| Evaluation | Frozen full/local requests, exact/native token counters, common-capacity gate, budget/resume journal, strict metrics, breakdowns, bootstrap, CSV export |
| Model adapters | Claude/Gemini/vLLM implemented and fixture-tested; native paid calls and GPU servers still require operator pilot |
| Baselines | Presidio and ko-pii installed and exercised; OpenMed native token adapter implemented, GPU loading untested |
| Operator docs | README, AGENTS, runbook, config templates, label-map limitations prepared |
| Paper/related work | Dataset/protocol/review scope updated; TWICE/NMIXX included; actual results remain placeholders |
| Leaderboard | No detector scores yet; historical header only |

Validation: **106 tests passed** (offline provider fixtures, budget/resume/capacity/export guards, generation/release regressions). Verified release → two-document smoke → actual Presidio/ko-pii extraction/scoring completed. Smoke scores are not benchmark findings. Native paid providers and GPU model loading were not exercised.

Ownership and delivery: [assignment roster](experiments/ASSIGNMENTS.md) (성현: API; 은빈: GPU LLM + OpenMed; 한울: CPU rules; 사라: context-effect research; operational aggregation owner pending). Each operator must push completed results and interruption reports to GitHub under the [result-sharing procedure](experiments/results/README.md); large raw artifacts use repository Release assets. ADR-0030.

Research work can start immediately: 사라 follows [the context-analysis brief](docs/research/sara-context-analysis.md) to freeze a pre-result analysis plan and implement fixture-tested analysis/figures, then interpret existing paired runs and write concise results/discussion. No additional inference conditions. ADR-0032.

Candidate review (2026-09-24): [small local model proposal](docs/research/small-model-roster-2026-09-24.md), ADR-0033 **proposed**. GPU capacity is unknown; accepted assignments and inference settings remain unchanged. No new detector runs or spending initiated.

## Next actions

1. Assign experiment operator and servers; verify exact four-model IDs/revisions, tokenizer/template versions, limits, prices and paid allocation.
2. Separate pilot for live adapter compatibility and shared core/halo/output calibration; freeze settings. Do not tune on test results.
3. Count all requests for all models and both conditions; fix common eligible documents; preserve exclusion reasons.
4. Run four LLMs × two context conditions and three frozen baselines, resume from journals, finalize, export and analyze.
5. Populate figures and paper results only from finalized artifacts; preserve Overleaf comments during edits.

Default core/halo 1,200 chars and output cap 4,096 tokens yield 13,723 requests per model per condition on all 1,440 docs. This is a provisional inventory, **not a token/cost estimate**. Exact live counts and detector costs are not available yet.

## Boundaries

Generation is finished: GLM 820 / Astra 620; generators are excluded from headline detector ranking. Old generation budgets and historical pending-generation notes do not apply to detector inference. No training or validation split; no fine-tuned KLUE baseline. TAB risk-weighted recall and semantic de-identification utility are not implemented.

Research aim remains the ICAIF'26 financial AI security/privacy/safety workshop short paper. Venue/deadline details are recorded in ADR-0003 and should be reconfirmed before submission. Detailed history is preserved in docs/decisions/, generation notes and git history.
