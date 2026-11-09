"""Generate the A–K research report from immutable experiment CSVs and audits."""
import csv
import json
from pathlib import Path

ROOT=Path('output/study_refined_v1')

def read(path):
    with path.open(newline='') as f:return list(csv.DictReader(f))

sets={name:{'path':path,'summary':read(path/'summary.csv'),'paired':read(path/'paired_differences.csv'),
            'completion':json.loads((path/'completion.json').read_text()),'audit':json.loads((path/'audit.json').read_text()),
            'manifest':json.loads((path/'manifest.json').read_text())}
      for name,path in [('main',ROOT),('scaling',ROOT/'scaling'),('sensitivity',ROOT/'sensitivity'),('bucket_load',ROOT/'bucket_load')]}
for d in sets.values():
    d['index']={(r['scenario'],r['policy'],r['metric']):r for r in d['summary']}
    d['pairs']={(r['scenario'],r['baseline'],r['metric']):r for r in d['paired']}

def ci(row,paired=False):
    key='delta_fud_minus_baseline' if paired else 'mean'
    if not row[key]:return 'NA'
    return f"{float(row[key]):.5f} [{float(row['ci_low']):.5f}, {float(row['ci_high']):.5f}]"

def value(d,s,p,m):return ci(d['index'][s,p,m])

def delta(d,s,p,m):return ci(d['pairs'][s,p,m],True)

main=sets['main'];sens=sets['sensitivity'];scale=sets['scaling']
lines=['# NetAdapt-IoT 第一轮精修报告',
'记录日期：2026-11-09。项目研究多业务 IoT 共享网关出口调度。FUD 的评分、系数和欠账更新保持发布版本；本轮修订统计、模型参数与实验控制。',
'## A. 修改文件',
'完整文件清单见 [changed_files.txt](../docs/validation/refined_v1/changed_files.txt)。主要修改如下：',
'| 文件 | 内容 |','|---|---|',
'| src/netadapt/model.py、traffic.py | 公共尾窗、模型参数、固定总负载及分类到达控制 |',
'| metrics.py、simulation.py | 互斥终态、截止点快照、分类指标、实际服务占用、每流 QoS |',
'| scheduler.py、hardware/run.py | 共用 PF slot EWMA；choose AST 与 FUD 公式保持一致 |',
'| runner.py、analysis.py | v2 版本元数据、全字段汇总、资源公平性图和配对区间 |',
'| configs/refined_v1/、scripts/*refined*.py | 冻结矩阵、执行、独立审计与报告生成 |',
'| hardware/firmware/boards/、platformio.ini | N16R8 flash/OPI PSRAM/USB 本地板定义 |',
'| tests/test_refined.py、README、docs、research 文档 | 窗口/资源/PF 测试与研究口径同步 |',
'## B. 问题与实质变化',
'| 问题 | 修改前 | 修改后 |','|---|---|---|',
'| 仿真结束 | 事件保护区 cohort；全量记录留下 queued/inflight | 主窗口全生成 cohort 跟踪到统一尾窗；终点未完成单列 |',
'| 状态替换与丢包 | 汇入整体 PDR | 替换率、已判定尝试成功率、事件 deadline miss 分列 |',
'| 公平性 | Jain(PDR) 描述交付率均衡 | 增加实际服务 slots 的 Jain、权重归一化 Jain、每流份额和 QoS |',
'| 规模混杂 | 每流固定速率，总需求随 N 增长 | 保留 A，新增分类到达时刻与总包数一致的固定总负载 B |',
'| 模型敏感性 | 桶容量固定；Markov 转移常数 | 25 条单因素/外生物理量保持的离散化条件，另补充4条高负载桶容量条件 |',
'| PF | 仿真按 slot，硬件按事务 | 共用每 slot 衰减；成功 ACK payload 计入对应边界，失败为零 |',
'| 板定义 | N8 元数据加 overrides | 16 MB QIO Flash、qio_opi SDK、OPI PSRAM 和 USB 配置进入本地板定义 |',
'## C. 数学定义',
'完整定义见 [metrics-v2.md](../docs/metrics-v2.md)。主观察为 [W,T)，尾窗为 [T,E)，生成 cohort 为 W≤g<T。L=(T−W)dt。',
'- AoI_i = dt/(T−W) Σ(t−u_i(t))；Normalized AoI_i = AoI_i/(tau_i dt)。',
'- 状态替换率=替换数/状态生成数；状态发送成功率=成功尝试/已判定尝试；状态 Goodput=8×成功 cohort payload/L。',
'- 事件 R=N−pending；deadline success=D/R，miss=(R−D)/R，late=A/R；overflow=O/N，expiration=X/N。时延/P95 条件于成功事件。',
'- S_i=Σ|服务区间∩[W,T)|；share_i=S_i/ΣS；J(S)=(ΣS)^2/(NΣS²)，加权指标 J(S_i/weight_i)。失败尝试消耗相同资源。',
'- 每流 Goodput=8×最终交付 cohort payload/L。状态 QoS=AoI≤tau*dt 的主窗口时间比例；事件 QoS=deadline success。',
'空分母为 null，全部配置流进入资源向量，全零 Jain 为 0。pending 不归入已判定事件失败。legacy 字段使用原保护区和原截止边界，分别标注版本。',
'## D. 实验配置与规模',
'| 实验族 | 场景 | seed | 策略 | 实际/期望运行 | 失败 | 审计包数 |','|---|---:|---:|---:|---:|---:|---:|']
for name,d in sets.items():
    st=d['manifest']['study'];c=d['completion'];a=d['audit']
    lines.append(f"| {name} | {len(st['scenarios'])} | {len(st['seeds'])} | {len(st['policies'])} | {c['runs']}/{c['expected_runs']} | {c['failures']} | {a['audited_packets']} |")
