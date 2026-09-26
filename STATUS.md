# STATUS — 2026-09-26

## Current outcome

**Dataset complete and public; detector execution infrastructure prepared; CPU baseline runs complete on all 1,440 documents; GPU experiments reported in progress by the operator; finalized GPU results not yet verified here.** Experiment collaborators should begin with README.md → AGENTS.md → docs/guide/experiment-runbook.md.

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
| Paper/related work | Dataset/protocol/review scope updated; TWICE/NMIXX included; actual results remain placeholders |
| Leaderboard | Two full-release baseline results available; consolidated headline table deferred until common cohort is frozen |

Validation: **106 tests passed** (offline provider fixtures, budget/resume/capacity/export guards, generation/release regressions). Verified release → two-document smoke → actual Presidio/ko-pii extraction/scoring completed. Smoke scores are not benchmark findings. Native paid providers and GPU model loading were not exercised.

Ownership and delivery: [assignment roster](experiments/ASSIGNMENTS.md) (성현: API deferred; 은빈: Qwen3.5-2B/4B + Kanana-2-3B + OpenMed; 한울: CPU rules; 사라: context-effect research; operational aggregation owner pending). Each operator must push completed results and interruption reports to GitHub under the [result-sharing procedure](experiments/results/README.md); large raw artifacts use repository Release assets. ADR-0030.

Research work can start immediately: 사라 follows [the context-analysis brief](docs/research/sara-context-analysis.md) to freeze a pre-result analysis plan and implement fixture-tested analysis/figures, then interpret existing paired runs and write concise results/discussion. No duplicate inference by the analyst. ADR-0032; the separately authorized medium extension is documented in ADR-0035.

Accepted roster (ADR-0034, 2026-09-24): Qwen3.5-2B, Qwen3.5-4B, Kanana-2-3B-Instruct + Presidio/ko-pii/OpenMed = **6 systems / 9 conditions**. Gemini is optional and deferred; Claude and previous large MoE runs are out of current scope. Config matrix and research handoff updated. GPU capacity and actual token limits remain unverified; no new inference/spending initiated.

## Medium extension — 2026-09-26

ADR-0035 assigns Qwen3.5-9B (priority 1) and Kanana-1.5-8B-Instruct-2505 (priority 2), both full/local, to 은빈. Core remains six systems/nine conditions; extension adds four conditions (eight systems/thirteen total). This follows a user report of format errors, so extension analysis is exploratory. [Handoff and raw response requirements](docs/guide/eunbin-medium-extension.md). No new GPU/paid inference initiated here.

Remote `feat/exp-eb` at `757d707` contains run folders/checkpoint notes and a nullable usage adapter fix. Exact run completion/error rates are unverified; preserve that branch and all live source/config/gate hashes. Main executor was not changed. The extended capacity matrix is separate; current exporter rejects different cohort-gate hashes, so do not silently combine core and extension runs.

## CPU baseline execution — 2026-09-24

한울 담당 Presidio/ko-pii 모두 1,440/1,440문서 완료, 유료 API 호출 0. 고정된 규칙과 라벨 매핑을 사용했으며 결과를 보고 수정하지 않았습니다. 전체 36-category strict micro F1: Presidio 0.10149098, ko-pii 0.09426134. 정답 218,664스팬을 모두 분모에 포함합니다. 이는 전체 릴리스 결과이며 LLM 공통 cohort가 확정되면 저장 예측을 동일 문서 집합으로 재집계합니다.

- [Presidio report](experiments/results/runs/0924-01-presidio-full1440/REPORT.md)
- [ko-pii report](experiments/results/runs/0924-01-ko-pii-full1440/REPORT.md)

## Next actions

1. Verify operator deployment records for the three core and two extension LLMs: IDs/revisions, tokenizer/templates, limits, GPU availability and compute allocation. Preserve live runs.
2. Separate pilot for live adapter compatibility and shared core/halo/output calibration; freeze settings. Do not tune on test results.
3. Count all requests for all models and both conditions; fix common eligible documents; preserve exclusion reasons.
4. Preserve/resume the three core LLMs × two conditions and three baselines; prepare the two medium LLMs separately under ADR-0035, then finalize and analyze with explicit cohort provenance.
5. Populate figures and paper results only from finalized artifacts; preserve Overleaf comments during edits.

Default core/halo 1,200 chars and output cap 4,096 tokens yield 13,723 requests per model per condition on all 1,440 docs. This is a provisional inventory, **not a token/cost estimate**. Exact live counts and detector costs are not available yet.

## Boundaries

Generation is finished: GLM 820 / Astra 620; generators are excluded from headline detector ranking. Old generation budgets and historical pending-generation notes do not apply to detector inference. No training or validation split; no fine-tuned KLUE baseline. TAB risk-weighted recall and semantic de-identification utility are not implemented.

Research aim remains the ICAIF'26 financial AI security/privacy/safety workshop short paper. Venue/deadline details are recorded in ADR-0003 and should be reconfirmed before submission. Detailed history is preserved in docs/decisions/, generation notes and git history.
