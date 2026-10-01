# ADR-0037 — Separate format, grounding and detection diagnostics

Date: 2026-10-01. Status: accepted. Supplements ADR-0036 at the operator's request.

## Context and scope

Low strict scores mix request-level rejection with incorrect or missing PII. The operator requested a decomposition to explain what the benchmark measures. This is post-hoc analysis after inspecting results, not a preregistered change to the primary endpoint. Keep official strict and ADR-0036 scores, all failed requests, original cohorts, live evaluator source hashes and raw responses unchanged. No new inference or benchmark tuning. Additional models remain outside the accepted roster until separately decided.

## Decision

Use three distinct axes; do not turn them into a single adjusted ability score.

1. **Format and execution:** all-request denominators for terminal failure, truncation, invalid JSON, wrong root schema, parseable empty/nonempty lists, and structural compliance. Structural compliance requires normal termination, raw JSON (no fence), the exact root/item keys and field types, positive integer occurrence, nonempty quote, and no duplicate object keys. It does not require the quote to exist or a string category to belong to the vocabulary. Empty lists may comply; report their frequency explicitly. Request outcome buckets are exclusive; compliance, fences and duplicate flags are separate overlapping diagnostics.
2. **Grounding:** count one first-failing check per parseable item in the frozen validator order: item schema, invalid category, invalid quote field, invalid occurrence field, quote absent in TARGET, occurrence exceeds actual matches, start outside owned core, valid. These are output-contract/grounding observations, not all syntax errors or hallucinations. Denominator is parsed items; syntax/terminal failures have unknown item counts. Keep ADR-0036 one-invalid-item/one-FP penalties.
3. **Observed detection:** report ADR-0036 fence/itemwise exact P/R/F1 over all gold, and category-aware character coverage with its invalid-item caveat. Add a supplemental boundary-only P/R/F1 on the same valid anchored items, collapsing identical boundaries across labels, with the same invalid-item FP penalty. It measures location performance of valid known-category outputs, not label-independent latent ability: unknown categories remain invalid. Its boundary denominator may differ from typed gold if labels share coordinates. Never score only successful requests.

Partition every unique typed gold mention using this fixed priority: exact hit; owner request truncated/other terminal failure/invalid JSON/root schema failure/empty list; exact boundary with wrong category; overlapping wrong boundary with the correct category; overlap with another category; unresolved miss in a request containing rejected items; otherwise no overlapping prediction. Ownership is determined by the frozen core containing the gold start, never used in prompting or repair. Overlap is descriptive, not a match granting mention credit; many-to-many overlaps are allowed and this is not a fractional mention metric. A rejected item cannot be assigned to a specific missed gold span, so the unresolved bucket must not be relabeled a detected PII or a pure format loss. This priority partition is not causal attribution and can conceal coexisting errors.

Duplicate-key detection is observational. Existing scores retain Python's last-value behavior, including its information loss; format compliance rejects these outputs. Do not silently replace the original parser or reconstruct discarded items. Unknown unparseable content cannot establish what the model detected. No semantics-based, fuzzy or gold-guided response repair.

## Verification and presentation

New code lives only in `src/analysis/failure_decomposition.py`. Bind inputs to a completed replay-verified ADR-0036 artifact, verify raw/gold/reference/taxonomy/scorer hashes, reconstruct every request, and replay every document's strict and itemwise exact TP/FP/FN and failure records. Check gold partitions sum to the entire typed gold denominator and parsed-item failures exactly equal the existing invalid-item penalty. Store per-request and per-document diagnostics, source hashes and explicit denominators.

Suggested paper presentation: strict end-to-end F1, structural compliance, empty-list rate, and all-gold itemwise detection P/R/F1 in one compact table; a stacked gold-outcome chart in supplementary material. Include the precision and recall, not only an increased F1. Character coverage and location-only scores remain supplemental. Show original cohort sizes; neither this analysis nor recorded gate hashes establishes native capacity validity. Do not merge unequal gates or describe different conditions as a final ranking.
