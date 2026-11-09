<h1 align="center">NetAdapt-IoT</h1>

<p align="center"><strong>面向多业务 IoT 共享网关出口的自适应调度研究</strong></p>

<p align="center">信息年龄 AoI · 截止期感知调度 · 公平资源分配</p>

---

<p align="center">
  <a href="#project-overview">概览</a> ·
  <a href="#research-question-and-method">研究方法</a> ·
  <a href="#key-findings">实验结果</a> ·
  <a href="#implementation-status">实现状态</a> ·
  <a href="#quick-start">快速开始</a> ·
  <a href="README.md">English</a>
</p>

---

<a id="project-overview"></a>

NetAdapt-IoT 是一个面向多业务 IoT 网络的资源调度研究平台，研究多个设备共享有限通信出口时，如何在状态更新的新鲜度、事件截止期和设备服务公平性之间分配资源。

项目包含 Python 离散时隙模型、九种基线调度、Freshness–Urgency–Debt（FUD）策略、三种机制消融和自动实验流程。精修版完成 **48 条命名条件、20 个种子、13 种策略，共 12,480 次运行**：主实验 15 条、固定总负载规模组 4 条、模型敏感性 25 条、高负载桶容量 4 条。保存逐包结局、分类交付指标、实际服务份额和配对区间。ESP32-S3/E220 固件及 PC 重放工具用于下一阶段的物理链路实验。

<a id="research-question-and-method"></a>

## 研究问题与方法

当负载与链路条件变化时，共享 IoT 网关应该怎样安排不同业务的发送顺序，兼顾信息时效、事件截止期与服务公平性？

FUD 的每次调度决策包含三个部分：

1. **信息时效 Freshness：** 交付状态更新后，预期归一化平方 AoI 的下降量。
2. **事件紧迫度 Urgency：** 事件包的剩余截止期余量与等待时间。
3. **服务欠账 Debt：** 积压业务流累积的服务需求。

调度器结合三个分量、基于 ACK 的成功率估计和包服务成本，选择满足预算的队首包。三个分量系数为 `1 / 1 / 0.25`。对于 `N` 条业务流，每次决策扫描的复杂度为 `O(N)`，队列过期处理另计。

状态流保留最新待发更新，事件流使用有限 FIFO。Token 桶管理通信预算，共享服务器每次完成一个不可抢占的传输。

```mermaid
flowchart LR
    CFG["配置与种子"] --> TRACE["流量与信道轨迹"]
    TRACE --> QUEUE["状态队列 / 事件队列"]
    QUEUE --> SCHED["调度策略"]
    SCHED --> LINK["共享出口与资源预算"]
    LINK --> ACK["ACK 反馈"]
    ACK --> SCHED
    LINK --> LOG["逐包记录"]
    LOG --> ANALYSIS["指标、配对分析与图表"]
```

默认仿真采用 100 ms 时隙、64 B payload、16 B 抽象头部和 6,400 bit/s 有效服务率，Token 桶容量为四个服务时隙。[方法说明](research/design/proposal.md)给出了评分公式、队列规则、时间顺序和指标定义。

## 基线与实验设计

| 方法 | 调度依据 |
| --- | --- |
| `fifo` | 最早产生且满足预算的队首包 |
| `rr` / `wrr` | 轮询 / 加权轮询 |
| `edf` / `priority` | 最早截止期 / 固定业务优先级 |
| `maxweight` / `pf` | 队列压力 / 比例公平 |
| `aoi_gain` / `debt` | 信息时效收益 / 累积服务欠账 |
| `fud` | 结合信息时效、紧迫度与欠账 |
| `fud_no_age` / `fud_no_urgency` / `fud_no_debt` | 分别去除一个分量的消融实验 |

每组场景与种子下，13 种方法使用相同的输入流量、按绝对时刻索引的潜在信道结果、队列规则和资源预算。调度依据包括包时间戳、队列状态与历史 ACK 观测。

15 个场景覆盖正常负载、拥塞、8/24/48/96 个逻辑设备、异构产生率、等优先级、弱链路、Markov 损失、突发、预算变化、反馈延迟、异包长和无损服务。

评价体系分别报告状态 AoI、替换率和发送成功率，以及事件及时交付、溢出和过期。资源公平性采用实际占用的抽象服务 slots，并给出等份和权重比例参考。各方法共享主窗口与停止到达后的公共尾窗，主截止点快照与最终结局分别记录。数学定义和控制条件见[指标文档](docs/metrics-v2.md)、[实验协议](research/experiments/protocol.md)与[冻结配置](configs/refined_v1/)。

<a id="key-findings"></a>

## 主要发现：精修版软件评估

主实验 3,900 次、固定总负载组 1,040 次、敏感性组 6,500 次、高负载桶容量组 1,040 次；每条条件均使用 seeds 100–119 和全部 13 种方法。敏感性各组保留自己的基准水平，重复基准在组内分析。状态 AoI 与 Service Share 仅统计主观察窗口，事件结局追踪至公共尾窗结束。

