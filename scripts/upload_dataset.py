"""Preview verified release contents; upload only with --upload and HF_TOKEN."""
import argparse
import json
import os
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.eval.dataset import verify_release


def upload(folder, repo, execute=False, public=False):
    folder=Path(folder);manifest=verify_release(folder)
    allowed=sorted([*manifest['files'],'release-manifest.json'])
    result={'repo':repo,'documents':manifest['documents'],'files':allowed,'upload':False,'visibility':'public' if public else 'private'}
    if not execute:return result
    if not repo or '/' not in repo:raise ValueError('explicit OWNER/REPO required')
    token=os.environ.get('HF_TOKEN')
    if not token:raise ValueError('set HF_TOKEN locally before uploading')
    from huggingface_hub import HfApi
    from huggingface_hub.errors import RepositoryNotFoundError
    api=HfApi(token=token)
    try:
        info=api.repo_info(repo_id=repo,repo_type='dataset')
        if not info.private and not public:raise ValueError('public repository requires explicit --public')
        if info.private and public:raise ValueError('existing repository is private; change visibility explicitly before uploading')
    except RepositoryNotFoundError:
        api.create_repo(repo_id=repo,repo_type='dataset',private=not public,exist_ok=False)
    commit=api.upload_folder(repo_id=repo,repo_type='dataset',folder_path=str(folder),
                             allow_patterns=allowed,commit_message=f"Dataset release {manifest['version']}")
    return {**result,'upload':True,'commit_sha':commit.oid,'commit_url':commit.commit_url}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--folder',required=True);p.add_argument('--repo')
    p.add_argument('--upload',action='store_true');p.add_argument('--public',action='store_true');a=p.parse_args()
    print(json.dumps(upload(a.folder,a.repo,a.upload,a.public),ensure_ascii=False,indent=2))
