# Completed GPU response diagnostics — 2026-09-27

Post-hoc secondary analysis under [ADR-0036](../../../../docs/decisions/0036-posthoc-response-diagnostics.md). No new inference. Original strict results and live evaluator source are unchanged. These are three completed conditions, not the complete model roster or a consolidated leaderboard.

Each run contains 1,440 benchmark documents, 13,723 requests and 218,664 gold spans. All original strict metrics, breakdowns, per-document results and failure records were replayed exactly. Native token counts and the underlying cohort gate remain unavailable for independent verification.

## Scores

All F1 columns below use a 0–100 scale. Itemwise/fence exact F1 includes one FP for every rejected parsed item. Character F1 uses valid anchored spans and all gold; it cannot charge character FP for unanchorable rejected items.

| Run | Strict exact F1 | Itemwise exact F1 | Fence + itemwise exact F1 | Fence + itemwise character F1 | Invalid items (exact FP) |
|---|---:|---:|---:|---:|---:|
| [0925-01-kanana-3b-full](0925-01-kanana-3b-full/REPORT.md) | 1.0230 | 3.1603 | 3.1682 | 1.8658 | 75,465 |
| [0925-02-kanana-3b-local](0925-02-kanana-3b-local/REPORT.md) | 1.6156 | 4.0913 | 4.0934 | 1.9654 | 31,764 |
| [0925-03-qwen-2b-full](0925-03-qwen-2b-full/REPORT.md) | 0.1169 | 0.8691 | 1.6351 | 0.6649 | 64,498 |

## Interpretation and handoff

- Retaining valid siblings recovers predictions in all three runs. Whole-response fence unwrapping changes Kanana exact F1 little; its contribution is larger for Qwen 2B. Neither procedure produces strong coverage: after both steps exact recall is 2.20% / 2.47% / 1.08% respectively. Format handling alone is not established as a sufficient explanation for low performance.
- Character F1 is not guaranteed to exceed mention F1. Long gold attribute spans receive more weight; these are different denominators. Do not equate the difference with a pure boundary-error rate.
- Invalid-item penalties are 75,465 / 31,764 / 64,498. Penalized exact precision after both steps is 5.64% / 12.02% / 3.39%; anchored character precision excludes the unknown extents of those invalid items. Always retain this qualification.
- `quote_not_found` includes wrong occurrence indices as well as missing exact quotes. Error categories do not uniquely identify hallucination. Per-request errors can overlap; counts in request-errors.csv are not additive.
- Preserve original runs and prompts. This analysis was defined after strict failure inspection; it is exploratory, not a preregistered model ranking or a causal format ablation. No changes to model settings or new inference follow automatically.
- Qwen 2B local and Qwen 4B full uploads at this source revision contain only 10 pilot documents. They are excluded here and their scores are not published. Qwen 4B local/OpenMed have report templates only. Ask the operator for full artifacts rather than duplicate inference.
- Before paper-wide comparisons, obtain the native count files, original cohort gate, completed operator/environment records and remaining benchmark conditions. All three result files record the same cohort hash, but this does not independently verify capacity eligibility.

## Inspect the decomposition

- [summary.csv](summary.csv): all three scoring stages, exact/character P/R/F1 (0–1), invalid items and request errors.
- [tables/breakdowns.csv](tables/breakdowns.csv): 1,290 rows, by category, tier×kind×T, T-level, document type, length, subject count and generator. Filter analysis_id, stage, metric, axis and group; do not sum across overlapping axes.
- [request-errors.csv](request-errors.csv): number of requests affected by each error, separately by stage.
- Per-run analysis.json: all metrics, op/subject-role recall, per-document values and provenance. Per-request gzip: decoding routes and item/error counts, with raw text accessible in the original response by request ID.
- [INPUTS.json](INPUTS.json): immutable source links and byte-level SHA-256. Analysis code was frozen at `66e4b46` before computing secondary scores. Table export source hash is in tables/provenance.json.

## Reproduce

Use Python 3.12 and repository dependencies. Retrieve result.json and responses.jsonl from the immutable links in INPUTS.json. Use the exact frozen-release gold JSONL whose SHA is recorded there. Do not edit original source/config hashes. Run once per completed condition:

```bash
python -m src.analysis.response_diagnostics \
  --gold path/to/gold.jsonl \
  --responses path/to/run/responses.jsonl \
  --strict-result path/to/run/result.json \
  --output path/to/new-analysis/run-id
python -m src.analysis.export_diagnostics \
  --analyses path/to/new-analysis/*/analysis.json \
  --output path/to/new-analysis/tables
```

Strict original code/source hashes must match. Full rule definitions and limitations: [guide](../../../../docs/guide/response-diagnostics.md). Summary rows are a concatenation of per-run summary.csv files with directory name added as analysis_id. request-errors.csv counts each normalized error type at most once per request; strict item index prefixes are removed. These tables do not pool model results.
