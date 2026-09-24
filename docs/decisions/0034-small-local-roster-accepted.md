# ADR-0034 — Accept the small local evaluation roster

Date: 2026-09-24. Status: accepted by user ("좋아 제안한 대로 가자"). Supersedes the execution roster in ADR-0019/0031 and adopts the core proposal of ADR-0033. Historical ADRs remain intact.

## Accepted execution scope

- `Qwen/Qwen3.5-2B`, `Qwen/Qwen3.5-4B`, `kakaocorp/kanana-2-3b-instruct`, each full_context_targeted and local_window.
- Existing Presidio Korean/custom rules, ko-pii and OpenMed: one baseline run each.
- **Six systems, nine conditions.** Gemini is an optional future API anchor, deferred until separately selected and budgeted. Claude and previous large Qwen/Kanana MoE models are removed from the current default matrix. Alternatives 9B/EXAONE/Gemma are not implicitly authorized substitutes.

## Owners and unchanged requirements

은빈 owns the three GPU LLMs and OpenMed, 한울 owns CPU rules, 사라 owns context-effect research. 성현's API runs are deferred; no unrelated duty is assigned to him. Operational cohort coordination remains unassigned.

Use verified FP16-compatible serving as preferred; record actual precision/fallback and model/tokenizer/server revisions. Hardware capacity, JSON output reliability, separate-pilot settings and actual-token limits remain to be established. Kanana's published 32K limit must not cause silent truncation or selective removal after seeing performance. Report coverage and exclusions before inference and retain one common cohort across models/conditions.

No benchmark training, no generator headline rows, no scoring/protocol changes, no automatic retries. The provisional partition still produces 82,338 requests over three LLMs and both conditions on all 1,440 documents. Smaller weights alone do not reduce request count. No model downloads, new paid inference or GPU rental are initiated by this documentation/config update. Preserve any previous runs as historical artifacts.

Update entrypoints, assignment table, Sara's brief, runbook and matrix together. Provider adapters and API example configs remain available for possible future authorized use.
