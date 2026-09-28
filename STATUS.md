# STATUS — 2026-09-28

## Current outcome

**Dataset complete and public; detector execution infrastructure prepared; CPU baseline runs complete on all 1,440 documents; eight completed GPU LLM conditions replay-verified (core: Kanana 3B full/local, Qwen 2B full, Qwen 4B local; extension: Qwen 9B full/local on 1,440 docs, Kanana 1.5 8B full/local on 1,438 docs); remaining GPU results and underlying native-count/cohort artifacts pending.** Experiment collaborators should begin with README.md → AGENTS.md → docs/guide/experiment-runbook.md.

| Item | Status |
|---|---|
| Taxonomy | v1.2 accepted, 36 categories, T0–T3 |
| Corpus | 1,440 documents / 218,664 spans; one test split, no benchmark training |
| Public release | nmixx-fin/kiii-kiii, CC BY-NC 4.0 preview, content pin `2df0589d695c18665fd83d4ca5512e03ca0767f6` |
| Practitioner review | Five financial-sector-experienced reviewers, each a different 10% sample, broad appropriateness only; not span validation/IAA |
| Evaluation | Frozen full/local requests, exact/native token counters, common-capacity gate, budget/resume journal, strict metrics, breakdowns, bootstrap, CSV export |
| Model adapters | Claude/Gemini/vLLM implemented and fixture-tested; native paid calls and GPU servers still require operator pilot |
| Baselines | Presidio/ko-pii completed all 1,440 docs on 9/24; raw predictions + results pushed under experiments/results/runs. Common LLM cohort rescore pending. OpenMed GPU untested |
| Operator docs | README, AGENTS, runbook, config templates, label-map limitations prepared |
| Paper/related work | 9/27 result-table scaffold synced from Overleaf (`d876752`): main comparison, taxonomy-group P/R/F1, paired CI and 4-condition provisional response diagnostics. Main text remains 4 pages; total 6 with refs/appendix. [Table handoff](docs/guide/paper-results-handoff.md). Final cohort/comparative findings pending; TWICE/NMIXX retained. |
| Leaderboard | Two full-release baseline results available; consolidated headline table deferred until common cohort is frozen |

Validation: **128 tests passed** (offline provider fixtures, budget/resume/capacity/export guards, generation/release regressions). Verified release → two-document smoke → actual Presidio/ko-pii extraction/scoring completed. Smoke scores are not benchmark findings. Native paid providers and GPU model loading were not exercised locally; archived GPU responses from the operator were replayed offline.

Ownership and delivery: [assignment roster](experiments/ASSIGNMENTS.md) (성현: API deferred; 은빈: Qwen3.5-2B/4B + Kanana-2-3B + OpenMed; 한울: CPU rules; 사라: context-effect research; operational aggregation owner pending). Each operator must push completed results and interruption reports to GitHub under the [result-sharing procedure](experiments/results/README.md); large raw artifacts use repository Release assets. ADR-0030.

Research work can start immediately: 사라 follows [the context-analysis brief](docs/research/sara-context-analysis.md) to freeze a pre-result analysis plan and implement fixture-tested analysis/figures, then interpret existing paired runs and write concise results/discussion. No duplicate inference by the analyst. ADR-0032; the separately authorized medium extension is documented in ADR-0035.

Accepted roster (ADR-0034, 2026-09-24): Qwen3.5-2B, Qwen3.5-4B, Kanana-2-3B-Instruct + Presidio/ko-pii/OpenMed = **6 systems / 9 conditions**. Gemini is optional and deferred; Claude and previous large MoE runs are out of current scope. Config matrix and research handoff updated. GPU capacity and actual token limits remain unverified; no new inference/spending initiated.

## Latest GPU upload review — 24a3595 (2026-09-28)

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