lines+=['正式总计 12,480 次；开发验证 78 次。默认 4,000 slots、warmup 500、dt=0.1 s；dt 敏感性保持 400 s/50 s 和物理到达率/截止期/预算容量。',
'配置见 [实验协议](experiments/protocol.md) 和 configs/refined_v1。各实验族独立 manifest、completion、audit、全量 CSV、图和报告。所有对照按同 seed 配对，CI 为 2,000 次 seed bootstrap 的 95% 区间。',
'## E. 新旧版本比较',
'原 output/study 的 v1 结果、manifest、配置和审计逐字节保留。基线比较对 5 种代表场景×20 seeds 的 FUD 主窗口调度决定及 11 个 legacy 指标逐项检查。结果见 [baseline_comparison.json](../docs/validation/refined_v1/baseline_comparison.json)。',
'| 场景 | v1 状态 AoI | v2 状态 AoI | v1 event_miss（保护区） | v2 event_deadline_miss（全主 cohort+尾窗） |','|---|---:|---:|---:|---:|']
old={(r['scenario'],r['policy'],r['metric']):r for r in read(Path('output/study/summary.csv'))}
for s in ['normal','congestion','bursty','nodes_96']:
    lines.append(f"| {s} | {float(old[s,'fud','mean_aoi_s']['mean']):.5f} | {value(main,s,'fud','mean_aoi_s')} | {float(old[s,'fud','event_miss']['mean']):.5f} | {value(main,s,'fud','event_deadline_miss')} |")
lines+=[f"表中两种事件字段统计窗口不同，分列展示；AoI 的主窗口和定义相同。FUD 主窗口策略保持一致，变化来自新增尾窗与分类统计。拥塞 FUD 的 legacy 总体 PDR={float(main['index']['congestion','fud','pdr']['mean']):.5f}，v2 状态发送成功率={float(main['index']['congestion','fud','state_transmission_success']['mean']):.5f}；后者仅以已判定发送尝试为分母，差异反映指标拆分。",
'## F. FUD 与五种主要基线',
'以下均为 FUD−对照，括号内为 95% CI；AoI、miss 越低越好，Jain 越高越均衡。全部场景/对照/指标保存在 paired_differences.csv。',
'| 场景 | 对照 | 状态 AoI(s)差 | 事件 miss差 | Service Share Jain差 |','|---|---|---|---|---|']
for s in ['normal','congestion','bursty']:
    for p in ['fifo','edf','maxweight','pf','aoi_gain']:
        lines.append('| '+s+' | '+p+' | '+' | '.join(delta(main,s,p,m) for m in ['mean_aoi_s','event_deadline_miss','jain_service_share'])+' |')
