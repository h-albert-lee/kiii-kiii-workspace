# ADR-0020: Full-context targeted extraction and shared output partition

- Date: 2026-09-20
- Status: accepted protocol direction; numerical limits provisional until development calibration
- Context: 1,440-document target, compact evaluation per ADR-0019. Long input capacity and the ability to output every span are separate constraints. User requested advance evaluation tooling and a fair protocol.

## Decision

Primary LLM condition is `full_context_targeted`: each call sees the entire document, but returns only spans starting in a deterministic target core. Adjacent right context permits spans crossing the core boundary. Core partition uses text length only, never gold labels. All models use identical cores, taxonomy, output schema and output allowance. This evaluates a multiple-call extraction system, not single-call ability.

Paired ablation `local_window` keeps those same cores but supplies only nearby context. Its performance is not presented as evidence of full-document reasoning. Whole-document versus local context comparisons report cost and failure rates alongside F1.

Initial development defaults are core 1,200 Unicode characters, halo 1,200, output allowance 4,096 tokens. These are engineering starting points, not empirically validated settings. Select and freeze them on a disjoint development set, considering output density, entity boundary coverage, actual tokenizer lengths and input cost. No tuning on final test labels or model-specific test-time window adjustment.

Use real tokenizer/chat-template counts or provider token-count endpoints. Reserve the same output allowance; where reasoning shares that allowance, include it and record the reasoning configuration. Compare on the common eligible document set, selected before inference, and report excluded counts by length bucket. No silent input truncation. Official model limits must be rechecked at execution.

Quotes are anchored exactly to TARGET using one-based occurrence counts; no fuzzy gold-based repairs. Any invalid item rejects the whole request. Missing, truncated and failed responses predict no spans for their owned core; their gold remains false negatives. This is an end-to-end extraction score; always show request failures separately. Do not retry invalid answers with a different prompt. Infrastructure-only retries must have one preset cap and retain every attempt's cost.

Strict category+boundary mention F1 is primary; category-aware character F1 and entity-all-mentions exact recall supplement it. Report category, tier×kind×T, subject count, length, generator, operation recall and subject-role recall. Character coverage is not TAB risk-weighted recall. Entity all-mentions recall does not test model entity linking.

## Consequences

Repeated full input increases cost. Larger cores may reduce cost after development calibration. An optional one-call condition can be separate; it must not be silently mixed into the primary condition. Report calls, input/output/reasoning tokens, latency, failures and monetary cost when available. Equal token allowances are a reproducible resource constraint, not equal information content across tokenizers.

Audit gold spans that extend beyond the target halo after partitioning. Never exclude those spans or move boundaries using gold; publish representability limits. Full-context access alone does not establish that every example requires long-range reasoning.

NER/rule baselines need their own native adapters and frozen label mappings. Report full taxonomy and a declared shared-label subset separately. Their shorter receptive fields are part of their capabilities, not grounds for calling their windowed scores full-context LLM scores. Fine-tuning and prompt development must avoid the final test documents and linked variants.

## Implementation scope

`src/eval/` now prepares frozen request manifests, checks externally measured capacity, decodes standard response records, scores and performs document-paired bootstrap comparison. API dispatch, real tokenizer integrations, baseline adapters, monetary pricing and TAB weights remain separate implementation work. This ADR does not authorize paid evaluation runs.
