"""Wait for an existing runner to release its lock, then continue within a total cap."""
import argparse
import fcntl
import json
import math
from pathlib import Path
import parallel_mango as parallel
import resume_mango as sequential
from src.generate.batch import _atomic, _json


def run(previous, directory, ceiling):
    if not math.isfinite(ceiling) or ceiling <= 0:
        raise ValueError('positive finite cumulative ceiling required')
    status = directory.parent / (directory.name + '.continuation.json')
    _atomic(status, _json({'status': 'waiting_for_predecessor', 'previous': str(previous), 'directory': str(directory), 'total_budget_usd': ceiling}))
    # Kernel wait, no API calls and no LLM monitoring. Keep the predecessor lock
    # through preparation so another process cannot resume it during ledger reads.
    with (previous / '.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        manifest = json.loads((previous / 'manifest.json').read_text())
        roots = manifest['prior_roots'] + [str(p / 'attempts') for p in sorted(previous.glob('lane-*'))]
        spent = sequential.cost(roots)
        if spent >= ceiling:
            _atomic(status, _json({'status': 'budget', 'total_budget_usd': ceiling, 'committed_usd': spent}))
            return
        result = parallel.prepare(directory, previous, concurrency=8,
                                  additional_budget=ceiling-spent,
                                  data_version=manifest.get('data_version', 'main-1440-v1'))
        if abs(result['budget_usd']-ceiling) > 1e-8:
            raise ValueError('cumulative budget mismatch')
        _atomic(status, _json({'status': 'running', 'directory': str(directory), 'total_budget_usd': ceiling}))
    parallel.run(directory)
    _atomic(status, _json({'status': 'pass_finished', 'directory': str(directory), 'total_budget_usd': ceiling}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--previous', required=True, type=Path)
    p.add_argument('--directory', required=True, type=Path)
    p.add_argument('--total-budget', required=True, type=float)
    a = p.parse_args()
    run(a.previous, a.directory, a.total_budget)
