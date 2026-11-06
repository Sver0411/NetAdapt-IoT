"""Boundary-ordered event loop, immutable traces, packet conservation and audits."""
from dataclasses import asdict
import gzip
import heapq
import json
from pathlib import Path
import numpy as np
from .model import Config, flows_for
from .queues import Queues
from .scheduler import Scheduler
from .metrics import summarize


def simulate(c:Config,trace,policy,seed,out=None):
    flows=flows_for(c);n=len(flows)
    queues=Queues(flows,c.event_buffer);scheduler=Scheduler(policy,flows)
    last=np.zeros(n,dtype=int);prob=np.full(n,0.8);debt=np.zeros(n);throughput=np.ones(n)
    targets=np.array([0.5*c.duty*0.8*f.weight/(sum(x.weight for x in flows)*f.service) for f in flows])
    pending=[];records={};decisions=[]
    tokens=0.;cap=c.bucket_slots;busy_until=0
    aoi_sum=np.zeros(n);queue_sum=0.;observed_bytes=0;occupied=0
    observation_slots=c.slots-c.warmup
    attempts=0;wire_bytes=0;total_reserved=0;max_budget_excess=0.
    def finish(p,status,t):
        record=records[p.id];record['status']=status;record['finished']=t
    for t in range(c.slots+1):
        received=np.zeros(n)
        while pending and pending[0][0]<=t:
            at,_,p,ok=heapq.heappop(pending);i=p.flow;f=flows[i]
            prob[i]=0.9*prob[i]+0.1*int(ok)
            if ok:
                fresh=p.generated>last[i]
                timely=f.deadline is None or at<=p.generated+f.deadline
                # Event timestamps also track the AoI proxy used by the pure-AoI
                # comparator. Only state flows enter reported AoI metrics.
                last[i]=max(last[i],p.generated)
                if timely and (f.kind=='event' or fresh):received[i]+=1
                finish(p,'delivered' if timely else 'late',at)
                records[p.id]['received']=at
                if c.warmup<=at<c.slots:observed_bytes+=p.size
            else:finish(p,'link_loss',at)
        if t==c.slots:break
        for p in trace.arrivals[t]:
            records[p.id]={**asdict(p),'status':'queued','started':None,'received':None,'finished':None}
            for old,status in queues.admit(p):finish(old,status,t)
        for p,status in queues.expire(t,c.delay):finish(p,status,t)
        backlogged=np.array([bool(q) for q in queues.items])
        debt=np.minimum(50,np.maximum(0,debt+targets*backlogged-received))
        throughput=0.99*throughput+0.01*received*np.array([f.size for f in flows])
        tokens=min(cap,tokens+c.duty)
        if t>=busy_until:
            p=scheduler.choose(t,queues,last,prob,debt,throughput,c.delay,tokens)
            if p is not None:
                f=flows[p.flow];s=f.service
                assert queues.items[p.flow].popleft()==p
                tokens-=s;attempts+=1;wire_bytes+=p.size+c.header;total_reserved+=s
                assert tokens>=-1e-8
                max_budget_excess=max(max_budget_excess,total_reserved-(t+1)*c.duty)
                assert max_budget_excess<1e-6
                busy_until=t+s
                records[p.id].update(status='inflight',started=t)
                heapq.heappush(pending,(t+s+c.delay,p.id,p,bool(trace.success[t,p.flow])))
                decisions.append({'t':t,'flow':p.flow,'packet':p.id,'service':s})
        if t>=c.warmup:
            aoi_sum+=t-last
            queue_sum+=sum(len(q) for q in queues.items)
            occupied+=int(t<busy_until)
    # No tail draining: cohort guard allows all its feasible event deliveries to mature.
    result=summarize(c,flows,records,aoi_sum/observation_slots*c.dt)
    result.update(scenario=c.name,policy=policy,seed=seed,config_hash=c.digest(),trace_hash=trace.digest,
        mean_queue=queue_sum/observation_slots,utilization=occupied/observation_slots,
        observation_goodput_bps=8*observed_bytes/(observation_slots*c.dt),attempts=attempts,
        wire_bytes=wire_bytes,payload_attempt_bytes=wire_bytes-attempts*c.header,
        reserved_slots=total_reserved,max_budget_excess=max_budget_excess)
    assert sum(result['status_counts'].values())==len(records)
    assert all(b['t']>=a['t']+a['service'] for a,b in zip(decisions,decisions[1:]))
    if out:
        out=Path(out);out.mkdir(parents=True,exist_ok=False)
        (out/'config.json').write_text(json.dumps(asdict(c),indent=2))
        (out/'metrics.json').write_text(json.dumps(result,indent=2,allow_nan=False))
        with gzip.open(out/'packets.jsonl.gz','wt') as f:
            for r in records.values():f.write(json.dumps(r)+'\n')
        with gzip.open(out/'decisions.jsonl.gz','wt') as f:
            for r in decisions:f.write(json.dumps(r)+'\n')
    return result
