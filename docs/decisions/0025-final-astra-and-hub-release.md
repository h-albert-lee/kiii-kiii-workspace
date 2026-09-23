# ADR-0025: Final Astra recovery and local Hub release preparation

- Date: 2026-09-21
- Status: accepted; user authorized the previously requested OpenAI $10 increase, data organization and experimental preparation, with upload deferred until a later API key.

Final 12 unresolved documents (11 long, one medium) are submitted to GPT-6 Astra Batch under `final12-astra`. The prior stage OpenAI allowance of $47 becomes $57. The stage used $44.81025, leaving a final-run ceiling of $12.18975. This is a separate ledger from previous-stage OpenAI spending. No validation criteria are relaxed. GLM cumulative cap remains $200.

Package all 1,440 accepted documents into `kiii-v1-rc1`, a local Hugging Face-compatible release candidate. Revalidate offsets, supported checksums/formats, taxonomy, subjects and exact duplicate text; refuse incomplete releases. Strip generator operational metadata using an allowlist. Preserve actual generating model, prompt/profile version, surface/canonical values and document-local entities. Local source provenance and failure logs remain outside the upload folder.

Use 360 validation and 1,080 test documents: deterministic SHA-256 ordering by ID selects one validation document from each four-document planned cell. This is a declared split before detector evaluation, not a claim that the generator was never debugged on these documents. No train split. Keep planned length and actual length separately; an initial audit found 11 length-cell mismatches among the 1,428 already accepted documents. Exact-text duplication is checked, near-duplicate and semantic dependence are not certified absent.

The data card explicitly states automatic validation only, pending human review and pending license. No affiliations/repository URL are inserted into the anonymous paper. First Hub upload will be private, only after a destination and token are supplied; this task performs no upload. No license is invented.

The local finalization process waits for generation using the existing process lock, builds only if complete, verifies loading both splits with Hugging Face Datasets and prepares three validation examples with the existing evaluator. Inference is not run. Hub-backed evaluation requires a commit SHA and checks file hashes, allowing local and uploaded experiments to use the same release artifacts. Provider/NER adapters remain separate work.
