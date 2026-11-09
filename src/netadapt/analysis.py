"""All-policy tables, paired seed intervals, figures and explicit negative results."""
from collections import defaultdict
import csv
import json
from pathlib import Path
import numpy as np

METRICS=('mean_aoi_s','normalized_aoi','event_miss','pdr','jain_pdr',
         'jain_delivery','latency_s','p95_latency_s','cohort_goodput_bps','utilization','mean_queue',
         'state_replacement_rate','state_transmission_success','state_goodput_bps',
         'event_deadline_success','event_deadline_miss','event_late_ratio','event_overflow_rate',
         'event_expiration_rate','event_latency_s','event_p95_latency_s',
         'jain_service_share','jain_weighted_service_share','goodput_bps')
LOWER={'mean_aoi_s','normalized_aoi','event_miss','latency_s','p95_latency_s','mean_queue',
       'event_deadline_miss','event_late_ratio','event_overflow_rate','event_expiration_rate',
       'event_latency_s','event_p95_latency_s'}
DESCRIPTIVE={'state_replacement_rate','utilization','mean_queue'}


def interval(values,seed=20261106):
    x=np.asarray(values,dtype=float)
    if not len(x):return None,None,None
    rng=np.random.default_rng(seed)
    boot=rng.choice(x,size=(2000,len(x)),replace=True).mean(axis=1)
    return float(x.mean()),float(np.quantile(boot,.025)),float(np.quantile(boot,.975))


def csv_write(path,rows):
    if not rows:return
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows(rows)


def analyze(output):
    root=Path(output)
    manifest=json.loads((root/'manifest.json').read_text())
    if manifest['metric_version']!=2:raise ValueError('analysis requires metric_version=2')
    rows=[json.loads(p.read_text()) for p in sorted((root/'runs').glob('*/*/*/metrics.json'))]
    expected=len(manifest['study']['scenarios'])*len(manifest['study']['seeds'])*len(manifest['study']['policies'])
    if len(rows)!=expected:raise ValueError(f'incomplete study: {len(rows)}/{expected}')
    csv_write(root/'all_runs.csv',[{k:r[k] for k in ('scenario','policy','seed','metric_version','trace_hash','config_hash','total_generated','observed_generated','state_generated','event_observed_generated','event_resolved','event_pending','state_resolved_attempts','state_pending_attempts','pending_at_main_cutoff','tail_delivered_bytes',*METRICS)} for r in rows])
    csv_write(root/'per_flow.csv',[{'scenario':r['scenario'],'policy':r['policy'],'seed':r['seed'],'metric_version':r['metric_version'],**{k:v for k,v in f.items() if not k.endswith('status_counts')}} for r in rows for f in r['per_flow']])
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
                    fud_worse=metric not in DESCRIPTIVE and mean is not None and (mean>0 if metric in LOWER else mean<0)))
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
    for ax,metric,label in zip(axes,['mean_aoi_s','event_deadline_miss','jain_service_share'],['State mean AoI (s)','Event deadline miss ratio (v2)','Jain service share']):
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
    if not selected:selected=scenarios[:5]
    fig,axes=plt.subplots(1,3,figsize=(14,4.8),layout='constrained')
    methods=['fud','fud_no_age','fud_no_urgency','fud_no_debt']
    for ax,metric,label in zip(axes,['mean_aoi_s','event_deadline_miss','jain_service_share'],['State AoI (s)','Event miss (v2)','Jain service share']):
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
    text=['# 仿真实验结果（metric version 2）',
          f'共 {n} 次运行。每个场景使用共同到达与信道轨迹；配置、源码摘要与软件环境见 manifest.json。',
          '主窗口到达 cohort 追踪至公共尾窗结束；AoI 和 Service Share 仅统计主观察窗口。',
          '\n## FUD 场景表现\n',
          '\n| 场景 | 状态 AoI(s) | 事件 miss(v2) | Jain Service Share | 加权 Jain | Goodput(bit/s) |',
          '|---|---:|---:|---:|---:|---:|']
    for scenario in scenarios:
        values=[idx[scenario,'fud',m]['mean'] for m in ['mean_aoi_s','event_deadline_miss','jain_service_share','jain_weighted_service_share','goodput_bps']]
        text.append('| '+scenario+' | '+' | '.join('NA' if v is None else f'{v:.5f}' for v in values)+' |')
    text+=['\n## 配对比较\n',
           '差值为 FUD − 对照，区间为对 seed 配对差值进行 2,000 次 bootstrap 的 95% CI。AoI/miss 越低越好，Service Share Jain 越高越均衡。完整比较见 paired_differences.csv。',
           '\n| 场景 | 对照 | 指标 | 差值 | 95% CI |','|---|---|---|---:|---|']
    selected=[s for s in scenarios if s in ('normal','congestion','bursty')]
    if not selected:selected=scenarios[:3]
    for p in paired:
        if p['baseline'] in ('fifo','edf','maxweight','pf','aoi_gain') and p['scenario'] in selected and p['metric'] in ('mean_aoi_s','event_deadline_miss','jain_service_share') and p['n']:
            text.append(f"| {p['scenario']} | {p['baseline']} | {p['metric']} | {p['delta_fud_minus_baseline']:.5f} | [{p['ci_low']:.5f}, {p['ci_high']:.5f}] |")
    text+=['\n## 不利结果\n',
           'negative_results.csv 保存全部不利均值方向；区间跨零的比较表示方向尚不明确。以下列出三项主要指标的前 30 条记录。',
           '\n| 场景 | 对照 | 指标 | FUD−对照 | 95% CI |','|---|---|---|---:|---|']
    negatives=[p for p in paired if p['fud_worse'] and p['metric'] in ('mean_aoi_s','event_deadline_miss','jain_service_share')]
    for p in negatives[:30]:
        text.append(f"| {p['scenario']} | {p['baseline']} | {p['metric']} | {p['delta_fud_minus_baseline']:.5f} | [{p['ci_low']:.5f}, {p['ci_high']:.5f}] |")
    text+=['\n## 统计定义\n',
           'event_deadline_success/miss/late 的分母为主观察生成 cohort 内已经判定的事件数；pending 单列。overflow/expiration 的分母为该 cohort 全部事件。状态成功率按已完成发送尝试计算，替换率按状态生成数计算。',
           'Service Share 使用观察窗口内实际占用的抽象服务 slots，含失败尝试；加权 Jain 使用 service_slots/weight。每条配置流均进入资源向量，全零向量 Jain=0。',
           'pdr、event_miss、jain_pdr、jain_delivery、latency_s 和 cohort_goodput_bps 保留 legacy v1 保护区口径；新版业务指标使用不同字段。状态替换率和资源利用率作为描述量，不作单向优劣排序。',
           '事件时延/P95 条件于成功交付；Goodput 按主 cohort 的最终交付 payload 字节除以主观察时长。尾窗交付与成本另存 metrics.json。',
           'summary.csv 保存各策略均值与区间；per_flow.csv 保存分类指标、QoS、资源份额；runs/ 保存逐包生命周期与决策。']
    (root/'results.md').write_text('\n'.join(text)+'\n')
