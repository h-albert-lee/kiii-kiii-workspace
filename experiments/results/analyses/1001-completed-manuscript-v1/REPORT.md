# Completed manuscript snapshot — 2026-10-01

ADR-0038 closes inference collection at completed artifacts: **12 LLM models / 22 conditions + 3 frozen baselines = 15 systems / 25 conditions**. Qwen3.5-2B local and Qwen3.5-4B full are pilot-only and omitted, not scored zero. All ten full/local model pairs are retained. Selection is by artifact completeness, not score. No new inference.

## Results

Strict and D scores below use a 0–100 scale. D is the observable detection proxy from whole-response JSON-fence removal plus itemwise validation, retaining all gold and charging one exact FP per invalid parsed item. It remains affected by unparseable/truncated responses. Baseline D and format are N/A.

| Model | Context | Docs | Strict F1 | Format % | D-P | D-R | D-F1 |
|---|---|---:|---:|---:|---:|---:|---:|
| kakaocorp/kanana-2-3b-instruct | full_context_targeted | 1440 | 1.023 | 72.222 | 5.636 | 2.203 | 3.168 |
| kakaocorp/kanana-2-3b-instruct | local_window | 1440 | 1.616 | 63.616 | 12.018 | 2.467 | 4.093 |
| Qwen/Qwen3.5-2B | full_context_targeted | 1440 | 0.117 | 28.478 | 3.394 | 1.077 | 1.635 |
| Qwen/Qwen3.5-4B | local_window | 1440 | 0.970 | 47.366 | 12.586 | 6.516 | 8.587 |
| Qwen/Qwen3.5-9B | full_context_targeted | 1440 | 3.269 | 75.792 | 18.582 | 11.812 | 14.443 |
| Qwen/Qwen3.5-9B | local_window | 1440 | 3.662 | 76.346 | 22.618 | 15.020 | 18.052 |
| kakaocorp/kanana-1.5-8b-instruct-2505 | full_context_targeted | 1438 | 0.334 | 46.092 | 5.107 | 6.086 | 5.554 |
| kakaocorp/kanana-1.5-8b-instruct-2505 | local_window | 1438 | 0.843 | 40.006 | 12.014 | 6.401 | 8.352 |
| LGAI-EXAONE/EXAONE-4.5-33B | full_context_targeted | 1440 | 0.811 | 62.880 | 8.673 | 9.070 | 8.867 |
| LGAI-EXAONE/EXAONE-4.5-33B | local_window | 1440 | 1.854 | 80.128 | 14.678 | 14.329 | 14.501 |
| Qwen/Qwen3-30B-A3B | full_context_targeted | 1440 | 0.516 | 90.418 | 9.383 | 6.309 | 7.545 |
| Qwen/Qwen3-30B-A3B | local_window | 1440 | 1.725 | 93.777 | 15.037 | 11.842 | 13.250 |
| google/gemma-4-E2B-it | full_context_targeted | 1440 | 0.003 | 0.036 | 16.550 | 6.894 | 9.734 |
| google/gemma-4-E2B-it | local_window | 1440 | 0.005 | 1.275 | 28.097 | 7.701 | 12.089 |
| google/gemma-4-E4B-it | full_context_targeted | 1440 | 5.337 | 83.998 | 16.346 | 12.635 | 14.253 |
| google/gemma-4-E4B-it | local_window | 1440 | 7.225 | 87.342 | 30.417 | 16.981 | 21.795 |
| google/gemma-4-12B-it | full_context_targeted | 1440 | 0.043 | 5.545 | 31.941 | 26.147 | 28.755 |
| google/gemma-4-12B-it | local_window | 1440 | 0.046 | 5.553 | 30.836 | 28.848 | 29.809 |
| google/gemma-4-26B-A4B-it | full_context_targeted | 1440 | 7.971 | 95.774 | 34.779 | 24.603 | 28.819 |
| google/gemma-4-26B-A4B-it | local_window | 1440 | 7.398 | 96.101 | 31.135 | 27.200 | 29.035 |
| google/gemma-4-31B-it | full_context_targeted | 1440 | 0.004 | 4.977 | 28.997 | 31.587 | 30.237 |
| google/gemma-4-31B-it | local_window | 1440 | 0.017 | 4.562 | 28.862 | 34.862 | 31.579 |
| presidio | document | 1440 | 10.149 | N/A | N/A | N/A | N/A |
| ko-pii | document | 1440 | 9.426 | N/A | N/A | N/A | N/A |
| openmed | document | 1440 | 2.087 | N/A | N/A | N/A | N/A |

## Interpretation and limits

Local D-F1 exceeds full in all ten completed pairs; strict F1 favors local in nine. Gemma-26B-A4B is the strict exception (+0.573 full−local points), while its D contrast is −0.216 points. Paired pointwise bootstrap intervals are in tables/paired.csv; post-hoc, 2,000 draws, seed 0, no multiplicity correction or stochastic reruns.

Cross-family values are descriptive. Kanana-1.5-8B uses 1,438 documents and all other runs 1,440; no cohort pooling or gate substitution. Original count files remain unavailable for independent native-capacity audit. Separate representative pilot calibration is not established. Model selection/extensions follow qualitative formatting failures. Gemma native sampling differs and 31B uses FP8 weights/KV, other Gemma models BF16. The external runner is preserved as external: output replay is not evidence of deployment/source equivalence.

## Audit and reproduction

INPUTS.json pins every result/diagnostic hash and operator source URL. Native-run replay evidence is in ../1001-failure-decomposition-v1; Gemma replay is in ../1001-gemma-external-replay-v1 and ../1001-gemma-failure-decomposition-v1. Gemma shared artifact hashes, raw unique coverage, result raw hash and recorded cohort summary hash were checked for all ten runs; strict metrics, per-document counts, failures and reconstructed requests all match. Original result.json files are unchanged.

Retrieve the exact input files using INPUTS.json source directories, keeping their indicated local paths or adapting a copy of the manifest. Then:

```sh
python -m src.analysis.completed_manuscript --inputs experiments/results/analyses/1001-completed-manuscript-v1/INPUTS.json --output /tmp/kiii-completed-tables
```

The output is a descriptive manuscript snapshot, not src.eval.export or a newly certified common-capacity leaderboard. No live src/eval source was modified. Original result/response hashes and unverified execution facts remain visible.
