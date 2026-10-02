"""Vector figures from pinned ADR-0038 tables; no inference or new statistics."""
import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors, font_manager
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

PAPER = Path(__file__).resolve().parents[1]
ROOT = PAPER.parents[1]
sys.path.insert(0, str(ROOT / 'figures/src'))
from _style import setup

NAVY, RUST, TEAL = '#233D56', '#B45B32', '#287C83'
INK, MUTED, GRID, PALE = '#243241', '#65717E', '#E4E9ED', '#F3F6F8'
META = {'Creator': 'Kiii-Kiii figure builder', 'CreationDate': None, 'ModDate': None}
FULL, LOCAL = 'full_context_targeted', 'local_window'
MODELS = [
    ('Qwen/Qwen3.5-2B', 'Qwen3.5-2B'),
    ('Qwen/Qwen3.5-4B', 'Qwen3.5-4B'),
    ('kakaocorp/kanana-2-3b-instruct', 'Kanana-2-3B'),
    ('Qwen/Qwen3.5-9B', 'Qwen3.5-9B'),
    ('kakaocorp/kanana-1.5-8b-instruct-2505', 'Kanana-1.5-8B*'),
    ('LGAI-EXAONE/EXAONE-4.5-33B', 'EXAONE-4.5-33B'),
    ('Qwen/Qwen3-30B-A3B', 'Qwen3-30B-A3B'),
    ('google/gemma-4-E2B-it', 'Gemma-4-E2B'),
    ('google/gemma-4-E4B-it', 'Gemma-4-E4B'),
    ('google/gemma-4-12B-it', 'Gemma-4-12B'),
    ('google/gemma-4-26B-A4B-it', 'Gemma-4-26B-A4B'),
    ('google/gemma-4-31B-it', 'Gemma-4-31B (FP8)'),
    ('presidio', 'Presidio'), ('ko-pii', 'ko-pii'), ('openmed', 'OpenMed'),
]


def load():
    pins = json.loads((PAPER / 'notes/analysis-inputs.json').read_text())
    for rel, expected in pins['sha256'].items():
        if hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Frozen manuscript input changed: {rel}')
    base = ROOT / 'experiments/results/analyses/1001-completed-manuscript-v1/tables'
    def read(name):
        with (base / name).open(newline='') as f:
            return list(csv.DictReader(f))
    summary, groups, paired = read('summary.csv'), read('taxonomy_groups.csv'), read('paired.csv')
    assert len(summary) == 25 and len(groups) == 75 and len(paired) == 10
    lookup = {(r['model'], r['condition']): r for r in summary}
    assert len(lookup) == 25
    for r in paired:
        f, l = lookup[r['model'], FULL], lookup[r['model'], LOCAL]
        assert f['documents'] == l['documents'] == r['documents']
        assert abs(float(f['strict_f1']) - float(l['strict_f1']) - float(r['delta_f1'])) < 1e-12
    for g in groups:
        tp, fp, fn = (int(g[k]) for k in ('tp', 'fp', 'fn'))
        assert abs(float(g['f1']) - 2*tp/(2*tp+fp+fn)) < 1e-12
    return summary, lookup, groups, paired


def style():
    setup()
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8,
                         'text.color': INK, 'axes.labelcolor': MUTED,
                         'xtick.color': MUTED, 'ytick.color': INK,
                         'axes.edgecolor': GRID, 'axes.linewidth': .7,
                         'savefig.bbox': None, 'savefig.pad_inches': .02})


def save(fig, name):
    directory = PAPER / 'figures'
    fig.savefig(directory / f'{name}.pdf', metadata=META)
    fig.savefig(directory / f'{name}.svg', metadata={'Date': None})
    fig.savefig(directory / f'{name}.png', dpi=220)
    plt.close(fig)


def title(ax, letter, text):
    ax.text(0, 1.055, letter, transform=ax.transAxes, weight='bold', fontsize=10, color=INK)
    ax.text(.105, 1.055, text, transform=ax.transAxes, weight='bold', fontsize=8.5)


