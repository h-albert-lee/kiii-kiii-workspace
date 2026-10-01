from copy import deepcopy
import pytest
from src.analysis.completed_manuscript import pair_check


def fixture():
    a=dict(model='m',task='span',manifest=dict(data_sha256='d',taxonomy_sha256='t',documents=2,requests=3,protocol=dict(mode='full_context_targeted',core_chars=1200)),execution=dict(cohort_sha256='g',source_sha256={'runner':'s'},config=dict(model_revision='r',tokenizer_revision='r',generation={'temperature':1})))
    b=deepcopy(a);b['manifest']['protocol']['mode']='local_window'
    return a,b


def test_pair_rejects_deployment_and_data_mismatches():
    a,b=fixture();pair_check(a,b)
    for section,key,value in [('manifest','data_sha256','other'),('execution','cohort_sha256','other'),('execution','source_sha256',{'runner':'other'})]:
        c=deepcopy(b);c[section][key]=value
        with pytest.raises(ValueError):pair_check(a,c)
    c=deepcopy(b);c['execution']['config']['generation']={'temperature':0}
    with pytest.raises(ValueError):pair_check(a,c)
    c=deepcopy(b);c['manifest']['protocol']['core_chars']=600
    with pytest.raises(ValueError):pair_check(a,c)
