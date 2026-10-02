# SAC figure design — 2026-10-02

The four figures form a research argument: what the benchmark measures, what
the systems recover, how context changes that recovery, and how unrecovered gold is distributed across observable output failures.
Taxonomy coverage remains a fifth companion asset. They reuse the frozen ADR-0038 tables; no
inference, rescoring, new bootstrap intervals or roster changes are involved.

| Figure | Question | Visual encoding | Source |
|---|---|---|---|
| 1: benchmark overview | What is controlled and measured? | Policy/forms, shared target ownership, strict versus itemwise scoring | Existing taxonomy/protocol; explicitly illustrative synthetic examples |
| 2: score portrait | Does strict extraction reflect recoverable evidence? | Shared-scale full/local strict and D-F1 dots, all-request structural compliance cells | 25 rows in `summary.csv` |
| 3: context contrasts | Does more context improve this fixed output task? | Strict forest plot with archived CIs; separate D-F1 point contrasts | 10 rows in `paired.csv` and matched summary rows |
| Companion: taxonomy coverage | Which policy groups are recovered? | Annotated full/local heatmaps with a shared linear 0–25 scale | 75 group rows in `taxonomy_groups.csv` |

| 4: error atlas | Where does unrecovered gold appear? | Full/local stacked bars; conserved all-gold priority partitions | 22 rows in ADR-0040 `summary.csv` |

## Consistent visual language

- Navy filled circles: strict F1; rust open diamonds: D-F1. Shape reinforces
  color. Squares identify document-level baseline strict scores.
- Model order is fixed across figures, independent of performance. The context
  plot selects only the ten complete pairs from that order.
- Kanana-1.5-8B's asterisk marks its 1,438-document cohort; other conditions use
  1,440. Gemma-31B carries an FP8 label. The figures do not imply shared gates,
  uniform decoding/precision or causal model-size effects.
- Missing Qwen conditions are visibly missing, never plotted as zero.
  Baseline D/format/local-pair values are N/A. Tiny positive values are shown
  as `<.01` (F1) or `<0.1` (format percentage) instead of rounded zero where
  that distinction affects interpretation.
- Heatmap normalization is shared across columns and conditions; attribute
  columns are not independently stretched to make low scores look high.
- No 3D, dual-axis overlay, hidden nonzero origin, size-encoded model ranking,
  success-only denominator, or inferred decomposition of latent ability.

## Reading caveats carried into captions

Figure 2's gray segment connects two scoring views of the **same received
responses**. It is not a confidence interval or causal gain from a format
intervention. D retains all gold and invalid-item exact-FP penalties; terminal
or unparseable responses remain empty. Format compliance is structural and
is distinct from strict acceptance and PII recall. Empty-list rates and
invalid-item counts remain in the full diagnostic table.

Figure 3 retains the original strict pointwise 95% document-paired bootstrap
intervals (2,000 draws, seed 0). D-F1 contrasts are points only; there are no
new or borrowed D intervals. Tiny strict contrasts/intervals legitimately
cluster around zero on a common axis; exact values remain in the archived
paired CSV. No multiplicity-adjusted or stochastic-rerun inference is claimed.

The companion taxonomy figure shows strict group micro-F1 from aggregated TP/FP/FN, not an average
of category F1. Group precision/recall remain in the frozen CSV. Color measures
observed extraction, not legal importance or sensitivity.

## Reproduction and layout

Run `scripts/build_publication_figures.py` from the workspace root as described
in the parent README. The builder verifies all pinned source hashes, 25 unique
conditions, 75 group scores against archived counts, and ten strict paired
contrasts against summary values. Output: `figures/{benchmark-overview,
score-portrait,context-contrasts,taxonomy-coverage,error-atlas}.{pdf,svg,png}`.

The manuscript replaces the compact score table with Figure 2, retains exact
strict values in the complete diagnostic table, and uses Figure 4 for errors; the redundant strict-CI table is removed in favor
of Figure 3 and the archived exact values. Two tables remain: taxonomy
definitions and complete response diagnostics. Main text plus references
remain eight pages. Existing workshop/Overleaf source is unchanged.

Figure 4 uses six disjoint gold groups from the existing ordered partition.
Unresolved rejected items never become evidence of gold detection. The archived
analysis retains unmerged counts. Missing conditions are blank, not zero; no
cohorts are pooled and no gold is dropped. The five illustrative cases are
purposively stratified and hash-selected, not a representative manual audit.

GitHub publication remains subject to the unresolved approval request from
the previous turn; figure preparation does not authorize a retry of the
rejected manuscript push.
