# ADR-0022: Complete the remaining 45 documents

- Date: 2026-09-21
- Status: accepted; user authorized continuing after the 675/720 status report.

Preserve the 675 accepted unique documents (140 original GLM, 247 additional GLM, 288 Astra). Prepare only the 45 missing original plans with unchanged seeds: 22 at 16k, 11 at 4k and 12 at 1k. Reassign the two rejected Astra documents to GLM for this completion pass; retain actual generator provenance. No new stage-two generation in this run.

Run GLM with eight disjoint lanes in `data/corpus/main-720-v2/completion-0921-glm`. Carry all previous Mango costs/reservations ($63.9208882 at preparation) into the unchanged $150 ceiling. Explicitly retry the two interrupted documents from ADR-0021 under this user-authorized completion pass, retaining their full historical reservations; their original provider charges remain unknown. Original ledgers are unchanged. Astra's completed campaign remains $80.04415 estimated, with no new OpenAI submissions.

An output-limit failure now records that document and advances to the next independent plan. Three consecutive output-limit failures stop the lane. Existing transport-error, quality and budget gates remain. There is no unbounded retry loop: this pass can still finish with rejected documents requiring review. Local execution runs in the background without recurring LLM monitoring.
