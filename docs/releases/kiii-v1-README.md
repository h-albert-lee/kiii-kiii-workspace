---
license: cc-by-nc-4.0
language:
- ko
task_categories:
- token-classification
pretty_name: Kiii² — Korean Financial PII Benchmark
size_categories:
- 1K<n<10K
tags:
- synthetic
- privacy
- pii
- finance
- korean
- benchmark
configs:
- config_name: default
  default: true
  data_files:
  - split: test
    path: data/test.jsonl
---

# Kiii²: Korean Financial PII Benchmark

> **Preview release:** This is a preview version of Kiii². The official release is coming soon.
>
> **프리뷰 버전:** 현재 데이터셋은 프리뷰 버전이며, 정식 버전은 조만간 공개될 예정입니다.

**Kiii-Kiii: Korean Identifiers, Identifiability, and Ill-formed Inputs** is a regulation-grounded benchmark for detecting personally identifiable information in synthetic Korean financial documents.

Kiii² contains **1,440 documents** and **218,664 annotated spans**, covering **36 PII categories**, **10 document types**, four surface-transformation levels, and documents with one, three or eight customer subjects. The full corpus is released as a **single evaluation set**.

한국 금융 문서의 개인정보 탐지를 평가하기 위한 합성 벤치마크입니다. 총 1,440개 문서와 218,664개 개인정보 스팬을 포함하며, 전체 데이터를 하나의 평가 세트로 제공합니다.

## At a glance

| Property | Contents |
|---|---|
| Release | `kiii-v1` |
| Language | Korean |
| Documents / PII spans | 1,440 / 218,664 |
| Taxonomy | 36 categories across Legal and Identifiability tiers; identifier and attribute kinds |
| Transformation levels | T0, T1, T2, T3 — 360 documents each |
| Customer subjects per document | 1, 3 or 8 — 480 documents each |
| Document types | 10 — 144 documents each |
| Split | `test` only; no train or validation partition |
| License | [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) |

## Quickstart

```python
from datasets import load_dataset

dataset = load_dataset("nmixx-fin/kiii-kiii", split="test")
example = dataset[0]

print(example["doc_id"], example["doc_type"])
for span in example["spans"]:
    surface = example["text"][span["start"]:span["end"]]
    assert surface == span["surface"]
    print(span["category"], surface)
```

For reproducible experiments, pin the dataset commit:

```python
dataset = load_dataset(
    "nmixx-fin/kiii-kiii",
    revision="<full dataset commit SHA>",
    split="test",
)
```

The repository uses standard JSONL files and requires no custom dataset loading code.

## Benchmark design

The taxonomy separates regulation-grounded **Legal** categories from context-dependent **Identifiability** categories, with **identifier** and **attribute** kinds in each tier. Category definitions, span policies, source references and transformation operators are provided in [`taxonomy.yaml`](taxonomy.yaml).

Documents vary along document type, transformation level, customer count and planned length. The four transformation levels range from canonical forms to structural variation, including fragmented mentions and conversational references. Use each span's `applied_ops` for operator-specific analysis rather than assuming all spans in a document receive its maximum transformation level.

| Document type | Documents |
|---|---:|
| Bank statements | 144 |
| Card statements | 144 |
| Customer-service transcripts | 144 |
| Complaint cases | 144 |
| Securities trade reports | 144 |
| Loan contracts | 144 |
| Insurance claims | 144 |
| KYC forms | 144 |
| Internal memos | 144 |
| Phishing reports | 144 |

Actual approximate length buckets contain **482 `1k`**, **478 `4k`** and **480 `16k`** documents. These labels and `n_tokens` are character-based generation estimates, **not tokenizer measurements**. Twelve documents differ from their originally planned length bucket; both actual and planned values are retained. Measure complete prompt lengths with the evaluation model's tokenizer before inference.

## Construction and validation

Language models compose document templates with placeholders. Code supplies synthetic identifier values and transformations, fills the placeholders and derives annotation offsets. Selected documents were generated with **GLM-5.2-FP8 (820)** and **GPT-6 Astra (620)**; per-document provenance records the generator and prompt/profile versions. Failed attempts are excluded from the released data.

The release passes automated checks for document schema, span boundaries and surfaces, category consistency, supported identifier checksums/formats, subject references, length rules and exact duplicate text. All 1,440 expected document IDs are present, generation seeds are unique, and no exact duplicate document text was found. These checks do not guarantee exhaustive PII coverage or semantic correctness of every annotation.

