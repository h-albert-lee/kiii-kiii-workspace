# Evaluation protocol and offline scoring

For the runnable provider/baseline workflow, use [the experiment runbook](experiment-runbook.md). This page documents offline protocol/scoring primitives.

Protocol: [ADR-0020](../decisions/0020-long-context-evaluation.md). All commands below are offline and never call a model. Run from repository root. Use the frozen single evaluation set (ADR-0026). Calibrate on separate non-overlapping pilot examples; do not carve a development split out of the 1,440 benchmark documents.

```sh
.venv/bin/python -m src.eval.run prepare --corpus data/test.jsonl --directory experiments/prepared/full
.venv/bin/python -m src.eval.run prepare --corpus data/test.jsonl --directory experiments/prepared/local --mode local_window
```

Each new directory contains `requests.jsonl`, `gold.jsonl`, `manifest.json` and `boundary-audit.json`. Pass **only each request's messages** to the model adapter, never gold/audit files. IDs, hashes and windows stay in orchestration metadata. Existing directories/results are not overwritten. Manifest hashes include corpus, taxonomy, requests and evaluation source files, including uncommitted changes. Default partition sizes require development calibration before final experiments.

## Capacity measurements

Adapters must measure the complete messages using the actual model tokenizer including chat framing. Supply one JSONL row per model per request:

```json
{"model":"model-revision","request_id":"doc:0000","request_sha256":"from-request","tokenizer_revision":"exact tokenizer/chat-template revision","input_tokens":12345,"input_limit":32768,"output_limit":4096,"total_limit":32768}
```

These numbers are illustrative. `input_limit` and `output_limit` are endpoint caps; `total_limit` is the combined cap. If a provider documents independent input/output limits, their sum can represent the combined limit. Reasoning that shares output budget must be included. Do not substitute character estimates or corpus `n_tokens`.

```sh
.venv/bin/python -m src.eval.run preflight --directory experiments/prepared/full --measurements counts.jsonl --output capacity.json
```

The result lists common eligible document IDs. The checker trusts adapter measurements; it cannot authenticate a token count. Before inference, explicitly prepare both final conditions from the same common eligible corpus and measure the new manifests again. The low-level scoring command does not automatically apply exclusions. The main `src.eval.execute` benchmark runner requires the all-model, both-condition `src.eval.cohort` gate. Publish exclusion counts and reasons; never drop failed inference documents after seeing results.

## Response contract and scoring

An adapter writes one row per request, preserving exact returned content:

```json
{"request_id":"doc:0000","request_sha256":"from-request","model":"model-revision","status":"ok","finish_reason":"stop","text":"{\"spans\":[]}","usage":{"input_tokens":12345,"output_tokens":6,"reasoning_tokens":0,"latency_seconds":1.2}}
```

Only successful terminal reasons `stop`, `end_turn`, `STOP` are accepted. Normalize provider status/finish reasons explicitly in the adapter. `length`, refusal and network errors must not become successful empty responses. Missing responses count as failures. Malformed JSON, unknown labels, changed quotes, invalid occurrence counts or spans outside the owned core reject the whole request. No markdown stripping or fuzzy matching. Offsets use Python Unicode code points and exclusive end; repeated exact quotes are anchored by occurrence within TARGET, including overlapping matches.

```sh
.venv/bin/python -m src.eval.run score --directory experiments/prepared/full --responses responses.jsonl --model model-revision --output result.json
.venv/bin/python -m src.eval.run compare --first result-a.json --second result-b.json --output comparison.json
```

Scoring includes every plan document, including failures. Comparison checks identical corpus/taxonomy and output settings and resamples whole documents (2,000 draws, seed 0). It may compare full/local context, so inspect condition names when interpreting results. For correlated variants, a cluster bootstrap is required instead of this independent-document bootstrap.

Results include strict mention micro F1, category-aware character coverage F1, all-mentions entity recall, hard-negative false-positive rate and non-PII character mask rate. The last measure is an overmasking proxy, not semantic information loss. Role/operation tables are recall only: predictions do not assert role or operation. Per-category and tier×kind×T tables include false positives. Usage totals reflect supplied records only; `requests_missing_usage` marks incomplete accounting. Adapter retries and costs must be logged separately; summed request latency is not wall-clock duration.

Provider dispatch, native counters, resumable budget execution, frozen baseline mappings and final result export are implemented. See the runbook and ADR-0029 for supported variants and live-validation requirements. No detector results have been measured in this preparation step.
