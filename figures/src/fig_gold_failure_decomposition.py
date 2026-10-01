"""Descriptive all-gold outcome partition; no inference or pooled ranking."""
import argparse
import json
import hashlib
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

GROUPS=[('Exact hit',['exact_hit'],'#16836b'),
        ('Category / boundary mismatch',['exact_boundary_wrong_category','overlapping_boundary_same_category','overlapping_boundary_wrong_category'],'#dcae42'),
        ('Unresolved miss with rejected items',['unresolved_with_rejected_items'],'#8470b2'),
        ('No overlapping prediction',['no_overlapping_prediction'],'#d28a97'),
        ('Empty list',['empty_list'],'#b8bdc6'),
        ('JSON / root schema failure',['invalid_json','root_schema'],'#c45846'),
        ('Truncation / terminal failure',['output_truncated','other_terminal_failure'],'#4386b7')]
NAMES={'kakaocorp/kanana-2-3b-instruct':'Kanana 2 3B', 'Qwen/Qwen3.5-2B':'Qwen3.5 2B',
       'Qwen/Qwen3.5-4B':'Qwen3.5 4B','Qwen/Qwen3.5-9B':'Qwen3.5 9B',
       'kakaocorp/kanana-1.5-8b-instruct-2505':'Kanana 1.5 8B',
       'Qwen/Qwen3-30B-A3B':'Qwen3 30B-A3B', 'LGAI-EXAONE/EXAONE-4.5-33B':'EXAONE 4.5 33B'}


def render(paths,output):
    out=Path(output);out.mkdir(parents=True,exist_ok=False)
    data=[json.loads(Path(p).read_text()) for p in paths]
    fig,ax=plt.subplots(figsize=(12,7.4));fig.subplots_adjust(left=.23,right=.98,top=.91,bottom=.32)
    starts=[0.]*len(data)
    for label,keys,color in GROUPS:
        values=[sum(d['gold_outcomes'].get(k,0) for k in keys)/sum(d['gold_outcomes'].values()) for d in data]
        ax.barh(range(len(data)),values,left=starts,color=color,label=label,height=.72)
        starts=[a+b for a,b in zip(starts,values)]
    assert all(abs(v-1)<1e-9 for v in starts)
    ax.set_yticks(range(len(data)),[NAMES.get(d['model'],d['model'])+' / '+('Full' if d['condition']=='full_context_targeted' else 'Local')+(' *' if d['documents']!=1440 else '') for d in data])
    ax.invert_yaxis();ax.set_xlim(0,1);ax.xaxis.set_major_formatter(PercentFormatter(1));ax.set_xlabel('Share of ALL typed gold mentions (%)')
    ax.set_title('Where observed extraction misses occur',loc='left',fontsize=16,pad=15)
    for edge in ['top','right','left']:ax.spines[edge].set_visible(False)
    ax.tick_params(axis='y',length=0,labelsize=10)
    fig.legend(*ax.get_legend_handles_labels(),loc='upper left',bbox_to_anchor=(.025,.225),ncol=2,frameon=False,fontsize=9)
    fig.text(.03,.035,'Post-hoc priority partition after fixed itemwise validation; descriptive, not causal.\nUnresolved rejected items cannot be attributed to particular missed PII.\n* Kanana 1.5 8B: 1,438 documents; others: 1,440. Native capacity/cohort audit pending.',fontsize=9,color='#444444')
    fig.savefig(out/'gold-outcomes.png',dpi=180);fig.savefig(out/'gold-outcomes.svg');plt.close(fig)
    sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    (out/'provenance.json').write_text(json.dumps(dict(source_sha256=sha(__file__),inputs={str(p):sha(p) for p in paths}),indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--analyses',nargs='+',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();render(a.analyses,a.output)
