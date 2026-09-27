"""Readable long-form tables from diagnostic JSON; no rescoring or inference."""
import argparse
import csv
import json
from pathlib import Path

from .response_diagnostics import VERSION, file_sha


def breakdown_rows(result, analysis_id):
    if (result.get('purpose') != 'posthoc_secondary_diagnostics' or
            result.get('input_scope') != 'completed_benchmark' or
            result.get('analysis_version') != VERSION or result.get('headline_eligible') is not False):
        raise ValueError('require completed benchmark secondary diagnostics')
    for stage, values in result['stages'].items():
        for metric, partitions in (
            ('exact_with_invalid_item_fp', values),
            ('anchored_character_coverage', values['character_coverage_breakdowns']),
        ):
            groups = dict(partitions['by_axis'], category=partitions['by_category'],
                          tier_kind_tlevel=partitions['tier_kind_tlevel'])
            for axis, buckets in groups.items():
                for group, score in buckets.items():
                    yield dict(analysis_id=analysis_id, model=result['model'],
                               condition=result['protocol']['mode'], stage=stage,
                               metric=metric, axis=axis, group=group,
                               **{k: score[k] for k in ('tp', 'fp', 'fn', 'precision', 'recall', 'f1')})


def export(paths, output):
    paths = [Path(p) for p in paths]
    ids = [p.parent.name for p in paths]
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate analysis directory names')
    rows = [row for path, name in zip(paths, ids)
            for row in breakdown_rows(json.loads(path.read_text()), name)]
    if not rows:
        raise ValueError('no diagnostic rows')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    with (output/'breakdowns.csv').open('x', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0])
        writer.writeheader(); writer.writerows(rows)
    (output/'provenance.json').write_text(json.dumps({
        'purpose': 'secondary_tables_only', 'source_sha256': file_sha(__file__),
        'inputs': {name: file_sha(path) for name, path in zip(ids, paths)},
        'breakdowns_sha256': file_sha(output/'breakdowns.csv'),
        'note': 'No pooling across runs or eligibility validation. F1 is 0–1. See source reports for invalid-item and character-score limitations.'}, indent=2)+'\n')
    return len(rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--analyses', required=True, nargs='+')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    print(f'{export(args.analyses, args.output)} diagnostic rows exported')
