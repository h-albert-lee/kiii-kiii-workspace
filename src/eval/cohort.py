"""Freeze the all-model, both-condition capacity gate before paid evaluation."""
import argparse
import json
from pathlib import Path
from .execute import checked_counts, config_hash, load_config
from .run import load_plan, write_json
from .protocol import sha


def freeze(matrix_path, output):
    matrix = json.loads(Path(matrix_path).read_text())
    entries = []; data = None; protocols = {}; roster = {}
    for item in matrix['entries']:
        c = load_config(item['config'])
        manifest, docs, requests, _ = load_plan(item['directory'])
        checked_counts(requests, c, item['measurements'])
        if manifest.get('purpose') != 'benchmark':
            raise ValueError('headline cohort requires benchmark plans')
        if data is not None and data != manifest['data_sha256']:
            raise ValueError('all models and conditions must share identical documents')
        data = manifest['data_sha256']; mode = manifest['protocol']['mode']
        definition = {k:v for k,v in manifest['protocol'].items() if k != 'mode'}
        if protocols and any(v != definition for v in protocols.values()):
            raise ValueError('all models/conditions must share output partition and limits')
        protocols[mode] = definition
        roster.setdefault(mode, []).append(c['model'])
        entries.append({'model': c['model'], 'mode': mode, 'config_sha256': config_hash(c),
                        'requests_sha256': manifest['requests_sha256'],
                        'measurements_sha256': sha(Path(item['measurements']).read_text())})
    if set(roster) != {'full_context_targeted', 'local_window'}:
        raise ValueError('both conditions required')
    a,b = roster.values()
    if len(set(a)) != len(a) or len(set(b)) != len(b) or set(a) != set(b) or not a:
        raise ValueError('each model required exactly once per condition')
    if len(set(json.dumps(v, sort_keys=True) for v in protocols.values())) != 1:
        raise ValueError('conditions must share output partition and limits')
    report = {'data_sha256': data, 'models': sorted(a), 'entries': entries}
    write_json(output, report)
    return report


def verify(path, manifest, c, measurements):
    report = json.loads(Path(path).read_text())
    expected = {'model': c['model'], 'mode': manifest['protocol']['mode'], 'config_sha256': config_hash(c),
                'requests_sha256': manifest['requests_sha256'],
                'measurements_sha256': sha(Path(measurements).read_text())}
    if report['data_sha256'] != manifest['data_sha256'] or expected not in report['entries']:
        raise ValueError('cohort gate does not match this plan/config/counts')
    return sha(Path(path).read_text())


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--matrix', required=True); p.add_argument('--output', required=True)
    a = p.parse_args(); print(json.dumps(freeze(a.matrix, a.output), indent=2))
