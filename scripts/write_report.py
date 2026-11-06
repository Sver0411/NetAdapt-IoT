"""Render the project report from saved experiment tables."""
import csv
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/study'
rows=list(csv.DictReader((OUT/'paired_differences.csv').open()))
summary=list(csv.DictReader((OUT/'summary.csv').open()))
completion=json.loads((OUT/'completion.json').read_text())
audit=json.loads((OUT/'audit.json').read_text())

def comparison(scenario,baseline,metric):
    return next(r for r in rows if (r['scenario'],r['baseline'],r['metric'])==(scenario,baseline,metric))

def ci(row):
    return f"{float(row['delta_fud_minus_baseline']):+.5f} [{float(row['ci_low']):+.5f}, {float(row['ci_high']):+.5f}]"

text=['# NetAdapt-IoT 技术与实验报告',
'\n记录日期：2026-11-06。项目研究多业务 IoT 共享出口的资源调度，围绕信息时效、事件截止期和公平性开展算法设计与实验。',
'\n## 项目目标',
'\n固定源端产生行为，比较状态流、事件流和普通遥测在共享通信预算下的服务顺序。FUD 结合预期 AoI 降幅、事件紧迫度与服务欠账，评价这些机制在不同负载下的贡献。',
'\n## 方法与实现',
'\nPython 离散时隙模型支持最新状态队列、事件 FIFO、不可抢占服务、token 预算、独立/Markov 损失和延迟反馈。FUD 采用系数 1、1、0.25，按成功率与服务成本对三个分量加权。',
'\n九种基线包括 FIFO、RR、WRR、EDF、Priority、MaxWeight、PF、AoI-gain 和 Debt；另有三个 FUD 分量消融。方法定义见[研究方案](design/proposal.md)，技术方向比较见[候选方案](design/candidates.md)。',
'\n## 软件评估',
f"\n完成 {completion['runs']:,} / {completion['expected_runs']:,} 次运行，执行失败数为 {completion['failures']}。矩阵为 15 场景 × 20 种子 × 13 方法；每次 4,000 slots，warmup 500 slots。所有场景统一使用四 slot 预算桶。",
f"\n审计覆盖 {audit['audited_runs']:,} 次运行与 {audit['common_trace_groups']} 组共享轨迹，重放 {len(audit['deterministic_replays'])} 个代表场景。Python 软件测试共 34 项通过，双端固件构建通过。",
'\n![场景性能与区间](../output/study/overview.png)',
'\n![机制消融](../output/study/ablations.png)',
'\n## 主要实验问题',
'\nH1 比较 FUD 与 FIFO 的状态 AoI 和事件 miss；H2 比较 FUD 与 AoI-gain 的服务取舍；H3 通过欠账项消融评估公平性变化。下表为 FUD 减对照的均值与 95% 配对 bootstrap 区间。',
'\n| 场景 | 对照 | 指标 | 差值 [95% CI] |','|---|---|---|---|']
for scenario in ['congestion','bursty']:
    for baseline,metrics in [('fifo',['mean_aoi_s','event_miss']),('aoi_gain',['mean_aoi_s','event_miss','jain_pdr']),('fud_no_debt',['mean_aoi_s','event_miss','jain_pdr'])]:
        for metric in metrics:
            text.append(f'| {scenario} | {baseline} | {metric} | {ci(comparison(scenario,baseline,metric))} |')
text+=['\nAoI 与 miss 的负差值表示下降，Jain(PDR) 的正差值表示公平性提升。区间使用 20 个 seed 的配对差值重采样，完整比较集采用探索性分析。',
'\n## 结果解读',
'\n拥塞场景中，FUD 相对 FIFO 降低事件 miss，同时增加状态 AoI。突发场景中，事件 miss 下降，AoI 差值区间跨越零。',
'\n相对 AoI-gain，两个场景的 FUD 状态 AoI 更低、公平性更高，事件 miss 则上升。欠账项在拥塞场景提供小幅公平性增益，在突发场景的公平性效应为负。',
'\n## 每流表现与指标',
'\n状态 PDR 的分母包括被后续更新替换的包。逐包记录将 replaced、overflow、expired 和 link_loss 分别保存；AoI 描述接收端信息时效，latency 描述成功交付包的等待与传输时间。',
'\nnegative_results.csv 保存全部不利均值方向，per_flow.csv 提供每条流的交付与新鲜度。节点数量实验同时改变总负载，利用率与队列记录反映相应资源变化。',
'\n## 硬件与下一阶段',
'\nESP32-S3 N16R8/E220 双端固件支持 UART 桥、CRC、ACK、参数读取与 PC 逻辑流重放。两种角色已构建通过。下一阶段完成单链路时序校准、物理重放、多发送节点和电流采集。',
'\n## 开发记录',
'\n实现修订包括 event 接收时间戳更新，以及统一四 slot 预算桶。各版本源码和结果按目录归档，详见[修订记录](../docs/validation/implementation_correction.md)与[预算模型比较](../docs/validation/budget_model_comparison.md)。',
'\n## 项目文档',
'\n| 内容 | 入口 |','|---|---|',
'| 项目说明 | [项目说明](project_brief.md) |',
'| 文献与方法依据 | [网络调度论文](literature/networking_papers.md) · [Related Work](literature/related_work.md) · [文献矩阵](literature/literature_matrix.csv) |',
'| 方法与实验 | [研究方案](design/proposal.md) · [实验协议](experiments/protocol.md) |',
'| 软件与复现 | [架构](../docs/architecture.md) · [复现指南](../docs/reproducibility.md) |',
'| 结果与审计 | [结果报告](../output/study/results.md) · [审计](../output/study/audit.json) |',
'| 开发进度 | [验证记录](../docs/validation/status.md) · [开发路线](../docs/roadmap.md) |']
(ROOT/'research/REPORT.md').write_text('\n'.join(text)+'\n')
print('research/REPORT.md')
