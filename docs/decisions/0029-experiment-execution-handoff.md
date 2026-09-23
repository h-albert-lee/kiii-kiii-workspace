# ADR-0029 — Runnable detector experiments and agent handoff

Date: 2026-09-23. Status: accepted implementation; live deployments/pilot calibration pending.

## Context

The user requested that collaborators can hand this repository to an agent and prepare the main experiments. The release is complete and the offline evaluation protocol exists, but dispatch, baseline integration, budget handling and up-to-date entrypoint documentation were missing.

## Decision

- Add native Claude/Gemini calls and counters, vLLM-compatible chat plus native tokenize. No approximate character token counts or hidden truncation.
- Configs require operator/run/model/tokenizer revision, endpoint caps, verified rates/date, allocated budget and a declaration that pilot settings are frozen. Secrets are environment-only. Actual model availability is operator-verified, not inferred from historical names.
- Use an all-model, both-condition capacity gate bound to input/request/config/count hashes. Any capacity exclusion is decided before inference, applied to both conditions, and counted/reported. Pilot/smoke artifacts cannot enter the exported leaderboard.
- No implicit retries or response repair. Request maximum costs are journaled before dispatch. Resume does not resend finalized calls; interrupted calls become uncertain failures and retain maximum reservations. Budget is per run; total allocation across runs remains the operator's responsibility.
- Add frozen direct Presidio Korean pattern recognizers (five Korean types plus email/KR phone, score threshold .3, account/card rules), ko-pii raw-text mode, and native OpenMed token classification. Explicit source-label maps include null/out-of-scope labels. All 36 gold categories remain in the denominator.
- OpenMed implementation uses argmax BIOES grouping and explicit overlapping token windows, not the wrapper's Viterbi decoder. This variant must be named/disclosed; GPU compatibility remains a live pilot requirement. No benchmark-driven boundary repair or map tuning.
- Store dependencies, source/config hashes, raw responses, accounting and all metric breakdowns. CSV export uses one row per model/condition; the old multi-seed placeholder header is superseded when actual completed results exist.
- README + AGENTS + runbook are the current execution entrypoint; older generation-era task lists are superseded. No new paid detector inference is launched by this preparation work.

## Validation and limitations

Offline fixtures cover native request/counter shapes, response normalization, resumability, budget denial, uncertain requests, config mismatches, cohort gates, Unicode baseline offsets and export guards. Presidio/ko-pii run locally. This does not establish native paid API access or GPU model compatibility. Representative independent pilot calibration and actual deployed model/cost verification are required before headline execution.
