"""Independent artifact checks and deterministic rerun of five representative runs."""
from collections import defaultdict
from dataclasses import asdict
import ast
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from netadapt.model import Config
from netadapt.runner import code_hash
from netadapt.traffic import generate
from netadapt.simulation import simulate

root=Path(sys.argv[1] if len(sys.argv)>1 else 'output/study')
manifest=json.loads((root/'manifest.json').read_text())
study=manifest['study'];policies=set(study['policies'])
current_source=code_hash()
source_verification='exact_source'
if manifest['code_hash']!=current_source:
    project=Path(__file__).resolve().parents[1]
    revision=json.loads((project/'docs/validation/documentation_revision.json').read_text())
    digest=hashlib.sha256()
    for source in sorted((project/'src').rglob('*.py')):
        tree=ast.parse(source.read_text())
        if tree.body and isinstance(tree.body[0],ast.Expr) and isinstance(tree.body[0].value,ast.Constant) and isinstance(tree.body[0].value.value,str):
            tree.body.pop(0)
        if source.name=='analysis.py':
            tree.body=[node for node in tree.body if not isinstance(node,ast.FunctionDef) or node.name!='report']
        digest.update(str(source.relative_to(project)).encode())
        digest.update(ast.dump(tree,include_attributes=False).encode())
    assert revision['experiment_source_hash']==manifest['code_hash']
    assert revision['current_source_hash']==current_source
    assert revision['computation_ast_sha256']==digest.hexdigest()
    source_verification='documented_presentation_revision'
groups=defaultdict(list);count=0
for p in (root/'runs').glob('*/*/*/metrics.json'):
    r=json.loads(p.read_text());count+=1
    c=Config(**json.loads((p.parent/'config.json').read_text()))
    assert c.digest()==r['config_hash']
    assert r['reserved_slots']<=c.slots*c.duty+1e-6
    assert r['max_budget_excess']<1e-6
    assert r['generated']==sum(r['cohort_status_counts'].values())
    assert r['generated']==sum(x['generated'] for x in r['per_flow'])
    assert r['delivered']==sum(x['delivered'] for x in r['per_flow'])
    assert not any(x['status_counts'].get(s,0) for x in r['per_flow'] if x['kind']=='event' for s in ['queued','inflight'])
    groups[r['scenario'],r['seed']].append(r)
expected=len(study['scenarios'])*len(study['seeds'])*len(policies)
assert count==expected,(count,expected)
for rows in groups.values():
    assert {r['policy'] for r in rows}==policies
    assert len({r['trace_hash'] for r in rows})==1
checks=[]
for name in ['normal','congestion','markov_link','mixed_sizes','nodes_96']:
    c=Config(**next(c for c in study['scenarios'] if c['name']==name))
    seed=study['seeds'][0]
    existing=json.loads((root/'runs'/name/str(seed)/'fud/metrics.json').read_text())
    replay=simulate(c,generate(c,seed),'fud',seed)
    assert existing==replay,f'replay mismatch: {name}'
    checks.append(name)
report={'status':'PASS','audited_runs':count,'common_trace_groups':len(groups),
        'deterministic_replays':checks,'source_hash_verified':True,'cohort_event_censoring':0,
        'hardware_measurements':0,'source_verification':source_verification,
        'experiment_source_hash':manifest['code_hash'],'current_source_hash':current_source}
(root/'audit.json').write_text(json.dumps(report,indent=2));print(report)