def rows_axis(ax, n, labels=False):
    ax.set_ylim(n-.5, -.5)
    ax.set_yticks(range(n), [label for _, label in MODELS] if labels else [])
    ax.tick_params(axis='y', length=0, pad=6)
    for spine in ('top', 'right', 'left'):
        ax.spines[spine].set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(axis='x', color=GRID, linewidth=.5)
    for i in range(n):
        if i % 2 == 0:
            ax.axhspan(i-.46, i+.46, color=PALE, zorder=0)
    ax.axhline(11.5, color='#A9B3BC', linewidth=.7)


def score_portrait(lookup):
    fig = plt.figure(figsize=(7.0, 3.77))
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, .43], left=.225, right=.99,
                          top=.82, bottom=.17, wspace=.22)
    axes = [fig.add_subplot(gs[0, i]) for i in range(3)]
    for ax, condition, letter, name in zip(axes[:2], [FULL, LOCAL], 'AB', ['Full context', 'Local context']):
        rows_axis(ax, 15, labels=ax is axes[0]);title(ax, letter, name)
        ax.set_xlim(-1, 35);ax.set_xticks([0, 10, 20, 30])
        ax.set_xlabel('F1 (0–100 scale)', fontsize=7.5)
        for i, (model, _) in enumerate(MODELS):
            baseline = i >= 12
            row = lookup.get((model, 'document' if baseline else condition))
            if baseline:
                if condition == FULL:
                    ax.plot(100*float(row['strict_f1']), i, 's', markersize=4, color=INK, zorder=3)
                else:
                    ax.text(17, i, 'document-level reference', ha='center', va='center', fontsize=6.2, color=MUTED)
                continue
            if row is None:
                ax.text(17, i, 'not completed', ha='center', va='center', fontsize=6.5, color=MUTED)
                continue
            strict, diagnostic = (100*float(row[k]) for k in ('strict_f1', 'detection_f1'))
            ax.plot([strict, diagnostic], [i, i], color='#AAB6C1', linewidth=1.05, zorder=2)
            ax.plot(strict, i, 'o', color=NAVY, markersize=4, zorder=4)
            ax.plot(diagnostic, i, 'D', markeredgecolor=RUST, markerfacecolor='white',
                    markersize=4.3, markeredgewidth=1.2, zorder=4)
    ax = axes[2];rows_axis(ax, 15)
    ax.text(0, 1.055, 'C', transform=ax.transAxes, weight='bold', fontsize=10)
    ax.text(.25, 1.055, 'Format %', transform=ax.transAxes, weight='bold', fontsize=8.5)
    ax.set_xlim(-.5, 1.5);ax.set_xticks([0, 1], ['Full', 'Local'])
    ax.tick_params(axis='x', length=0);ax.grid(False)
    cmap = colors.LinearSegmentedColormap.from_list('compliance', ['#F5F7F9', '#CBD7E2', NAVY])
    for i, (model, _) in enumerate(MODELS):
        for j, condition in enumerate([FULL, LOCAL]):
            row = lookup.get((model, condition))
            val = 100*float(row['format_compliance']) if row else None
            ax.add_patch(Rectangle((j-.47, i-.46), .94, .92,
                         facecolor=cmap(val/100) if val is not None else '#F0F0F0', edgecolor='white', lw=.5))
            label = ('<0.1' if 0 < val < .1 else f'{val:.1f}') if val is not None else ('N/A' if i >= 12 else '—')
            ax.text(j, i, label, ha='center', va='center', fontsize=6.6,
                    color='white' if val is not None and val > 65 else INK)
    handles = [Line2D([], [], marker='o', color='none', markerfacecolor=NAVY, markeredgecolor=NAVY,
                      markersize=4, label='Strict: end-to-end extraction'),
               Line2D([], [], marker='D', color='none', markerfacecolor='white', markeredgecolor=RUST,
                      markersize=4, label='D: observable detection proxy'),
               Line2D([], [], marker='s', color='none', markerfacecolor=INK, markeredgecolor=INK,
                      markersize=4, label='Baseline strict')]
    fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(.55, .995),
               ncol=3, frameon=False, fontsize=6.8, handletextpad=.4, columnspacing=1.0)
    fig.text(.225, .025, 'Same archived outputs · all gold retained · original cohorts · no score-based model selection', fontsize=7, color=MUTED)
    save(fig, 'score-portrait')


