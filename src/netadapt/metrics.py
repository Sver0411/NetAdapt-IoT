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


METRIC_VERSION=2
FINAL_STATES={'delivered','late','replaced','overflow','expired','link_loss','pending_at_cutoff'}


def classified(c,flows,records,legacy,service_slots,tail_service,qos_slots):
    """v2 main-generation cohort, with delivery outcomes followed through tail."""
    cohort=[r for r in records.values() if c.warmup<=r['generated']<c.slots]
    duration=(c.slots-c.warmup)*c.dt
    ratio=lambda a,b:a/b if b else None
    state=[r for r in cohort if flows[r['flow']].kind!='event']
    event=[r for r in cohort if flows[r['flow']].kind=='event']
    def outcomes(rows):return Counter(r['status'] for r in rows)
    def delivered(rows):return [r for r in rows if r['status'] in ('delivered','late')]
    def event_metrics(rows):
        counts=outcomes(rows);resolved=len(rows)-counts['pending_at_cutoff']
        delays=[(r['received']-r['generated'])*c.dt for r in delivered(rows)]
        return dict(event_resolved=resolved,event_pending=counts['pending_at_cutoff'],
            event_deadline_success=ratio(counts['delivered'],resolved),
            event_deadline_miss=ratio(resolved-counts['delivered'],resolved),
            event_late_ratio=ratio(counts['late'],resolved),
            event_overflow_rate=ratio(counts['overflow'],len(rows)),
            event_expiration_rate=ratio(counts['expired'],len(rows)),
            event_latency_s=float(np.mean(delays)) if delays else None,
            event_p95_latency_s=float(np.percentile(delays,95)) if delays else None)
    def state_metrics(rows):
        counts=outcomes(rows)
        resolved_attempts=counts['delivered']+counts['late']+counts['link_loss']
        return dict(state_replacement_rate=ratio(counts['replaced'],len(rows)),
            state_transmission_success=ratio(counts['delivered']+counts['late'],resolved_attempts),
            state_resolved_attempts=resolved_attempts,
            state_pending_attempts=sum(r['started'] is not None and r['status']=='pending_at_cutoff' for r in rows),
            state_goodput_bps=8*sum(r['size'] for r in delivered(rows))/duration)
    total_service=float(sum(service_slots))
    per_flow=[]
    for f,old in zip(flows,legacy['per_flow']):
        rows=[r for r in cohort if r['flow']==f.id]
        metrics=event_metrics(rows) if f.kind=='event' else state_metrics(rows)
        qos=metrics['event_deadline_success'] if f.kind=='event' else qos_slots[f.id]/(c.slots-c.warmup)
        per_flow.append({**old,**metrics,'observed_generated':len(rows),
            'v2_status_counts':dict(outcomes(rows)),
            'service_slots':int(service_slots[f.id]),'tail_service_slots':int(tail_service[f.id]),
            'service_share':ratio(float(service_slots[f.id]),total_service),
            'weight_reference_share':f.weight/sum(x.weight for x in flows),
            'goodput_bps':8*sum(r['size'] for r in delivered(rows))/duration,
            'qos_satisfaction':qos})
    return dict(metric_version=METRIC_VERSION,legacy_metric_version=1,
        total_generated=len(records),observed_generated=len(cohort),observed_status_counts=dict(outcomes(cohort)),
        state_generated=len(state),event_observed_generated=len(event),
        **state_metrics(state),**event_metrics(event),
        jain_service_share=jain(service_slots),
        jain_weighted_service_share=jain([s/f.weight for s,f in zip(service_slots,flows)]),
        goodput_bps=8*sum(r['size'] for r in delivered(cohort))/duration,
        status_counts=dict(outcomes(list(records.values()))),
        pending_at_main_cutoff=sum(r['status_at_main_cutoff'] in ('queued','inflight') for r in records.values()),
        tail_status_counts=dict(outcomes([r for r in records.values() if r['finished'] is not None and r['finished']>=c.slots])),
        tail_delivered_bytes=sum(r['size'] for r in records.values() if r['status'] in ('delivered','late') and r['received']>=c.slots),
        per_flow=per_flow)
