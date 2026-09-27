# Response diagnostics (secondary only)

Model: `Qwen/Qwen3.5-4B`. Condition: `local_window`. Scope: `completed_benchmark`.

Strict results were replayed and match the archived metrics and every document. Original inputs were not modified.

| Stage | Exact F1 / 100 | Character F1 / 100 | Invalid items (exact FP penalty) |
|---|---:|---:|---:|
| strict | 0.9696 | 0.4144 | 0 |
| itemwise | 5.9165 | 3.2735 | 47672 |
| fence_itemwise | 8.5869 | 5.4645 | 83370 |

- Selected after observing strict failures; exploratory, not preregistered.
- All gold and all requests remain in every denominator; no success-only scoring.
- Itemwise exact precision includes one FP per invalid parsed item; unknown labels use an unassigned bucket.
- Character coverage uses valid anchored predictions and all gold. Unanchorable invalid items cannot be assigned character FP; interpret with exact penalized precision and invalid-item counts.
- Whole-response parse/terminal failures remain empty. Their item count is unknown, not estimated.
- No quote, occurrence, category, truncation or boundary repair; no new model calls.
- Stage differences are diagnostic, not independent or necessarily monotonic gains.

Native counts and the underlying cohort gate were not independently checked by this offline analysis. See analysis.json for input and code hashes; per_request.jsonl.gz retains diagnostics without copying completion text.
