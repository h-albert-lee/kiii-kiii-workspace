# ADR-0021: GLM concurrency 8

- Date: 2026-09-20
- Status: accepted; user requested eight concurrent GLM requests.

Supersedes the four-lane GLM execution setting only. Existing Astra Batch continues unchanged. GLM's cumulative conservative budget remains $150, including prior runs. The supplied balance screenshot is not treated as a Mango-specific ledger or an increased spending cap.

`scripts/parallel_mango.py` supports 1–8 disjoint lanes. Historical reservations and settled costs are subtracted before distributing remaining budget equally across eight lanes. Existing accepted documents are excluded. New active directory: `data/corpus/main-720-v2/hybrid-0920-03/glm-8`; predecessor: sibling `glm`.

The old GLM runner was stopped before repartitioning. Two in-flight requests (`kiii-main-v2-00291`, `kiii-main-v2-00539`) were marked usage unknown with full reservations retained and deferred retries. They require reconciliation before any later retry. At migration, 32 documents in the 290-document GLM allocation were accepted; 256 pending documents were split into eight lanes. Prior 140 accepted GLM documents and the disjoint 290 Astra allocation remain intact.

Output-limit and provider-error stop rules remain active. Eight is a concurrency ceiling, not a guarantee that all lanes remain live after failures. No recurring LLM monitoring was created.
