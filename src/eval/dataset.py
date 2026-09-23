"""Load a verified local/Hub release and prepare the existing evaluation protocol."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import tempfile

from .protocol import Protocol
from .run import prepare, write_jsonl, read_jsonl


def verify_release(folder):
    folder=Path(folder)
    manifest=json.loads((folder/'release-manifest.json').read_text())
    for name, expected in manifest['files'].items():
        p=folder/name
        if Path(name).is_absolute() or '..' in Path(name).parts:
            raise ValueError('unsafe release path')
        if hashlib.sha256(p.read_bytes()).hexdigest()!=expected:
            raise ValueError(f'release checksum mismatch: {name}')
    return manifest


def resolve_release(local=None, repo=None, revision=None):
    if bool(local)==bool(repo):raise ValueError('choose either local folder or Hub repository')
    if local: folder=Path(local)
    else:
        if not revision or not re.fullmatch(r'[0-9a-f]{40}',revision):
            raise ValueError('Hub dataset must be pinned to a full commit SHA')
        from huggingface_hub import snapshot_download
        folder=Path(snapshot_download(repo_id=repo, repo_type='dataset', revision=revision,
                                      allow_patterns=['release-manifest.json','README.md','LICENSE','data/*.jsonl','statistics.json','split-manifest.json','taxonomy.yaml']))
    verify_release(folder)
    return folder


def prepare_dataset(folder, split, directory, protocol, limit=None, doc_ids=None, provenance=None):
    manifest=verify_release(folder)
    from src.generate.taxonomy import DEFAULT_PATH
    if (Path(folder)/'taxonomy.yaml').read_bytes() != DEFAULT_PATH.read_bytes():
        raise ValueError('release taxonomy differs from repository taxonomy')
    if split != 'test':raise ValueError('unknown split')
    if limit is not None and limit<1:
        raise ValueError('smoke limit must be positive')
    from datasets import load_dataset
    with tempfile.TemporaryDirectory(prefix='kiii-eval-input-') as temp:
        ds=load_dataset('json',data_files={split:str(Path(folder)/'data'/f'{split}.jsonl')},split=split,
                        cache_dir=str(Path(temp)/'cache'))
        if limit is not None:ds=ds.select(range(min(limit,len(ds))))
        document_count=len(ds)
        # HF/Arrow can infer ISO date strings as timestamps. Preserve the exact
        # JSON metadata types when freezing evaluation inputs and their hashes.
        original=read_jsonl(Path(folder)/'data'/f'{split}.jsonl')[:document_count]
        if any(row['text']!=source['text'] or row['doc_id']!=source['doc_id'] for row,source in zip(ds,original)):
            raise ValueError('dataset loader changed document identity/text')
        if doc_ids is not None:
            selected = set(json.loads(Path(doc_ids).read_text()))
            if not selected or not selected <= {d['doc_id'] for d in original}:
                raise ValueError('invalid eligible document IDs')
            original = [d for d in original if d['doc_id'] in selected]
            document_count = len(original)
        corpus=Path(temp)/'corpus.jsonl';write_jsonl(corpus,original)
        result=prepare(corpus,directory,protocol)
    source = {'release_version':manifest['version'],
        'release_manifest_sha256':hashlib.sha256((Path(folder)/'release-manifest.json').read_bytes()).hexdigest(),
        'split':split,'limit':limit,'documents':document_count,'selected_doc_ids':doc_ids,
        'provenance':provenance or {'kind':'verified_local_release'}}
    evaluation_manifest=Path(directory)/'manifest.json'
    evaluation_metadata=json.loads(evaluation_manifest.read_text())
    evaluation_metadata['purpose']='plumbing_smoke_only' if limit is not None else 'benchmark'
    evaluation_metadata['dataset_source']=source
    evaluation_manifest.write_text(json.dumps(evaluation_metadata,ensure_ascii=False,indent=2))
    (Path(directory)/'dataset-source.json').write_text(json.dumps(source,indent=2))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    source=p.add_mutually_exclusive_group(required=True);source.add_argument('--local');source.add_argument('--repo')
    p.add_argument('--revision');p.add_argument('--split',choices=['test'],default='test')
    p.add_argument('--smoke-limit',dest='limit',type=int,help='Pipeline check only; not benchmark results');p.add_argument('--directory',required=True)
    p.add_argument('--mode',choices=['full_context_targeted','local_window'],default='full_context_targeted')
    p.add_argument('--doc-ids', help='JSON array of common eligible IDs, fixed before inference')
    p.add_argument('--core-chars', type=int, default=1200); p.add_argument('--halo-chars', type=int, default=1200)
    p.add_argument('--max-output-tokens', type=int, default=4096)
    a=p.parse_args();folder=resolve_release(a.local,a.repo,a.revision)
    print(json.dumps(prepare_dataset(folder,a.split,a.directory,Protocol(a.mode,a.core_chars,a.halo_chars,a.max_output_tokens),a.limit,a.doc_ids,{'repo':a.repo,'revision':a.revision} if a.repo else {'kind':'verified_local_release'})))
