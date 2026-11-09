"""Execute the frozen v2 matrices, then analyze and independently audit each."""
import json
from pathlib import Path
import subprocess
import sys
import zipfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from netadapt.runner import run_study
from netadapt.analysis import analyze


def main():
    root=Path('output/study_refined_v1');root.mkdir(parents=True,exist_ok=True)
    matrices=[('main',root),('scaling',root/'scaling'),('sensitivity',root/'sensitivity'),('bucket_load',root/'bucket_load')]
    with zipfile.ZipFile(root/'source_snapshot.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for folder in ['src','tests','scripts','configs','hardware']:
            for p in sorted(Path(folder).rglob('*')):
                if p.is_file() and not any(part in ('.pio','__pycache__') for part in p.parts):archive.write(p)
    for name,out in matrices:
        print(f'RUN {name}',flush=True)
        run_study(json.loads(Path(f'configs/refined_v1/{name}.json').read_text()),out,workers=6)
    for name,out in matrices:
        print(f'ANALYZE {name}',flush=True);print(analyze(out),flush=True)
    for name,out in matrices:
        print(f'AUDIT {name}',flush=True)
        subprocess.run([sys.executable,'scripts/audit_refined.py',str(out)],check=True)


if __name__=='__main__':main()
