# Accepted matrix — ADR-0034

Default: `qwen-2b.example.json`, `qwen-4b.example.json`, `kanana.example.json` → three local models × two conditions in `matrix.example.json`.

Model IDs and GPU operator are populated. Actual weight/tokenizer revisions, deployment token limits, rates and frozen settings remain deliberately unset. If a local server has no token charge, explicitly set both per-million rates to 0 after verification; GPU rental/compute cost is accounted separately. A zero token rate does not authorize a GPU rental. Set the price-date field to the accounting verification date. Keep credentials in environment variables.

Each model may run sequentially on one server: the example ports are suggestions, not requirements for three simultaneous GPUs. Use distinct model config/count/run paths. Both Qwen models can use QWEN_API_KEY; configure separate environment variable names if needed. Ensure the actual served model ID matches the selected checkpoint and pin its revision. No automatic revision, precision or context-limit claims are made.

`claude.example.json` and `gemini.example.json` are retained adapter examples, **not current execution assignments**. Gemini remains optional/deferred and Claude is out of current scope. Do not reuse the removed generic `qwen.local.json` or an old four-model matrix without checking scope. Existing local configs are never overwritten by template updates.

Read ../../../docs/guide/experiment-runbook.md before counting or executing. Tests do not prove deployed FP16/native-tokenizer compatibility.
