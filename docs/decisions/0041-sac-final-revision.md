# ADR-0041 — Final revision of SAC submission #362

Date: 2026-10-02. Status: accepted under the operator's request to strengthen
the submitted manuscript and replace its final file. Update existing AIFT
submission **#362**; do not create another submission. ADR-0038's collection
cutoff and ADR-0039's independent SAC/workshop projects remain unchanged.

## Decision

Revise presentation and factual precision, without changing published scores,
predictions, cohorts, prompts, evaluators or model selection. No new inference.
Retain the primary strict score and label itemwise D-F1 as a post-hoc observable
proxy, not latent detection ability. State the ten completed within-model pairs
separately from the two unpaired LLM conditions and three baseline references.

Clarify that the 24 Tier L labels are operational categories grounded in cited
provisions; masking metadata is benchmark policy rather than a blanket legal
redaction finding. Keep corporate identifiers explicitly within the financial
record scope. Describe baseline configurations and their unequal label coverage.
Correct the Gemma-12B server-version exception and the description of Albanese
et al. as conversational text anonymization.

Add descriptive audits from the already frozen gold: all 218,664 spans fit their
owning target; document lengths are 1,168–43,576 Unicode characters (median
7,449). The baseline maps cover 9/17/13 target categories for Presidio/ko-pii/
OpenMed. These facts do not establish native token capacity, equal label
coverage, semantic annotation validity or performance ceilings. Sources and
verification are recorded in the [review](../reviews/2026-10-02-sac-final-revision.md).

## Disclosure and evidence boundaries

Keep factual AI assistance disclosure: implementation and plotting support in
methods, and manuscript drafting/restructuring/language revision in an
Acknowledgment. Distinguish these uses from dataset composition and from
deterministic scoring of archived predictions. Do not disguise writing support
as spell-checking or remove disclosure to influence reviewers. Authors retain
responsibility for claims, citations and the manuscript.

Preserve the documented limits: no span-label validation or IAA from practitioner
appropriateness review; no verified native capacity gate or representative pilot;
no causal model-size or context mechanism claim; original cohort, decoding and
precision differences; single executions and unexamined semantic near-duplicates.

## Publication workflow

Apply edits natively in the separate SAC Overleaf project, preserving comments.
Export outward, verify anonymous source/PDF and the eight-total-page limit, then
replace the file of #362. Verify the actual uploaded PDF and update the receipt.
At this decision's creation, the reviewed changes exist in a scratch manuscript;
native export and final upload verification are pending. The workshop project
and its comments must remain untouched.
