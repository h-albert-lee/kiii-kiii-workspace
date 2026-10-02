# ADR-0040 — SAC error analysis from completed archived outputs

Date: 2026-10-02. Status: accepted under the operator's request for substantive
error analysis in the SAC manuscript. Extends presentation/analysis, not scoring
or collection. ADR-0038's cutoff and original cohorts remain unchanged.

## Scope

Use all 22 completed LLM conditions' replay-verified ADR-0037 decompositions.
Report three separate denominators: all requests, usable parsed items, and all
gold mentions. Verify pinned hashes, strict/itemwise count identity, gold
partition conservation and invalid-item FP conservation before reporting.
Baseline format/item diagnostics remain N/A. No new inference, repair, model
selection, gate substitution or revision to primary/secondary scores.

For an all-gold figure, retain exact hits, unusable owner responses (terminal,
JSON or root-schema failures), empty owner responses, boundary/category
mismatches, unresolved misses with rejected items, and remaining no-overlap
misses. These are merged views of the existing ordered gold partition, not
causal mechanisms. Publish finer unmerged counts as well. Never reinterpret an
unresolved item as a detected gold mention. Do not pool across model cohorts.

Request fence/empty/compliance rates can overlap and must not be added. Item
failure shares use their explicit item denominator, not a gold denominator.
An exact quotation outside its assigned core is an ownership failure; a quote
absent from TARGET alone is not evidence of hallucination. Neither condition
establishes what latent PII knowledge a model has.

## Illustrative audit

Select examples deterministically within disclosed model/error strata using
the smallest SHA-256 request-ID key, then a deterministic candidate ordering.
Verify original response/gold hashes and reconstruct the selected request before
interpreting it. Use gold only to describe already scored matches/boundaries,
never to repair a prediction. Publish request/item selection and source hashes.
These are purposive illustrations, not a representative manual audit, gold-label
validation, causal explanation or annotation agreement study. If a requested
stratum has no case, report that fact rather than inventing an example.

## Manuscript priorities

Use a full/local error-distribution figure and concise measured failure profiles.
Keep the taxonomy coverage figure available as a companion asset if space is
needed. Replace repeated methods/discussion text to retain the eight-total-page
target; do not omit failed requests or substantive limitations to save space.
The existing workshop project remains untouched. SAC GitHub push authorization
is still pending; this analysis request does not authorize the rejected export.
