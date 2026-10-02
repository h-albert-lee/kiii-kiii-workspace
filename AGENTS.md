# Agent entrypoint — Kiii² (2026-09-23)

## Author/submission handoff — 2026-10-02

Use `docs/authors.yaml` and `papers/sac2027/notes/author-handoff.md` for the six-author order, current affiliations, operator-selected OpenReview IDs and equal-first/corresponding roles. Workshop #11 (`klGll15Rn5`) is submitted; latest PDF/source receipt is `docs/submissions/icaif2026.json`. SAC is still unsubmitted. Do not infer emails from masked profile domains, copy stale profile affiliations, or expose author metadata in anonymous source bundles. Paper license CC BY 4.0 and dataset license CC BY-NC 4.0 are separate.

## SAC preparation — ADR-0039 (2026-10-02)

Use `papers/sac2027/README.md` for the independent SAC AIFT manuscript and
submission checklist. The operator reports Prof. Yongjae Lee confirmed that
workshop/SAC parallel submission is acceptable. Sara is polishing the workshop
in the existing Overleaf project; do not overwrite it or sync SAC files into
it. SAC starts from pinned workshop commit `8d73e63`; later wording updates
must be selectively ported after inspecting an outbound Overleaf export.
Collection remains closed under ADR-0038. No Kiii² SAC submission has yet
been performed. Official extended deadline Oct 16 (EST as printed), internal
target Oct 14 KST; prepare <=8 total pages including references. A new SAC
Overleaf project, if used, must be separate and preserve its own comments.

## Current cutoff — ADR-0038 (2026-10-01)

The operator has closed collection and authorized writing from completed runs, including Sunghyun's five Gemma variants and the additional Qwen3-30B/EXAONE. Final scope: 12 LLMs / 22 conditions + 3 baselines = 15 systems / 25 conditions. Qwen2B local and Qwen4B full are pilot-only, omitted without imputation. No new inference. This supersedes older roster/remaining-execution instructions below, not scoring or provenance rules. Use experiments/results/analyses/1001-completed-manuscript-v1. Preserve original cohorts (Kanana8B 1438, others 1440); no fake shared gate. Gemma external-runner replay uses src.analysis.external_response_diagnostics, preserving foreign source hashes. D-F1 is an observable detection proxy, not format-independent latent ability. Native counts, representative pilot calibration and foreign source/deployment equivalence remain unverified. Paper updates use native Overleaf edits and outbound GitHub sync, preserving comments.

Read README.md → STATUS.md → docs/guide/experiment-runbook.md before acting. This repository is now at detector-experiment preparation, not dataset generation. Do not restart generation or follow obsolete September 13 task lists.

## Research contract

- Frozen public preview: nmixx-fin/kiii-kiii at `2df0589d695c18665fd83d4ca5512e03ca0767f6`, 1,440 documents, 218,664 spans, single `test`; no train/validation split or benchmark fine-tuning (ADR-0026). Dataset CC BY-NC 4.0.
- Accepted detectors (ADR-0034): three local LLMs (Qwen/Qwen3.5-2B, Qwen/Qwen3.5-4B, kakaocorp/kanana-2-3b-instruct), three frozen baselines (Presidio Korean rules, ko-pii, OpenMed). Verify served IDs/revisions; never silently substitute models. GLM/Astra generated the benchmark and are excluded from headline detector rankings.
- Medium extension (ADR-0035, 2026-09-26): 은빈 is assigned Qwen/Qwen3.5-9B then kakaocorp/kanana-1.5-8b-instruct-2505, both full/local. Core nine conditions remain; extension adds four (eight systems/thirteen total). Read docs/guide/eunbin-medium-extension.md. Preserve live fork code/settings/gates; extended matrix is separate. Do not bypass exporter gate-hash checks or replace poorly performing small models.
- Primary: full_context_targeted. Control: local_window. Same Unicode core/halo/output budget and common eligible documents across LLMs. No silent context truncation, gold-conditioned prompting, fuzzy boundary repair or dropping failed requests.
- Default 1,200-character core / 1,200 halo / 4,096 output tokens is provisional until separate pilot calibration. The benchmark must not serve as a tuning set. Use any benchmark smoke only for plumbing, never quality-driven adjustments.
- Actual native token counters, including full prompt/chat framing, determine eligibility before inference. Both-condition/all-model cohort gate is mandatory for benchmark execution. Report exclusions, failures, exact model/template versions and reasoning settings.
- Failed/malformed/truncated requests remain empty predictions with gold false negatives. No automatic retry. Interrupted in-flight calls are uncertain and retain their budget reservation; don't blindly resend them.
- Retain full received responses for success and failure, before extraction/cleanup, including available reasoning/finish/usage fields. Verify actual raw logging on the running version; normalization exceptions may lose raw content. Do not claim unreceived responses were saved or resend requests to reconstruct them. Separate adapter/transport failures from model-format errors.
- Strict category-and-boundary mention F1 is primary. Character overlap and all-mentions entity recall are supplemental. No claim that these are formal TAB risk weighting, semantic information loss, entity linking or human annotation agreement.
- Taxonomy source: taxonomy/taxonomy.yaml. Baseline mappings are explicit research configurations in experiments/label_maps; freeze before evaluation, never tune them from benchmark performance.
- Five financial-sector-experienced reviewers each examined a different 10% sample for broad document appropriateness. Sample overlap/IDs/method are not established. Do not claim unique 50% coverage, random sampling, span validation or IAA (ADR-0028).

