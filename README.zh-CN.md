<h1 align="center">NetAdapt-IoT</h1>

<p align="center"><strong>面向共享 IoT 网关的尺度匹配新鲜度、截止期与公平性自适应调度框架</strong></p>

<p align="center">信息年龄 AoI · 截止期感知调度 · 公平资源分配 · ESP32-S3 纯 C11 零分配实测</p>

---

<p align="center">
  <a href="#overview">概览</a> ·
  <a href="#method-and-architecture">调度方法</a> ·
  <a href="#experimental-results">实验结果</a> ·
  <a href="#embedded-c11-kernel-and-esp32-s3-benchmarks">ESP32-S3 C11 实测</a> ·
  <a href="#quick-start">快速开始</a> ·
  <a href="papers/netadapt-iot/manuscript.pdf">IEEE 论文 (PDF)</a> ·
  <a href="README.md">English</a>
</p>

---

<a id="overview"></a>

## 项目概览

**NetAdapt-IoT** 是一个面向多业务共享 IoT 网关出口的开源研究平台与嵌入式 C11 调度内核，研究在带宽受限、业务突发和真实无线丢包条件下，如何同时平衡**周期状态新鲜度（AoI）**、**硬截止期报警事件交付**以及**多设备服务公平性**。

项目整合了 **17,820 次审计仿真运行（15 种策略）**、**24 条真实 ESP32-S3 + E220-400T22D Sub-GHz 硬件丢包日志**（3,359 次实测射频尝试）、**MIT Intel Berkeley 54 节点真实无线传感网流量**以及 **ESP32-S3 240 MHz 真机片上基准**：

- **尺度匹配调度器 `FUD-Ada`**（`src/netadapt/ext/adaptive_scheduler.py`）：将亚二次状态新鲜度 $w_i\sqrt{G_i(t)}$、截止期余量紧迫度放大 $w_i(1+v_p/\tau_i)(1+\alpha_u/(1+\sigma_p^+))$ 与 Lyapunov 对数欠账 $\beta_d w_i \ln(1+d_i(t))$ 结合，在合成拥塞（`36.92%`）、突发负载（`7.42%`）和真实 E220 硬件日志（`53.17%`）下均取得**全部 14 个对比策略最低事件错失率**，并在真实 54 节点 Intel Berkeley 流量上四项指标同时严格帕累托支配 `EDF` 与 `MaxWeight`。
- **可验证的公平性收益**：在全部三大评测队列上均显著验证了欠账项的独立公平性增益（`FUD-Ada` vs. `FUD-Ada-NoDebt`：原始 Jain `+0.045–0.059`、加权 Jain `+0.055–0.081`，全部 $p_{\text{Holm}} \le 0.0364$）。
- **零动态分配纯 C11 嵌入式内核（ESP32-S3 真机实测）**（`src/netadapt/c11/`）：96 并发流仅占 **4,624 B（4.52 KB）静态 RAM** 与 **2,746 B（2.68 KB `.text`）Flash**；在真实 **240 MHz ESP32-S3** 上连续运行堆变化严格为 **0 B**，单时隙耗时 **0.20–2.91 ms**（占 100 ms 时隙 `<2.91%`），与 Python 参考轨迹实现 **24/24 位级一致**（误差 `< 1e-11`）。
- **完整学术与工程闭环**：附带 8 页独立 IEEEtran 英文论文（[manuscript.pdf](papers/netadapt-iot/manuscript.pdf)）、9 种经典基线（`FIFO`/`RR`/`WRR`/`EDF`/`Priority`/`MaxWeight`/`PF`/`AoI-Gain`/`Debt`）、参考版 `FUD`、全套消融与 **74 项通过的 Python + C11 测试**。

![NetAdapt-IoT Graphical Abstract](papers/netadapt-iot/graphical_abstract.png)

---

<a id="method-and-architecture"></a>

## 调度方法与系统模型

多个 IoT 设备共享单个受限网关出口（默认 100 ms 时隙、64 B 载荷、16 B 抽象头部、6,400 bit/s 有效速率及 Token 桶预算管理）：状态流采用最新覆盖队列，事件流采用有限 FIFO 队列。