def context(lookup, paired):
    order = {model: i for i, (model, _) in enumerate(MODELS)}
    paired = sorted(paired, key=lambda r: order[r['model']]);labels = dict(MODELS)
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.15), sharey=True)
    fig.subplots_adjust(left=.225, right=.93, top=.79, bottom=.17, wspace=.48)
    for i, r in enumerate(paired):
        x, lo, hi = (100*float(r[k]) for k in ('delta_f1', 'ci_low', 'ci_high'))
        axes[0].errorbar(x, i, xerr=[[x-lo], [hi-x]], fmt='o', markersize=4,
                         color=NAVY, capsize=2, linewidth=1.0, zorder=3)
        f, l = lookup[r['model'], FULL], lookup[r['model'], LOCAL]
        d = 100*(float(f['detection_f1']) - float(l['detection_f1']))
        axes[1].plot(d, i, 'D', markerfacecolor='white', markeredgecolor=RUST,
                     markeredgewidth=1.2, markersize=4.5)
        axes[1].text(1.04, i, f'{d:+.2f}', transform=axes[1].get_yaxis_transform(),
                     ha='left', va='center', fontsize=6.6, color=RUST)
    for ax, letter, label in zip(axes, 'AB', ['Strict F1', 'D-F1']):
        title(ax, letter, label);ax.set_ylim(9.65, -.65)
        ax.axvline(0, color=MUTED, lw=.8, ls=(0,(3,3)))
        ax.grid(axis='y', color=GRID, linewidth=.5);ax.tick_params(axis='y', length=0, pad=6)
        ax.spines['left'].set_visible(False);ax.set_xlabel('Full − local (F1 points)', fontsize=7.5)
    axes[0].set_yticks(range(10), [labels[r['model']] for r in paired])
    axes[0].set_xlim(-2.55, 1.05);axes[0].set_xticks([-2, -1, 0, 1])
    axes[1].set_xlim(-8.6, .6);axes[1].set_xticks([-8, -6, -4, -2, 0])
    fig.text(.225, .93, 'Matched targets. Different context.', weight='bold', fontsize=10)
    fig.text(.225, .865, '95% pointwise paired intervals', fontsize=7.2, color=MUTED)
    fig.text(.675, .865, 'Point differences only', fontsize=7.2, color=MUTED)
    fig.text(.225, .035, '← Local higher       Full higher →     |     10 complete pairs; missing pairs omitted', fontsize=7, color=MUTED)
    save(fig, 'context-contrasts')