| 场景 | 方法 | 状态平均 AoI(s) ↓ | 事件 miss(%) ↓ | Jain Service Share ↑ |
| --- | --- | ---: | ---: | ---: |
| 拥塞 | FIFO | 2.2841 | 96.42 | 0.7159 |
| 拥塞 | AoI-gain | 4.8532 | 47.31 | 0.7441 |
| 拥塞 | FUD | 3.5046 | 63.15 | 0.8187 |
| 突发 | FIFO | 5.5966 | 33.91 | 0.9751 |
| 突发 | AoI-gain | 5.6617 | 13.83 | 0.9808 |
| 突发 | FUD | 5.5926 | 18.13 | 0.9818 |

**拥塞：** FUD−FIFO 的事件 miss 差为 -33.27238 [-33.59573, -32.98051] 个百分点，状态 AoI 差为 +1.22049 [+1.20904, +1.23202] s（95% 配对 bootstrap CI）。相对 AoI-gain，FUD 的事件 miss 更高、状态 AoI 更低。

**欠账消融：** 拥塞下 Service Share Jain 的变化为 +0.00052 [-0.00074, +0.00171]，区间跨零，该条件的资源公平性提升尚无明确方向。

**规模与模型控制：** A 组固定每流速率，B 组在 8/24/48/96 条流之间保持总负载和分类到达相同；桶容量 2/4/8/16 与其余七组参数检验适用条件。[A–K 报告](research/REPORT.md)给出五项研究问题、完整比较区间及有利和不利结果。

![状态时效、事件截止期与服务资源分配](output/study_refined_v1/overview.png)

![FUD 分量消融](output/study_refined_v1/ablations.png)

完整数据：[汇总](output/study_refined_v1/summary.csv) · [配对比较](output/study_refined_v1/paired_differences.csv) · [每流指标](output/study_refined_v1/per_flow.csv) · [不利方向](output/study_refined_v1/negative_results.csv) · [固定总负载](output/study_refined_v1/scaling/results.md) · [敏感性](output/study_refined_v1/sensitivity/results.md) · [高负载桶容量](output/study_refined_v1/bucket_load/results.md)。历史 v1 数据保留在 [output/study](output/study/results.md)。

<a id="implementation-status"></a>

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

<a id="quick-start"></a>

## 快速开始与复现

使用 Python 3.11 或更新版本，从项目目录创建环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,hardware]'
python -m pytest -q
```

运行包含 78 次仿真的软件示例，并生成报告：

```bash
python run.py run --config configs/refined_v1/pilot.json --out output/quickstart --workers 2
python run.py analyze --out output/quickstart
```

运行主实验矩阵：

```bash
python run.py run --config configs/refined_v1/main.json --out output/reproduction --workers 4
python run.py analyze --out output/reproduction
```

固定总负载和敏感性的完整命令见[复现指南](docs/reproducibility.md)。

每个新实验使用新输出目录；源码 hash 与配置一致时，可恢复已有实验。`hardware` extra 包含串口协议测试依赖和 PlatformIO。

审计复现生成的数据，或构建固件：

```bash
python scripts/audit_refined.py output/reproduction
pio run -d hardware/firmware
```

每次运行保存配置、种子、源码/轨迹 hash、逐包结局和调度决策。分析生成 CSV 汇总、配对 bootstrap 区间、PNG 图表和 Markdown 报告。环境信息记录在[requirements-lock.txt](requirements-lock.txt)和实验 [manifest](output/study_refined_v1/manifest.json)中。

仓库包含实验汇总、每流统计、报告和图表。逐包日志与历史源码快照保存在本地输出目录，运行上述配置可重新生成逐包记录。

## 相关研究项目

| 项目 | 研究重点 |
| --- | --- |
| [AdaptiveSense](https://github.com/Sver0411/AdaptiveSense) | 变化感知采样与上传决策 |
| [SensorTrust](https://github.com/Sver0411/SensorTrust) | 传感器健康评估与故障检测 |
| [EventGuard-LoRa](https://github.com/Sver0411/EventGuard-LoRa) | 关键事件交付与有界通信冗余 |
| [Smart-Agriculture-Edge-AI](https://github.com/Sver0411/Smart-Agriculture-Edge-AI) | 多节点感知、边缘决策与离线恢复 |

NetAdapt-IoT 聚焦网络级服务顺序，固定源端产生行为，研究多个设备与业务流如何共享通信机会。

## 文档与开发路线

| 主题 | 文档 |
| --- | --- |
| 方法与数学定义 | [研究方案](research/design/proposal.md) |
| 实验设计 | [实验协议](research/experiments/protocol.md) · [配置](configs/refined_v1/main.json) |
| 软件结构 | [架构说明](docs/architecture.md) |
| 结果与数据 | [结果报告](output/study_refined_v1/results.md) · [统计 CSV](output/study_refined_v1/summary.csv) |
| 复现与审计 | [复现指南](docs/reproducibility.md) · [审计记录](output/study_refined_v1/audit.json) |
| 硬件与开发 | [硬件指南](hardware/README.md) · [路线图](docs/roadmap.md) |

下一阶段的开发重点：

- 在 ESP32-S3/E220 链路上校准单帧传输、ACK 时序与有效服务率。
- 将共享逻辑流负载重放到物理通信出口。
- 扩展独立发送节点与网络接入控制实验。
- 评估更长流量轨迹、更多调度方法及实际通信能耗。