```mermaid
flowchart LR
    CFG["配置与种子"] --> TRACE["流量与信道 / E220 轨迹"]
    TRACE --> QUEUE["最新覆盖状态队列 / FIFO 事件队列"]
    QUEUE --> SCHED["FUD-Ada / FUD / 9 种经典基线"]
    SCHED --> LINK["共享出口与 Token 桶预算"]
    LINK --> ACK["ACK 反馈"]
    ACK --> SCHED
    LINK --> LOG["逐包记录"]
    LOG --> ANALYSIS["指标、Holm 统计检验与图表"]
```

`FUD-Ada` 在每个时隙以严格 $O(N)$ 复杂度对所有满足预算的队首包打分（结合 ACK 成功率估计与服务成本归一化）：

1. **亚二次新鲜度**：$w_i\sqrt{G_i(t)}$ 避免拥塞下状态分值二次膨胀而淹没紧急事件。
2. **截止期可行紧迫度**：$w_i(1+v_p/\tau_i)(1+\alpha_u/(1+\sigma_p^+))$ 在截止期余量 $\sigma_p^+$ 收紧时显著放大紧急事件优先级，并自然跳过已过期包。
3. **Lyapunov 对数欠账**：$\beta_d w_i \ln(1+d_i(t))$ 在不抢占紧急截止期的前提下防止弱势流长期饿死（于独立校准集 `200–204` 冻结 $\alpha_u=1.0, \beta_d=2.5$）。

仓库同时完整保留了参考版二次 AoI 调度器 `FUD`（`1 / 1 / 0.25`，位于 `src/netadapt/scheduler.py`）、9 种经典基线以及完整分量消融。详见[方法说明](research/design/proposal.md)与[指标定义](docs/metrics-v2.md)。

---

<a id="experimental-results"></a>

## 实验结果

### 1. 合成压力、真实 E220 硬件日志与 54 节点真实传感网评测

在 **5,340 次严格留出运行**（20 个独立种子 `300–319` + 12 个真实 Intel Berkeley 日期）上采用配对自助法 95% 置信区间与全局 Holm-Bonferroni 校正：

| 评测队列 | 策略 | 事件 Miss (%) ↓ | 状态平均 AoI (s) ↓ | 原始 Jain ↑ | 加权 Jain ↑ |
| :--- | :--- | ---: | ---: | ---: | ---: |
| **合成拥塞**（20 留出种子） | `FIFO` | 96.32 | 2.28 | 0.7167 | 0.5499 |
| | `EDF` | 46.54 | 10.27 | 0.7101 | 0.8975 |
| | `AoI-Gain` | 46.84 | 4.83 | 0.7443 | 0.9600 |
| | `MaxWeight` | 37.95 | 103.24 | 0.5822 | 0.5033 |
| | `FUD`（参考版） | 62.75 | 3.50 | 0.8201 | 0.9560 |
| | **`FUD-Ada`（本文）** | **36.92** | **8.09** | **0.6293** | **0.8089** |
| **真实 E220 硬件日志**（24 条，拥塞） | `FIFO` | 97.11 | 2.87 | 0.7167 | 0.5499 |
| | `EDF` | 57.72 | 12.69 | 0.7101 | 0.8975 |
| | `AoI-Gain` | 58.79 | 5.68 | 0.7505 | 0.9680 |
| | `FUD`（参考版） | 75.49 | 3.76 | 0.8126 | 0.9124 |
| | **`FUD-Ada`（本文）** | **53.17** | **8.44** | **0.6650** | **0.8622** |
| **真实 54 节点 Intel × E220**（12 天） | `FIFO` | 98.18 | 19.16 | 0.6564 | 0.5214 |
| | `EDF` | 69.80 | 53.05 | 0.5826 | 0.6572 |
| | `MaxWeight` | 82.51 | 81.99 | 0.4706 | 0.3451 |
| | `AoI-Gain` | **61.72** | **22.15** | 0.7004 | 0.9113 |
| | `FUD`（参考版） | 87.84 | 19.19 | 0.6338 | 0.7528 |
| | **`FUD-Ada`（本文）** | **63.86** | **24.01** | **0.6666** | **0.8275** |