def taxonomy(groups):
    lookup = {(r['model'], r['condition'], r['group']): r for r in groups}
    cats = ['L/identifier', 'L/attribute', 'I/attribute'];data = np.full((15, 6), np.nan)
    for i, (model, _) in enumerate(MODELS):
        for j, condition in enumerate([FULL, LOCAL]):
            for k, group in enumerate(cats):
                key = model, 'document' if i >= 12 else condition, group
                if key in lookup and not (i >= 12 and j == 1):data[i, 3*j+k] = 100*float(lookup[key]['f1'])
    assert np.count_nonzero(~np.isnan(data)) == 75
    fig, ax = plt.subplots(figsize=(7.0, 3.25));fig.subplots_adjust(left=.225, right=.90, bottom=.12, top=.83)
    cmap = colors.LinearSegmentedColormap.from_list('coverage', ['#F5F8FA', '#ADC7D6', '#265D78', NAVY]);cmap.set_bad('#EEEEEE')
    ax.imshow(np.ma.masked_invalid(data), cmap=cmap, vmin=0, vmax=25, aspect='auto', interpolation='nearest')
    ax.set_yticks(range(15), [label for _, label in MODELS])
    ax.set_xticks(range(6), ['L: identifiers', 'L: attributes', 'I: attributes']*2, fontsize=6.8)
    ax.tick_params(length=0, pad=6)
    for spine in ax.spines.values():spine.set_visible(False)
    for i in range(15):
        for j in range(6):
            value = data[i,j]
            if np.isnan(value):label = 'N/A' if i >= 12 else '—'
            elif 0 < value < .01:label = '<.01'
            elif value == 0:label = '0'
            else:label = f'{value:.2f}'
            ax.text(j, i, label, ha='center', va='center', fontsize=6.8,
                    color='white' if value >= 13 else INK)
    ax.set_xticks(np.arange(-.5, 6, 1), minor=True);ax.set_yticks(np.arange(-.5, 15, 1), minor=True)
    ax.grid(which='minor', color='white', linewidth=1.2);ax.tick_params(which='minor', length=0)
    ax.axvline(2.5, color='white', linewidth=8);ax.axhline(11.5, color='#ACB6BF', linewidth=.9)
    ax.text(.25, 1.055, 'A   Full / document-level references', transform=ax.transAxes, ha='center', fontsize=8.1, weight='bold')
    ax.text(.75, 1.055, 'B   Local context', transform=ax.transAxes, ha='center', fontsize=8.1, weight='bold')
    cax = fig.add_axes([.935, .36, .012, .30]);cb = fig.colorbar(ax.images[0], cax=cax, ticks=[0, 10, 20, 25])
    cb.outline.set_visible(False);cb.ax.tick_params(length=0, labelsize=6.5);cax.set_title('Strict\nF1', fontsize=7, pad=7)
    fig.text(.225, .025, 'Shared linear scale · 0 = measured zero · — = missing condition · N/A = no context pair', fontsize=6.8, color=MUTED)
    save(fig, 'taxonomy-coverage')


def diagnostic_table(lookup):
    """Keep exact primary scores reviewable alongside the graphical summary."""
    def score(value):
        if value is None:return '--'
        n=100*float(value)
        return r'$<0.01$' if 0<n<.01 else f'{n:.2f}'
    lines=[r'%% Generated from pinned ADR-0038 summary.csv; do not edit numbers.',
           r'\begin{table*}[t]',
           r'\caption{Completed-run strict scores and post-hoc diagnostics. Scores and rates use 0--100; invalid items are counts. Fmt: structural compliance; Empty: empty-list rate; D: observable detection proxy with invalid-item exact-FP penalties. F/L: full/local; Doc: document-level baseline. *Kanana-1.5-8B uses 1,438 documents; others use 1,440. Baseline diagnostics are not applicable.}',
           r'\label{tab:response-diagnostics}',r'\small',
           r'\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llrrrrrrr@{}}',
           r'\toprule',r'System & Context & Strict F1 & Fmt & Empty & D-Prc & D-Rec & D-F1 & Invalid items \\',r'\midrule']
    for i,(model,label) in enumerate(MODELS):
        if i==12:lines.append(r'\midrule')
        for condition in (['document'] if i>=12 else [FULL,LOCAL]):
            row=lookup.get((model,condition))
            if row is None:continue
            ctx={'document':'Doc',FULL:'F',LOCAL:'L'}[condition]
            nums=[score(row[k] if row[k] else None) for k in ['strict_f1','format_compliance','empty_list_rate','detection_precision','detection_recall','detection_f1']]
            invalid=f"{int(row['invalid_item_fp']):,}" if row['invalid_item_fp'] else '--'
            lines.append(' & '.join([label,ctx]+nums+[invalid])+r' \\')
    lines.extend([r'\bottomrule',r'\end{tabular*}',r'\end{table*}'])
    (PAPER/'sections/response-table.tex').write_text('\n'.join(lines)+'\n')


