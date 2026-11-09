# 软件架构

NetAdapt-IoT 使用 Python 离散时隙模型，围绕外生流量、共享队列、调度决策和延迟反馈组织实验。算法原型、实验管理和统计分析通过统一配置连接。

~~~mermaid
flowchart LR
  C[JSON 配置] --> T[流量与信道轨迹]
  T --> Q[业务队列]
  Q --> S[13 种调度方法]
  S --> L[共享出口与预算]
  L --> A[ACK 反馈与 AoI 状态]
  A --> S
  L --> R[逐包记录与指标]
  R --> E[配对统计与图表]
  S -.调度接口.-> H[PC 逻辑流与 ESP32 单链路]
~~~

| 文件 | 职责 |
|---|---|
| src/netadapt/model.py | 配置、流类型、服务时间与场景 |
| src/netadapt/traffic.py | 外生到达与按绝对时刻索引的信道结果 |
| src/netadapt/queues.py | 最新状态替换、事件 FIFO 与过期处理 |
| src/netadapt/scheduler.py | 九种基线、FUD 与三种消融 |
| src/netadapt/simulation.py | 时隙循环、反馈事件堆、服务预算与逐包账本 |
| src/netadapt/metrics.py | cohort 交付指标、状态 AoI、吞吐与公平性 |
| src/netadapt/runner.py | 多进程实验、manifest、运行记录与恢复 |
| src/netadapt/analysis.py | seed 配对统计、结果表与图表 |
| src/netadapt/cli.py | 配置生成、运行与分析命令 |
| hardware/protocol.py、hardware/run.py | 串口协议与逻辑流重放 |
| hardware/firmware | ESP32 双端 UART 桥、CRC、ACK 与参数读取 |

业务需求通过 Flow 配置表达。源端到达率、资源预算和信道过程共同决定负载；调度器负责分配可用服务机会。流级准入与拥塞反馈是后续扩展方向。

每个 slot 按以下顺序执行：处理反馈 → 接收新包 → 更新队列 → 清理过期事件 → 更新欠账与吞吐 EWMA → 补充预算 → 调度传输 → 记录指标。截止期比较包含等号，逐包结局按互斥状态保存。

## 第一轮精修

仿真分为主期与公共尾窗：主期产生流量；尾窗继续预算、调度与反馈，不产生新包。主窗口指标与尾窗账本分列。`metrics.summarize` 保存 legacy 保护区口径；`metrics.classified` 计算 v2 分类指标。每包在主截止点有状态快照，结束时只有一个最终结局。

资源公平性直接从每个服务区间与观察窗口的交集累计；失败尝试计入占用。独立审计程序 `scripts/audit_refined.py` 从压缩逐包日志与调度日志重算指标，不调用指标汇总实现。

PF 共用 `scheduler.pf_update`，初值每流 1 byte/slot，alpha=0.01；仿真按到期 ACK 所属 slot 更新，硬件重放将主机 ACK 完成时刻量化到下一个逻辑边界。FUD 仍使用原评分与原及时/新鲜 ACK 欠账更新。

固定总负载轨迹先按三类业务生成 Poisson 到达，再均匀拆分到同类逻辑流；同种子跨规模保留分类到达过程。敏感性使用独立配置，不增加算法分支。
