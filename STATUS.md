<!-- SAC receipt verified: EasyChair #362, AIFT, 8 pages; docs/submissions/sac2027.json. -->
# STATUS — 2026-10-04

## SAC layout revision — 2026-10-04

**Existing #362 updated and re-downloaded/verified.** Figure 4 moved from page 8 to page 6 alongside Figure 3; Table 2 accompanies detailed error analysis on page 7. Discussion, conclusion and references occupy page 8 with no intervening floats. Eight pages, zero compile errors/overfull boxes; 13 warnings include the intentional figure-only page. Captions, narrative, numbers and figure assets are unchanged; only float declarations/placement and 4 bp of verified blank padding at each vertical edge of Figure 3 changed. Native Overleaf source exported; workshop untouched. [Receipt](docs/submissions/sac2027.json).

## SAC reference revision — 2026-10-04

Existing **SAC AIFT #362** updated after auditing all 18 cited references. Corrected the ICLR 2025 anonymizer title/link and PII-Bench author capitalization; completed KDPII and PrivacyLens publication metadata; pinned NMIXX to its 2025 v2 in the note/URL. Native SAC Overleaf export differs only in `references.bib`; no active or resolved comments were present. Eight pages, zero compile errors, 12 warnings (down from 16). First six pages are unchanged pixel-for-pixel; reference pages visually checked. Re-downloaded submission matches prepared PDF text and all eight page rasters. [Receipt](docs/submissions/sac2027.json). No changes to results, authors, abstract or workshop files.

## ICAIF workshop submission — 2026-10-02

**Submitted: #11**, [OpenReview](https://openreview.net/forum?noteId=klGll15Rn5). Six authors in the operator-approved order; paper CC BY 4.0. English-gloss revision (`2d7f6cf`) submitted and downloaded SHA-256 verified; initial `8d73e63` receipt preserved in history. Four main-text pages, six total; five native Overleaf comments preserved. Full abstract unchanged. [Receipt](docs/submissions/icaif2026.json). This is the workshop submission; SAC is separately submitted as #362.

## SAC 2027 submitted — 2026-10-02

**Final revision uploaded and verified (ADR-0041):** #362 updated PDF and matching abstract; 8 pages, 0 compile errors, 16 documented warnings. All eight downloaded pages and text match the approved native Overleaf export. Added precise legal/policy distinctions, baseline label coverage, boundary/length audit, corrected Gemma-12B server provenance and related-work characterization, and factual AI-use disclosure. Scores, cohorts and inference unchanged. [Final review](docs/reviews/2026-10-02-sac-final-revision.md).

**Submitted: #362, AIFT**, personally completed by the operator and verified in EasyChair. Six authors; Hanwool is corresponding/submitting author using the operator-selected Gmail address. Downloaded PDF: 8 pages, extracted text and all eight 900-pixel rendered pages identical to the prepared draft, despite different file bytes. [Receipt](docs/submissions/sac2027.json). The operator approved all three submission declarations; AI writing-assistance disclosure is now included in Acknowledgment. No fee paid.

### Preparation history

[ADR-0039](docs/decisions/0039-sac2027-submission-preparation.md) authorizes a
separate SAC AIFT manuscript based on the completed ADR-0038 snapshot.
[SAC workspace and checklist](papers/sac2027/README.md). Sara continues workshop
polishing in the existing Overleaf project; `paper/` stays at `8d73e63` for this
snapshot. The operator reports Prof. Yongjae Lee confirmed both submissions
are acceptable. No new inference or EasyChair submission; no live workshop
source/comments changed. Official extended deadline Oct 16 (EST as printed),
internal target Oct 14 KST; anonymous 8-total-page target. Final source/PDF
checks and outstanding submission items are recorded in the SAC folder.

## SAC error analysis — 2026-10-02