- **全基线最低事件 Miss**：在合成拥塞（`36.92%`）、4 倍突发（`7.42%`）与 **24 条真实 E220 硬件丢包日志**（`53.17%`）下均取得全部 14 个对比策略最低事件错失率（全部 $p_{\text{Holm}}=0.0096$；相对 `EDF` 同时压低状态 AoI `−2.18 s` 至 `−4.25 s`，相对参考版 `FUD` 降低 `−22.3` 至 `−25.8 pp`）。
- **真实 54 节点 Intel Berkeley 流量四指标严格帕累托支配 `EDF` 与 `MaxWeight`**：相对 `EDF` 实现事件 Miss `−5.94 pp`、状态 AoI `−29.03 s`（`−54.7%`）、原始 Jain `+0.084`、加权 Jain `+0.170`（全部 $p_{\text{Holm}} \le 0.0392$）。同时如实披露：`AoI-Gain` 在真实异步突发下与 `FUD-Ada` 事件错失率统计学打平（`61.72%` vs. `63.86%`, $p_{\text{Holm}}=0.927$）且 AoI 略优。
- **欠账公平性消融全面显著（`FUD-Ada` vs. `FUD-Ada-NoDebt`）**：合成拥塞 `+0.0486` 原始 / `+0.0812` 加权 Jain 且 AoI 降 `−2.23 s`（$p_{\text{Holm}}=0.0096$）；真实 E220 `+0.0447` / `+0.0652` Jain 且 AoI 降 `−1.49 s`（$p_{\text{Holm}}=0.0096$）；真实 54 节点 Intel Berkeley `+0.0586` / `+0.0550` Jain（$p_{\text{Holm}}=0.0364$，且无显著事件错失代价 $p_{\text{Holm}}=0.141$）。

![合成拥塞与突发帕累托前沿](output/phase2_validation/figures/fig02_pareto_stress.png)

![真实 ESP32-S3 + E220 Sub-GHz 硬件丢包日志验证](output/phase2_validation/figures/fig03_e220_hardware_traces.png)

![真实 54 节点 Intel Berkeley 负载与欠账公平性消融](output/phase2_validation/figures/fig04_intel_real_traffic.png)

### 2. 全场景敏感性与参考 `FUD` 基准矩阵

配套的 **12,480 次软件敏感性矩阵**（覆盖 8/24/48/96 逻辑流规模扩展、固定每流 vs. 固定总负载、Markov 丢包、反馈延迟、异构包长及 Token 桶容量 `2/4/8/16`，共 48 条命名条件）完整刻画了各参数边界及未缩放二次参考版 `FUD` 的基线权衡。

![15 个场景下的状态时效、事件截止期与服务资源分配](output/study_refined_v1/overview.png)

[IEEEtran 英文论文 (PDF)](papers/netadapt-iot/manuscript.pdf) · [实证与 C11 中文技术报告](docs/PHASE2_HARDWARE_REALDATA_C11_ZH.md) · [敏感性与假设报告](research/REPORT.md) · [配对效应 CSV](output/phase2_validation/paired_effects.csv)

---

<a id="embedded-c11-kernel-and-esp32-s3-benchmarks"></a>

## 零分配纯 C11 内核与 ESP32-S3 真机实测

核心调度器（`src/netadapt/c11/netadapt_sched.h` / `.c`）采用零动态分配 ISO C11 实现（`-std=c11 -Wall -Wextra -Werror`），并在宿主机与 **ESP32-S3 N16R8 真机**（`hardware/firmware/`，PlatformIO `c11_bench` / `sender` / `receiver`）上完成实测：

