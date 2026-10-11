# EXAONE-4.5-33B full finalize workaround (2026-09-30).
# src/eval/run.py read_jsonl uses str.splitlines(), which also splits on U+2028 that the model emitted
# inside 14 response strings (valid JSONL). Patch only the line splitting at runtime ('\n' only, per JSONL);
# source files (and source_sha256) unchanged; scoring logic unchanged; no model calls.
import json, sys
from pathlib import Path
import src.eval.run as run, src.eval.execute as ex
def read_jsonl_nl(path):
    return [json.loads(l) for l in Path(path).read_text().split('\n') if l.strip()]
run.read_jsonl = read_jsonl_nl; ex.read_jsonl = read_jsonl_nl
c = ex.load_config('experiments/configs/evaluation/exaone-33b.local.json')
res = ex.finalize('experiments/prepared/full_context_targeted', c, 'experiments/runs/exaone-33b-full')
print(json.dumps(res, ensure_ascii=False)[:400])
