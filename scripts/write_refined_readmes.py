"""Keep the bilingual repository layout while refreshing v2 results and status."""
import csv
from pathlib import Path

root=Path('output/study_refined_v1')
with (root/'summary.csv').open() as f:summary=list(csv.DictReader(f))
with (root/'paired_differences.csv').open() as f:pairs=list(csv.DictReader(f))
idx={(r['scenario'],r['policy'],r['metric']):r for r in summary}
pi={(r['scenario'],r['baseline'],r['metric']):r for r in pairs}

def mean(s,p,m):return float(idx[s,p,m]['mean'])

def effect(s,p,m,scale=1):
    r=pi[s,p,m]
    return f"{float(r['delta_fud_minus_baseline'])*scale:+.5f} [{float(r['ci_low'])*scale:+.5f}, {float(r['ci_high'])*scale:+.5f}]"

for lang in ['en','zh']:
    p=Path('README.md' if lang=='en' else 'README.zh-CN.md');s=p.read_text()
    if lang=='en':
        s=s.replace('Adaptive Resource Scheduling for Multi-Flow IoT Networks','Adaptive Scheduling for a Shared IoT Gateway Outlet')
        a=s.index('The project combines');b=s.index('<a id="research-question-and-method">')
        s=s[:a]+'''The project combines a Python slotted model, nine baseline schedulers, the Freshness–Urgency–Debt (FUD) policy, three mechanism ablations, and an automated experiment pipeline. The refined evaluation contains **12,480 runs across 48 named conditions, 20 seeds, and 13 policies**: the original 15-scenario matrix, four fixed-total-load scale conditions, 25 model-sensitivity conditions, and four congestion bucket-capacity conditions. It records packet outcomes, class-specific delivery metrics, actual service shares, and paired intervals. ESP32-S3/E220 firmware and a PC replay tool support the next stage of physical link experiments.

'''+s[b:]
        a=s.index('\n\n',s.index('The 15 scenarios'))+2;b=s.index('<a id="key-findings">')
        s=s[:a]+'''Evaluation separates state AoI, replacement and transmission success from event deadline outcomes. Resource fairness uses actual abstract service slots, with equal-share and weight-proportional Jain references. Every policy uses the same main window and arrival-free tail; main-window pending snapshots are separate from final outcomes. The [metric definitions](docs/metrics-v2.md), [protocol](research/experiments/protocol.md), and [frozen configurations](configs/refined_v1/) define each denominator and control.

'''+s[b:]
        result=['<a id="key-findings"></a>','','## Key findings: refined software evaluation','',
        'The main matrix contains 3,900 runs, the fixed-total-load scale group 1,040, model sensitivity 6,500, and congestion bucket sensitivity 1,040. Each condition uses seeds 100–119 and all 13 methods. Sensitivity groups retain their own baseline; repeated baseline conditions are analyzed within their groups. State AoI and Service Share use the main observation window; event outcomes include the common tail.','',
        '| Scenario | Policy | State mean AoI (s) ↓ | Event miss (%) ↓ | Jain Service Share ↑ |','| --- | --- | ---: | ---: | ---: |']
        for scene,label in [('congestion','Congestion'),('bursty','Bursty')]:
            for policy,name in [('fifo','FIFO'),('aoi_gain','AoI-gain'),('fud','FUD')]:
                result.append(f'| {label} | {name} | {mean(scene,policy,"mean_aoi_s"):.4f} | {mean(scene,policy,"event_deadline_miss")*100:.2f} | {mean(scene,policy,"jain_service_share"):.4f} |')
        result+=['',f'**Congestion:** FUD−FIFO event miss is {effect("congestion","fifo","event_deadline_miss",100)} percentage points; state AoI changes by {effect("congestion","fifo","mean_aoi_s")} s (95% paired bootstrap CI). FUD has higher event miss and lower state AoI than AoI-gain.','',
        f'**Debt ablation:** congestion Service Share Jain changes by {effect("congestion","fud_no_debt","jain_service_share")}. The interval spans zero, so the resource-fairness gain is unresolved in this condition.','',
        '**Scale and model controls:** scale A keeps per-flow rate fixed; scale B keeps total traffic and class arrivals fixed across 8/24/48/96 flows. Bucket capacities 2/4/8/16 and seven other parameter groups test the model conditions. The [A–K report](research/REPORT.md) gives all five hypotheses, comparator intervals, favorable and adverse results.','',
        '![Main-window freshness, event deadlines, and service allocation](output/study_refined_v1/overview.png)','',
        '![FUD component ablations](output/study_refined_v1/ablations.png)','',
        'Full data: [summary](output/study_refined_v1/summary.csv) · [paired comparisons](output/study_refined_v1/paired_differences.csv) · [per-flow metrics](output/study_refined_v1/per_flow.csv) · [adverse directions](output/study_refined_v1/negative_results.csv) · [fixed-total scale](output/study_refined_v1/scaling/results.md) · [model sensitivity](output/study_refined_v1/sensitivity/results.md) · [congestion buckets](output/study_refined_v1/bucket_load/results.md). Historical v1 results remain in [output/study](output/study/results.md).','']
        status='''<a id="implementation-status"></a>

## Implementation status

| Component | Progress |
| --- | --- |
| Mixed-flow queues, common tail, and 13 scheduling policies | Implemented; FUD score unchanged |
| Refined software experiments | 12,480 completed runs; zero execution failures |
| Python unit and integration checks | 48 tests passed |
| Independent raw-ledger audit | All 12,480 runs; packet, resource, AoI, and QoS checks passed |
| Published baseline preservation | 40,111 historical files unchanged; 100 FUD main-window runs match |
| PF simulation and replay | Shared slot EWMA; mocked ACK timing tests passed |
| ESP32-S3 N16R8 firmware | Sender/receiver builds passed; QIO/OPI SDK and 16 MB image header verified |
| Physical calibration, radio runs, and power capture | Next stage |

The hardware path uses two ESP32-S3 boards and two E220-400T22S radios. The PC schedules logical flows through the sender; the receiver validates CRC-protected frames and returns ACKs. See the [hardware guide](hardware/README.md) and [validation record](docs/validation/status.md).

'''
    else:
        s=s.replace('面向多业务物联网网络的自适应资源调度研究','面向多业务 IoT 共享网关出口的自适应调度研究')
        a=s.index('项目包含 Python');b=s.index('<a id="research-question-and-method">')
        s=s[:a]+'''项目包含 Python 离散时隙模型、九种基线调度、Freshness–Urgency–Debt（FUD）策略、三种机制消融和自动实验流程。精修版完成 **48 条命名条件、20 个种子、13 种策略，共 12,480 次运行**：主实验 15 条、固定总负载规模组 4 条、模型敏感性 25 条、高负载桶容量 4 条。保存逐包结局、分类交付指标、实际服务份额和配对区间。ESP32-S3/E220 固件及 PC 重放工具用于下一阶段的物理链路实验。

'''+s[b:]
        a=s.index('\n\n',s.index('15 个场景覆盖'))+2;b=s.index('<a id="key-findings">')
        s=s[:a]+'''评价体系分别报告状态 AoI、替换率和发送成功率，以及事件及时交付、溢出和过期。资源公平性采用实际占用的抽象服务 slots，并给出等份和权重比例参考。各方法共享主窗口与停止到达后的公共尾窗，主截止点快照与最终结局分别记录。数学定义和控制条件见[指标文档](docs/metrics-v2.md)、[实验协议](research/experiments/protocol.md)与[冻结配置](configs/refined_v1/)。

'''+s[b:]
        result=['<a id="key-findings"></a>','','## 主要发现：精修版软件评估','',
        '主实验 3,900 次、固定总负载组 1,040 次、敏感性组 6,500 次、高负载桶容量组 1,040 次；每条条件均使用 seeds 100–119 和全部 13 种方法。敏感性各组保留自己的基准水平，重复基准在组内分析。状态 AoI 与 Service Share 仅统计主观察窗口，事件结局追踪至公共尾窗结束。','',
        '| 场景 | 方法 | 状态平均 AoI(s) ↓ | 事件 miss(%) ↓ | Jain Service Share ↑ |','| --- | --- | ---: | ---: | ---: |']
        for scene,label in [('congestion','拥塞'),('bursty','突发')]:
            for policy,name in [('fifo','FIFO'),('aoi_gain','AoI-gain'),('fud','FUD')]:
                result.append(f'| {label} | {name} | {mean(scene,policy,"mean_aoi_s"):.4f} | {mean(scene,policy,"event_deadline_miss")*100:.2f} | {mean(scene,policy,"jain_service_share"):.4f} |')
        result+=['',f'**拥塞：** FUD−FIFO 的事件 miss 差为 {effect("congestion","fifo","event_deadline_miss",100)} 个百分点，状态 AoI 差为 {effect("congestion","fifo","mean_aoi_s")} s（95% 配对 bootstrap CI）。相对 AoI-gain，FUD 的事件 miss 更高、状态 AoI 更低。','',
        f'**欠账消融：** 拥塞下 Service Share Jain 的变化为 {effect("congestion","fud_no_debt","jain_service_share")}，区间跨零，该条件的资源公平性提升尚无明确方向。','',
        '**规模与模型控制：** A 组固定每流速率，B 组在 8/24/48/96 条流之间保持总负载和分类到达相同；桶容量 2/4/8/16 与其余七组参数检验适用条件。[A–K 报告](research/REPORT.md)给出五项研究问题、完整比较区间及有利和不利结果。','',
        '![状态时效、事件截止期与服务资源分配](output/study_refined_v1/overview.png)','',
        '![FUD 分量消融](output/study_refined_v1/ablations.png)','',
        '完整数据：[汇总](output/study_refined_v1/summary.csv) · [配对比较](output/study_refined_v1/paired_differences.csv) · [每流指标](output/study_refined_v1/per_flow.csv) · [不利方向](output/study_refined_v1/negative_results.csv) · [固定总负载](output/study_refined_v1/scaling/results.md) · [敏感性](output/study_refined_v1/sensitivity/results.md) · [高负载桶容量](output/study_refined_v1/bucket_load/results.md)。历史 v1 数据保留在 [output/study](output/study/results.md)。','']
        status='''<a id="implementation-status"></a>

## 实现状态

| 模块 | 进展 |
| --- | --- |
| 混合业务队列、公共尾窗、13 种策略 | 已实现；FUD 评分保持一致 |
| 精修版软件实验 | 12,480 次完成，0 次执行失败 |
| Python 单元与集成检查 | 48 项测试通过 |
| 原始日志独立审计 | 12,480 次包账本、资源、AoI、QoS 检查通过 |
| 发布基线保留 | 40,111 个历史文件原样保留；100 次 FUD 主窗口运行一致 |
| PF 仿真与重放 | 共用 slot EWMA，模拟 ACK 时序测试通过 |
| ESP32-S3 N16R8 固件 | 双端构建成功；QIO/OPI SDK 与 16 MB 镜像头核对通过 |
| 物理标定、无线实验与电流采集 | 下一阶段 |

硬件路径使用两块 ESP32-S3 和两套 E220-400T22S，PC 安排逻辑流发送顺序，接收端校验 CRC 并返回 ACK。接线与运行见[硬件指南](hardware/README.md)，构建与软件证据见[验证记录](docs/validation/status.md)。

'''
    a=s.index('<a id="key-findings">');b=s.index('<a id="implementation-status">');s=s[:a]+'\n'.join(result)+'\n'+s[b:]
    a=s.index('<a id="implementation-status">');b=s.index('<a id="quick-start">');s=s[:a]+status+s[b:]
    s=s.replace('52-run software example','78-run software example').replace('包含 52 次仿真','包含 78 次仿真')
    s=s.replace('Run the full experiment matrix:', 'Run the main experiment matrix:').replace('运行完整实验矩阵：','运行主实验矩阵：')
    s=s.replace('[结果报告](output/study/results.md) · [统计 CSV](output/study/summary.csv)', '[结果报告](output/study_refined_v1/results.md) · [统计 CSV](output/study_refined_v1/summary.csv)')
    s=s.replace('configs/pilot.json','configs/refined_v1/pilot.json').replace('configs/study.json','configs/refined_v1/main.json')
    s=s.replace('scripts/audit_study.py','scripts/audit_refined.py')
    s=s.replace('(output/study/manifest.json)','(output/study_refined_v1/manifest.json)')
    s=s.replace('(output/study/audit.json)','(output/study_refined_v1/audit.json)')
    s=s.replace('| [Results report](output/study/results.md) · [Summary CSV](output/study/summary.csv) |','| [Results report](output/study_refined_v1/results.md) · [Summary CSV](output/study_refined_v1/summary.csv) |')
    s=s.replace('| [结果报告](output/study/results.md) · [汇总 CSV](output/study/summary.csv) |','| [结果报告](output/study_refined_v1/results.md) · [汇总 CSV](output/study_refined_v1/summary.csv) |')
    # The quick start runs the main matrix; the complete command set is linked.
    anchor='Choose a new output directory' if lang=='en' else '每个新实验'
    extra='Full scale and sensitivity commands are in the [reproduction guide](docs/reproducibility.md).\n\n' if lang=='en' else '固定总负载和敏感性的完整命令见[复现指南](docs/reproducibility.md)。\n\n'
    s=s.replace(extra,'')
    if anchor in s:s=s.replace(anchor,extra+anchor,1)
    p.write_text(s)
print('bilingual README files updated')
