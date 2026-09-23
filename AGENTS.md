# Agent entrypoint — Kiii² (2026-09-23)

Read README.md → STATUS.md → docs/guide/experiment-runbook.md before acting. This repository is now at detector-experiment preparation, not dataset generation. Do not restart generation or follow obsolete September 13 task lists.

## Research contract

- Frozen public preview: nmixx-fin/kiii-kiii at `2df0589d695c18665fd83d4ca5512e03ca0767f6`, 1,440 documents, 218,664 spans, single `test`; no train/validation split or benchmark fine-tuning (ADR-0026). Dataset CC BY-NC 4.0.
- Planned detectors: four LLMs (Claude, Gemini, Qwen, Kanana), three frozen baselines (Presidio Korean rules, ko-pii, OpenMed). Verify served IDs/revisions; never silently substitute models. GLM/Astra generated the benchmark and are excluded from headline detector rankings.
- Primary: full_context_targeted. Control: local_window. Same Unicode core/halo/output budget and common eligible documents across LLMs. No silent context truncation, gold-conditioned prompting, fuzzy boundary repair or dropping failed requests.
- Default 1,200-character core / 1,200 halo / 4,096 output tokens is provisional until separate pilot calibration. The benchmark must not serve as a tuning set. Use any benchmark smoke only for plumbing, never quality-driven adjustments.
- Actual native token counters, including full prompt/chat framing, determine eligibility before inference. Both-condition/all-model cohort gate is mandatory for benchmark execution. Report exclusions, failures, exact model/template versions and reasoning settings.
- Failed/malformed/truncated requests remain empty predictions with gold false negatives. No automatic retry. Interrupted in-flight calls are uncertain and retain their budget reservation; don't blindly resend them.
- Strict category-and-boundary mention F1 is primary. Character overlap and all-mentions entity recall are supplemental. No claim that these are formal TAB risk weighting, semantic information loss, entity linking or human annotation agreement.
- Taxonomy source: taxonomy/taxonomy.yaml. Baseline mappings are explicit research configurations in experiments/label_maps; freeze before evaluation, never tune them from benchmark performance.
- Five financial-sector-experienced reviewers each examined a different 10% sample for broad document appropriateness. Sample overlap/IDs/method are not established. Do not claim unique 50% coverage, random sampling, span validation or IAA (ADR-0028).

## Execution and repository rules

- Prepare reversible local work autonomously. Credentials, exact deployment facts and new paid inference allocation must come from the operator. Historical generation budgets do not authorize new detector spending.
- Keys only in environment variables; never print/commit .env, credentials, authorization headers, raw secret-bearing URLs or local config. `.example.json` files deliberately fail validation until populated. Runtime `.local.json` and experiments/runs are ignored.
- Confirmed owners: 성현 handles Claude/Gemini; 은빈 handles Qwen/Kanana and GPU OpenMed; 한울 handles CPU Presidio/ko-pii. Recommend FP16 vLLM-compatible serving with API-connected evaluation for Qwen/Kanana, subject to verified architecture/hardware support; record actual dtype and any explicit fallback. OpenMed uses the separate Transformers token-classification path, not chat completions.
- Check experiments/ASSIGNMENTS.md for the assigned owner/models, status and run IDs. Do not invent assignees. Every operator must commit and push completed results and reproducibility metadata following experiments/results/README.md, and link them in the roster. During interruptions push progress/incident reports only, not partial performance. Keep live experiments/runs ignored; publish reviewed copies under experiments/results/runs/<run-id> and large raw/count/journal bundles as GitHub Release assets with hashes.
- Use src.eval.execute, not ad-hoc paid API loops. Same run directory resumes; do not change code/model/prompt/counts midway. Counts and results are bound to configuration/source/data hashes. Budget is per run directory, so explicitly allocate the total across conditions and models.
- Run `python -m pytest tests -q` after relevant changes. Unit fixtures do not establish native API/GPU compatibility. Clearly report what has actually been exercised.
- Never publish partial/pilot scores. Use finalized result.json → src.eval.export; retain result files, raw response journal, counts, cohort gate, dependency inventory and operator record for audit. Existing old leaderboard header is historical; replace only with a genuine completed export.
- Research changes need a new ADR, rather than rewriting historical decisions. Commit messages: `exp: ...`, `docs: ...`, etc. Keep edits scoped; do not discard collaborators' changes.
- `paper/` is a separate repository. Preserve Overleaf comments; inspect/preserve native comments before edits/sync. Do not blindly git-push paper changes or replace files. Anonymous drafts must omit identities/affiliations/repo links.
- No actual customer data. No fabrication of model scores, revisions, token measurements or validation outcomes.

## Current remaining work

Execution code exists. Rules and offline fixtures are tested; native paid provider calls and GPU OpenMed/Qwen/Kanana must be exercised on the operator's environment. Follow the runbook to provision, calibrate on separate pilot data, freeze, count, approve budget, and run. Do not describe the benchmark experiments as complete.
