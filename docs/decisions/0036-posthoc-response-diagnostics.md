# ADR-0036 — Decompose extraction failures without replacing strict scores

Date: 2026-09-27. Status: accepted. Supplements ADR-0029/0035.

## Context

The operator requested partial scores and breakdowns after inspection of three completed GPU runs. Their strict request failure rates and raw response patterns (including JSON fences and invalid items alongside valid items) were already known. This decision is **post-hoc and exploratory**, not preregistered. Freeze these rules before computing the new secondary scores.

## Decision

Keep official request-atomic strict category-and-boundary mention F1 and every archived artifact unchanged. Add an offline module in `src/analysis/`, outside the source-hashed live executor directory, with three explicitly labeled stages:

1. `strict`: reproduce the original decoder and scores exactly.
2. `itemwise`: require the original top-level JSON schema, then apply the original strict validator independently to every item. Retain valid siblings; every rejected parsed item counts as one additional exact false positive. Unknown labels go to an explicit unassigned diagnostic bucket. Do not repair items.
3. `fence_itemwise`: additionally unwrap one entire-response JSON/unlabeled Markdown code fence. No prose extraction, JSON completion or nested fence search. Then apply stage 2.

All stages retain all gold, documents and requests. Terminal failures/truncation and unparseable top-level responses remain empty. The latter have unknown item counts; do not invent item penalties. Valid spans follow existing deduplication; invalid parsed items each incur one FP.

For partial boundary credit, retain the existing **category-aware Unicode character union** precision/recall/F1, now also by category, tier×kind×T, and document axes. It rewards exact-quote predictions that overlap a gold boundary; it does not repair that boundary or give wrong-category credit. It weights characters, not mentions. Unanchorable rejected items have no defensible character extent, so their FP penalty applies only to mention metrics. Always show invalid-item counts and penalized exact precision alongside character scores; never present character precision as accounting for every invalid item.

Do not create a combined quality score or substitute these stages into the headline leaderboard. Exact-score changes combine parsing/atomicity effects with recovered extraction quality; they do not isolate a causal format effect and need not be monotonic. No additional inference or benchmark-driven prompt/model tuning is authorized.

## Audit and delivery

Require complete finalized inputs, recorded benchmark gate, matching input/source/request hashes, full response coverage and replay of all original strict metrics/breakdowns/documents/failures. Publish separately under `experiments/results/analyses/`, with input and source hashes, per-request diagnostics, denominator/penalty counts and interpretation. Default-reject pilots; explicit local pilot diagnostics remain labeled and unpublished as benchmark results.

Recorded cohort hashes do not establish correctness of the missing native counts/gate artifacts. Mark that validation as pending until those artifacts are inspected. Preserve running code, templates, gate hashes and original results. [Operational guide](../guide/response-diagnostics.md).