[ADR-0040](docs/decisions/0040-sac-error-analysis.md) and the
[offline report](experiments/results/analyses/1002-sac-error-analysis-v1/REPORT.md)
add conserved all-gold partitions for all 22 completed LLM conditions and five
hash-verified, purposively selected response illustrations. Strict/D scores,
cohorts and live evaluator source are unchanged. SAC draft: **8 total pages,
4 main vector figures / 2 tables**, plus a companion taxonomy heatmap. Original
workshop source/comments remain untouched. **142 offline tests pass**; no new
inference or claim of verified native capacity. SAC preparation and English-gloss updates were subsequently exported to GitHub (`72711be`, `1c7b9b5`).

## Current outcome

**Collection closed by operator (ADR-0038): 25 completed conditions from 15 systems, including Sunghyun’s ten Gemma conditions, verified for manuscript use. Unfinished/pilot-only conditions are excluded. No new inference. Native count/source deployment limitations remain explicit.**

[Final tables, paired contrasts, settings and input hashes](experiments/results/analyses/1001-completed-manuscript-v1/REPORT.md). Historical execution plans below are superseded for collection scope.

| Item | Status |
|---|---|
| Taxonomy | v1.2 accepted, 36 categories, T0–T3 |
| Corpus | 1,440 documents / 218,664 spans; one test split, no benchmark training |
| Public release | nmixx-fin/kiii-kiii, CC BY-NC 4.0 preview, content pin `2df0589d695c18665fd83d4ca5512e03ca0767f6` |
| Practitioner review | Five financial-sector-experienced reviewers, each a different 10% sample, broad appropriateness only; not span validation/IAA |
| Evaluation | Frozen full/local requests, exact/native token counters, common-capacity gate, budget/resume journal, strict metrics, breakdowns, bootstrap, CSV export |
| Model adapters | Claude/Gemini/vLLM implemented and fixture-tested; native paid calls and GPU servers still require operator pilot |
| Baselines | Presidio/ko-pii completed all 1,440 docs on 9/24; raw predictions + results pushed under experiments/results/runs. Common LLM cohort rescore pending. OpenMed GPU completed by operator; archived predictions/mapping and all scores replay-verified on 1,440 docs (strict F1 2.0866/100), local GPU loading not exercised |
| Operator docs | README, AGENTS, runbook, config templates, label-map limitations prepared |
| Paper/related work | Completed results/discussion/conclusion synced via Overleaf → GitHub `8d73e63`: 15 systems / 25 conditions, strict vs observable detection proxy, taxonomy groups and paired CIs. Main text 4 pages, total 6 with references/appendix. [Review/QA](docs/reviews/2026-10-01-completed-manuscript.md). TWICE/NMIXX retained; 5 native comments preserved. |
| Leaderboard | Two full-release baseline results available; consolidated headline table deferred until common cohort is frozen |

Validation: **134 tests passed** (offline provider fixtures, budget/resume/capacity/export guards, generation/release regressions). Verified release → two-document smoke → actual Presidio/ko-pii extraction/scoring completed. Smoke scores are not benchmark findings. Native paid providers and GPU model loading were not exercised locally; archived GPU responses from the operator were replayed offline.

Ownership and delivery: [assignment roster](experiments/ASSIGNMENTS.md) (성현: API deferred; 은빈: Qwen3.5-2B/4B + Kanana-2-3B + OpenMed; 한울: CPU rules; 사라: context-effect research; operational aggregation owner pending). Each operator must push completed results and interruption reports to GitHub under the [result-sharing procedure](experiments/results/README.md); large raw artifacts use repository Release assets. ADR-0030.

Research work can start immediately: 사라 follows [the context-analysis brief](docs/research/sara-context-analysis.md) to freeze a pre-result analysis plan and implement fixture-tested analysis/figures, then interpret existing paired runs and write concise results/discussion. No duplicate inference by the analyst. ADR-0032; the separately authorized medium extension is documented in ADR-0035.

Accepted roster (ADR-0034, 2026-09-24): Qwen3.5-2B, Qwen3.5-4B, Kanana-2-3B-Instruct + Presidio/ko-pii/OpenMed = **6 systems / 9 conditions**. Gemini is optional and deferred; Claude and previous large MoE runs are out of current scope. Config matrix and research handoff updated. GPU capacity and actual token limits remain unverified; no new inference/spending initiated.

