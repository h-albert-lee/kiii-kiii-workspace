# Source layout

- `generate/`: completed slot-based synthetic generation, validation, budget campaigns and Batch integration.
- `eval/`: dataset loader, fixed extraction protocol, native provider/token counters, capacity gate, resumable budget runner, frozen baselines, metrics/bootstrap/export.
- `prompts/`: versioned generation prompts. Extraction messages are constructed from the taxonomy in `eval/protocol.py`.

For runnable commands and remaining deployment checks, see [the experiment runbook](../docs/guide/experiment-runbook.md). Read [AGENTS.md](../AGENTS.md) before changes.
