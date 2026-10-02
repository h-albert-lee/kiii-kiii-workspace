from copy import deepcopy
import pytest
from src.analysis.sac_error_atlas import summarize


def diagnostic():
    return dict(headline_eligible=False,provenance={'strict_and_itemwise_replayed':True},
                model='fixture',condition='local_window',documents=2,
                gold_outcomes={'exact_hit':2,'invalid_json':3,'empty_list':1,
                               'overlapping_boundary_same_category':2,'unresolved_with_rejected_items':2},
                itemwise_exact={'tp':2,'fp':5,'fn':8},strict_exact={'tp':1,'fp':1,'fn':9},
                invalid_item_fp=4,item_outcomes={'valid':3,'quote_absent_from_target':1,'outside_owned_core':3},
                request_counts={'total':4,'invalid_json':1,'empty_list':1,'nonempty_list':2,
                                'format_compliant':1,'whole_fence_parseable':2})


def test_distinct_denominators_and_noncausal_unresolved_bucket():
    r=summarize(diagnostic())
    assert r['request_whole_fence_parseable_rate']==.5
    assert r['gold_unusable_output_rate']==.3
    assert r['item_outside_owned_core_share_of_invalid']==.75
    assert r['gold_unresolved_rejected_rate']==.2
    assert r['detection_recall']==.2  # rejected items are not promoted to gold hits
    assert sum(r['gold_'+k+'_rate'] for k in ['exact_hit','unusable_output','empty_output',
               'boundary_or_category','unresolved_rejected','no_overlap'])==pytest.approx(1)


@pytest.mark.parametrize('mutation',[
    lambda d:d['gold_outcomes'].update(empty_list=0),
    lambda d:d.update(invalid_item_fp=3),
    lambda d:d['request_counts'].update(total=5),
    lambda d:d['gold_outcomes'].update(unknown=0),
    lambda d:d['provenance'].update(strict_and_itemwise_replayed=False),
])
def test_incomplete_or_changed_accounting_is_rejected(mutation):
    d=deepcopy(diagnostic());mutation(d)
    with pytest.raises(ValueError):summarize(d)
