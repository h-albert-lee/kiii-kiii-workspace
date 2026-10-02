# SAC claim / evidence ledger

All analysis inputs are pinned in `analysis-inputs.json`; no inference is run.

| Claim | Evidence | Permitted interpretation |
|---|---|---|
| 1,440 documents / 218,664 spans | Frozen preview revision, ADR-0038 report | Synthetic test collection; not production representativeness |
| 15 systems / 25 completed conditions | `tables/summary.csv` | 12 LLMs / 22 conditions + 3 baselines; two incomplete Qwen pairs omitted |
| Local D-F1 > full in ten complete pairs | `summary.csv`, exact within-model condition matching | Descriptive observed contrasts; no D-F1 confidence interval currently in snapshot |
| Strict local > full in nine pairs | `paired.csv` | Pointwise paired bootstrap, 2,000 draws, seed 0; no multiplicity correction |
| Gemma-31B local D-F1 31.58 | `summary.csv` | FP8 execution; observable proxy retaining invalid-item FP and all gold |
| Qwen3-30B full format 90.42%, empty 53.06% | `summary.csv` | Both use all requests; compliance is not detection recall |
| Legal identifiers outperform attributes under strict scoring | `taxonomy_groups.csv` | Operational taxonomy coverage; not a claim about a model's legal/cultural beliefs |
| All archived strict scores replayed | `INPUTS.json`, replay artifacts, ADR-0038 report | Output/scoring consistency; not server/source equivalence or verified native capacity |
| Five reviewers each inspected a different 10% sample | ADR-0028 and source manuscript | Broad document appropriateness only; overlap/IDs/sampling unknown; no 50% unique coverage or IAA |
| T0–T3 controlled variation | taxonomy and frozen release design | Different documents per stratum; not paired transformations or causal effects |

## Claims explicitly excluded

- D-F1 measures format-independent latent ability or permits ignoring failures.
- Strict-to-D F1 differences causally quantify how much error formatting caused.
- Every model used one verified common capacity gate, identical sampling or dtype.
- Output replay establishes foreign-runner implementation/deployment equivalence.
- Near-duplicate clusters, gold-span correctness, or representative pilot
  calibration have been validated when the current record does not show that.
- Model size causes the observed differences across families/execution blocks.
- More context always hurts, or a detector's PII score certifies legal compliance.
- Additional collection or benchmark-based prompt tuning is needed/authorized.

## Further writing priorities (offline, no new experiment)

1. Tighten duplication between methods and diagnostic-table commentary.
2. Preserve the distinction between structural compliance and strict acceptance.
3. Incorporate Sara's final wording corrections only after inspecting her export.
4. If adding a new analysis from stored outputs, record its post-hoc status,
   original cohort, exact input hashes and verification before citing values.
5. Keep TWICE/NMIXX as third-person prior work; do not cite the pending SAC
   NMIXX submission as an accepted publication.
