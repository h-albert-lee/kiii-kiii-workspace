# Overleaf review and manuscript update — 2026-09-22

Project: https://www.overleaf.com/project/6a9fd3f13552b8aca9a09304

Read the project-wide review overview before editing: five unresolved comment threads across four files; no resolved comments. Full comment text, source snapshots and anchor ranges are saved locally under `data/paper-review/2026-09-22/`. The comments are retained, without replies or resolution actions.

## Comments and response in manuscript

| File / original anchor | Comment | Manuscript action |
| --- | --- | --- |
| `00_abstract.tex`: `centre` | “typo” | Standardized to US `call-center`; `centre` was valid British spelling. Thread remains attached to `cent` within the corrected word. |
| `03_taxonomy.tex`: `36 categories` | National sensitivity standards differ; a common definition is needed for model comparisons. | Added shared Korean operational policy. L/I are inclusion grounds, not a universal sensitivity ranking. All systems use a fixed gold taxonomy; prompted models receive definitions, baseline labels use frozen mappings. Tier I does not imply absence of legal protection. |
| `04_benchmark.tex`: Korean-numeral example | Add mixed Sino-Korean/native numerals, including `삼하나육사`. | Added requested mixed numeral example next to the original anchored example. |
| `04_benchmark.tex`: `T3` | Concern about the effort of post-generation checking. | Added concrete automatic validation and provenance; explicitly limited those checks to structural validity, not semantic completeness or realism. No invented reviewer or IAA claims. |
| `06_results.tex`: `main leaderboard` | Analyze each model under L/I, potentially reflecting cultural/legal differences. | Added L-identifier/L-attribute/I-attribute precision/recall crossed with T0–T3. Cultural/legal interpretation requires a separate experiment; a missed span alone is insufficient evidence. |

## Updated project facts

- 1,440 documents, 218,664 spans, 36 categories and ten document types.
- GLM-5.2-FP8: 820; GPT-6 Astra: 620. Both API generators; excluded from headline detector ranking.
- One `test` evaluation set, no training or validation partition and no benchmark-trained baseline.
- Four planned prompted LLMs plus three frozen inference baselines; detector runs are still pending.
- Full-context targeted-output protocol, matching local-window ablation, actual-token capacity preflight, strict span F1 and failed-request accounting.
- Planned versus realized length buckets and generator/length confounding disclosed.
- Preview status and CC BY-NC 4.0. Public identity-bearing dataset URL appears only in the camera-ready branch.
- Removed speculative findings, old 80/20 generator plan, training-split fine-tuning, fabricated IAA placeholder and unsupported universal checksum/production-STT-frequency claims.

## Preservation workflow

1. Read and back up all comments and their exact source ranges.
2. Trigger Overleaf → GitHub sync; fetch and fast-forward the local paper submodule to `0aef4b2` before editing.
3. Edit existing Overleaf documents through native CodeMirror change transactions, preserving file identity and untouched comment anchors. Verify source text and per-file thread IDs after changes.
4. Compile in Overleaf; then export Overleaf changes to GitHub and fast-forward local paper checkout. Do not replace files through an incoming GitHub import.

Validation and final sync receipt are recorded below when complete.

## Completion

- Published paper commit: `38c60ae` — `Update 1440-document preview and evaluation protocol; address review comments`.
- Overleaf → GitHub sync completed; `paper/` is clean and matches `origin/main` exactly.
- Rechecked all five original comment IDs and full message bodies after the final sync: unchanged. None was resolved or replied to.
- Overleaf compile: 0 errors, 33 warnings (bibliography metadata plus ACM reference-format/column-balance warnings); no overfull-box warning. Underfull-box informational messages remain.
- PDF: four pages total including references and draft appendix; all four pages rendered and visually checked. Dataset counts appear correctly. No identity-bearing organization names or dataset/repository URLs appear in the anonymous PDF.
- Empirical results and appendix tables/prompts remain draft TODOs; no detector experiments were run during this update.