## Format grounding and detection decomposition — 2026-10-01

[ADR-0037](docs/decisions/0037-format-grounding-detection-decomposition.md) separates all-request structural compliance/empty outputs, parsed-item grounding failures, and all-gold itemwise detection P/R/F1. Twelve completed LLM conditions were replay-checked against unchanged strict and ADR-0036 per-document counts. [Tables](experiments/results/analyses/1001-failure-decomposition-v1/tables/REPORT.md) and [gold-outcome figure](experiments/results/analyses/1001-failure-decomposition-v1/figures/gold-outcomes.png). This is post-hoc and descriptive, not latent ability or causal attribution. All gold and invalid-item FP remain; no inference or live scorer changes. **134 tests pass.**

Latest operator snapshot `9e0570a` adds OpenMed (1,440 docs), EXAONE 4.5 33B full/local and Qwen3-30B-A3B full/local (each 1,440 docs). Raw/prediction hashes, journals and scores agree. EXAONE full's documented U+2028 JSONL-reader workaround was independently reproduced using the existing offline line reader; no frozen evaluator file was changed. Accepted roster completion is **11/13**; Qwen 2B local and Qwen 4B full remain pilot uploads. The additional four large-model conditions do not automatically expand the accepted roster. Native count/gate originals remain pending; do not pool different gates or silently adopt new models.

## Previous GPU upload review — 24a3595 (2026-09-28)

Four medium-extension conditions are complete and all archived strict metrics, failures, request hashes, raw responses and journals replay/agree. [Review, secondary scores and 1,720-row breakdowns](experiments/results/analyses/0928-response-diagnostics-v1-update-24a3595/REPORT.md). Strict F1 / 100: Qwen 9B full/local **3.2686 / 3.6618**; Kanana 1.5 8B full/local **0.3337 / 0.8429**. ADR-0036 fence/itemwise F1: **14.4432 / 18.0520** and **5.5536 / 8.3522**. Secondary diagnostics do not replace official scores.

Kanana excludes two documents for reported native length limits, leaving 1,438 docs / 218,197 spans / 13,653 requests. Shared capacity summary/eligible IDs and reconstructed gold hash agree; native per-request counts and final cohort gate files are still absent. Core/Qwen-9B/Kanana-8B gate hashes differ. New REPORTs document deployment, BF16 and settings; pilot compatibility evidence does not establish representative calibration. Existing parser accepts duplicate JSON keys using the last value, observed in both model families; preserve scores and record this limitation pending a versioned research decision. No runtime/parser changes or new inference.

Completed uploaded/replayed conditions now total **10 of 13** (8 LLM + 2 CPU). Qwen 2B local and Qwen 4B full still have only pilot uploads; OpenMed only a report. Missing uploads do not establish that runs were not performed. Historical reviews below remain unchanged.

## Previous GPU upload review — ac25513

Remote `feat/exp-eb@ac25513` adds completed Qwen3.5-4B local: 1,440 docs / 13,723 requests. All strict scores/breakdowns/failures and request hashes replay correctly; raw responses and reservation/finish journal agree. Strict F1 is 0.9696/100 with 89.9803% request failures; ADR-0036 itemwise F1 is 5.9165 and fence/itemwise F1 is 8.5869, retaining invalid-item FP and all gold. [Review and secondary breakdowns](experiments/results/analyses/0927-response-diagnostics-v1-update-ac25513/REPORT.md).

Qwen 4B full / Qwen 2B local remain pilot uploads. OpenMed and medium-model completed artifacts are absent in this snapshot. Native counts/gate and completed operator reports remain pending; Qwen 4B local's frozen config run_id is `0925-05` despite directory `0925-06`, requiring explanation without hash edits. No inference or live evaluator modification. Previous review snapshots below remain historical.

## Medium extension — 2026-09-26

ADR-0035 assigns Qwen3.5-9B (priority 1) and Kanana-1.5-8B-Instruct-2505 (priority 2), both full/local, to 은빈. Core remains six systems/nine conditions; extension adds four conditions (eight systems/thirteen total). This follows a user report of format errors, so extension analysis is exploratory. [Handoff and raw response requirements](docs/guide/eunbin-medium-extension.md). No new GPU/paid inference initiated here.

