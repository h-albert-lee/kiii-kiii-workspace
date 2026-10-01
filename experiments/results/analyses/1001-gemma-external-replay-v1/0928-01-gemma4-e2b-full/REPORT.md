# Response diagnostics (secondary only)

Model: `google/gemma-4-E2B-it`. Condition: `full_context_targeted`. Scope: `completed_benchmark`.

Strict results were replayed and match the archived metrics and every document. Original inputs were not modified.

| Stage | Exact F1 / 100 | Character F1 / 100 | Invalid items (exact FP penalty) |
|---|---:|---:|---:|
| strict | 0.0027 | 0.0008 | 0 |
| itemwise | 0.0027 | 0.0008 | 0 |
| fence_itemwise | 9.7335 | 7.4665 | 62457 |

- External runner: input/output replay does not establish runner source or server equivalence.
- Original execution metadata and gate hashes were not changed; not eligible for headline export.
- Selected after observing strict failures; exploratory, not preregistered.
- All gold and all requests remain in every denominator; no success-only scoring.
- Itemwise exact precision includes one FP per invalid parsed item; unknown labels use an unassigned bucket.
- Character coverage uses valid anchored predictions and all gold. Unanchorable invalid items cannot be assigned character FP; interpret with exact penalized precision and invalid-item counts.
- Whole-response parse/terminal failures remain empty. Their item count is unknown, not estimated.
- No quote, occurrence, category, truncation or boundary repair; no new model calls.
- Stage differences are diagnostic, not independent or necessarily monotonic gains.

Native counts and the underlying cohort gate were not independently checked by this offline analysis. See analysis.json for input and code hashes; per_request.jsonl.gz retains diagnostics without copying completion text.
