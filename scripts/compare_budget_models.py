"""Compare service-budget model versions."""
import csv
from pathlib import Path

root=Path(__file__).resolve().parents[1]
old=root/'output/archive/strict_bucket_v1/study'
new=root/'output/study'
def read(path):
    return {(r['scenario'],r['policy'],r['metric']):float(r['mean']) for r in csv.DictReader((path/'summary.csv').open()) if r['mean']}
a=read(old);b=read(new)
lines=['# 预算桶模型敏感性（开发审查）',
'\n两个模型均完整运行15场景×20seed×13方法。旧模型B=max_packet_service，最终模型所有场景固定B=4。算法公式、权重、外生到达和信道生成过程未改；每个版本保留独立 config/trace hash 和统计表。',
'\n| 场景 | 方法 | 旧利用率 | 新利用率 | 旧AoI(s) | 新AoI(s) | 旧事件miss | 新事件miss |',
'|---|---|---:|---:|---:|---:|---:|---:|']
for s in ['normal','congestion','bursty','mixed_sizes','budget_40','budget_100']:
 for p in ['fifo','aoi_gain','fud']:
  vals=[a[s,p,'utilization'],b[s,p,'utilization'],a[s,p,'mean_aoi_s'],b[s,p,'mean_aoi_s'],a[s,p,'event_miss'],b[s,p,'event_miss']]
  lines.append('| '+s+' | '+p+' | '+' | '.join(f'{v:.5f}' for v in vals)+' |')
lines+=['\n单slot桶在duty=0.8下损失分数信用，饱和可达利用率约0.5；固定B=4后回归测试确认0.8可达。利用率受流量不足影响时仍低于预算。旧 mixed_sizes 同时改变包长与桶容量；最终模型固定桶容量后比较包长变化。',
'\n该表描述预算桶容量对利用率和服务指标的影响。最终模型采用固定容量与饱和预算可达性检查，各方法的完整表现与配对区间按版本保存。历史模型位于 output/archive/strict_bucket_v1/。']
(root/'docs/validation/budget_model_comparison.md').write_text('\n'.join(lines))
print('docs/validation/budget_model_comparison.md')
