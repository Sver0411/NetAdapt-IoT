# FUD 调度方法与网络模型

## 研究问题

多个 IoT 逻辑设备共享受限出口时，如何联合信息时效、事件截止期与服务欠账安排发送顺序？

## 研究假设

- H1：相对 FIFO、EDF、MaxWeight、PF 和 AoI-gain，FUD 的事件及时交付如何变化？
- H2：事件截止期改善对应怎样的状态 AoI 变化？
- H3：相对 fud_no_debt，欠账机制能否提高原始及权重归一化 Service Share Jain？
- H4：固定每节点速率和固定总速率两种规模设计中，FUD 的表现如何变化？
- H5：桶容量、预算、服务率、链路与离散化条件如何影响上述比较？

FUD 系数为 1、1、0.25。开发 seeds 0、1，正式 seeds 100–119。第一轮精修固定核心公式和欠账更新，新增分类指标、公共尾窗、负载控制和单因素实验。

## 网络模型

单共享出口服务 N 条流，每流对应一个逻辑设备。默认参数：

| 参数 | 值 |
|---|---|
| 时隙 dt | 0.1 s |
| payload | 64 B |
| 抽象协议开销 | 16 B |
| 有效服务率 | 6400 bit/s |
| 服务时间 | s=ceil(8(L+16)/(6400×0.1)) slots |
| 传播与反馈延迟 d | 1 slot |
| 预算补充 duty | 0.8/slot |
| 预算桶容量 | 4 个服务 slots |

流类别按 event、status、telemetry 轮换。event 权重 4、截止期 6 slots；status 权重 3、AoI 目标 12 slots；telemetry 权重 1、AoI 目标 30 slots。后两类保留最新待发更新，event 使用最多 32 包的 FIFO。

外生到达采用 Poisson、异速率或预定窗口四倍突发。单服务器提供不可抢占服务，每次尝试占用 s slots。包从发送队列移除，反馈于 t+s+d 到达；失败尝试同样计入资源成本。

状态接收时间戳取所有成功交付时间戳的最大值。event 按 arrival≤generation+deadline 判为及时；最早可达时间已超过截止期的等待包在队列中清理。

每个 slot 补充 duty 个 tokens，开始服务扣除 s。信道采用独立损失或按流二态 Markov 状态。潜在结果由绝对 slot 与 flow 索引；决策使用历史 ACK 的 EWMA 成功率，初值 0.8，步长 0.1。

## FUD 公式

t 时，队首包生成于 g_i，最近成功更新生成于 u_i。定义：

- A_i=t−u_i：接收端 AoI。
- w_i=t−g_i：队首包等待时间。
- c_i=t+s_i+d：本次传输预计到达时间。

状态流的新鲜度收益：

    G_i = weight_i × max(0, (A_i+s_i+d)^2 − (w_i+s_i+d)^2) / (2 tau_i^2)

event 的紧迫度：

    U_i = weight_i × (1+w_i/deadline_i) / (1+max(0,g_i+deadline_i−c_i))

event 的 G_i=0，状态流的 U_i=0。服务欠账更新为：

    D_i(t+1) = min(50,max(0,D_i(t)+r_i×I(queue_i nonempty)−Y_i(t)))
    r_i = 0.5×duty×0.8×weight_i / (sum_j weight_j×s_i)

Y_i 为本 slot 收到的及时 event 或新鲜 state 包数。最终评分：

    score_i = p_hat_i × (G_i + U_i + 0.25 D_i) / s_i

选择分数最大的可服务队首包，依次以生成时间与 flow id 打破平局。输入包括队列、最新生成时间戳、成功率估计、欠账、业务参数与当前预算，输出一个包或 idle。

G_i 由平方 AoI 的单步变化构造，D_i 采用虚拟服务队列，U_i 表达截止期余量。决策复杂度 O(N)，状态空间 O(N+总队列长度)，过期扫描最坏 O(总队列长度)。

## 对照与消融

FIFO 选择全局最早队首；RR 逐流轮询；WRR 按权重 4/3/1 分配服务次数。EDF 使用 event 截止期，并为状态流设置 generation+tau 的软时限。Priority 使用固定业务权重。

MaxWeight 使用 p_hat×queue_bytes/s；PF 使用预期 payload 服务率与 EWMA 交付吞吐之比。AoI-gain 使用 p_hat×G/s，并以 event 的 deadline 作为 tau；Debt 使用 p_hat×D/s。

三个消融分别去除 G、U、D。各方法共享输入轨迹、队列策略、预算和反馈时序。

## 指标定义与版本

主期为 `[0,T)`，稳态观察为 `[warmup,T)`，公共尾窗停止新到达并判定剩余结果。状态 AoI 与实际服务资源占用仅在主观察窗口计算，v2 生成 cohort 覆盖主观察窗口并追踪至尾窗结束。主截止点快照与最终终态分别记录。

状态业务报告 Mean/Normalized AoI、替换率、已判定尝试成功率、Goodput；事件报告 deadline success/miss、late、overflow、expiration 和交付时延/P95。pending 作为结束删失单列。

资源公平性使用主观察窗口内每流实际消耗的抽象服务 slots，含失败尝试；报告 Jain(S)、Jain(S/weight)、每流 share、Goodput 与业务 QoS。状态 QoS 为 AoI 达标时间比例；事件 QoS 为及时交付比例。

数学定义、分母及 legacy v1 字段见 [指标文档](../../docs/metrics-v2.md)。规模 A 固定每流速率；规模 B 固定总速率和三类业务负载份额。完整设计见 [实验协议](../experiments/protocol.md)。

PF 初始化每流 1 byte/slot，逐逻辑 slot 更新 `throughput=0.99*throughput+0.01*成功 ACK payload bytes`。失败及无 ACK slot 的字节数为零；物理重放 ACK 完成时刻向上取整到逻辑边界。FUD 的 Y_i 仍为及时 event / 新鲜 state 包数。

## 模型与后续实验

仿真采用已知包时间戳和固定反馈延迟。按流 Markov 状态表达逻辑链路差异；物理实验将采集单共享出口的事务时序与 ACK 结果。

当前重点评估过载、稀疏更新、链路变化、长包和反馈延迟。物理校准、独立节点接入与能耗采集按[开发路线](../../docs/roadmap.md)推进。

预算桶修订与历史版本对比见[修订记录](../../docs/validation/implementation_correction.md)。
