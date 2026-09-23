# ADR-0024: Correct GLM cumulative budget to $200

- Date: 2026-09-21
- Status: accepted, explicit user clarification

User clarified that the additional $50 increases the original $150 GLM cumulative ceiling to **$200**, not a new-stage-only $50 allowance. This supersedes ADR-0023's budget interpretation. OpenAI stage-two ceiling stays $47. Historical Mango usage and unknown reservations count toward the $200.

The active runner holds budget settings in memory. To preserve ongoing requests and avoid uncertain interrupted charges, keep that pass running under its already-lower cap. `scripts/continue_mango_budget.py` waits on its process-held file lock without polling a model or making API calls. When released, it reads final ledger costs, prepares disjoint remaining GLM plans at concurrency eight with allowance `200 - cumulative_cost`, and runs one bounded completion pass in `stage2-0921/glm-200`. It skips accepted documents and retains the existing failure/quality gates. Unknown in-flight states block preparation; no automatic uncertain retries are introduced.

The waiting supervisor is recorded in `glm-200.process.json`; its status is `glm-200.continuation.json`. A user pause must stop this supervisor as well as the active generator, otherwise the supervisor would interpret an exited predecessor as ready to continue. No generator source files or active frozen manifests were edited. The first-stage remaining annotation failure is still separately tracked.
