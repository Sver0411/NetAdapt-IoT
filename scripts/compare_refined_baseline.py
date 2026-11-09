"""Compare preserved v1 semantics and unchanged FUD main-window decisions."""
import csv
import gzip
import hashlib
import json
from pathlib import Path

old=Path('output/study');new=Path('output/study_refined_v1')
scenarios=['normal','congestion','markov_link','mixed_sizes','nodes_96']
fields=['mean_aoi_s','normalized_aoi','event_miss','pdr','jain_pdr','jain_delivery','latency_s','p95_latency_s','cohort_goodput_bps','utilization','mean_queue']
checks=[]
for name in scenarios:
    for seed in range(100,120):
        op=old/'runs'/name/str(seed)/'fud';np=new/'runs'/name/str(seed)/'fud'
        a=json.loads((op/'metrics.json').read_text());b=json.loads((np/'metrics.json').read_text())
        assert all(a[k]==b[k] for k in fields),(name,seed)
        with gzip.open(op/'decisions.jsonl.gz','rt') as f:od=[json.loads(x) for x in f]
        with gzip.open(np/'decisions.jsonl.gz','rt') as f:nd=[json.loads(x) for x in f]
        T=json.loads((np/'config.json').read_text())['slots']
        assert od==[d for d in nd if d['t']<T],(name,seed,'decisions')
        checks.append({'scenario':name,'seed':seed,'legacy_fields_equal':True,'main_decisions_equal':True})
inventory=json.loads(Path('docs/validation/refined_v1/baseline_inventory.json').read_text())
for name,digest in inventory['files'].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest,name
report={'status':'PASS','historical_files_unchanged':len(inventory['files']),
        'fud_main_replays_compared':len(checks),'legacy_fields':fields,'checks':checks}
Path('docs/validation/refined_v1/baseline_comparison.json').write_text(json.dumps(report,indent=2)+'\n')
print({k:v for k,v in report.items() if k not in ('checks','legacy_fields')})
