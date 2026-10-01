# Format grounding and detection diagnostics

Post-hoc secondary analysis under ADR-0037. Scores/rates below are on a 0–100 scale. Each row keeps its original cohort. No pooled ranking or native capacity validation.

| Model | Condition | Docs | Format compliant % | Empty list % | Strict F1 | Detection P | Detection R | Detection F1 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| kakaocorp/kanana-2-3b-instruct | full_context_targeted | 1440 | 72.22 | 2.18 | 1.02 | 5.64 | 2.20 | 3.17 |
| kakaocorp/kanana-2-3b-instruct | local_window | 1440 | 63.62 | 8.69 | 1.62 | 12.02 | 2.47 | 4.09 |
| Qwen/Qwen3.5-2B | full_context_targeted | 1440 | 28.48 | 1.38 | 0.12 | 3.39 | 1.08 | 1.64 |
| Qwen/Qwen3.5-4B | local_window | 1440 | 47.37 | 4.99 | 0.97 | 12.59 | 6.52 | 8.59 |
| Qwen/Qwen3.5-9B | full_context_targeted | 1440 | 75.79 | 16.83 | 3.27 | 18.58 | 11.81 | 14.44 |
| Qwen/Qwen3.5-9B | local_window | 1440 | 76.35 | 13.82 | 3.66 | 22.62 | 15.02 | 18.05 |
| kakaocorp/kanana-1.5-8b-instruct-2505 | full_context_targeted | 1438 | 46.09 | 0.74 | 0.33 | 5.11 | 6.09 | 5.55 |
| kakaocorp/kanana-1.5-8b-instruct-2505 | local_window | 1438 | 40.01 | 0.23 | 0.84 | 12.01 | 6.40 | 8.35 |
| LGAI-EXAONE/EXAONE-4.5-33B | full_context_targeted | 1440 | 62.88 | 26.36 | 0.81 | 8.67 | 9.07 | 8.87 |
| LGAI-EXAONE/EXAONE-4.5-33B | local_window | 1440 | 80.13 | 29.86 | 1.85 | 14.68 | 14.33 | 14.50 |
| Qwen/Qwen3-30B-A3B | full_context_targeted | 1440 | 90.42 | 53.06 | 0.52 | 9.38 | 6.31 | 7.55 |
| Qwen/Qwen3-30B-A3B | local_window | 1440 | 93.78 | 17.61 | 1.73 | 15.04 | 11.84 | 13.25 |

Format compliance requires normal completion, raw JSON, exact root/item structure and field types, and no duplicate keys. It does not validate quote existence or category vocabulary. Empty lists may comply; empty-list rate uses ALL requests, including failures, as denominator.

Detection P/R/F1 reuses ADR-0036 whole-fence/itemwise scoring: all gold remain, valid items survive malformed siblings, and every rejected parsed item adds one exact FP. This is observable extraction under a fixed parser, not latent ability independently of format. Unparseable and truncated responses stay empty. Original strict scores are unchanged.

failure_types.csv has disjoint request, item and typed-gold partitions with explicit denominators. Gold miss buckets describe the first applicable observation, not a causal decomposition. Unresolved misses with rejected items cannot establish which PII an invalid item intended.

summary.csv additionally contains exact location-only scores on valid known-category items and category-aware character scores. Location scores retain invalid-item FP and collapse same-coordinate labels. Character scores cannot penalize unanchorable items and must be read with exact precision and invalid-item counts.

Duplicate JSON keys retain frozen last-value scoring, but fail structural compliance. Some lost items are unobservable to the original parser. Counts and scores do not correct this limitation.

Kanana 1.5 8B uses 1,438 documents; other runs use 1,440. Native counts/final gates remain unverified. Qwen3-30B/EXAONE are additional operator runs outside the accepted roster. Do not infer a scale effect across model generations or architectures. Baselines have no generative format-compliance task and should show N/A, not 100%.

No new inference, success-only scoring, prompt tuning, fuzzy anchoring or gold-guided repair.
