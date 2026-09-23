# ADR-0026: One evaluation set, no benchmark-trained baselines

- Date: 2026-09-21
- Status: accepted; explicit user instruction

Supersedes the 360/1,080 split decision in ADR-0025. Keep every one of the 1,440 documents in a single evaluation set. Use the conventional Hugging Face split name `test`, stored as `data/test.jsonl`; this is a compatibility label, not a further dataset partition. No train or validation split is published.

Exclude models trained or fine-tuned on this benchmark, including the earlier KLUE-RoBERTa fine-tuning candidate. The compact experiment retains four prompted LLM candidates and three inference-only baseline candidates (Presidio/custom frozen rules, existing ko-pii weights, OpenMed/privacy-filter-multilingual weights). Their applicability and label mappings still need verification; no task-specific fitting on benchmark labels is allowed.

Develop prompts, mappings, window/output budgets and thresholds on separate non-overlapping pilot examples; freeze them before detector inference on the benchmark. Generator debugging and automatic data validation do not constitute a claim that benchmark contents were never inspected. No empirical claim about whether other current benchmarks use splits is needed for this decision.

The offline pipeline smoke check may serialize three documents to verify loading/offsets and prompt construction. It runs no model and performs no tuning. Such manifests are marked `purpose: plumbing_smoke_only`; benchmark preparation uses all 1,440 documents and `purpose: benchmark`. Capacity exclusions, if necessary, must follow the existing predeclared common-model protocol and be reported explicitly, not chosen after seeing scores.

Update the packaging code, dataset card, loader, finalizer, release configuration and current model scope together. Generation and paid request budgets remain unchanged. Hugging Face upload still awaits the user's token and repository destination.
