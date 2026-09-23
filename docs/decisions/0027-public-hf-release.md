# ADR-0027: Public Hugging Face release under CC BY-NC 4.0

- Date: 2026-09-22
- Status: accepted; explicit user authorization to upload to nmixx-fin, followed by explicit public visibility and CC BY-NC 4.0 instructions.

All final twelve Astra documents passed, bringing the corpus to 1,440 documents and 218,664 spans. Full release audit found no schema/offset validation errors or exact duplicate document text. Actual length buckets are 482 short, 478 medium and 480 long; twelve planned/actual length mismatches remain transparently represented. Generator counts are 820 GLM and 620 Astra.

Publish `nmixx-fin/kiii-kiii` as a public dataset with one `test` split under CC BY-NC 4.0. This supersedes private visibility and pending license language in ADR-0025/0026. The dataset card describes synthetic construction and automated validation without claims about human adjudication. User requested omitting discussion of human review from public materials; original local audit records are preserved.

Prepare a new immutable `data/releases/kiii-v1` folder from the rc1 corpus, updating only release metadata and documentation. Preserve the existing rc1 artifact and annotation values. The public manifest includes only dataset files, taxonomy, statistics, membership, README and the official CC license text; tokens, private source paths, request IDs, raw attempts and operational logs are excluded. The source README is retained at `docs/releases/kiii-v1-README.md`.

Upload only with explicit public mode and the user-provided token held in the upload process environment. The token is not saved in the dataset or workspace files. Record the returned commit SHA and pin experiment input to it. Validate public anonymous download, checksums and dataset loading before reporting completion.
