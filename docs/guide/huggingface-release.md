# Dataset release and evaluation

## Public v1 (2026-09-22)

Repository: https://huggingface.co/datasets/nmixx-fin/kiii-kiii

Frozen input config: `experiments/releases/kiii-v1-hub.json`.

```sh
.venv/bin/python -m src.eval.dataset \
  --repo nmixx-fin/kiii-kiii \
  --revision 2df0589d695c18665fd83d4ca5512e03ca0767f6 \
  --split test --directory experiments/prepared/kiii-v1-full
```

Add `--smoke-limit 3` for a pipeline check only, or `--mode local_window` for the local-context condition. This command prepares requests and does not call an evaluation model.

ADR-0027 supersedes the initial private-release policy below. The user authorized public repository `nmixx-fin/kiii-kiii` and CC BY-NC 4.0. The final folder is `data/releases/kiii-v1`, and source card is `docs/releases/kiii-v1-README.md`. Use the commit recorded in `data/releases/kiii-v1.upload.json` for experiments. Public upload requires the additional explicit `--public` flag. The rc1 workflow below remains useful for reproducible local preparation; its pending-license/private defaults describe the earlier staging phase, not the public v1 release.

The current release target is `data/releases/kiii-v1-rc1`. Packaging is local; providing an API key later does not automatically publish anything. The upload helper requires an explicit `--upload` and an `OWNER/REPO` destination. Initial publication is private; the draft license is unspecified and human annotation review remains pending.

## Build and verify

```sh
uv pip install --python .venv/bin/python -r requirements-hf.txt
.venv/bin/python scripts/package_dataset.py \
  --config experiments/releases/kiii-v1-rc1.json \
  --output data/releases/kiii-v1-rc1 \
  --report data/corpus/main-1440-v1/release-audit.json
```

The builder selects accepted documents from explicit sources, records local provenance separately, verifies all expected IDs and original plan seeds, rechecks validation and exact text duplicates, and publishes a local folder only if all 1,440 documents pass. No silent exclusion of failed documents. Interrupted-run summaries can be stale; that run is read from accepted attempt states instead. Existing release folders cannot be overwritten.

Expected files:

- `data/test.jsonl`: all 1,440 evaluation documents.
- `README.md`: dataset card, annotation caveats, schema and usage.
- `taxonomy.yaml`, `statistics.json`, `split-manifest.json`, `release-manifest.json`.

All documents belong to one evaluation set, named `test` for Hugging Face compatibility. No train/validation partition is created. Do not train or tune on this benchmark; use separate pilot documents for prompt/threshold calibration and freeze settings before inference. Benchmark-trained baselines, including KLUE fine-tuning, are excluded. Frozen pretrained NER models and rule-based baselines remain eligible. Actual length distribution may differ from planned length; preserve both. Exact text duplicates are rejected, while near-duplicates and repeated synthetic identifiers may remain.

`scripts/finalize_dataset.py` can wait on the final generation lock, build the folder, load the full evaluation set with Hugging Face Datasets and prepare three plumbing-only examples through the evaluation pipeline. It never uploads or invokes evaluation models. Status lives in `release-audit.status.json`; incomplete generation leaves an audit report rather than a falsely complete release.

## Prepare experiments from exactly the release files

```sh
.venv/bin/python -m src.eval.dataset \
  --local data/releases/kiii-v1-rc1 --split test --smoke-limit 3 \
  --directory experiments/prepared/plumbing-smoke

# After calibration on separate pilot data, prepare the complete benchmark.
.venv/bin/python -m src.eval.dataset \
  --local data/releases/kiii-v1-rc1 --split test \
  --directory experiments/prepared/test-full
.venv/bin/python -m src.eval.dataset \
  --local data/releases/kiii-v1-rc1 --split test --mode local_window \
  --directory experiments/prepared/test-local
```

Full-context request manifests repeat input text and can be large. The smoke check only verifies serialization and prompt construction; its manifest is marked `plumbing_smoke_only` and must not be used for model tuning or headline results. Real tokenizer preflight and common eligible document selection remain required before paid inference; see [evaluation.md](evaluation.md). Existing provider/NER dispatch adapters are not implemented by this release preparation.

After upload, use `--repo OWNER/REPO --revision FULL_COMMIT_SHA` instead of `--local`. Floating branches such as `main` are rejected. Files are checked against the release manifest before preparation; output includes release hash, split and version. No Hub contact is needed for local experiments.

## Later upload

Set `HF_TOKEN` in the process environment or the ignored local `.env`; do not commit or put it in the dataset card. The helper reads the environment, not `.env` automatically.

```sh
# Preview only; no credentials needed, no network calls:
.venv/bin/python scripts/upload_dataset.py \
  --folder data/releases/kiii-v1-rc1 --repo OWNER/REPO

# Only after the owner supplies the destination and token:
.venv/bin/python scripts/upload_dataset.py \
  --folder data/releases/kiii-v1-rc1 --repo OWNER/REPO --upload
```

The uploader checks hashes and sends only files named by the release manifest plus the manifest itself. Raw responses, failure logs, local source paths, evaluation outputs and credentials stay outside the upload folder. The repository is created private; an existing public repository is rejected for this draft. Record the returned commit SHA in evaluation runs. Public visibility, final license, human review and citation remain separate release decisions.

Official references: [supported file layout and split metadata](https://huggingface.co/docs/datasets/main/repository_structure), [Hub upload API](https://huggingface.co/docs/huggingface_hub/main/guides/upload).
