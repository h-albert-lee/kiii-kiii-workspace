# SAC #362 — final revision review, 2026-10-02

Scope: acceptance-oriented factual and methodological review of the independent
SAC manuscript, authorized by the operator after submission #362. Implements
[ADR-0041](../decisions/0041-sac-final-revision.md). All published strict and D
scores remain unchanged; no new inference, benchmark tuning or cohort changes.

## Changes reviewed

- Taxonomy: replace literal-enumeration claims with operational categories
  grounded in statutes; narrow the customer-identifier description to the
  Decree's specified scope. Distinguish masking policy from legal obligations,
  preserve the sensitive-information exception, and explain corporate targets.
- Protocol: distinguish ten complete context pairs, two unpaired conditions and
  three document-level baselines. Restrict core/halo/output-cap and atomic
  response-rejection claims to LLMs. Replace causal context-improvement wording
  with the observed within-model contrasts.
- Baselines: disclose direct Presidio rule recognizers/custom patterns, ko-pii
  rules and OpenMed argmax BIOES/fragment mappings. All 36 gold categories remain
  in every denominator despite unequal emit-able label sets.
- Evidence: add actual Unicode document lengths and the zero-unrepresentable-span
  audit, rather than relying on generation token estimates. Preserve the gap
  between mechanically valid spans and semantically validated gold.
- Literature/provenance review: describe Albanese et al. as conversational text
  anonymization, not specifically English financial de-identification. Record
  the reported Gemma-12B vLLM 0.30.0 exception to the other Gemma runs' 0.19.0.
  The source/serving distinctions remain; replay does not certify deployment.
- AI assistance: methods state Claude/Codex support for implementation and
  plotting; Acknowledgment states drafting, restructuring and language revision.
  Dataset generators remain separately identified. Scores are deterministic
  computations from archived predictions, not model-assigned judgments.

The scratch-source second pass caught and corrected two scope regressions:
"all completed conditions" must read "all completed LLM conditions", and a
sentence following Presidio's score must not attribute LLM atomic rejection to
the baseline. The final customer-identifier wording no longer says "any"
identifier assigned to a customer.

## Audit evidence

Frozen gold: `experiments/prepared/0924-cpu-full1440/gold.jsonl`, SHA-256
`d57b1cb0b8b67fe48a9b45ee985fb01e63b919147a8527f8231459a68b57456d`.
This matches `manifest.json`'s `data_sha256` in the same directory.

- `boundary-audit.json`: 1,440 records, 218,664 gold spans, sum of
  `unrepresentable_spans` = **0**. Independently reconstructed each document's
  windows using `src.eval.protocol.windows(text, Protocol())` and checked
  `core_start <= span.start < core_end` and `span.end <= target_end` for every
  gold span; the result is also zero. The maximum gold span length is 1,184
  Unicode code points. No gold boundary or ownership rule was changed.
- `len(document['text'])` over the same frozen gold gives minimum **1,168**,
  median **7,449**, maximum **43,576** Unicode characters. These are not token
  measurements or evidence of a native capacity gate.
- Distinct non-null values in `experiments/label_maps/presidio.json`,
  `ko-pii.json` and `openmed.json` give **9**, **17** and **13** target labels.
  See `experiments/label_maps/README.md` for implementation and mapping limits.
  These counts alone are not attainable recall ceilings.

Unchanged numerical result sources are pinned in
`experiments/results/analyses/1001-completed-manuscript-v1/INPUTS.json`;
ADR-0040's illustrative and all-gold error evidence remains in
`experiments/results/analyses/1002-sac-error-analysis-v1/`.

## Limits retained and final verification

Practitioner review concerns broad appropriateness, not span correctness or IAA;
sample overlap/selection records are not established. Native count files,
representative pilot calibration and foreign deployment equivalence remain
unverified. Different cohorts, decoding and precision limit cross-family claims.
Post-hoc document bootstrap intervals are not rerun/production uncertainty, and
semantic near-duplicate dependence is unaudited. D-F1 does not remove all format
effects, certify privacy or identify latent ability.

At record creation, scratch manuscript review is complete. Native Overleaf
editing/export, final PDF compilation/render/anonymity checks, eight-page
verification and replacement/upload verification for **existing #362** are
pending the parent task. This record does not claim the final file is uploaded.
Update the submission receipt after that verification; preserve the initial
receipt and the independent workshop manuscript.

## Final completion verification

Native SAC Overleaf edits exported as 21 source files and matched byte-for-byte to the repository snapshot. Final XeLaTeX build: 8 pages, 0 errors, 16 warnings (14 bibliography metadata, suppressed anonymous ACM reference strip, balance warning); no undefined citations, missing glyphs or overfull boxes. All eight pages visually inspected. The abstract and PDF were updated in existing EasyChair #362; receipt shows Oct 02, 06:12. Downloaded text and all eight page rasters at 1250-pixel maximum dimension exactly match the approved PDF. Hashes and initial receipt history are in `docs/submissions/sac2027.json`. No code/scorer change or new inference; prior unit tests were not rerun for prose-only edits. Native trailing blank lines are retained to match export.