| 指标 | 实测值 |
| :--- | :--- |
| 静态 RAM（`sizeof(na_sched_t)`，支持 96 并发流） | **4,624 B（4.52 KB）**，仅占 ESP32-S3 SRAM 的 0.88% |
| ESP32-S3 Xtensa `-Os` Flash（`netadapt_sched.o`，8 策略） | **2,746 B（2.68 KB `.text`）**，`0 B .data`，`0 B .bss` |
| **ESP32-S3 240 MHz 真机运行时堆变化**（`ESP.getFreeHeap()`） | **0 B**（20 组连续基准前后均为 `361,620 B`） |
| **ESP32-S3 240 MHz 真机单时隙实测耗时**（`FUD-Ada`，`N=8/24/48/96`） | **0.20 / 0.67 / 1.39 / 2.91 ms**（占 100 ms 时隙 `<2.91%`，软件 FP64） |
| 宿主机 arm64 $O(N)$ 单时隙耗时（`FUD-Ada`，`N=8/24/48/96`） | **0.15 / 0.37 / 0.66 / 1.20 µs**（Apple clang `-O2`，5 万次均值） |
| Python–C11 位级轨迹一致性（状态误差 `< 1e-11`） | **24 / 24 全轨迹零偏差**（8 策略 × 3 场景） |

![纯 C11 ESP32-S3 真机扩展性与资源占用](output/phase2_validation/figures/fig05_c11_scaling.png)

[ESP32-S3 真机实测 JSON](output/phase2_c11/esp32s3_onchip_benchmark.json) · [宿主机 C11 基准 JSON](output/phase2_c11/benchmark.json) · [硬件指南](hardware/README.md)

---

<a id="quick-start"></a>

## 快速开始与复现

需要 **Python 3.11+**，在仓库根目录执行：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,hardware]'
python -m pytest -q
```

运行快速示例或复现完整真实轨迹、敏感性、C11 与固件套件：

```bash
# 78 次软件快速示例
python run.py run --config configs/refined_v1/pilot.json --out output/quickstart --workers 2
python run.py analyze --out output/quickstart

# 真实 E220 / Intel Berkeley 验证、C11 基准与 IEEE 插图生成
python scripts/benchmark_c11_footprint.py
python scripts/run_phase2_real_validation.py --workers 6
python papers/netadapt-iot/build_figures.py

# 全量 15 场景敏感性矩阵与 ESP32-S3 固件编译
python run.py run --config configs/refined_v1/main.json --out output/reproduction --workers 4
python run.py analyze --out output/reproduction
python scripts/audit_refined.py output/reproduction
pio run -d hardware/firmware
```

## 文档索引与相关项目

| 主题 | 文档 |
| :--- | :--- |
| 独立 IEEEtran 英文论文 | [论文 PDF](papers/netadapt-iot/manuscript.pdf) · [LaTeX 源码](papers/netadapt-iot/manuscript.tex) · [Graphical Abstract](papers/netadapt-iot/graphical_abstract.png) |
| 实证与 C11 报告数据 | [中文技术报告](docs/PHASE2_HARDWARE_REALDATA_C11_ZH.md) · [汇总 CSV](output/phase2_validation/summary.csv) · [ESP32-S3 JSON](output/phase2_c11/esp32s3_onchip_benchmark.json) |
| 方法与敏感性研究 | [研究方案](research/design/proposal.md) · [假设与敏感性报告](research/REPORT.md) · [架构说明](docs/architecture.md) |
| 复现与硬件验证 | [复现指南](docs/reproducibility.md) · [硬件指南](hardware/README.md) · [验证记录](docs/validation/status.md) |

**相关研究仓库：** [SensorTrust](https://github.com/Sver0411/SensorTrust)（L1 健康监测） · [AdaptiveSense](https://github.com/Sver0411/AdaptiveSense) 与 [TAIS](https://github.com/Sver0411/TAIS)（L2 自适应观测） · [EventGuard-LoRa](https://github.com/Sver0411/EventGuard-LoRa) 与 [IoT-MPQUIC-Scheduler](https://github.com/Sver0411/IoT-MPQUIC-Scheduler)（L3 弱网传输） · [Smart-Agriculture-Edge-AI](https://github.com/Sver0411/Smart-Agriculture-Edge-AI)（L4 智慧农业 CPS）。

**后续探索方向：** 物理多节点 MAC 竞争实测、双板 ESP32-S3/E220 射频功耗示波器采集与更长周期多周真实轨迹重放。
