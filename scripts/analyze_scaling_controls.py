"""Separate source update sparsity from the receiver AoI in both scale designs."""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from netadapt.model import Config,flows_for
from netadapt.traffic import generate
from netadapt.analysis import csv_write,interval

root=Path('output/study_refined_v1');rows=[]
cases=[]
for family,folder in [('A',root),('B',root/'scaling')]:
    study=json.loads((folder/'manifest.json').read_text())['study']
    selected=study['scenarios'] if family=='B' else [c for c in study['scenarios'] if c['name'] in ('nodes_8','normal','nodes_48','nodes_96')]
    for config in selected:cases.append((family,folder,study,Config(**config)))
for family,folder,study,c in cases:
    fs=flows_for(c);state=np.array([f.kind!='event' for f in fs])
    for seed in study['seeds']:
        trace=generate(c,seed);latest=np.zeros(c.nodes,dtype=int);area=np.zeros(c.nodes)
        for t,batch in enumerate(trace.arrivals):
            for p in batch:latest[p.flow]=t
            if t>=c.warmup:area+=t-latest
        ideal=float(np.mean(area[state])/(c.slots-c.warmup)*c.dt)
        for policy in study['policies']:
            r=json.loads((folder/'runs'/c.name/str(seed)/policy/'metrics.json').read_text())
            excess=r['mean_aoi_s']-ideal
            assert excess>=-1e-10
            rows.append(dict(family=family,nodes=c.nodes,scenario=c.name,policy=policy,seed=seed,
                source_aoi_s=ideal,receiver_aoi_s=r['mean_aoi_s'],excess_aoi_s=excess,
                config_hash=r['config_hash'],trace_hash=r['trace_hash']))
summary=[]
for family,folder,study,c in cases:
    for policy in study['policies']:
        for metric in ['source_aoi_s','receiver_aoi_s','excess_aoi_s']:
            values=[r[metric] for r in rows if r['family']==family and r['nodes']==c.nodes and r['policy']==policy]
            mean,lo,hi=interval(values)
            summary.append(dict(family=family,nodes=c.nodes,scenario=c.name,policy=policy,metric=metric,mean=mean,ci_low=lo,ci_high=hi,n=len(values)))
csv_write(root/'scaling_controls.csv',rows);csv_write(root/'scaling_controls_summary.csv',summary)
(root/'scaling_controls.json').write_text(json.dumps({'analysis':'instantaneous lossless source freshness baseline',
    'formula':'excess_aoi = receiver_aoi - source_latest_generation_aoi; source update occurs at generation slot',
    'window':'[warmup,slots), initial source and receiver timestamps zero','rows':len(rows),
    'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n')
print('scaling controls',len(rows))
