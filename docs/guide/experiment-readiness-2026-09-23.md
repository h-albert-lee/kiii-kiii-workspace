# Earlier 2026-09-23 inventory snapshot

This snapshot predates implementation of the execution adapters. For current status see [STATUS](../../STATUS.md) and the [runbook](experiment-runbook.md). The inventory remains valid for the provisional protocol, but its implementation TODOs below have been superseded by ADR-0029.

# Experiment readiness — 2026-09-23

## Confirmed

- Final release: 1,440 documents, 218,664 spans; single `test` set, no benchmark training or validation split.
- Dataset Hub pin: `2df0589d695c18665fd83d4ca5512e03ca0767f6` (`experiments/releases/kiii-v1-hub.json`). Local release checksums verified today.
- User-reported document appropriateness review: five financial-sector practitioners, each a different 10% sample. This does not establish span annotation accuracy (ADR-0028).
- All 91 existing tests pass.
- Offline inventory: `experiments/preflight/0923-inventory.json`. No model calls or tuning on benchmark outcomes.

## Provisional protocol volume

At 1,200-character cores and 1,200-character halos, the 1,440 documents require 13,723 requests per prompted model per condition. Full-context CONTEXT fields alone repeat 263,942,634 Unicode characters, versus 44,259,940 for local-window CONTEXT. These are not token counts, billable usage or total prompt lengths: system definitions, TARGET duplication, serialization/chat framing, outputs, reasoning and retries are excluded. No dollar cost is inferred.

The coverage audit finds zero annotated spans extending past the assigned core's permitted output halo. This is a representability check, not evidence that a model can return every span within the 4,096-token output cap. Do not optimize protocol choices from benchmark detector results.

## Execution order

1. Implement provider dispatch, actual-token counters, resumable request logging, error/finish-reason normalization and explicit cost ceilings.
2. Verify access, exact model IDs/revisions, context limits and pricing for the four planned LLMs. Obtain endpoint/GPU details for Qwen/Kanana where needed.
3. Calibrate the shared extraction prompt, output budget and core size on separate pilot examples only; then freeze settings.
4. Implement frozen Presidio/custom-rule, ko-pii and OpenMed adapters, with explicit label mappings and out-of-scope treatment. No fitting on benchmark labels.
5. Measure model-specific actual tokens and establish the common eligible document set before preparing final full/local manifests.
6. Run one end-to-end pilot per adapter; verify response integrity, offsets, failures and usage accounting. Freeze run configuration and total cost before full paid inference.
7. Execute, score every planned request including failures, produce paired document bootstrap intervals and populate the leaderboard from result files.

No provider adapters or actual tokenizer counters exist yet. The inventory and passing offline tests must not be reported as completed detector experiments.