## Execution and repository rules

- Prepare reversible local work autonomously. Credentials, exact deployment facts and new paid inference allocation must come from the operator. Historical generation budgets do not authorize new detector spending.
- Keys only in environment variables; never print/commit .env, credentials, authorization headers, raw secret-bearing URLs or local config. `.example.json` files deliberately fail validation until populated. Runtime `.local.json` and experiments/runs are ignored.
- Confirmed owners: 성현’s API runs are deferred (Gemini optional, no paid run authorized); 은빈 handles Qwen3.5-2B/4B, Kanana-2-3B and GPU OpenMed; 한울 handles CPU Presidio/ko-pii. Recommend FP16 vLLM-compatible serving with API-connected evaluation for Qwen/Kanana, subject to verified architecture/hardware support; record actual dtype and any explicit fallback. OpenMed uses the separate Transformers token-classification path, not chat completions.
- 사라 owns the full-versus-local context research contribution: pre-result analysis plan, paired statistics, error interpretation, reproducible figures and results/discussion writing. Start with docs/research/sara-context-analysis.md. Prepare analysis code now without duplicating inference; keep core nine conditions and separately authorized four-condition extension within the four-page main-paper scope. Record that the extension follows qualitative format-failure reports; it is exploratory. Operational cohort coordination remains separately unassigned.
- Check experiments/ASSIGNMENTS.md for the assigned owner/models, status and run IDs. Do not invent assignees. Every operator must commit and push completed results and reproducibility metadata following experiments/results/README.md, and link them in the roster. During interruptions push progress/incident reports only, not partial performance. Keep live experiments/runs ignored; publish reviewed copies under experiments/results/runs/<run-id> and large raw/count/journal bundles as GitHub Release assets with hashes.
- Use src.eval.execute, not ad-hoc paid API loops. Same run directory resumes; do not change code/model/prompt/counts midway. Counts and results are bound to configuration/source/data hashes. Budget is per run directory, so explicitly allocate the total across conditions and models.
- Run `python -m pytest tests -q` after relevant changes. Unit fixtures do not establish native API/GPU compatibility. Clearly report what has actually been exercised.
- Never publish partial/pilot scores. Use finalized result.json → src.eval.export; retain result files, raw response journal, counts, cohort gate, dependency inventory and operator record for audit. Existing old leaderboard header is historical; replace only with a genuine completed export.
- Research changes need a new ADR, rather than rewriting historical decisions. Commit messages: `exp: ...`, `docs: ...`, etc. Keep edits scoped; do not discard collaborators' changes.
- `paper/` is a separate repository. Preserve Overleaf comments; inspect/preserve native comments before edits/sync. Do not blindly git-push paper changes or replace files. Anonymous drafts must omit identities/affiliations/repo links.
- No actual customer data. No fabrication of model scores, revisions, token measurements or validation outcomes.

## Current remaining work

Execution code exists. CPU Presidio/ko-pii completed all 1,440 documents on 2026-09-24; results and raw predictions are in experiments/results/runs/0924-01-*-full1440. Preserve these and rescore stored predictions on the eventual common LLM cohort; do not tune rules/maps from these outcomes. GPU OpenMed/Qwen/Kanana must be exercised on the operator's environment. No API model is required for the accepted core roster. Follow the runbook to provision, calibrate on separate pilot data, freeze, count, approve budget, and run. Do not describe the benchmark experiments as complete.

Kanana-2-3B has a published 32,768-token limit; measure the full prompt plus output reservation and report common-cohort exclusions before inference. Do not silently shorten documents or substitute a bigger model. Model/server/tokenizer revisions, actual limits, dtype and hardware availability remain to be verified.

## Offline response diagnostics (ADR-0036, 2026-09-27)

Use `src.analysis.response_diagnostics` and docs/guide/response-diagnostics.md for post-hoc secondary scoring of complete archived runs only. Preserve official strict results and live `src/eval/` source hashes. Itemwise salvage charges one exact FP per invalid parsed item; whole-response JSON fence unwrapping is separately labeled. No fuzzy anchoring, gold-guided repair, retry or prompt tuning. Character overlap uses valid anchored spans and all gold, cannot penalize unanchorable items in character units, and must be accompanied by invalid-item counts/penalized exact precision. Publish diagnostics under experiments/results/analyses, never the headline exporter. Recorded gate hashes alone do not validate native capacity.

## Format grounding and detection diagnostics (ADR-0037, 2026-10-01)

Use src.analysis.failure_decomposition after a replay-verified ADR-0036 analysis. Separate all-request structural compliance/empty-list rates, parsed-item grounding failure counts, and all-gold itemwise detection P/R/F1. Keep strict unchanged. Gold-outcome priority buckets are descriptive, not causal; unresolved rejected items do not establish a detected gold mention. Never claim format-independent latent ability or report success-only performance. Baseline format compliance is N/A. Recorded capacity gates remain unverified. Additional Qwen3-30B/EXAONE completed runs are outside the accepted roster; analysis does not authorize new inference or roster expansion.
