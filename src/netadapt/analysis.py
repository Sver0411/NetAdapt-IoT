"""All-policy tables, paired seed intervals, figures and explicit negative results."""
from collections import defaultdict
import csv
import json
from pathlib import Path
import numpy as np

METRICS=('mean_aoi_s','normalized_aoi','event_miss','pdr','jain_pdr',
         'jain_delivery','latency_s','p95_latency_s','cohort_goodput_bps','utilization','mean_queue')
LOWER={'mean_aoi_s','normalized_aoi','event_miss','latency_s','p95_latency_s','mean_queue'}


def interval(values,seed=20261106):
    x=np.asarray(values,dtype=float)
    if not len(x):return None,None,None
    rng=np.random.default_rng(seed)
    boot=rng.choice(x,size=(2000,len(x)),replace=True).mean(axis=1)
    return float(x.mean()),float(np.quantile(boot,.025)),float(np.quantile(boot,.975))


def csv_write(path,rows):
    if not rows:return
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def analyze(output):
    root=Path(output)
    manifest=json.loads((root/'manifest.json').read_text())
    rows=[json.loads(p.read_text()) for p in sorted((root/'runs').glob('*/*/*/metrics.json'))]
    expected=len(manifest['study']['scenarios'])*len(manifest['study']['seeds'])*len(manifest['study']['policies'])
    if len(rows)!=expected:raise ValueError(f'incomplete study: {len(rows)}/{expected}')
    csv_write(root/'all_runs.csv',[{k:r[k] for k in ('scenario','policy','seed','trace_hash','config_hash',*METRICS)} for r in rows])
    csv_write(root/'per_flow.csv',[{'scenario':r['scenario'],'policy':r['policy'],'seed':r['seed'],**{k:v for k,v in f.items() if k!='status_counts'}} for r in rows for f in r['per_flow']])
    groups=defaultdict(list)
    for r in rows:groups[r['scenario'],r['policy']].append(r)
    summary=[]
    for (scenario,policy),rs in groups.items():
        for metric in METRICS:
            vals=[r[metric] for r in rs if r[metric] is not None]
            mean,lo,hi=interval(vals)
            summary.append(dict(scenario=scenario,policy=policy,metric=metric,n=len(vals),mean=mean,ci_low=lo,ci_high=hi))
    csv_write(root/'summary.csv',summary)
    paired=[]
    for scenario in sorted({r['scenario'] for r in rows}):
        target={r['seed']:r for r in groups.get((scenario,'fud'),[])}
        for policy in sorted({r['policy'] for r in rows}-{'fud'}):
            base={r['seed']:r for r in groups[scenario,policy]}
            for metric in METRICS:
                vals=[target[s][metric]-base[s][metric] for s in sorted(target.keys()&base.keys())
                      if target[s][metric] is not None and base[s][metric] is not None]
                mean,lo,hi=interval(vals)
                paired.append(dict(scenario=scenario,baseline=policy,metric=metric,n=len(vals),
                    delta_fud_minus_baseline=mean,ci_low=lo,ci_high=hi,
                    lower_is_better=metric in LOWER,
                    fud_worse=mean is not None and (mean>0 if metric in LOWER else mean<0)))
    csv_write(root/'paired_differences.csv',paired)
    csv_write(root/'negative_results.csv',[r for r in paired if r['fud_worse']])
    make_figures(root,summary)
    report(root,summary,paired,len(rows))
    return {'runs':len(rows),'negative_comparisons':sum(r['fud_worse'] for r in paired)}


