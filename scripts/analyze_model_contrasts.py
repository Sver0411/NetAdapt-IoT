"""Within-policy, paired-seed parameter effects relative to each group baseline."""
import csv
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from netadapt.analysis import csv_write,interval

root=Path('output/study_refined_v1');metrics=['mean_aoi_s','event_deadline_miss','pdr','goodput_bps','jain_service_share','jain_weighted_service_share']
for folder,groups in [(root/'sensitivity',{
    'bucket_slots':'bucket_slots_4','duty':'duty_0.8','bitrate':'bitrate_6400','success':'success_0.95',
    'good_to_bad':'good_to_bad_0.025','bad_to_good':'bad_to_good_0.1','rate':'rate_0.015','dt':'dt_0.1'}),
    (root/'bucket_load',{'congested_bucket':'congested_bucket_4'})]:
    with (folder/'all_runs.csv').open() as f:rows=list(csv.DictReader(f))
    index={(r['scenario'],r['policy'],r['seed']):r for r in rows};result=[]
    for factor,baseline in groups.items():
        scenarios=sorted({r['scenario'] for r in rows if r['scenario'].startswith(factor+'_')})
        for scenario in scenarios:
            if scenario==baseline:continue
            for policy in sorted({r['policy'] for r in rows}):
                seeds=sorted({r['seed'] for r in rows if r['scenario']==scenario and r['policy']==policy})
                for metric in metrics:
                    vals=[float(index[scenario,policy,s][metric])-float(index[baseline,policy,s][metric]) for s in seeds]
                    mean,lo,hi=interval(vals)
                    result.append(dict(factor=factor,scenario=scenario,baseline_scenario=baseline,policy=policy,metric=metric,
                        n=len(vals),delta_level_minus_reference=mean,ci_low=lo,ci_high=hi))
    csv_write(folder/'model_contrasts.csv',result)
    print(folder,len(result))
