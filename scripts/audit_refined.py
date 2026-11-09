"""Independent raw-ledger reconstruction and exact deterministic metric replay."""
from collections import Counter,defaultdict
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from netadapt.model import Config,flows_for
from netadapt.runner import code_hash
from netadapt.traffic import generate
from netadapt.simulation import simulate

root=Path(sys.argv[1]);manifest=json.loads((root/'manifest.json').read_text())
assert manifest['metric_version']==2
assert manifest['code_hash']==code_hash(),'source differs from experiment manifest'
study=manifest['study'];count=0;packet_count=0;pending_count=0;trace_groups=0
FINAL={'delivered','late','replaced','overflow','expired','link_loss','pending_at_cutoff'}

def close(a,b):
    if b is None:assert a is None,(a,b)
    else:assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10),(a,b)

def ratio(a,b):return a/b if b else None

def ji(xs):
    den=len(xs)*sum(x*x for x in xs)
    return sum(xs)**2/den if den else 0.

def raw(path):
    with gzip.open(path,'rt') as f:return [json.loads(line) for line in f]

for config in study['scenarios']:
    c=Config(**config);flows=flows_for(c)
    for seed in study['seeds']:
        trace=generate(c,seed);trace_groups+=1
        for policy in study['policies']:
            path=root/'runs'/c.name/str(seed)/policy
            r=json.loads((path/'metrics.json').read_text())
            assert r['metric_version']==2 and r['config_hash']==c.digest() and r['trace_hash']==trace.digest
            packets=raw(path/'packets.jsonl.gz');decisions=raw(path/'decisions.jsonl.gz')
            assert len({p['id'] for p in packets})==len(packets)
            assert len(packets)==sum(map(len,trace.arrivals))==r['total_generated']
            assert {(p['id'],p['flow'],p['generated'],p['size']) for p in packets}=={(p.id,p.flow,p.generated,p.size) for batch in trace.arrivals for p in batch}
            counts=Counter(p['status'] for p in packets)
            assert set(counts)<=FINAL and dict(counts)==r['status_counts']
            assert counts['pending_at_cutoff']==0,'full configured tail must resolve every packet'
            cohort=[p for p in packets if c.warmup<=p['generated']<c.slots]
            assert len(cohort)==r['observed_generated']
            assert dict(Counter(p['status'] for p in cohort))==r['observed_status_counts']
            event=[p for p in cohort if flows[p['flow']].kind=='event']
            ec=Counter(p['status'] for p in event);resolved=len(event)-ec['pending_at_cutoff']
            assert r['event_resolved']==resolved and r['event_pending']==ec['pending_at_cutoff']
            close(r['event_deadline_success'],ratio(ec['delivered'],resolved))
            close(r['event_deadline_miss'],ratio(resolved-ec['delivered'],resolved))
            close(r['event_overflow_rate'],ratio(ec['overflow'],len(event)))
            close(r['event_expiration_rate'],ratio(ec['expired'],len(event)))
            close(r['event_late_ratio'],ratio(ec['late'],resolved))
            delays=[(p['received']-p['generated'])*c.dt for p in event if p['status'] in ('delivered','late')]
            close(r['event_latency_s'],float(np.mean(delays)) if delays else None)
            close(r['event_p95_latency_s'],float(np.percentile(delays,95)) if delays else None)
            state=[p for p in cohort if flows[p['flow']].kind!='event'];sc=Counter(p['status'] for p in state)
            close(r['state_replacement_rate'],ratio(sc['replaced'],len(state)))
            close(r['state_transmission_success'],ratio(sc['delivered']+sc['late'],sc['delivered']+sc['late']+sc['link_loss']))
            duration=(c.slots-c.warmup)*c.dt
            close(r['goodput_bps'],8*sum(p['size'] for p in cohort if p['status'] in ('delivered','late'))/duration)
            close(r['state_goodput_bps'],8*sum(p['size'] for p in state if p['status'] in ('delivered','late'))/duration)
            byid={p['id']:p for p in packets};costs=[0]*c.nodes;tail=[0]*c.nodes
            credit=0.;prev=-1;end=0;reserved=0
            assert len(decisions)==r['attempts'] and len({d['packet'] for d in decisions})==len(decisions)
            for d in decisions:
                t=d['t'];s=d['service'];i=d['flow'];p=byid[d['packet']];f=flows[i]
                assert t>=end and t>=p['generated'] and s==f.service and t==p['started']
                credit=min(c.bucket_slots,credit+(t-prev)*c.duty)-s
                assert credit>=-1e-7
                reserved+=s;prev=t;end=t+s
                assert reserved<=(t+1)*c.duty+1e-6
                costs[i]+=max(0,min(end,c.slots)-max(t,c.warmup))
                tail[i]+=max(0,min(end,c.end)-max(t,c.slots))
                expected=t+s+c.delay
                assert p['finished']==expected
                ok=bool(trace.success[t,i])
                assert (p['status'] in ('delivered','late'))==ok
                if ok:
                    assert p['received']==expected
                    assert p['status']==('delivered' if f.deadline is None or expected<=p['generated']+f.deadline else 'late')
            assert reserved==r['reserved_slots']+r['tail_reserved_slots']
            close(sum(costs)/(c.slots-c.warmup),r['utilization'])
            close(ji(costs),r['jain_service_share'])
            close(ji([s/f.weight for s,f in zip(costs,flows)]),r['jain_weighted_service_share'])
            ages=[];normalized=[]
            for f,pf in zip(flows,r['per_flow']):
                assert costs[f.id]==pf['service_slots'] and tail[f.id]==pf['tail_service_slots']
                close(pf['service_share'],ratio(costs[f.id],sum(costs)))
                fp=[p for p in cohort if p['flow']==f.id]
                close(pf['goodput_bps'],8*sum(p['size'] for p in fp if p['status'] in ('delivered','late'))/duration)
                if f.kind=='event':continue
                # Integrate t-u exactly on each piecewise-constant timestamp interval.
                acks=sorted((p['received'],p['generated']) for p in packets if p['flow']==f.id and p['status'] in ('delivered','late') and p['received']<c.slots)
                last=0;start=0;area=0;fresh=0
                for stop,g in acks+[(c.slots,last)]:
                    lo=max(start,c.warmup);hi=stop
                    if hi>lo:
                        area+=(lo+hi-1)*(hi-lo)/2-last*(hi-lo)
                        fresh+=max(0,min(hi,last+f.tau+1)-lo)
                    start=stop;last=max(last,g)
                age=area/(c.slots-c.warmup)*c.dt
                close(pf['aoi_s'],age);close(pf['qos_satisfaction'],fresh/(c.slots-c.warmup))
                ages.append(age);normalized.append(age/(f.tau*c.dt))
            close(r['mean_aoi_s'],float(np.mean(ages)) if ages else None)
            close(r['normalized_aoi'],float(np.mean(normalized)) if normalized else None)
            count+=1;packet_count+=len(packets);pending_count+=counts['pending_at_cutoff']
    print(f'audited {c.name}: {count} runs',flush=True)
expected=len(study['scenarios'])*len(study['seeds'])*len(study['policies'])
assert count==expected
checks=[]
selected=[x for x in study['scenarios'] if x['name'] in ('normal','congestion','markov_link','mixed_sizes','nodes_96','bucket_slots_2','dt_0.025','total_036_nodes_8')]
if not selected:selected=study['scenarios'][:2]
for config in selected:
    c=Config(**config);seed=study['seeds'][0]
    for policy in ('fud','pf'):
        existing=json.loads((root/'runs'/c.name/str(seed)/policy/'metrics.json').read_text())
        assert existing==simulate(c,generate(c,seed),policy,seed),(c.name,policy)
        checks.append({'scenario':c.name,'policy':policy,'seed':seed})
report={'status':'PASS','metric_version':2,'audited_runs':count,'audited_packets':packet_count,
    'common_trace_groups':trace_groups,'pending_at_terminal_cutoff':pending_count,
    'source_hash':code_hash(),'independent_checks':['raw packet identities and final outcomes','class-specific denominators and latency','token bucket and server intervals','main/tail resource overlap','AoI and QoS interval integration','common potential channel results'],
    'deterministic_replays':checks,'hardware_measurements':0}
(root/'audit.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
