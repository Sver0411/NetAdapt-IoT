"""Auditable batch execution; failed runs are retained and cause a nonzero exit."""
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path
import subprocess
import time
from .model import Config
from .scheduler import POLICIES
from .simulation import simulate
from .traffic import generate
from .metrics import METRIC_VERSION


def code_hash():
    root=Path(__file__).resolve().parents[2];h=hashlib.sha256()
    for p in sorted((root/'src').rglob('*.py')):
        h.update(str(p.relative_to(root)).encode());h.update(p.read_bytes())
    return h.hexdigest()


def work(args):
    config,seed,policies,root=args;c=Config(**config)
    trace=generate(c,seed);start=time.monotonic();rows=[]
    for policy in policies:
        path=Path(root)/'runs'/c.name/str(seed)/policy
        if path.exists():
            r=json.loads((path/'metrics.json').read_text())
            if r['trace_hash']!=trace.digest or r['config_hash']!=c.digest() or r['metric_version']!=METRIC_VERSION:
                raise ValueError(f'resume hash mismatch: {path}')
        else:r=simulate(c,trace,policy,seed,path)
        rows.append(r)
    return rows,time.monotonic()-start


def run_study(study,output,workers=4):
    root=Path(output);root.mkdir(parents=True,exist_ok=True)
    if workers<1:raise ValueError('workers must be positive')
    policies=study.get('policies',list(POLICIES))
    if not policies or any(p not in POLICIES for p in policies):raise ValueError('invalid policies')
    configs=[asdict(Config(**x)) for x in study['scenarios']]
    names=[c['name'] for c in configs]
    if len(set(names))!=len(names):raise ValueError('scenario names must be unique')
    seeds=study['seeds']
    if not seeds or len(set(seeds))!=len(seeds):raise ValueError('unique nonempty seeds required')
    manifest=dict(study={**study,'scenarios':configs},code_hash=code_hash(),metric_version=METRIC_VERSION,
        python=platform.python_version(),platform=platform.platform(),
        dependencies={x:importlib.metadata.version(x) for x in ['numpy','matplotlib']},
        started_utc=datetime.now(timezone.utc).isoformat(),measurement_type='synthetic_slotted_simulation')
    if (root/'manifest.json').exists():
        old=json.loads((root/'manifest.json').read_text())
        if old['code_hash']!=manifest['code_hash'] or old['study']!=manifest['study']:
            raise ValueError('output belongs to different code/config; use another output directory')
    else:(root/'manifest.json').write_text(json.dumps(manifest,indent=2))
    tasks=[(c,s,policies,str(root)) for c in configs for s in seeds]
    failures=[];results=[];start=time.monotonic()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures={pool.submit(work,task):task for task in tasks}
        for k,future in enumerate(as_completed(futures),1):
            task=futures[future]
            try:
                rows,elapsed=future.result();results.extend(rows)
            except Exception as e:
                failures.append({'scenario':task[0]['name'],'seed':task[1],'error':repr(e)})
            if k%10==0 or k==len(tasks):print(f'{k}/{len(tasks)} scenario-seeds; {len(results)} runs; {time.monotonic()-start:.1f}s',flush=True)
    (root/'failures.json').write_text(json.dumps(failures,indent=2))
    (root/'completion.json').write_text(json.dumps({'runs':len(results),'expected_runs':len(tasks)*len(policies),'seconds':time.monotonic()-start,'failures':len(failures)},indent=2))
    if failures:raise RuntimeError(f'{len(failures)} failed scenario-seeds; see failures.json')
    return results
