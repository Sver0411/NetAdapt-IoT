"""Generate current validation notes from refined experiment evidence."""
import json,re
from pathlib import Path

root=Path(__file__).resolve().parents[1];out=root/'output/study_refined_v1'
sets=[('主实验',out),('固定总负载',out/'scaling'),('模型敏感性',out/'sensitivity'),('高负载桶容量',out/'bucket_load')]
count=int(re.findall(r'(\d+) passed',(root/'docs/validation/refined_v1/pytest.log').read_text())[-1])
assert count==48
assert '2 succeeded' in (root/'docs/validation/refined_v1/firmware-build.log').read_text()
base=json.loads((root/'docs/validation/refined_v1/baseline_comparison.json').read_text())
assert base['status']=='PASS'
lines=['# 软件验证记录','',
'记录日期：2026-11-09。当前完成 metric v2 软件实验、原始日志审计和 ESP32-S3 N16R8 双端构建。','',
'| 检查 | 结果 | 证据 |','|---|---|---|',
f'| Python 单元/集成测试 | {count} passed | [pytest.log](refined_v1/pytest.log) |',
'| 开发验证 | 78/78，0 失败；27,040 包独立审计通过 | [pilot audit](../../output/study_refined_v1/pilot/audit.json) |']
run_total=0;packets=0;replays=0;groups=0
for name,path in sets:
 c=json.loads((path/'completion.json').read_text());a=json.loads((path/'audit.json').read_text())
 assert c['runs']==c['expected_runs'] and c['failures']==0 and a['status']=='PASS'
 run_total+=c['runs'];packets+=a['audited_packets'];replays+=len(a['deterministic_replays']);groups+=a['common_trace_groups']
 link=path.relative_to(root)
 lines.append(f"| {name} | {c['runs']:,}/{c['expected_runs']:,}，0 失败，audit PASS | [completion](../../{link}/completion.json) · [audit](../../{link}/audit.json) |")
lines += [f'| 全量原始日志重算 | {run_total:,} 次运行、{packets:,} 包、{groups} 组共同轨迹 | 包身份、结局、分类分母、资源预算、AoI 与 QoS |',
f'| 确定性复现 | {replays} 次 FUD/PF 逐字段一致 | 各组 audit.json |',
f"| 历史数据完整性 | {base['historical_files_unchanged']:,} 个文件原样保留 | [baseline_comparison.json](refined_v1/baseline_comparison.json) |",
'| FUD 原策略核对 | 100 次主窗口决策和 11 个 legacy 指标逐项相同 | baseline_comparison.json；choose AST 测试 |',
'| PF 更新 | 逐逻辑 slot，成功 ACK 字节反馈，失败与空闲为零 | 共享 pf_update 与模拟反馈测试 |',
'| 双端固件 | sender / receiver SUCCESS | [构建日志](refined_v1/firmware-build.log) |',
'| Flash/PSRAM/USB | 镜像头 16 MB；qio_opi SDK、OPI 模式、USB CDC 编译项核对通过 | [firmware-config.json](refined_v1/firmware-config.json) |',
'| 物理链路/内存读数/电流采集 | 下一阶段 | [硬件指南](../../hardware/README.md) |','',
'## 结论与版本','',
'研究结论和全部置信区间见 [A–K 报告](../../research/REPORT.md)。欠账机制按实际服务资源公平性重新评估；拥塞下 FUD 相对去欠账版本的 Jain Service Share 区间跨零。','',
'v1 的 3,900 次正式实验及早期历史版本保留原路径；原报告副本位于 output/archive/refinement_baseline/。本轮窗口、指标、规模与敏感性修订见 [执行记录](refined_v1/stages.md) 和 [模型问题清单](refined_v1/model_review.md)。','',
'本轮测试覆盖：包含等号的 deadline、尾窗交付、结束删失、状态替换与链路失败分离、溢出/过期互斥、服务占用跨窗口裁切、固定总负载及分类到达一致性、Markov 参数、PF 衰减与 ACK 边界、FUD 评分 AST、物理时间保持的 dt 配置。']
(root/'docs/validation/status.md').write_text('\n'.join(lines)+'\n');print(f'{count} tests, {run_total} refined runs, {packets} packets, {replays} replays')