def make_figures(root,summary):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    index={(r['scenario'],r['policy'],r['metric']):r for r in summary}
    scenarios=[c['name'] for c in json.loads((root/'manifest.json').read_text())['study']['scenarios']]
    policies=['fifo','rr','edf','pf','aoi_gain','debt','fud']
    fig,axes=plt.subplots(3,1,figsize=(14,11),layout='constrained')
    for ax,metric,label in zip(axes,['mean_aoi_s','event_miss','jain_pdr'],['State mean AoI (s)','Event deadline miss ratio','Jain index of per-flow PDR']):
        for offset,policy in enumerate(policies):
            points=[index.get((s,policy,metric)) for s in scenarios]
            if any(x is None or x['mean'] is None for x in points):continue
            y=np.array([x['mean'] for x in points]);lo=np.array([x['ci_low'] for x in points]);hi=np.array([x['ci_high'] for x in points])
            ax.errorbar(np.arange(len(scenarios))+(offset-3)*.075,y,yerr=[np.maximum(0,y-lo),np.maximum(0,hi-y)],fmt='o',markersize=4,capsize=2,label=policy)
        ax.set_ylabel(label);ax.set_xticks(range(len(scenarios)),scenarios,rotation=35,ha='right');ax.grid(alpha=.2)
    axes[0].legend(ncol=7,fontsize=9)
    fig.suptitle('NetAdapt-IoT | synthetic slotted simulation | seed means and 95% bootstrap CI')
    fig.savefig(root/'overview.png',dpi=170);plt.close(fig)
    selected=[s for s in ['normal','congestion','bursty','weak_link','nodes_96'] if s in scenarios]
    fig,axes=plt.subplots(1,3,figsize=(14,4.8),layout='constrained')
    methods=['fud','fud_no_age','fud_no_urgency','fud_no_debt']
    for ax,metric,label in zip(axes,['mean_aoi_s','event_miss','jain_pdr'],['State AoI (s)','Event miss','Jain(PDR)']):
        for k,p in enumerate(methods):
            points=[index.get((s,p,metric)) for s in selected]
            if any(x is None or x['mean'] is None for x in points):continue
            ax.plot(range(len(selected)),[x['mean'] for x in points],'o-',label=p)
        ax.set_xticks(range(len(selected)),selected,rotation=30,ha='right');ax.set_ylabel(label);ax.grid(alpha=.2)
    axes[0].legend(fontsize=8);fig.suptitle('Mechanism ablations | synthetic simulation (means; intervals in summary.csv)')
    fig.savefig(root/'ablations.png',dpi=170);plt.close(fig)


def report(root,summary,paired,n):
    idx={(r['scenario'],r['policy'],r['metric']):r for r in summary}
    scenarios=sorted({r['scenario'] for r in summary})
    text=['# 仿真实验结果（自动生成）',f'\n共 {n} 次运行。数据来自离散时隙网络模型，配置、源码版本与环境见 manifest.json。',
          '\n## FUD 场景表现','\n| 场景 | 状态AoI(s) | 事件miss | PDR | Jain(PDR) |','|---|---:|---:|---:|---:|']
    for s in scenarios:
        values=[idx[s,'fud',m]['mean'] for m in ['mean_aoi_s','event_miss','pdr','jain_pdr']]
        text.append('| '+s+' | '+' | '.join('NA' if v is None else f'{v:.4f}' for v in values)+' |')
    text+=['\n## 主要配对比较','\n以下差值为 FUD − FIFO；负值有利于AoI/miss。CI为按seed配对的95%bootstrap区间，采用探索性比较。','\n| 场景 | 指标 | 差值 | 95% CI |','|---|---|---:|---|']
    for p in paired:
        if p['baseline']=='fifo' and p['scenario'] in ['congestion','bursty'] and p['metric'] in ['mean_aoi_s','event_miss'] and p['n']:
            text.append(f"| {p['scenario']} | {p['metric']} | {p['delta_fud_minus_baseline']:.5f} | [{p['ci_low']:.5f}, {p['ci_high']:.5f}] |")
    negatives=[p for p in paired if p['fud_worse'] and p['metric'] in ['mean_aoi_s','event_miss','jain_pdr']]
    text+=['\n## 负面结果示例（全部记录见negative_results.csv）','\n| 场景 | 对照 | 指标 | FUD−对照 |','|---|---|---|---:|']
    for p in negatives[:25]:text.append(f"| {p['scenario']} | {p['baseline']} | {p['metric']} | {p['delta_fud_minus_baseline']:.5f} |")
    text+=['\n## 指标解读','\nPDR 按生成 cohort 统计，并区分状态替换、队列丢弃与链路损失。公平性按每流 PDR 计算，时延按交付包统计。节点数量实验同时改变总负载。模型采用已知时间戳、固定反馈时延与有效服务率。',
           '\nsummary.csv 保存各方法均值与区间；paired_differences.csv 保存全部配对差值；per_flow.csv 提供每流服务水平；runs/ 保存逐包结局和调度决策。']
    (root/'results.md').write_text('\n'.join(text))