def overview():
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.55))
    fig.subplots_adjust(left=.025, right=.99, top=.84, bottom=.04, wspace=.15)
    for ax in axes:ax.set(xlim=(0,1), ylim=(0,1));ax.axis('off')
    for ax, letter, text in zip(axes, 'ABC', ['Define the policy', 'Hold the target fixed', 'Inspect the same response']):
        ax.text(0, 1.09, letter, fontsize=10, weight='bold');ax.text(.1, 1.09, text, fontsize=8.1, weight='bold')
    ax=axes[0];ax.text(0, .94, 'Korean financial privacy', fontsize=8.1, weight='bold')
    for y, color, heading, sub in [(.73, NAVY, '24 statutory categories', '17 identifiers + 7 attributes'),
                                   (.51, TEAL, '12 identifiability categories', 'Contextual / profiling attributes')]:
        ax.add_patch(Rectangle((0,y-.02),1,.18,facecolor=PALE,edgecolor='none'))
        ax.add_patch(Rectangle((0,y-.02),.018,.18,facecolor=color,edgecolor='none'))
        ax.text(.05,y+.095,heading,fontsize=7.5,weight='bold');ax.text(.05,y+.025,sub,fontsize=6.5,color=MUTED)
    ax.text(0,.405,'Noncanonical input forms',fontsize=7.5,weight='bold')
    ko = next((f.fname for f in font_manager.fontManager.ttflist if f.name == 'Arial Unicode MS'),None)
    if ko is None:ko = next((f.fname for f in font_manager.fontManager.ttflist if 'Noto Sans CJK' in f.name),None)
    if ko is None:raise RuntimeError('Install Arial Unicode MS or Noto Sans CJK for Korean examples.')
    kp=font_manager.FontProperties(fname=ko,size=6.6)
    samples=[('T0', '010-3344-5566'),('T1', '010 3344 5566'),('T2', '공일공 삼삼사사 오오육육'),('T3', 'A: 010-3344  …  A: 5566')]
    for i,(t,text) in enumerate(samples):
        y=.305-i*.084;ax.text(0,y,t,fontsize=6.8,color=TEAL,weight='bold')
        if t=='T2':ax.text(.16,y,text,fontproperties=kp)
        else:ax.text(.16,y,text,fontsize=6.6)
    ax=axes[1];ax.text(0,.94,'Gold-blind character windows',fontsize=8.1,weight='bold')
    def window(y, full):
        ax.text(0,y+.105,'Full context' if full else 'Local context',fontsize=7.3,weight='bold')
        ax.add_patch(Rectangle((0,y),1,.067,facecolor='#E8EDF0',edgecolor='none'))
        if not full:
            ax.add_patch(Rectangle((0,y),.16,.067,facecolor='white',edgecolor='#E8EDF0',lw=.5,hatch='////'))
            ax.add_patch(Rectangle((.83,y),.17,.067,facecolor='white',edgecolor='#E8EDF0',lw=.5,hatch='////'))
        ax.add_patch(Rectangle((.37,y),.23,.067,facecolor=TEAL,edgecolor='none'))
        ax.add_patch(Rectangle((.60,y),.23,.067,facecolor='#B8D5D6',edgecolor='none'))
    window(.70,True);window(.45,False)
    for x in (.37,.60,.83):ax.plot([x,x],[.425,.80],color=TEAL,lw=.55,ls=(0,(2,2)),alpha=.65)
    ax.text(.46,.34,'core',fontsize=6.8,ha='center',color=TEAL);ax.text(.715,.34,'halo',fontsize=6.8,ha='center',color=MUTED)
    ax.text(0,.215,'Same output ownership',fontsize=7.5,weight='bold');ax.text(0,.125,'Start in core; end within target',fontsize=7)
    ax.text(0,.04,'1,200 core / halo · 4,096 output tokens',fontsize=6.3,color=MUTED)
    ax=axes[2];ax.text(0,.94,'Illustrative parsed items',fontsize=8.1,weight='bold')
    for i,(text,color) in enumerate([('Exact valid quotation',TEAL),('Invalid parsed item',RUST)]):
        y=.755-i*.13;ax.add_patch(Rectangle((0,y-.04),1,.105,facecolor=PALE,edgecolor='none'))
        ax.scatter(.055,y+.012,s=14,c=color,marker='o' if i==0 else 'x');ax.text(.13,y,text,fontsize=7.3)
    for x in [.22,.76]:ax.annotate('',xy=(x,.41),xytext=(.5,.59),arrowprops={'arrowstyle':'->','color':MUTED,'lw':.8})
    ax.text(.02,.35,'Strict',fontsize=8,weight='bold',color=NAVY);ax.text(.02,.25,'Reject request',fontsize=7)
    ax.text(.54,.35,'Diagnostic D',fontsize=8,weight='bold',color=RUST);ax.text(.54,.25,'Keep valid item',fontsize=6.8)
    ax.text(.54,.16,'Invalid item: +1 FP',fontsize=6.5);ax.text(0,.04,'All gold retained in both scoring views',fontsize=6.5,color=MUTED)
    save(fig,'benchmark-overview')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--only',choices=['context']);args=p.parse_args()
    style();_,lookup,groups,paired=load();context(lookup,paired)
    if not args.only:overview();score_portrait(lookup);taxonomy(groups);diagnostic_table(lookup);error_atlas()
    print('Verified 25 conditions / 75 group metrics / 10 contrasts; built vector figures.')


