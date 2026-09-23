# ADR-0031 — Confirmed assignees and GPU serving preference

Date: 2026-09-23. Status: accepted.

The user assigned API experiments to 성현, GPU experiments to 은빈, and GPU-free baselines to 한울, explicitly including any GPU-requiring baseline under 은빈. The user requested a recommendation to serve models in FP16 with vLLM or a similar server and connect evaluation through an API.

- 성현: Claude Sonnet 5 and Gemini 3.8 Flash, both full/local conditions.
- 은빈: Qwen3.6-35B-A3B and Kanana2-30B-A3B-Instruct2601, both conditions; GPU OpenMed baseline.
- 한울: CPU Presidio and ko-pii baselines.
- Aggregation owner is still unspecified; do not infer an assignment.
- Recommend FP16 vLLM-compatible deployment for the GPU LLMs, with OpenAI-compatible inference and actual served-template token counting. Verify architecture/hardware/runtime support and memory on independent pilot inputs. Freeze and record actual dtype, quantization status, server version/command and tensor parallel settings. A necessary fallback must be explicit and justified, not silently substituted.
- OpenMed is a token-classification model using the current Transformers adapter; the LLM chat-serving recommendation does not establish vLLM compatibility or mandate untested FP16 for this model.

This updates ownership and deployment guidance, not the evaluation cohort, metrics, model roster or existing GitHub result-sharing requirement. No new live model execution or FP16 compatibility claim is made.
