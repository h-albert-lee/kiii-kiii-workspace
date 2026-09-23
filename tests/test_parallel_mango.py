import importlib.util
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import parallel_mango as parallel


def test_disjoint_plan_and_budget_partitions():
    plans=[{'doc_id':str(i)} for i in range(720)]
    done={str(i) for i in range(39)}
    lanes,share=parallel.split_remaining(plans,done,7.9)
    ids=[p['doc_id'] for lane in lanes for p in lane]
    assert len(ids)==len(set(ids))==681
    assert not set(ids)&done
    assert abs(4*share+7.9-150)<1e-9
    assert max(map(len,lanes))-min(map(len,lanes))<=1


def test_eight_lanes_keep_global_budget_and_exclude_completed():
    plans = [{'doc_id':str(i)} for i in range(290)]
    lanes, allowance = parallel.split_remaining(plans, {'0', '1'}, 40, concurrency=8)
    ids = [p['doc_id'] for lane in lanes for p in lane]
    assert len(lanes) == 8
    assert len(ids) == len(set(ids)) == 288
    assert not {'0', '1'} & set(ids)
    assert 40 + 8 * allowance == 150


def test_additional_budget_does_not_reuse_old_headroom():
    spent = 74.5065897
    lanes, allowance = parallel.split_remaining([{'doc_id':str(i)} for i in range(400)], set(), spent, ceiling=spent+50, concurrency=8)
    assert len(lanes) == 8
    assert abs(8*allowance-50) < 1e-9