lines+=['## G. H1–H5 与适用条件',
'### H1、H2：及时交付与新鲜度的取舍',
f"拥塞相对 FIFO：事件 miss差 {delta(main,'congestion','fifo','event_deadline_miss')}，AoI差 {delta(main,'congestion','fifo','mean_aoi_s')}。",
f"拥塞相对 AoI-gain：事件 miss差 {delta(main,'congestion','aoi_gain','event_deadline_miss')}，AoI差 {delta(main,'congestion','aoi_gain','mean_aoi_s')}。",
f"突发相对 FIFO：事件 miss差 {delta(main,'bursty','fifo','event_deadline_miss')}，AoI差 {delta(main,'bursty','fifo','mean_aoi_s')}。",
'H1 在拥塞/突发中相对 FIFO 的事件及时性获得支持；拥塞中 EDF、MaxWeight 和 AoI-gain 的事件 miss 更低。H2 显示明确取舍：拥塞相对 FIFO 用更高 AoI 换取更低 miss，相对 AoI-gain 则是更低 AoI 和更高 miss。突发相对 FIFO 的 AoI 差区间跨零。具体比较见上表及全量 CSV。',
f"拥塞中 FUD−PF 的原始 Service Share Jain 差为 {delta(main,'congestion','pf','jain_service_share')}，权重归一化 Jain 差为 {delta(main,'congestion','pf','jain_weighted_service_share')}。PF 更接近等份资源分配，FUD 更接近业务权重比例；两种参考分别报告。",
'### H3：欠账的资源分配效应',
'比较 FUD−fud_no_debt，直接评估实际服务资源及权重参考；完整列出全部 15 个主场景。',
'| 场景 | 原始 Service Share Jain差 | 加权 Jain差 |','|---|---|---|']
for c in main['manifest']['study']['scenarios']:
    s=c['name'];lines.append(f"| {s} | {delta(main,s,'fud_no_debt','jain_service_share')} | {delta(main,s,'fud_no_debt','jain_weighted_service_share')} |")
lines+=[f"拥塞原始 Jain 差 {delta(main,'congestion','fud_no_debt','jain_service_share')}，加权差 {delta(main,'congestion','fud_no_debt','jain_weighted_service_share')}；突发原始 Jain 差 {delta(main,'bursty','fud_no_debt','jain_service_share')}。这些区间跨零，H3 在这两类负载下未得到明确支持。其他场景按表中区间判断，不将交付率均衡替代服务资源均衡。",
'### H4：节点数与总负载',
'表中为 FUD 均值 [95% CI]。A 固定每流 rate=0.015；B 固定总 rate=0.36，三类负载各占 1/3。',
'| 组 | N | 总 rate/slot | 状态 AoI(s) | 事件 miss | Service Share Jain |','|---|---:|---:|---|---|---|']
for n,s in [(8,'nodes_8'),(24,'normal'),(48,'nodes_48'),(96,'nodes_96')]:
    lines.append(f"| A | {n} | {n*.015:.2f} | "+' | '.join(value(main,s,'fud',m) for m in ['mean_aoi_s','event_deadline_miss','jain_service_share'])+' |')
for n in [8,24,48,96]:
    s=f'total_036_nodes_{n}';lines.append(f"| B | {n} | 0.36 | "+' | '.join(value(scale,s,'fud',m) for m in ['mean_aoi_s','event_deadline_miss','jain_service_share'])+' |')
