from dataclasses import replace
import numpy as np
import pytest
from netadapt.model import Config,flows_for
from netadapt.traffic import generate,Trace,Packet
from netadapt.simulation import simulate
from netadapt.scheduler import POLICIES,Scheduler
from netadapt.queues import Queues
from netadapt.metrics import jain


def test_hand_computed_deadline_and_aoi():
    c=Config(nodes=2,slots=30,warmup=0,duty=1,delay=1,success=1,rate=0)
    arrivals=[[] for _ in range(c.slots)]
    arrivals[1]=[Packet(0,0,1,64),Packet(1,1,1,64)]
    trace=Trace(arrivals,np.ones((c.slots,2),dtype=bool),'manual')
    r=simulate(c,trace,'fifo',100)
    assert r['event_miss']==0
    # Event at t1 -> t3; state starts t2 -> t4. Initial timestamp=0.
    expected=(sum(range(4))+sum(t-1 for t in range(4,30)))/30*.1
    assert r['mean_aoi_s']==pytest.approx(expected)
    assert r['latency_s']==pytest.approx(.25)
    assert r['status_counts']=={'delivered':2}


@pytest.mark.parametrize('policy',POLICIES)
def test_policy_conservation_resources_determinism(policy):
    c=Config(nodes=9,slots=180,warmup=20,rate=.25,duty=.6,mixed_sizes=True,link='markov')
    trace=generate(c,101)
    a=simulate(c,trace,policy,101);b=simulate(c,trace,policy,101)
    assert a==b
    assert sum(a['status_counts'].values())==sum(map(len,trace.arrivals))
    assert sum(a['cohort_status_counts'].values())==a['generated']
    assert 0<=a['event_miss']<=1
    assert 0<=a['pdr']<=1 and 0<=a['jain_pdr']<=1+1e-9
    assert a['max_budget_excess']<1e-6
    assert len(a['per_flow'])==c.nodes


def test_common_random_conditions():
    c=Config(slots=100,warmup=10)
    a=generate(c,100);b=generate(c,100);d=generate(c,101)
    assert a.digest==b.digest and a.arrivals==b.arrivals
    assert np.array_equal(a.success,b.success)
    assert a.digest!=d.digest
    changed=generate(replace(c,success=.2),100)
    assert a.arrivals==changed.arrivals


def test_latest_only_and_event_overflow():
    c=Config(nodes=2,slots=50,warmup=0,event_buffer=1)
    q=Queues(flows_for(c),1)
    assert q.admit(Packet(0,1,1,64))==[]
    assert q.admit(Packet(1,1,2,64))==[(Packet(0,1,1,64),'replaced')]
    q.admit(Packet(2,0,2,64))
    assert q.admit(Packet(3,0,2,64))[0][1]=='overflow'
    assert q.expire(8,1)[0][1]=='expired'


def test_no_delivery_is_not_perfect_fairness():
    c=Config(slots=200,warmup=20,success=0,rate=.1)
    r=simulate(c,generate(c,102),'fud',102)
    assert r['event_miss']==1 and r['pdr']==0
    assert r['jain_pdr']==0 and jain([0,0])==0


def test_rr_wrr_and_edf_order():
    c=Config(nodes=3,slots=50,warmup=0)
    fs=flows_for(c);q=Queues(fs,100)
    for i in range(3):q.admit(Packet(i,i,1,64))
    inputs=(2,q,np.zeros(3),np.ones(3),np.zeros(3),np.ones(3),1,100)
    rr=Scheduler('rr',fs);assert [rr.choose(*inputs).flow for _ in range(6)]==[0,1,2,0,1,2]
    wr=Scheduler('wrr',fs);assert [wr.choose(*inputs).flow for _ in range(8)]==[0,0,0,0,1,1,1,2]
    assert Scheduler('edf',fs).choose(*inputs).flow==0


def test_empty_arrivals_have_undefined_pdr():
    c=Config(slots=100,warmup=10,rate=0)
    r=simulate(c,generate(c,1),'fud',1)
    assert r['pdr'] is None and r['event_miss'] is None
    assert r['latency_s'] is None


def test_event_timestamp_updates_for_aoi_comparator(monkeypatch):
    c=Config(nodes=2,slots=30,warmup=0,duty=1,rate=0,delay=1)
    arrivals=[[] for _ in range(c.slots)]
    arrivals[1]=[Packet(0,0,1,64)]
    seen=[]
    original=Scheduler.choose
    def observe(self,t,queues,last,*args):
        if t==3:seen.append(int(last[0]))
        return original(self,t,queues,last,*args)
    monkeypatch.setattr(Scheduler,'choose',observe)
    r=simulate(c,Trace(arrivals,np.ones((c.slots,2),dtype=bool),'manual'),'aoi_gain',1)
    assert seen==[1]
    assert r['event_miss']==0


def test_deadline_inclusive_boundary():
    c=Config(nodes=1,slots=30,warmup=0,duty=1,rate=0,delay=5)
    arrivals=[[] for _ in range(c.slots)];arrivals[1]=[Packet(0,0,1,64)]
    r=simulate(c,Trace(arrivals,np.ones((c.slots,1),dtype=bool),'manual'),'edf',1)
    assert r['event_miss']==0  # 1+1+5 == 1+deadline(6)
    assert r['latency_s']==pytest.approx(.6)


def test_saturated_service_reaches_fractional_budget():
    c=Config(nodes=1,slots=1000,warmup=100,rate=3,duty=.8,success=1)
    r=simulate(c,generate(c,103),'fifo',103)
    # A one-slot cap would quantize this to 0.5. Fractional credit must carry.
    assert r['reserved_slots']==800
    assert r['utilization']==pytest.approx(.8,abs=.002)


@pytest.mark.parametrize('kwargs',[{'duty':0},{'nodes':0},{'success':1.1},{'warmup':4000},{'delay':-1},{'link':'fake'}])
def test_invalid_config(kwargs):
    with pytest.raises(ValueError):Config(**kwargs)
