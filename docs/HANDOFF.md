> 2026-09-24 execution update: Presidio and ko-pii completed all 1,440 documents. See experiments/results/runs/0924-01-{presidio,ko-pii}-full1440/REPORT.md. No rule/map tuning from outcomes. Full-release results are retained; rescore stored predictions on the eventual common LLM cohort before combined ranking. The older no-results notes below are historical.

# Current scope update — 2026-09-24

ADR-0034 accepts three small local LLMs (Qwen3.5-2B/4B, Kanana-2-3B-Instruct) and three existing baselines: six systems, nine conditions. Gemini is optional/deferred, Claude and the previous large MoE models are outside the current run scope. Use the updated matrix; do not restart older four-LLM runs. The history below preserves implemented capabilities, not an instruction to run every adapter.

# Experiment handoff — 2026-09-23

Start with [AGENTS.md](../AGENTS.md) and the [execution runbook](guide/experiment-runbook.md). This handoff supersedes the generation-stage September 13 handoff. Earlier reasoning remains in the numbered ADRs.

## What is complete

- Kiii² preview: 1,440 documents, 218,664 spans, 36 categories; T0–T3 each 360; ten document types each 144; 1/3/8 customer subjects each 480. One test split. No benchmark training.
- Data release is public at nmixx-fin/kiii-kiii, pinned content commit `2df0589d695c18665fd83d4ca5512e03ca0767f6`, CC BY-NC 4.0. GLM generated 820 and Astra 620 documents. Planned length buckets are 480 each; actual buckets 482/478/480, with 12 planned/actual mismatches retained and documented.
- Generation is finished. New collaborators should download the release, not rerun generation. Credentials and old generation budgets are not needed for evaluation.
- Protocol, strict scoring, supplementary metrics, breakdowns and paired bootstrap; verified Hub loader; Claude/Gemini/vLLM extraction and actual-token adapters; budget journal/resume; common capacity gate; rule and OpenMed adapters; result export. See ADR-0029 for implementation choices.
- README, AGENTS, configs and runbook form the experiment entrypoint. Rules were exercised locally; paid native provider calls and GPU model loading have not been exercised in this preparation step.
- Related work now cites TWICE and NMIXX, with Korean finance evaluation notes in literature/notes/korean-financial-evaluation.md. Paper changes are in the paper submodule; do not overwrite Overleaf comments through blind file replacement/sync.

## What the experiment operator must supply

Actual model access, served IDs and immutable revisions, tokenizer/template/server versions, endpoint context limits, prices/date, allocated inference budgets, API keys in environment, and GPU endpoint details. Verify the provisional model roster from docs/models.md. No API secrets are in templates. Missing fields deliberately prevent execution.

Calibrate shared output partition/budget and provider settings on independent synthetic pilot examples. Then freeze all settings, measure full prompts for every model and both conditions, derive a common eligible corpus before inference, run within allocated budgets, finalize and export. The runbook includes exact commands and failure/recovery behavior.

## Research caveats that must survive handoff

- Five reviewers with financial-sector employment experience each inspected a different 10% sample for broad resemblance/appropriateness only. Overlap, IDs and sampling method are unknown. No claim of unique 50% coverage, span verification or IAA.
- Uncertain API calls retain their maximum reservation and count as failed predictions. Do not resend completed/failed requests or remove failures to improve scores.
- Character masking is only an information-loss proxy; all-mentions recall is not entity-linking accuracy. TAB risk weighting and formal de-identification utility are not implemented.
- OpenMed's native label space/argmax decoder and finite overlapping context differ from prompted LLMs; state this explicitly. All-category primary scores retain unsupported categories as false negatives.
- No actual detector leaderboard exists yet. Do not fill paper result placeholders from dry runs or estimated performance.

## Navigation

- Protocol: ADR-0020; single test: ADR-0026; review scope: ADR-0028; execution/handoff: ADR-0029.
- Data provenance: experiments/releases/, docs/releases/, docs/guide/huggingface-release.md.
- Current tasks: STATUS.md. Historical generation notes remain for reproducibility only.
- Paper: separate submodule, XeLaTeX, anonymous review settings, `\anonv` macro; preserve native Overleaf comment threads.

## Assignment and result delivery update

ADR-0030: experiments/ASSIGNMENTS.md is the owner/status/result-link roster (current ADR-0034: 성현 API deferred; 은빈 Qwen3.5-2B/4B, Kanana-2-3B, OpenMed; 한울 Presidio/ko-pii; aggregation pending). Every operator must commit and push finalized result bundles to experiments/results/runs/<run-id>/ and report interruptions on GitHub. Large raw artifacts use the same repository’s Release assets with hashes. See experiments/results/README.md and docs/templates/experiment-report.md. This supersedes any instruction to keep results only in local backups.

GPU deployment preference (ADR-0031): Qwen/Kanana should use verified FP16 vLLM-compatible serving and API-connected evaluation; preserve actual tokenizer/template counting. Verify support before freezing; record any dtype fallback explicitly. OpenMed remains a separate Transformers token-classification GPU workload assigned to 은빈, not a chat-completion endpoint.

## Context-effect research owner

ADR-0032 assigns 사라 the full-versus-local context research contribution (hypotheses, statistics, error analysis, reproducible figures and results/discussion). Start at docs/research/sara-context-analysis.md. She can prepare and freeze the analysis plan and fixture-tested code before results arrive. Keep the accepted 9 conditions and a main-paper footprint of one shared table, at most one analysis figure and concise interpretation. Operational cohort aggregation remains separately unassigned.
