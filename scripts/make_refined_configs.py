"""Frozen main, fixed-total scale, and one-factor sensitivity matrices."""
from dataclasses import asdict,replace
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from netadapt.model import Config,study_scenarios
from netadapt.scheduler import POLICIES

out=Path('configs/refined_v1');out.mkdir(parents=True,exist_ok=True)
base=Config()
main=study_scenarios(base)
scale=[replace(base,name=f'total_036_nodes_{n}',nodes=n,total_rate=.36) for n in [8,24,48,96]]
sensitivity=[]
# All parameters except the named factor match the baseline. Each group has
# its own baseline, allowing self-contained contrasts within the group.
for key,values in [('bucket_slots',[2,4,8,16]),('duty',[.4,.8,1.]),
                   ('bitrate',[3200,6400,12800]),('success',[.55,.8,.95]),
                   ('good_to_bad',[.01,.025,.1]),('bad_to_good',[.05,.1,.25]),
                   ('rate',[.015,.04,.1])]:
    for value in values:
        change={key:value}
        if key in ('good_to_bad','bad_to_good'):change['link']='markov'
        sensitivity.append(replace(base,name=f'{key}_{value}',**change))
# Discretization study: hold physical rates, durations, deadlines, bucket time,
# and feedback delay fixed. Derived slot counts preserve their physical units.
for dt in [.025,.05,.1]:
    k=round(.1/dt)
    sensitivity.append(replace(base,name=f'dt_{dt}',dt=dt,slots=4000*k,warmup=500*k,
        rate=.015/k,delay=k,event_deadline=6*k,status_tau=12*k,telemetry_tau=30*k,bucket_slots=4*k))
for name,scenarios in [('main',main),('scaling',scale),('sensitivity',sensitivity)]:
    study={'metric_version':2,'family':name,'seeds':list(range(100,120)),
           'policies':list(POLICIES),'scenarios':[asdict(c) for c in scenarios]}
    (out/f'{name}.json').write_text(json.dumps(study,indent=2)+'\n')
pilot=[replace(base,name='tail_check',slots=200,warmup=20,rate=.1),
       replace(scale[0],slots=200,warmup=20),
       replace(base,name='markov_check',slots=200,warmup=20,link='markov',rate=.1)]
(out/'pilot.json').write_text(json.dumps({'metric_version':2,'family':'pilot','seeds':[0,1],
    'policies':list(POLICIES),'scenarios':[asdict(c) for c in pilot]},indent=2)+'\n')
print({name:len(scenarios)*20*len(POLICIES) for name,scenarios in [('main',main),('scaling',scale),('sensitivity',sensitivity)]})

# Conditional capacity study: same four levels under a fixed high-load background.
bucket_load=[replace(base,name=f'congested_bucket_{k}',rate=.1,bucket_slots=k) for k in [2,4,8,16]]
(out/'bucket_load.json').write_text(json.dumps({'metric_version':2,'family':'bucket_load','design':'Conditional capacity sensitivity at fixed congestion rate 0.10; identical FUD coefficients','seeds':list(range(100,120)),'policies':list(POLICIES),'scenarios':[asdict(c) for c in bucket_load]},indent=2)+'\n')
