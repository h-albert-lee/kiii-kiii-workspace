# SAC error analysis — ADR-0040, 2026-10-02

Post-hoc offline description of **all 22 completed LLM conditions**. No new
inference, model selection, gold-conditioned repair, parser change or score
replacement. The three baselines do not have comparable request-format or
item diagnostics. Original cohorts remain: Kanana-1.5-8B 1,438 documents /
218,197 gold; others 1,440 / 218,664. Native capacity and foreign deployment
equivalence remain unverified. All strict and D scores are unchanged.

## Reproduction

```sh
python -m src.analysis.sac_error_atlas \
  --inputs experiments/results/analyses/1001-completed-manuscript-v1/INPUTS.json \
  --output /tmp/kiii-sac-error-atlas-new
python -m src.analysis.sac_case_audit \
  --inputs experiments/results/analyses/1001-completed-manuscript-v1/INPUTS.json \
  --gold experiments/prepared/0924-cpu-full1440/gold.jsonl \
  --output /tmp/kiii-sac-cases-new.json
```

Use fresh output paths. The first command checks pinned source/result hashes,
completed benchmark status, strict count identity, all-gold conservation and
invalid-item FP conservation. The second also checks ledger/raw/gold/taxonomy
hashes, reconstructs the selected document's requests, and reproduces selected
request and gold outcomes. Raw bundles must be restored to the recorded input
paths; they are not copied into this report. `INPUTS.json` and `cases.json`
record sources and code hashes. `fine_outcomes.csv` preserves unmerged counts.

## Read the denominators correctly

- Request rates use every request, including failures. Fence, compliance and
  empty-list indicators can overlap and are not an additive partition.
- Invalid-item shares use **invalid parsed items**, not requests or gold. The
  fine table's item rates instead use **all usable parsed items**, explicitly
  recorded in its denominator column. Unparseable outputs have no item count.
- Gold shares account for **all gold** under the frozen priority partition.
  Exact hit takes precedence; unusable/empty owner responses follow, then
  anchored category/boundary mismatch, unresolved with rejected items, and
  remaining no-overlap. Shared output issues are not causally disentangled.
- Unresolved misses are not recovered PII. A literal quotation outside its
  assigned core is a protocol ownership failure, not an absent quotation.
  Quote absence from TARGET alone does not establish hallucination.

## Measured profiles

| Condition | Observation | Denominator and interpretation |
|---|---|---|
| Qwen3-30B full | 100,873 mentions, 46.13%, belong to empty-output requests | All 218,664 gold; not the 53.06% all-request empty rate |
| Qwen3-30B local | 23,673 mentions, 10.83%, belong to empty-output requests | All 218,664 gold; paired observed contrast, not a causal mechanism |
| Kanana-1.5-8B local | 119,200 mentions, 54.63%, belong to invalid-JSON requests | Its original 218,197 gold; no imputation of excluded documents |
| Gemma-31B local | 98,200 / 104,568 invalid items, 93.91%, start outside their core | Invalid parsed items; quotations exist in TARGET |
| Gemma-26B-A4B local | 76,806 / 84,943 invalid items, 90.42%, start outside their core | Same denominator definition; distinct original run |
| Gemma-31B local | Exact hit 34.86%; same-category partial boundary 23.33%; exact wrong label 0.65%; other wrong-label overlap 5.63% | All gold, disjoint priority buckets; overlap is not semantic validation |
| Gemma-31B local | 89.66% whole-fence parseable requests | All requests; strict–D F1 gap cannot be attributed solely to fences |

## Illustrations and selection

Five run/error strata were chosen purposively after inspecting aggregate
profiles. Within each stratum we selected the smallest SHA256(request_id),
then the lexicographically first eligible item or (start, end, category).
This deterministic selection makes the illustrations reproducible; it does
**not** make the strata random, representative or preregistered. Gold describes
already-scored matches only. It never reinterprets or repairs a prediction.
Full machine-readable excerpts, offsets, request/input hashes and eligibility
counts are in `cases.json`. All excerpts are synthetic benchmark text.

### fence_only — 0929-05-gemma4-31b-fp8-local

Request `kiii-main-v2-00245:0010`; 1,821 eligible requests.

Gold (bank_account_no): 110-148-124444

Prediction (bank_account_no): 110-148-124444

The whole-response fence triggers strict rejection; the selected response has zero invalid items and the quoted account is an exact typed match.

### outside_owned_core — 0928-04-gemma4-26b-a4b-local

Request `kiii-main-v2-00930:0005`; 9,823 eligible requests.

Prediction (address): 대구 수성구 송도과학로 325, 205호

Starts 236 characters after core end, inside the following halo.

### exact_boundary_wrong_category — 0926-02-qwen-9b-local

Request `kiii-main-v2-00663:0001`; 1,615 eligible requests.

Gold (contract_no): 2026-277485

Prediction (customer_id): 2026-277485


### overlapping_boundary_same_category — 0929-05-gemma4-31b-fp8-local

Request `kiii-main-v2-00355:0008`; 9,046 eligible requests.

Gold (consultation_content): 앱의 월간 승인 합계에 포함된 추가 주문이 명세서에는 왜 빠져 있는지 문의하였다

Prediction (consultation_content): 앱의 월간 승인 합계에 포함된 추가 주문이 명세서에는 왜 빠져 있는지 문의하였다.


### empty_list — 0928-03-qwen3-30b-full

Request `kiii-main-v2-00355:0008`; 6,819 eligible requests.

Gold (consultation_content): 앱의 월간 승인 합계에 포함된 추가 주문이 명세서에는 왜 빠져 있는지 문의하였다

The received response has an empty spans list; no quotation is reconstructed.

## Manuscript use and limits

Figure 4 (`papers/sac2027/figures/error-atlas.pdf`) shows per-condition all-gold
partitions, never pooling across cohorts. The prior taxonomy heatmap remains a
companion asset. The Error Analysis section reports the measured profiles and illustrative
boundary/label/ownership cases. Existing frozen strict/D-F1 and paired CIs
remain unchanged. No success-only denominator, latent-ability claim, risk
certification, new human annotation or prospective validation is implied.
