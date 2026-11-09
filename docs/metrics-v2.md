# 指标与窗口定义（v2）

## 时间与生命周期

设主截止点为 T，预热截止为 W，公共尾窗长度为 H，终点 E=T+H。生成期为整数 slot `[0,T)`；主观察窗口为 `[W,T)`；尾窗为 `[T,E)`。所有策略使用相同窗口。每个 slot 先处理到期 ACK，再接收入队、清理不可及时到达事件、更新调度状态、补充 tokens、选择服务，最后采样 AoI 和队长。

尾窗停止新到达，继续采用原队列、调度和预算规则。默认 `H=deadline+ceil((N+1)*s_max/duty)+s_max+delay+2`：事件结局判定后，为每条流至多一个待发状态包和一个在服任务预留预算与反馈时间。`tail_slots` 可显式设为非负整数，用于结束删失测试。主截止点处理 ACK 前记录 `status_at_main_cutoff`；终点 E 的到期 ACK 仍完成判定。尾窗的服务、结局和交付字节单列。

一个包最终只属于以下一个结局：

| 结局 | 定义 |
|---|---|
| delivered | 成功交付；事件到达时刻不超过 `generation+deadline` |
| late | 成功交付但事件超过截止期；当前固定时延与可行性清理机制通常使其计数为零 |
| replaced | 待发状态更新被同流的新更新替换；在途包继续完成 |
| overflow | 事件 FIFO 满，拒绝新包 |
| expired | 等待事件的 `t+service+delay > generation+deadline`，即使立即开始也无法及时到达 |
| link_loss | 已发送尝试得到预生成的失败结果 |
| pending_at_cutoff | E 时仍排队或在途；`pending_kind` 记录两者区别，`finished` 为空 |

`total_generated = sum(status_counts)` 覆盖全部生成包。`observed_generated = sum(observed_status_counts)` 覆盖 `W≤generation<T` 的 v2 生成 cohort。主截止点的待处理快照不参与终态求和。事件 deadline 等号边界计为及时。没有重传。

## 状态流

status、telemetry 为状态流。设 `u_i(t)` 为 ACK 已确认的最新生成时间戳，初值为 0；`L=(T-W)*dt`。

- `aoi_s_i = dt/(T-W) * Σ[t=W..T-1](t-u_i(t))`；总体 Mean AoI 对状态流等权平均。
- `normalized_aoi_i = aoi_s_i/(tau_i*dt)`；总体对状态流等权平均。
- `state_replacement_rate = replaced_state / generated_state`，生成数来自 v2 cohort。
- `state_transmission_success = (delivered_state+late_state)/(delivered_state+late_state+link_loss_state)`；仅统计已得到结果的发送尝试。`state_pending_attempts` 单列。
- `state_goodput_bps = 8*成功交付的状态 cohort payload bytes/L`，含该 cohort 在尾窗完成的交付。

替换是最新状态队列的管理结果，链路失败是发送尝试的结果。空分母记为 JSON null / CSV 空值。

## 事件流

令 N 为 v2 cohort 事件生成数，P 为终点尚未判定数，R=N-P 为已判定数。D、A、O、X 分别为 delivered、late、overflow、expired 计数。

| 字段 | 计算 |
|---|---|
| event_deadline_success | D/R |
| event_deadline_miss | (R-D)/R |
| event_late_ratio | A/R |
| event_overflow_rate | O/N |
| event_expiration_rate | X/N |
| event_latency_s | 已成功交付事件 `(received-generated)*dt` 的均值 |
| event_p95_latency_s | 同一成功交付集合的 NumPy 第 95 百分位 |

`event_observed_generated`、`event_resolved`、`event_pending` 明列分母。短尾窗留下的事件列为 pending；未完成状态不进入已判定事件分母。正式实验的公共尾窗完成全部事件判定。时延分布条件于交付成功，配合 miss 一起解读。

## 资源与每流服务

调度决定 `(t,i,s)` 实际占用服务区间 `[t,t+s)`。观察资源 `S_i=Σ |[t,t+s)∩[W,T)|`；尾窗资源单独裁切到 `[T,E)`。失败尝试同样计入资源。发送开始时预留的完整服务成本另记为 reserved_slots。

- `service_share_i = S_i/ΣS_j`。
- `jain_service_share = (ΣS_i)^2/(N*ΣS_i^2)`，参考为每条配置流等份。
- `jain_weighted_service_share = (Σ(S_i/weight_i))^2/(N*Σ(S_i/weight_i)^2)`，参考为权重比例分配；`weight_reference_share=weight_i/Σweight`。
- `goodput_bps_i = 8*该流 v2 cohort 最终成功 payload bytes/L`；总体按字节求和。
- `qos_satisfaction_i`：事件为 deadline success；状态为主观察 slot 中 AoI 不超过 `tau_i*dt` 的比例。

资源向量包含全部配置流；全零向量 Jain=0，无资源时每流 share 为 null。Jain 描述实际分配的均衡程度；同时给出负载、权重参考和业务 QoS。这里的资源单位为共享网关出口的抽象服务 slot。

`observation_goodput_bps` 按 `[W,T)` 内实际收到的 payload bytes/L 计算，与生成 cohort goodput 分列。

## 历史字段

`metric_version=2` 明列新增口径。`legacy_metric_version=1` 对应保留的 `pdr`、`event_miss`、`jain_pdr`、`jain_delivery`、`latency_s`、`p95_latency_s`、`cohort_goodput_bps` 及每流 generated/delivered/pdr 字段：生成 cohort 为 `[W,T-guard)`，结局取原停止边界处理完 t=T 的 ACK 后，`guard=deadline+s_max+delay`。每流新增 `observed_generated`、`v2_status_counts` 对应 v2 cohort。`status_counts` 为 v2 最终全量结局；`cohort_status_counts` 保留 legacy 保护区口径。

`output/study/` 的 v1 文件保持原样。跨版本比较只对相同定义的字段进行；v1 PDR 与 v2 状态发送成功率属于不同分母。

## 规模解释与参数效应的后处理

固定总负载下，每流产生率随流数下降。为分解接收 AoI，令 `v_i(t)` 为截至 t 已生成的最新源端时间戳，初值 0；即时无损交付的基线为 `A_source_i=dt/(T-W)*Σ(t-v_i(t))`。`A_excess_i=A_receiver_i-A_source_i` 包含排队、服务、反馈和链路失败的共同影响。按状态流等权汇总，并对 seed 均值给出 CI。数据见 [scaling_controls_summary.csv](../output/study_refined_v1/scaling_controls_summary.csv)。

同一策略的参数效应为每 seed 的 `metric(level)-metric(reference)`，然后按 20 个 seed 配对 bootstrap。各因素基准写入 model_contrasts.csv；其中 pdr 保持 legacy v1 保护区定义。正常负载和拥塞桶容量分别分析。
