# ADR-0033 — Smaller local model roster (proposal)

Date: 2026-09-24. Status: **proposed, not an execution change**.

The user requested a refreshed candidate roster grounded in recent papers after discussing API costs and unknown GPU capacity.

Recommend Qwen3.5-2B + Qwen3.5-4B + Kanana-2-3B-Instruct with existing Presidio, ko-pii and OpenMed. This is six systems/nine conditions. Gemini is an optional paid anchor (seven/eleven if included). With adequate measured GPU capacity, consider replacing the Qwen pair with 4B/9B instead of adding another row. EXAONE-4.0-1.2B and Gemma-4-E4B-it are alternatives, not automatic additions.

Rationale and primary sources: docs/research/small-model-roster-2026-09-24.md. Thunder-DeID, CAPID, REDACT and PIIBench inform the comparison design; official model cards establish current deployment candidates. None establishes these models' performance on Kiii².

Adoption requires verified deployment support, independent pilot protocol calibration and actual-token common-cohort coverage, particularly Kanana's 32K limit. No benchmark-driven model selection, hidden truncation, new training or automatic paid allocation. Small weights do not reduce request count.

Existing accepted roster, ownership and manifests remain unchanged pending selection. On acceptance update all shared entrypoints/configs/Sara's model scope together and retain old runs. No inference was launched for this proposal.
