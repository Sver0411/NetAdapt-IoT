"""Hand-computed window, resource, class-load, and PF timing contracts."""
import ast
from collections import Counter
from dataclasses import replace
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np
import pytest
from netadapt.model import Config,flows_for
from netadapt.traffic import Trace,Packet,generate
from netadapt.simulation import simulate
from netadapt.scheduler import pf_update

ROOT=Path(__file__).parents[1]


def trace_for(c,arrivals):
    batches=[[] for _ in range(c.slots)]
    for p in arrivals:batches[p.generated].append(p)
    return Trace(batches,np.ones((c.end,c.nodes),dtype=bool),'manual')


def test_final_slot_event_is_delivered_in_tail(tmp_path):
    c=Config(nodes=2,slots=30,warmup=0,duty=1,rate=0)
    packets=[Packet(0,0,29,64),Packet(1,1,29,64)]
    r=simulate(c,trace_for(c,packets),'fifo',1,tmp_path/'run')
    assert r['observed_generated']==2 and r['generated']==0
    assert r['pending_at_main_cutoff']==2
    assert r['event_deadline_success']==1 and r['event_pending']==0
    assert r['status_counts']=={'delivered':2}
    assert r['tail_status_counts']=={'delivered':2}
    assert r['tail_delivered_bytes']==128
    assert r['mean_aoi_s']==pytest.approx(sum(range(30))/30*.1)
    assert sum(f['service_slots'] for f in r['per_flow'])==1
    assert sum(f['tail_service_slots'] for f in r['per_flow'])==1


def test_short_tail_censors_future_deadline_without_counting_loss():
    c=Config(nodes=1,slots=30,warmup=0,duty=1,rate=0,tail_slots=0)
    packets=[Packet(0,0,1,64),Packet(1,0,29,64)]
    r=simulate(c,trace_for(c,packets),'edf',1)
    assert r['event_observed_generated']==2
    assert r['event_resolved']==1 and r['event_pending']==1
    assert r['event_deadline_success']==1 and r['event_deadline_miss']==0
    assert r['status_counts']=={'delivered':1,'pending_at_cutoff':1}


def test_actual_service_is_clipped_at_warmup():
    c=Config(nodes=1,slots=30,warmup=2,duty=1,rate=0,bitrate=3200)
    p=Packet(0,0,1,64)
    r=simulate(c,trace_for(c,[p]),'edf',1)
    # Two tokens first become available at slot 1; service occupies [1,3).
    assert r['per_flow'][0]['service_slots']==1
    assert r['utilization']==pytest.approx(1/28)
    assert r['per_flow'][0]['service_share']==1


def test_replacement_and_loss_have_distinct_denominators():
    c=Config(nodes=2,slots=30,warmup=0,duty=.1,rate=0,success=0)
    packets=[Packet(0,1,1,64),Packet(1,1,2,64)]
    trace=trace_for(c,packets);trace.success[:]=False
    r=simulate(c,trace,'fifo',1)
    assert r['status_counts']=={'replaced':1,'link_loss':1}
    assert r['state_replacement_rate']==.5
    assert r['state_resolved_attempts']==1 and r['state_transmission_success']==0
    assert r['state_goodput_bps']==0 and r['jain_service_share']==.5


def test_event_overflow_and_expiration_are_exclusive():
    c=Config(nodes=1,slots=30,warmup=0,duty=.1,rate=0,event_buffer=1)
    packets=[Packet(0,0,1,64),Packet(1,0,1,64)]
    r=simulate(c,trace_for(c,packets),'edf',1)
    assert r['status_counts']=={'expired':1,'overflow':1}
    assert r['event_expiration_rate']==.5 and r['event_overflow_rate']==.5
    assert r['event_deadline_miss']==1 and r['event_late_ratio']==0


@pytest.mark.parametrize('n',[8,24,48,96])
def test_fixed_total_rate_preserves_all_class_shares(n):
    fs=flows_for(Config(nodes=n,total_rate=.36))
    rates=Counter()
    for f in fs:rates[f.kind]+=f.rate
    assert sum(rates.values())==pytest.approx(.36)
    assert list(rates.values())==pytest.approx([.12,.12,.12])


def test_markov_parameters_control_deterministic_states():
    c=Config(nodes=3,slots=30,warmup=0,link='markov',good_to_bad=1,bad_to_good=0,bad_success=0,success=1)
    assert not generate(c,1).success.any()
    assert generate(replace(c,good_to_bad=0),1).success.all()


def test_fixed_total_trace_has_identical_class_arrivals_across_scales():
    def classes(n):
        c=Config(nodes=n,total_rate=.36,slots=200,warmup=20)
        trace=generate(c,100)
        return [Counter(p.flow%3 for p in batch) for batch in trace.arrivals]
    assert classes(8)==classes(24)==classes(48)==classes(96)


def test_pf_sparse_ack_schedule_matches_replay_slot_updates():
    spec=importlib.util.spec_from_file_location('hw_pf',ROOT/'hardware/run.py')
    hw=importlib.util.module_from_spec(spec);spec.loader.exec_module(hw)
    # ACK at host slot 3.2 is applied at boundary 4; failures add no bytes.
    feedback=[(4,0,64),(4,1,64),(8,0,64)]
    sim=np.ones(2);replay=np.ones(2)
    for t in range(12):
        ack=np.zeros(2)
        for at,i,size in feedback:
            if at==t:ack[i]+=size
        sim=pf_update(sim,ack)
        replay=hw.pf_slot(replay,t,feedback)
        assert replay==pytest.approx(sim)
    assert pf_update(np.ones(2),np.zeros(2),slots=12)==pytest.approx(np.full(2,.99**12))
    assert sim[0]==pytest.approx(.99**12+.64*.99**7+.64*.99**3)


def test_fud_choose_formula_is_identical_to_published_baseline():
    expected=json.loads((ROOT/'docs/validation/refined_v1/fud_invariant.json').read_text())
    tree=ast.parse((ROOT/'src/netadapt/scheduler.py').read_text())
    choose=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='choose')
    digest=hashlib.sha256(ast.dump(choose,include_attributes=False).encode()).hexdigest()
    assert digest==expected['scheduler_choose_ast_sha256']


def test_dt_sensitivity_preserves_physical_parameters():
    study=json.loads((ROOT/'configs/refined_v1/sensitivity.json').read_text())
    cases=[Config(**c) for c in study['scenarios'] if c['name'].startswith('dt_')]
    for c in cases:
        assert c.slots*c.dt==400 and c.warmup*c.dt==50
        assert c.rate/c.dt==pytest.approx(.15)
        assert c.event_deadline*c.dt==pytest.approx(.6)
        assert c.bucket_slots*c.dt==pytest.approx(.4)
        assert c.service(64)*c.dt==pytest.approx(.1)
        assert c.delay*c.dt==pytest.approx(.1)