def error_atlas():
    pins = json.loads((PAPER/'notes/error-analysis-inputs.json').read_text())
    for rel, expected in pins['sha256'].items():
        if hashlib.sha256((ROOT/rel).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Error-analysis input changed: {rel}')
    with (ROOT/pins['summary']).open(newline='') as f:
        lookup = {(r['model'],r['condition']):r for r in csv.DictReader(f)}
    assert len(lookup) == 22
    groups = [('exact_hit','Exact hit',TEAL),
              ('boundary_or_category','Boundary / category','#7DAAB9'),
              ('empty_output','Empty output','#E6BD70'),
              ('unusable_output','Unusable output','#B56F56'),
              ('unresolved_rejected','Unresolved + rejected','#A5A4B4'),
              ('no_overlap','No overlap','#E2E5E8')]
    fig, axes = plt.subplots(1,2,figsize=(7,3.38),sharey=True)
    fig.subplots_adjust(left=.23,right=.987,top=.81,bottom=.16,wspace=.16)
    for ax,condition,letter,heading in zip(axes,[FULL,LOCAL],'AB',['Full context','Local context']):
        ax.set_ylim(11.65,-.65);ax.set_xlim(0,100)
        ax.set_yticks(range(12),[label for _,label in MODELS[:12]])
        ax.tick_params(axis='y',length=0,labelsize=7,pad=6)
        ax.set_xticks([0,25,50,75,100]);ax.tick_params(axis='x',labelsize=7)
        ax.set_xlabel('Share of all gold mentions (%)',fontsize=7.5)
        title(ax,letter,heading)
        for spine in ['top','right','left']:ax.spines[spine].set_visible(False)
        for i,(model,_) in enumerate(MODELS[:12]):
            r=lookup.get((model,condition))
            if r is None:
                ax.text(50,i,'not completed',ha='center',va='center',fontsize=6.7,color=MUTED);continue
            assert sum(int(r['gold_'+k]) for k,_,_ in groups)==int(r['gold'])
            left=0
            for k,_,color in groups:
                width=100*float(r['gold_'+k+'_rate'])
                ax.barh(i,width,left=left,height=.64,color=color,edgecolor='white',linewidth=.25)
                left+=width
            exact=100*float(r['gold_exact_hit_rate'])
            if exact>=5:
                ax.text(exact/2,i,f'{exact:.0f}',ha='center',va='center',fontsize=6,color='white')
    handles=[Rectangle((0,0),1,1,facecolor=color) for _,_,color in groups]
    fig.legend(handles,[label for _,label,_ in groups],ncol=3,loc='upper center',
               bbox_to_anchor=(.55,1.01),frameon=False,fontsize=6.9,columnspacing=1.5,handlelength=1.3)
    fig.text(.23,.015,'Descriptive priority partition, not causal attribution. *1,438 documents; other runs: 1,440.',fontsize=6.5,color=MUTED)
    save(fig,'error-atlas')


if __name__=='__main__':main()