lines+=['B 控制实际分类到达时刻与包数；N 增大时单流产生率下降，源端更新本身变稀疏。为解释 AoI，另计算即时无损交付的源端年龄基线；接收 AoI 减去该基线得到额外年龄，包含排队、服务、反馈及链路失败的共同影响。该分析不改变调度或主实验指标。',
'| 组 | N | FUD 源端理想 AoI(s) | FUD 额外 AoI(s) |','|---|---:|---|---|']
controls=read(ROOT/'scaling_controls_summary.csv')
for family in ['A','B']:
    for n in [8,24,48,96]:
        vals=[next(r for r in controls if r['family']==family and int(r['nodes'])==n and r['policy']=='fud' and r['metric']==m) for m in ['source_aoi_s','excess_aoi_s']]
        lines.append(f'| {family} | {n} | '+' | '.join(ci(r) for r in vals)+' |')
lines+=['源端基线定义与逐 seed 结果见 scaling_controls.json、scaling_controls.csv。A 同时改变总负载；B 的剩余差异包括流拆分、类内稀疏性、类别流数、权重和调度。各规模的基线配对区间见对应目录。H4 因而按负载控制后的业务表现及额外 AoI 判断，绝对 AoI 随流数增长本身不能单独归因为调度效率下降。',
'### H5：预算与链路等模型条件',
'全部 25 条敏感性条件列于下表；各组基准重复是组内参照，未合并扩充独立样本。',
'| 条件 | FUD 状态 AoI(s) | FUD 事件 miss | FUD Service Jain | FUD−FIFO 事件 miss差 |','|---|---|---|---|---|']
for c in sens['manifest']['study']['scenarios']:
    s=c['name'];lines.append('| '+s+' | '+' | '.join(value(sens,s,'fud',m) for m in ['mean_aoi_s','event_deadline_miss','jain_service_share'])+' | '+delta(sens,s,'fifo','event_deadline_miss')+' |')
lines+=['高负载桶容量条件：固定 rate=0.10，其余参数一致。该补充组单独记录，覆盖完整四容量、20 seeds 和 13 方法。',
'| 条件 | FUD 状态 AoI(s) | FUD 事件 miss | FUD Service Jain | FUD−FIFO 事件 miss差 |','|---|---|---|---|---|']
for c in sets['bucket_load']['manifest']['study']['scenarios']:
    d=sets['bucket_load'];s=c['name']
    lines.append('| '+s+' | '+' | '.join(value(d,s,'fud',m) for m in ['mean_aoi_s','event_deadline_miss','jain_service_share'])+' | '+delta(d,s,'fifo','event_deadline_miss')+' |')
contrasts=read(ROOT/'sensitivity/model_contrasts.csv')
r=next(x for x in contrasts if x['scenario']=='bucket_slots_2' and x['policy']=='fud' and x['metric']=='event_deadline_miss')
lines+=[f"正常负载中，桶2相对桶4的 FUD 事件 miss 差为 {float(r['delta_level_minus_reference']):.5f} [{float(r['ci_low']):.5f}, {float(r['ci_high']):.5f}]。拥塞背景下，四种桶容量的 FUD 均值相同：AoI={float(sets['bucket_load']['index']['congested_bucket_4','fud','mean_aoi_s']['mean']):.5f} s，miss={float(sets['bucket_load']['index']['congested_bucket_4','fud','event_deadline_miss']['mean']):.5f}。",
'在该饱和负载和一 slot 服务成本下，预算补充率与服务占用主导结果，增大桶容量未产生性能增益。H5 的容量效应依赖负载背景；链路和预算条件下的适用方向见各行配对区间。参数水平相对各组基准的同方法配对效应（含 legacy PDR、Goodput 和 Service Share）见 model_contrasts.csv。']
lines+=['桶容量只改变可积累预算；高 bitrate 仍受最小一 slot 服务粒度限制。dt 组保持外生物理量，算法仍采用逻辑 slot 常数：FUD 紧迫度中的余量和常数项随离散化变化；PF 的 alpha=0.01/slot 对应约 2.49/4.97/9.95 s 的物理衰减时常数。因此该组评估完整离散实现的敏感性。适用范围按各条件的效应与 CI 判断。',
'### 全量不利方向',
'| 实验族 | 主要指标的不利均值比较 | 其中区间完全位于不利侧 |','|---|---:|---:|']
for name,d in sets.items():
    rows=[p for p in d['paired'] if p['metric'] in ('mean_aoi_s','event_deadline_miss','jain_service_share') and p['fud_worse']=='True']
    sig=sum(float(p['ci_low'])>0 if p['lower_is_better']=='True' else float(p['ci_high'])<0 for p in rows)
    lines.append(f'| {name} | {len(rows)} | {sig} |')
