import argparse
from dataclasses import asdict
import json
from pathlib import Path
from .model import Config,study_scenarios
from .scheduler import POLICIES


def main():
    parser=argparse.ArgumentParser(description='Reproducible gateway scheduling simulation')
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('make-config');p.add_argument('--out',default='configs/study.json')
    p=sub.add_parser('run');p.add_argument('--config',default='configs/study.json');p.add_argument('--out',default='output/study');p.add_argument('--workers',type=int,default=4)
    p=sub.add_parser('analyze');p.add_argument('--out',default='output/study')
    args=parser.parse_args()
    if args.command=='make-config':
        path=Path(args.out);path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps({'seeds':list(range(100,120)),'policies':list(POLICIES),'scenarios':[asdict(c) for c in study_scenarios(Config())]},indent=2))
        print(path)
    elif args.command=='run':
        from .runner import run_study
        run_study(json.loads(Path(args.config).read_text()),args.out,args.workers)
    else:
        from .analysis import analyze
        print(analyze(args.out))


if __name__=='__main__':main()
