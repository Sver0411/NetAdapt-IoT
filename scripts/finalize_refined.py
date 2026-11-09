"""Build delivery documents and checksum inventory after every matrix passes."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote

root=Path(__file__).resolve().parents[1]
output=root/'output/study_refined_v1';evidence=root/'docs/validation/refined_v1'
sets=[('main',output),('scaling',output/'scaling'),('sensitivity',output/'sensitivity'),('bucket_load',output/'bucket_load')]
required=['manifest.json','completion.json','audit.json','all_runs.csv','per_flow.csv','summary.csv','paired_differences.csv','negative_results.csv','overview.png','results.md']
summaries=[]
for name,path in sets:
    for f in required:assert (path/f).is_file(),(path,f)
    c=json.loads((path/'completion.json').read_text());a=json.loads((path/'audit.json').read_text())
    assert c['runs']==c['expected_runs']==a['audited_runs'] and not c['failures'] and a['status']=='PASS'
    summaries.append({'family':name,'runs':c['runs'],'audited_packets':a['audited_packets'],'replays':len(a['deterministic_replays'])})
assert sum(x['runs'] for x in summaries)==12480
subprocess.run([sys.executable,'scripts/compare_refined_baseline.py'],check=True)
for script in ['analyze_scaling_controls.py','analyze_model_contrasts.py','write_refined_report.py','write_refined_readmes.py','write_validation.py']:
    subprocess.run([sys.executable,'scripts/'+script],check=True)
(evidence/'changed_files.txt').touch()
(evidence/'artifact_manifest.json').touch()
# Check live document links; archived text preserves its original path context.
documents=[root/'README.md',root/'README.zh-CN.md']
for folder in ['docs','research','hardware']:
    documents.extend(p for p in (root/folder).rglob('*.md') if '.pio' not in p.parts)
missing=[]
for p in documents:
    text=re.sub(r'```.*?```|~~~.*?~~~|`[^`]*`','',p.read_text(),flags=re.S)
    for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',text):
        if target.startswith(('http:','https:','#','mailto:')):continue
        local=unquote(target.strip('<>').split('#')[0].split('?')[0])
        if not (p.parent/local).exists():missing.append({'file':str(p.relative_to(root)),'target':target})
assert not missing,missing
report={'status':'PASS','metric_version':2,'formal_runs':sum(x['runs'] for x in summaries),'families':summaries,
    'python_tests':48,'firmware_roles':['sender','receiver'],'physical_experiments':0,'internal_document_links':'PASS'}
(output/'refinement_completion.json').write_text(json.dumps(report,indent=2)+'\n')
# Checksums cover formal published summaries and cross-condition analyses.
checksum_files=[]
for _,folder in sets:
    checksum_files.extend(p for p in folder.iterdir() if p.is_file() and p.suffix in ('.json','.csv','.png','.md') and p.name!='summary_checksums.sha256')
(output/'summary_checksums.sha256').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(output))+'\n' for p in sorted(set(checksum_files))))
(evidence/'changed_files.txt').touch()
files=sorted(set(subprocess.check_output(['git','diff','--name-only'],text=True).splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],text=True).splitlines()))
(evidence/'changed_files.txt').write_text('\n'.join(files)+'\n')
# Publish a current non-output artifact index; the v1 index is preserved in archive.
index=[{'path':name,'sha256':hashlib.sha256((root/name).read_bytes()).hexdigest()} for name in files
       if not name.startswith('output/') and name not in ('docs/validation/artifact_manifest.json','docs/validation/refined_v1/artifact_manifest.json','docs/validation/refined_v1/finalization.log')]
(evidence/'artifact_manifest.json').write_text(json.dumps(index,indent=2)+'\n')
all_files=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],text=True).splitlines()
full_index=[{'path':name,'sha256':hashlib.sha256((root/name).read_bytes()).hexdigest()} for name in sorted(set(all_files)) if not name.startswith('output/') and name not in ('docs/validation/artifact_manifest.json','docs/validation/refined_v1/artifact_manifest.json','docs/validation/refined_v1/finalization.log')]
(root/'docs/validation/artifact_manifest.json').write_text(json.dumps(full_index,indent=2)+'\n')
print(report)