lines+=['全部不利方向包含所有对照与三种消融。CI 跨零的比较与确定方向分别呈现。统计为探索性逐项比较。',
'## H. 测试与独立审计',
'Python 自动化测试：**48 passed**。原 34 项保持通过，新增窗口、删失、资源裁切、分类到达、Markov 参数、PF 逻辑时隙、FUD AST 和 dt 物理参数约束。日志见 docs/validation/refined_v1/pytest.log。',
f"独立审计覆盖 {sum(d['audit']['audited_runs'] for d in sets.values()):,} 次正式运行、{sum(d['audit']['audited_packets'] for d in sets.values()):,} 个包；全部终点 pending=0。",
'审计从原始日志重构包身份、终态、分类分母、事件时延、服务预算、跨窗口资源、AoI/QoS，验证共同轨迹，并精确复现 FUD/PF 的代表运行。',
'## I. ESP32-S3 双端构建',
'sender 和 receiver 均 SUCCESS。PlatformIO espressif32 6.9.0、Arduino ESP32 2.0.17、16 MB QIO Flash、qio_opi SDK、OPI PSRAM、USB CDC。GPIO RX17/TX18/M0=4/M1=5/AUX=6，UART1 9600 8N1，USB 115200。',
'证据见 docs/validation/refined_v1/firmware-build.log 和 firmware-config.json。完成项为双端编译；物理链路、PSRAM 容量读数、无线 ACK 时序与电流采集安排在实机阶段。',
'## J. 尚待解决的研究问题',
'- 有效 bitrate、服务成本、反馈时延和损失过程目前由模型指定，需要物理轨迹校准。',
'- Service Share 是出口抽象资源；等份和权重参考各回答一种分配问题，异负载下还需结合需求与业务 QoS。',
'- 状态 QoS 与事件 QoS 含义不同；时延条件于成功；当前实验为有限时长、固定反馈与单次尝试。',
'- FUD 的离散紧迫度项、PF 的物理记忆时长、欠账与活跃队列关系需要进一步分析；当前置信区间为探索性逐项区间。',
'## K. 下一阶段三项研究',
'1. 标定 ESP32-S3/E220 单帧服务、反馈和失败相关性，用实测参数及轨迹重跑既定软件矩阵。',
'2. 研究需求与权重归一化的资源基准，结合每流 AoI 达标率和事件及时率评估欠账机制。',
'3. 在独立到达轨迹、更长观察期及物理时间一致的离散化条件下验证 FUD 的稳定区间，再开展算法分量调整。',
'\n数据入口：[主实验](../output/study_refined_v1/results.md) · [固定总负载](../output/study_refined_v1/scaling/results.md) · [敏感性](../output/study_refined_v1/sensitivity/results.md) · [高负载桶容量](../output/study_refined_v1/bucket_load/results.md)。']
Path('research/REPORT.md').write_text('\n\n'.join(x if not x.startswith('|') else x for x in lines)+'\n')
# Tables need contiguous rows; prose and headings keep blank lines.
p=Path('research/REPORT.md');s=p.read_text().replace(' |\n\n|',' |\n|').replace('|\n\n|','|\n|');p.write_text(s)
print(p)
