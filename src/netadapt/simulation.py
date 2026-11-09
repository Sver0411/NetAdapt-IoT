"""Ordered main and tail windows with exclusive packet outcomes and resource ledgers."""
from dataclasses import asdict
import gzip
import heapq
import json
from pathlib import Path
import numpy as np
from .model import Config, flows_for
from .queues import Queues
from .scheduler import Scheduler,pf_update
from .metrics import summarize,classified,FINAL_STATES


def simulate(c:Config,trace,policy,seed,out=None):
    flows=flows_for(c);n=len(flows)
    queues=Queues(flows,c.event_buffer);scheduler=Scheduler(policy,flows)
    last=np.zeros(n,dtype=int);prob=np.full(n,0.8);debt=np.zeros(n);throughput=np.ones(n)
    targets=np.array([0.5*c.duty*0.8*f.weight/(sum(x.weight for x in flows)*f.service) for f in flows])
    pending=[];records={};decisions=[]
    tokens=0.;cap=c.bucket_slots;busy_until=0
    aoi_sum=np.zeros(n);qos_slots=np.zeros(n,dtype=int);queue_sum=0.;observed_bytes=0;occupied=0
    service_slots=np.zeros(n,dtype=int);tail_service=np.zeros(n,dtype=int)
    observation_slots=c.slots-c.warmup
    attempts=0;wire_bytes=0;total_reserved=0;main_reserved=0;tail_attempts=0;max_budget_excess=0.
    def finish(p,status,t):
        record=records[p.id]
        assert record['status'] in ('queued','inflight'),(p.id,record['status'],status)
        record['status']=status;record['finished']=t
    for t in range(c.end+1):
        if t==c.slots:
            for r in records.values():r['status_at_main_cutoff']=r['status']
        received=np.zeros(n);ack_bytes=np.zeros(n)
        while pending and pending[0][0]<=t:
            at,_,p,ok=heapq.heappop(pending);i=p.flow;f=flows[i]
            prob[i]=0.9*prob[i]+0.1*int(ok)
            if ok:
                fresh=p.generated>last[i]
                timely=f.deadline is None or at<=p.generated+f.deadline
                last[i]=max(last[i],p.generated)
                if timely and (f.kind=='event' or fresh):received[i]+=1
                ack_bytes[i]+=p.size
                finish(p,'delivered' if timely else 'late',at)
                records[p.id]['received']=at
                if c.warmup<=at<c.slots:observed_bytes+=p.size
            else:finish(p,'link_loss',at)
        if t==c.slots:
            # Legacy fields retain the former protected generation cohort and
            # outcomes available at the original stopping boundary.
            legacy=summarize(c,flows,records,aoi_sum/observation_slots*c.dt)
        if t==c.end:break
        if t<c.slots:
            for p in trace.arrivals[t]:
                records[p.id]={**asdict(p),'status':'queued','started':None,'received':None,'finished':None}
                for old,status in queues.admit(p):finish(old,status,t)
        for p,status in queues.expire(t,c.delay):finish(p,status,t)
        backlogged=np.array([bool(q) for q in queues.items])
        debt=np.minimum(50,np.maximum(0,debt+targets*backlogged-received))
        throughput=pf_update(throughput,ack_bytes)
        tokens=min(cap,tokens+c.duty)
        if t>=busy_until:
            p=scheduler.choose(t,queues,last,prob,debt,throughput,c.delay,tokens)
            if p is not None:
                f=flows[p.flow];s=f.service
                assert queues.items[p.flow].popleft()==p
                tokens-=s;attempts+=1;wire_bytes+=p.size+c.header;total_reserved+=s
                if t<c.slots:main_reserved+=s
                else:tail_attempts+=1
                assert tokens>=-1e-8
                max_budget_excess=max(max_budget_excess,total_reserved-(t+1)*c.duty)
                assert max_budget_excess<1e-6
                busy_until=t+s
                records[p.id].update(status='inflight',started=t)
                heapq.heappush(pending,(t+s+c.delay,p.id,p,bool(trace.success[t,p.flow])))
                decisions.append({'t':t,'flow':p.flow,'packet':p.id,'service':s})
                service_slots[p.flow]+=max(0,min(t+s,c.slots)-max(t,c.warmup))
                tail_service[p.flow]+=max(0,min(t+s,c.end)-max(t,c.slots))
        if c.warmup<=t<c.slots:
            age=t-last
            aoi_sum+=age
            qos_slots+=age<=np.array([f.tau for f in flows])
            queue_sum+=sum(len(q) for q in queues.items)
            occupied+=int(t<busy_until)
    for r in records.values():
        if r['status'] in ('queued','inflight'):
            r['pending_kind']=r['status'];r['status']='pending_at_cutoff'
        assert r['status'] in FINAL_STATES
    result={**legacy,**classified(c,flows,records,legacy,service_slots,tail_service,qos_slots)}
    result.update(scenario=c.name,policy=policy,seed=seed,config_hash=c.digest(),trace_hash=trace.digest,
        main_window=[c.warmup,c.slots],tail_window=[c.slots,c.end],
        mean_queue=queue_sum/observation_slots,utilization=occupied/observation_slots,
        observation_goodput_bps=8*observed_bytes/(observation_slots*c.dt),attempts=attempts,
        tail_attempts=tail_attempts,wire_bytes=wire_bytes,payload_attempt_bytes=wire_bytes-attempts*c.header,
        reserved_slots=main_reserved,tail_reserved_slots=total_reserved-main_reserved,
        max_budget_excess=max_budget_excess)
    assert sum(result['status_counts'].values())==len(records)
    assert sum(service_slots)==occupied
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
