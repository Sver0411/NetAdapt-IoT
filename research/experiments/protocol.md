# 第一轮精修实验协议

记录日期：2026-11-09。指标版本：2。FUD 评分与欠账更新沿用发布基线，系数为 1、1、0.25。

## 矩阵与预先固定的参数

全部正式实验使用 seeds 100–119、13 种策略；开发验证使用 seeds 0、1。每个条件按同一 seed 共享到达和绝对 slot/flow 索引的潜在信道结果。

| 实验族 | 条件数 | 运行数 | 配置 | 输出 |
|---|---:|---:|---|---|
| 主实验 | 15 | 3,900 | configs/refined_v1/main.json | output/study_refined_v1/ |
| 固定总负载 B | 4 | 1,040 | configs/refined_v1/scaling.json | output/study_refined_v1/scaling/ |
| 模型敏感性 | 25 | 6,500 | configs/refined_v1/sensitivity.json | output/study_refined_v1/sensitivity/ |
| 高负载桶容量 | 4 | 1,040 | configs/refined_v1/bucket_load.json | output/study_refined_v1/bucket_load/ |
| 开发验证 | 3×2 seeds | 78 | configs/refined_v1/pilot.json | output/study_refined_v1/pilot/ |

正式矩阵共 12,480 次。主实验保留正常、拥塞、8/48/96 节点、异速率、等权重、弱链路、Markov、突发、两档预算、长反馈、混合包长、无损条件。基准为 24 节点、4,000 slots、预热 500、dt=0.1 s、rate=0.015/节点/slot、duty=0.8、bucket=4、p=0.95。

## 两组节点规模实验

A 使用主实验的 nodes_8、normal（24）、nodes_48、nodes_96，每节点到达率固定 0.015。总到达率依次为 0.12、0.36、0.72、1.44/slot。按 event/status/telemetry 轮换分配流；8 节点构成为 3/3/2。

B 的 8/24/48/96 节点总到达率固定 0.36/slot，三类各 0.12/slot。每类有 n_k 条流，则该类单流 rate=0.12/n_k；8 节点分别为 0.04、0.04、0.06。按类生成共同 Poisson 到达，再均匀分配至该类业务流；同一种子下，四种规模的分类到达时刻、包数和 payload 负载完全相同。24/48/96 节点类内单流分别为 0.015/0.0075/0.00375。duty、包长、截止期和反馈保持一致。

A 与 B 分别回答“节点与总需求共同增长”和“总需求固定而业务流拆分增加”的问题。跨规模的信道索引随流数改变；算法配对始终在同一规模、同一 seed 内进行。

## 单因素敏感性

| 因素 | 水平 | 其余条件 |
|---|---|---|
| bucket_slots | 2、4、8、16 | 基准 |
| duty | 0.4、0.8、1.0 | 基准 |
| bitrate | 3200、6400、12800 bit/s | 基准；服务成本按 ceil 计算 |
| success | 0.55、0.8、0.95 | IID 基准 |
| good_to_bad | 0.01、0.025、0.1 | Markov，bad_to_good=0.1 |
| bad_to_good | 0.05、0.1、0.25 | Markov，good_to_bad=0.025 |
| rate | 0.015、0.04、0.1/流/slot | 基准 |
| dt | 0.025、0.05、0.1 s | 保持物理量，见下文 |

Markov 从 good 开始，good 成功率 0.95、bad 为 0.2；每条流独立转移。两个转移概率分别改变，避免改变两项参数。

dt 组比较离散实现的敏感性：保持外生物理量，包括主时长 400 s、预热 50 s、每流 0.15 包/s、deadline=0.6 s、状态目标 1.2/3 s、反馈 0.1 s、桶容量等价服务时长 0.4 s、payload 64 B、bitrate=6400 bit/s。相应 slot 数、rate/slot、deadline/slot、反馈/slot 和 bucket/slot 按单位换算写入配置。FUD 的离散 slot 评分形式保持一致。PF 保持 alpha=0.01/slot，物理衰减时常数随 dt 为约 2.49/4.97/9.95 s；FUD 余量中的一个 slot 常数也随物理时长变化。这些是被评估离散实现的时间语义。

额外 bucket_load 组固定 rate=0.10，重复 2/4/8/16 四容量，检验负载背景对预算桶敏感性的影响；与正常负载组分别记录。该组在初始 11,440 次矩阵完成后补充，FUD 系数与全部其他参数保持固定，保留全部条件和方法。

各敏感性组自带基准水平；重复的相同基准条件用于组内对照，未作为额外独立样本合并。有效服务率高于一包/slot 时受最小一个 slot 服务粒度约束。

## 窗口、统计和审计

主期 `[0,T)` 产生业务，AoI、队长、利用率和 Service Share 在 `[W,T)` 计算；停止到达后，所有策略按相同配置继续运行公共尾窗。定义及分母见 [metrics-v2.md](../../docs/metrics-v2.md)。原保护区口径字段保留 legacy 标签。

每个 seed 的指标为统计单位，均值和 FUD−对照配对差值使用 2,000 次 bootstrap，分析 seed 固定 20261106，报告 95% CI。所有策略和场景进入汇总；negative_results.csv 收录不利均值方向，包含 CI 跨零的条目。多重比较作为探索性结果呈现。

每次运行保存 config hash、trace hash、逐包终态与调度决定。manifest 保存完整配置、源码摘要、Python、NumPy、Matplotlib 和平台；completion 保存成功数与失败数。独立审计直接读取原始日志，重算事件/状态分母、资源区间、预算、AoI 和 QoS，并精确复现代表性 FUD/PF 运行。原结果文件摘要清单用于验证历史数据完整保留。

## 物理实验

本轮进行软件实验、串口模拟反馈测试和双端固件构建。物理重放安排在双端通信及事务时序标定后进行，采集 ACK、超时和实际资源成本。PF 共用 slot EWMA，但物理事务的时间消耗和 ACK 量化来自主机时钟。
