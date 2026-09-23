"""Wait for final generation, then package and smoke-test locally. Never uploads."""
import argparse
import fcntl
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from package_dataset import build, dump
from src.eval.dataset import prepare_dataset
from src.eval.protocol import Protocol


def run(generation,config,output,report):
    status=Path(report).with_suffix('.status.json')
    dump(status,{'status':'waiting_for_generation','upload':False})
    with (Path(generation)/'.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        result=build(config,output,report)
    if not result['complete']:
        dump(status,{'status':'incomplete_or_invalid','audit':str(report),'upload':False});return
    # Read the single evaluation set with Hugging Face before declaring local package ready.
    from datasets import load_dataset
    ds=load_dataset('json',data_files={s:str(Path(output)/'data'/f'{s}.jsonl') for s in ['test']})
    if len(ds['test'])!=1440:raise ValueError('unexpected split sizes')
    target=Path(output).parent/'eval-smoke-kiii-v1-rc1'
    smoke=prepare_dataset(output,'test',target,Protocol(),limit=3)
    dump(status,{'status':'ready_local','upload':False,'output':str(output),'splits':{k:len(v) for k,v in ds.items()},
                 'evaluation_smoke':smoke,'human_reviewed':False})


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['generation','config','output','report']:p.add_argument('--'+key,required=True)
    a=p.parse_args()
    try:run(a.generation,a.config,a.output,a.report)
    except Exception as e:
        dump(Path(a.report).with_suffix('.status.json'),{'status':'error','error_type':type(e).__name__,'error':str(e),'upload':False})
        raise
