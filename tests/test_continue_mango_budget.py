import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import continue_mango_budget as continuation


def test_total_ceiling_uses_actual_predecessor_cost(tmp_path, monkeypatch):
    old = tmp_path / 'old'; old.mkdir()
    (old/'manifest.json').write_text(json.dumps({'prior_roots': [], 'data_version': 'v2'}))
    monkeypatch.setattr(continuation.sequential, 'cost', lambda roots: 97.25)
    calls = []
    def prepare(directory, previous, **kwargs):
        calls.append(kwargs)
        return {'budget_usd':97.25+kwargs['additional_budget']}
    monkeypatch.setattr(continuation.parallel, 'prepare', prepare)
    monkeypatch.setattr(continuation.parallel, 'run', lambda root: None)
    continuation.run(old, tmp_path/'next', 200)
    assert calls[0]['additional_budget'] == 102.75
    assert calls[0]['concurrency'] == 8


def test_no_more_spending_if_already_at_ceiling(tmp_path, monkeypatch):
    old = tmp_path/'old';old.mkdir()
    (old/'manifest.json').write_text(json.dumps({'prior_roots': []}))
    monkeypatch.setattr(continuation.sequential, 'cost', lambda roots: 200)
    monkeypatch.setattr(continuation.parallel, 'prepare', lambda *a, **k: (_ for _ in ()).throw(AssertionError('must not prepare')))
    continuation.run(old,tmp_path/'next',200)
    assert json.loads((tmp_path/'next.continuation.json').read_text())['status'] == 'budget'
