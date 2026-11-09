# 第一轮模型审查

审查基线：`1b302342`。原始结果、配置、manifest、audit 和报告保存在原路径及 `output/archive/refinement_baseline/`；文件摘要见 baseline_inventory.json。

| 项目 | 当前行为 | 本轮处理 |
|---|---|---|
| 到达与竞争 | 独立 Poisson；单不可抢占服务器；按绝对 slot/flow 共享随机信道 | 保留；扩展尾窗的信道轨迹 |
| 状态与事件队列 | 状态只保留最新待发包；事件有限 FIFO，tail drop | 保留；分别统计替换与溢出 |
| 截止期 | 到达时刻含服务和反馈；等于 deadline 及时；不可及时到达的队首提前过期 | 保留；明确 expired 是可行性淘汰 |
| 预算与服务 | 每 slot 补充 duty，启动时预留整数服务成本；失败同样耗资源 | 保留；增加实际占用窗口裁切的每流 Service Share |
| 结束处理 | 保护 cohort 排除末尾生成包；全量记录仍有 queued/inflight | 新增停止到达后的固定公共尾窗、主截止点快照、终态守恒 |
| AoI | slot 边界处理 ACK 后积分；初始接收时间戳 0 | 保留主窗口定义；尾窗不进入 AoI |
| PDR/公平性 | 状态替换、事件过期、链路失败汇入总 PDR；Jain(PDR) 表示交付比例均衡 | 保留 legacy 字段；v2 增加分类交付指标、实际服务资源公平性 |
| 节点规模 | 固定每节点速率同时改变总到达量 | 保留 A；新增总到达率及三类负载份额固定的 B |
| 模型敏感性 | Markov 转移写死；桶容量固定 4 | 参数化转移；独立单因素配置和物理时间保持的离散化组 |
| PF | 仿真逐 slot 衰减；重放逐事务衰减 | 共用逻辑 slot EWMA；成功 ACK 字节记于反馈所属边界，失败为零 |
| N16R8 | N8 板定义叠加 flash/OPI overrides，板元数据仍为 N8 | 建立含真实 flash/OPI 设置的本地板定义；分别构建双端 |

FUD choose 方法的 AST 摘要与欠账公式固定记录在 fud_invariant.json。新实验使用 metric_version=2，输出到 study_refined_v1。各指标的分母及尾窗裁切规则在指标文档中定义。