No real customer records were used as source material. Synthetic names and identifiers may coincidentally resemble real ones; the data is not a directory of real people or accounts.

## Schema

Each JSONL row is one document. Offsets are **Unicode code-point indices**, with an inclusive start and exclusive end, as in Python slicing. Do not normalize whitespace or Unicode before applying the offsets.

| Field | Meaning |
|---|---|
| `doc_id`, `text` | Unique ID and original document text |
| `doc_type`, `variation_level` | Document family and maximum transformation level |
| `num_subjects`, `subjects` | Customer count; document-local subject IDs and roles |
| `context_len_bucket`, `planned_context_len_bucket`, `n_tokens` | Actual/planned approximate length buckets and estimated token count |
| `spans` | PII annotations described below |
| `hard_negatives` | Annotated non-PII examples with offsets, surface and type |
| `generator` | Model, prompt version, profile version, reference date, slice and transport |
| `taxonomy_version`, `release_version`, `generation_seed` | Reproducibility metadata |
| `pre_masked` | Whether the document includes pre-masking |

Each span includes `id`, `start`, `end`, `surface`, `canonical`, `category`, `tier`, `kind`, `span_policy`, `entity_id`, `subject_id`, `subject_role`, `subtype`, `applied_ops`, `regex_catchable` and optional `fragment` metadata. Entity and subject IDs are scoped to their document. Fragment metadata records the group, index and fragment count. Canonical values and gold metadata are scoring annotations and must not be included in model inputs.

## Evaluation protocol

For benchmark reporting, use the entire `test` set with frozen models and settings. There is no benchmark training or development split. Tune prompts, thresholds and adapters on separate, non-overlapping pilot data, then freeze them before benchmark inference. The intended comparison includes prompted LLMs, pretrained extractors used without task-specific fitting, and rule-based detectors.

For long documents, full-context targeted extraction can provide the complete document while requesting spans from a predetermined output region. Compare with local-window extraction using the same output regions, output allowance and failure rules. Partition without gold labels, measure actual input capacity, and report exclusions, failed/truncated requests and inference cost. Do not silently drop failed documents from scoring.

Report strict category-and-boundary span precision, recall and F1, supplemented by category-aware character coverage and breakdowns by tier/kind, transformation level, operation, document length, subject count and generator. Fragmented spans and repeated entity mentions need explicit aggregation rules. Character coverage is not risk-weighted recall; detecting all mentions does not establish entity-linking accuracy.

## Limitations

- The data is synthetic and may retain generator or template artifacts. Performance need not transfer directly to real financial records.
- Generator allocation is not balanced across lengths. Stratify comparisons by generator and length; flag generator models if they are also evaluated as detectors.
- Exact deduplication does not exclude near-duplicates, shared templates or repeated synthetic values. Unique seeds do not prove semantic independence.
- Some annotation boundaries and context-dependent categories are inherently ambiguous. Regulatory mappings reflect this benchmark's operational definitions.
- Results measure benchmark detection performance; they do not establish legal compliance or production readiness.

## Files and reproducibility

- [`data/test.jsonl`](data/test.jsonl): the full 1,440-document evaluation set.
- [`taxonomy.yaml`](taxonomy.yaml): category and transformation definitions.
- [`statistics.json`](statistics.json): distributions and annotation counts.
- [`split-manifest.json`](split-manifest.json): membership of the single evaluation set.
- [`release-manifest.json`](release-manifest.json): release metadata and SHA-256 checksums.
- [`LICENSE`](LICENSE): CC BY-NC 4.0 license text.

## License and attribution

This dataset is released under **Creative Commons Attribution–NonCommercial 4.0 International (CC BY-NC 4.0)**. Attribute **Kiii² / nmixx-fin**, link to this dataset and the license, and indicate modifications when sharing adapted versions. See [the full license](LICENSE) for the governing terms.

Suggested dataset citation:

```bibtex
@misc{kiii2026dataset,
  author = {{nmixx-fin}},
  title = {Kiii-Kiii: Korean Identifiers, Identifiability, and Ill-formed Inputs},
  year = {2026},
  howpublished = {Hugging Face dataset},
  url = {https://huggingface.co/datasets/nmixx-fin/kiii-kiii}
}
```
