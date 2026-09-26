# ADR-0035 — Add two medium local detectors without replacing running experiments

Date: 2026-09-26. Status: accepted scope; model selection delegated to the agent. Supplements ADR-0034.

## Context

The operator reports that 은빈 is running the small models and has encountered frequent output-format failures. The operator requested full response retention and assigned available capacity to additional medium models. This extension was selected **after a qualitative failure report**, not before any outcomes were known. Failure rates and final model scores have not been verified here.

## Decision

Assign both models to 은빈, in this order:

1. `Qwen/Qwen3.5-9B`: extend the existing Qwen3.5 2B/4B family comparison.
2. `kakaocorp/kanana-1.5-8b-instruct-2505`: add a larger Korean/English model. It is an older generation than Kanana-2-3B, so this is not an isolated parameter-count ablation.

Each receives full_context_targeted and local_window with the existing frozen protocol. The original six systems/nine conditions remain the core; the extension adds two systems/four conditions, for eight systems/thirteen conditions if completed. Retain all existing failures and runs. Do not replace small-model rows because of unfavorable outcomes.

Official model cards checked on 2026-09-26: [Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B), [Kanana 1.5 8B 2505](https://huggingface.co/kakaocorp/kanana-1.5-8b-instruct-2505). Exact weight/tokenizer revisions, native endpoint counts, deployment memory and available compute must still be recorded by the operator. No GPU deployment or paid inference was initiated by this assignment.

## Execution and interpretation

- Preserve active source/config/prompt/count/gate hashes. New model runs need new run directories. Do not merge executor changes into a live checkout.
- Preserve full received responses, including invalid/truncated outputs. Main scoring still treats failed requests as empty predictions; do not repair them or change prompts from benchmark feedback. Distinguish provider/adapter faults from model formatting failures.
- Count all five models/both conditions before a combined comparison. The separate extended capacity matrix does not replace the core gate. Different gate hashes cannot be combined by the current exporter, even if document IDs match. Preserve original runs and report the extension separately until an audited, provenance-preserving common-cohort analysis is available; never bypass the guard by editing hashes.
- The extension is exploratory. Sara may analyze final paired outputs and failure modes; do not claim a preregistered size-effect test. Keep the four-page paper scope: compact main comparison and context-effect figure, detailed diagnostics in repository artifacts.

Operational details: [은빈 extension handoff](../guide/eunbin-medium-extension.md). API runs remain deferred; cohort coordination remains unassigned.
