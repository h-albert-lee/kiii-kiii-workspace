"""Build a local, immutable Hugging Face dataset folder. No network or upload."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.generate.schema import Document
from src.generate.taxonomy import Taxonomy, DEFAULT_PATH
from src.generate.validate import validate


ROOT = Path(__file__).resolve().parents[1]
AXES = ('doc_type', 'variation_level', 'num_subjects', 'context_len_bucket')
GENERATOR_FIELDS = ('model', 'prompt_version', 'slice', 'profile_version', 'reference_date', 'transport')


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()


def rows(path):
    return [json.loads(s) for s in Path(path).read_text().splitlines() if s.strip()]


def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def collect(config):
    """Ordered, explicit sources; the latest accepted variant wins per plan ID."""
    selected = {}; provenance = {}; hashes = {}
    for source in config['sources']:
        path = ROOT / source['path']
        if source['kind'] == 'jsonl':
            if not path.exists(): continue
            found = [(d, path) for d in rows(path)]
        elif source['kind'] == 'accepted_states':
            found = []
            for state_path in sorted(path.rglob('state.json')):
                state = json.loads(state_path.read_text())
                for doc_id, entry in state.get('records', {}).items():
                    if entry['status'] == 'accepted':
                        doc_path = state_path.parent / f'document.{doc_id}.json'
                        found.append((json.loads(doc_path.read_text()), doc_path))
        else: raise ValueError('unknown source kind')
        for doc, file in found:
            selected[doc['doc_id']] = doc
            if file not in hashes: hashes[file] = digest(file)
            provenance[doc['doc_id']] = {'source': str(file.relative_to(ROOT)), 'sha256': hashes[file]}
    return selected, provenance


def split_plans(plans):
    ids = [p['doc_id'] for p in plans]
    if len(set(ids)) != len(ids):
        raise ValueError('duplicate plan IDs')
    return {doc_id: 'test' for doc_id in ids}



def audit(plans, selected, taxonomy):
    expected = {p['doc_id']: p for p in plans}
    if len(expected) != len(plans): raise ValueError('duplicate plan IDs')
    if len({p['seed'] for p in plans}) != len(plans): raise ValueError('duplicate plan seeds')
    missing = sorted(set(expected)-set(selected)); errors = {}; texts = defaultdict(list)
    mismatches = []
    for doc_id in sorted(set(expected) & set(selected)):
        d = selected[doc_id]; p = expected[doc_id]
        try:
            reasons = validate(Document.from_json(d), taxonomy)
            for span in d['spans'] + d.get('hard_negatives', []):
                if type(span['start']) is not int or type(span['end']) is not int or not 0 <= span['start'] < span['end'] <= len(d['text']):
                    reasons.append('invalid Unicode span bounds')
                if d['text'][span['start']:span['end']] != span['surface']: reasons.append('span surface mismatch')
            if d['taxonomy_version'] != taxonomy.version: reasons.append('taxonomy version mismatch')
            if len({s['id'] for s in d['spans']}) != len(d['spans']): reasons.append('duplicate span ID')
            for axis in AXES:
                if d[axis] != p[axis]: mismatches.append({'doc_id':doc_id, 'axis':axis, 'planned':p[axis], 'actual':d[axis]})
            if p['context_len_bucket'] == '16k' and d['context_len_bucket'] != '16k': reasons.append('long plan became short document')
            if reasons: errors[doc_id] = reasons
            texts[hashlib.sha256(d['text'].encode()).hexdigest()].append(doc_id)
        except (ValueError, TypeError, KeyError) as exc:
            errors[doc_id] = [f'schema error: {type(exc).__name__}']
    duplicates = [v for v in texts.values() if len(v)>1]
    return {'expected':len(plans),'available':len(set(expected)&set(selected)), 'missing_ids':missing,
            'validation_errors':errors,'duplicate_text_groups':duplicates,'planned_actual_mismatches':mismatches,
            'human_reviewed':False,'complete':not missing and not errors and not duplicates}


def build(config_path, output, report_path):
    config = json.loads(Path(config_path).read_text()); plans = rows(ROOT/config['plan'])
    selected, provenance = collect(config); taxonomy = Taxonomy()
    result = audit(plans, selected, taxonomy); dump(report_path, result)
    if not result['complete']: return result
    if len(plans) != config['expected_documents']: raise ValueError('unexpected corpus size')
    assignment = split_plans(plans)
    output = Path(output)
    if output.exists(): raise FileExistsError('release folders are immutable; choose another version')
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix='.kiii-release-', dir=output.parent))
    try:
        (temp/'data').mkdir(); by_split = defaultdict(list)
        planmap = {p['doc_id']:p for p in plans}
        for doc_id in sorted(assignment):
            # Schema reconstruction excludes unknown top-level metadata.
            d = Document.from_json(selected[doc_id]).to_json()
            d['generator'] = {k:str(d['generator'].get(k) or '') for k in GENERATOR_FIELDS}
            d['release_version'] = config['version']
            d['generation_seed'] = planmap[doc_id]['seed']
            d['planned_context_len_bucket'] = planmap[doc_id]['context_len_bucket']
            by_split[assignment[doc_id]].append(d)
        for name, docs in by_split.items():
            with (temp/'data'/f'{name}.jsonl').open('w') as f:
                for d in docs: f.write(json.dumps(d,ensure_ascii=False)+'\n')
        stats = {'documents':len(plans),'human_reviewed':False,'split_method':'single evaluation set; no train or validation split',
                 'splits':{s:{'documents':len(ds),'spans':sum(len(d['spans']) for d in ds),
                           **{axis:dict(Counter(str(d[axis]) for d in ds)) for axis in AXES},
                           'generator_models':dict(Counter(d['generator']['model'] for d in ds))} for s,ds in by_split.items()},
                 'planned_actual_mismatch_count':len(result['planned_actual_mismatches']),
                 'near_duplicate_audit':'not performed; exact duplicate text rejected'}
        dump(temp/'statistics.json', stats)
        dump(temp/'split-manifest.json', {'version':config['version'],'assignment':assignment})
        shutil.copyfile(DEFAULT_PATH,temp/'taxonomy.yaml')
        card = (ROOT/'docs/templates/dataset-card.md').read_text()
        card = card.replace('{{VERSION}}',config['version']).replace('{{COUNT}}',str(len(plans)))
        (temp/'README.md').write_text(card)
        manifest = {'version':config['version'],'documents':len(plans),'human_reviewed':False,
                    'files':{str(p.relative_to(temp)):digest(p) for p in sorted(temp.rglob('*')) if p.is_file()}}
        dump(temp/'release-manifest.json',manifest)
        # Local audit only: this file contains source paths and never enters upload folder.
        dump(Path(report_path).with_suffix('.provenance.json'),provenance)
        temp.rename(output)
    except BaseException:
        shutil.rmtree(temp,ignore_errors=True);raise
    return {**result,'output':str(output),'splits':{k:len(v) for k,v in by_split.items()}}


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',required=True);p.add_argument('--output',required=True);p.add_argument('--report',required=True)
    a=p.parse_args();result=build(a.config,a.output,a.report)
    print(json.dumps({k:v for k,v in result.items() if k not in ['validation_errors','planned_actual_mismatches']},ensure_ascii=False,indent=2))
    sys.exit(0 if result['complete'] else 2)
