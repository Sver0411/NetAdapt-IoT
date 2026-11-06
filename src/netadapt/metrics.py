"""Cohort-based losses and explicitly separate time-average freshness."""
from collections import Counter
import numpy as np


def jain(values):
    x=np.asarray(values,dtype=float)
    if x.size==0 or np.sum(x*x)==0:return 0.0
    return float(x.sum()**2/(len(x)*np.sum(x*x)))


def summarize(c,flows,records,aoi):
    cohort=[r for r in records.values() if c.warmup<=r['generated']<c.cohort_end]
    each=[];latencies=[]
    for f in flows:
        rows=[r for r in cohort if r['flow']==f.id]
        delivered=[r for r in rows if r['status'] in ('delivered','late')]
        timely=[r for r in rows if r['status']=='delivered']
        latencies.extend((r['received']-r['generated'])*c.dt for r in delivered)
        each.append(dict(flow=f.id,kind=f.kind,generated=len(rows),delivered=len(delivered),
            timely=len(timely),pdr=len(delivered)/len(rows) if rows else None,
            timely_pdr=len(timely)/len(rows) if rows else None,
            aoi_s=float(aoi[f.id]) if f.kind!='event' else None,
            normalized_aoi=float(aoi[f.id]/(f.tau*c.dt)) if f.kind!='event' else None,
            status_counts=dict(Counter(r['status'] for r in rows))))
    event=[r for r in cohort if flows[r['flow']].kind=='event']
    state=[x for x in each if x['kind']!='event']
    delivered=[r for r in cohort if r['status'] in ('delivered','late')]
    success=sum(r['status']=='delivered' for r in event)
    mean=lambda x:float(np.mean(x)) if x else None
    return dict(generated=len(cohort),delivered=len(delivered),
        pdr=len(delivered)/len(cohort) if cohort else None,
        event_generated=len(event),event_miss=1-success/len(event) if event else None,
        mean_aoi_s=mean([x['aoi_s'] for x in state]),normalized_aoi=mean([x['normalized_aoi'] for x in state]),
        latency_s=mean(latencies),p95_latency_s=float(np.percentile(latencies,95)) if latencies else None,
        cohort_goodput_bps=8*sum(r['size'] for r in delivered)/((c.cohort_end-c.warmup)*c.dt),
        jain_delivery=jain([x['delivered'] for x in each if x['generated']]),
        jain_pdr=jain([x['pdr'] for x in each if x['generated']]),
        cohort_status_counts=dict(Counter(r['status'] for r in cohort)),
        status_counts=dict(Counter(r['status'] for r in records.values())),per_flow=each)