Remote `feat/exp-eb` at `b4f76f4` includes three completed benchmark conditions and two 10-document pilot uploads. The three full runs each cover 1,440 documents / 13,723 requests; strict replay and raw hashes are verified. Qwen 2B local and Qwen 4B full uploads are pilot data, not benchmark completion. Qwen 4B local/OpenMed have report templates only. Preserve the collaborator branch and live source/config/gate hashes. Main executor was not changed. The extended capacity matrix is separate; current exporter rejects different cohort-gate hashes, so do not silently combine core and extension runs.

## Response diagnostics — 2026-09-27

ADR-0036 adds separate post-hoc analysis in `src/analysis/`; live evaluator hashes and archived strict results are unchanged. Three completed GPU conditions were replayed, then scored under itemwise validation and whole-response JSON-fence handling. All stages retain 218,664 gold spans and invalid parsed items add exact FP. Category-aware character coverage is supplemental and cannot assign character FP to unanchorable items. Code frozen at `66e4b46` before computing secondary scores. **128 offline tests pass**; no new inference.

[Completed analysis and caveats](experiments/results/analyses/0927-response-diagnostics-v1/REPORT.md) · [1,290-row breakdown CSV](experiments/results/analyses/0927-response-diagnostics-v1/tables/breakdowns.csv) · [Usage](docs/guide/response-diagnostics.md).

Strict → fence/itemwise exact F1 (0–100): Kanana full 1.0230 → 3.1682; Kanana local 1.6156 → 4.0934; Qwen 2B full 0.1169 → 1.6351. These exploratory diagnostics do not replace headline results. Qwen local/4B uploaded pilot scores are excluded. All-model native capacity and complete operator records still need verification.

## CPU baseline execution — 2026-09-24

한울 담당 Presidio/ko-pii 모두 1,440/1,440문서 완료, 유료 API 호출 0. 고정된 규칙과 라벨 매핑을 사용했으며 결과를 보고 수정하지 않았습니다. 전체 36-category strict micro F1: Presidio 0.10149098, ko-pii 0.09426134. 정답 218,664스팬을 모두 분모에 포함합니다. 이는 전체 릴리스 결과이며 LLM 공통 cohort가 확정되면 저장 예측을 동일 문서 집합으로 재집계합니다.

- [Presidio report](experiments/results/runs/0924-01-presidio-full1440/REPORT.md)
- [ko-pii report](experiments/results/runs/0924-01-ko-pii-full1440/REPORT.md)

## Next actions

1. Verify operator deployment records for the three core and two extension LLMs: IDs/revisions, tokenizer/templates, limits, GPU availability and compute allocation. Preserve live runs.
2. Separate pilot for live adapter compatibility and shared core/halo/output calibration; freeze settings. Do not tune on test results.
3. Count all requests for all models and both conditions; fix common eligible documents; preserve exclusion reasons.
4. Obtain the remaining Qwen 2B local, Qwen 4B full and OpenMed completed artifacts or operator progress reports. Preserve the eight completed LLM conditions and both CPU baselines; analyze the medium extension separately with explicit cohort provenance.
5. Populate figures and paper results only from finalized artifacts; preserve Overleaf comments during edits.

Default core/halo 1,200 chars and output cap 4,096 tokens yield 13,723 requests per model per condition on all 1,440 docs. This is a provisional inventory, **not a token/cost estimate**. Exact live counts and detector costs are not available yet.

## Boundaries

Generation is finished: GLM 820 / Astra 620; generators are excluded from headline detector ranking. Old generation budgets and historical pending-generation notes do not apply to detector inference. No training or validation split; no fine-tuned KLUE baseline. TAB risk-weighted recall and semantic de-identification utility are not implemented.

Research aim remains the ICAIF'26 financial AI security/privacy/safety workshop short paper. Venue/deadline details are recorded in ADR-0003 and should be reconfirmed before submission. Detailed history is preserved in docs/decisions/, generation notes and git history.
