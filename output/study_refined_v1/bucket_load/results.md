# 仿真实验结果（metric version 2）
共 1040 次运行。每个场景使用共同到达与信道轨迹；配置、源码摘要与软件环境见 manifest.json。
主窗口到达 cohort 追踪至公共尾窗结束；AoI 和 Service Share 仅统计主观察窗口。

## FUD 场景表现


| 场景 | 状态 AoI(s) | 事件 miss(v2) | Jain Service Share | 加权 Jain | Goodput(bit/s) |
|---|---:|---:|---:|---:|---:|
| congested_bucket_16 | 3.50460 | 0.63152 | 0.81870 | 0.95527 | 3904.14629 |
| congested_bucket_2 | 3.50460 | 0.63152 | 0.81870 | 0.95527 | 3904.14629 |
| congested_bucket_4 | 3.50460 | 0.63152 | 0.81870 | 0.95527 | 3904.14629 |
| congested_bucket_8 | 3.50460 | 0.63152 | 0.81870 | 0.95527 | 3904.14629 |

## 配对比较

差值为 FUD − 对照，区间为对 seed 配对差值进行 2,000 次 bootstrap 的 95% CI。AoI/miss 越低越好，Service Share Jain 越高越均衡。完整比较见 paired_differences.csv。

| 场景 | 对照 | 指标 | 差值 | 95% CI |
|---|---|---|---:|---|
| congested_bucket_16 | aoi_gain | mean_aoi_s | -1.34862 | [-1.37831, -1.32085] |
| congested_bucket_16 | aoi_gain | event_deadline_miss | 0.15837 | [0.15437, 0.16185] |
| congested_bucket_16 | aoi_gain | jain_service_share | 0.07460 | [0.07164, 0.07765] |
| congested_bucket_16 | edf | mean_aoi_s | -6.61740 | [-6.95567, -6.35104] |
| congested_bucket_16 | edf | event_deadline_miss | 0.16231 | [0.15867, 0.16551] |
| congested_bucket_16 | edf | jain_service_share | 0.10977 | [0.10625, 0.11331] |
| congested_bucket_16 | fifo | mean_aoi_s | 1.22049 | [1.20904, 1.23202] |
| congested_bucket_16 | fifo | event_deadline_miss | -0.33272 | [-0.33596, -0.32981] |
| congested_bucket_16 | fifo | jain_service_share | 0.10282 | [0.09956, 0.10585] |
| congested_bucket_16 | maxweight | mean_aoi_s | -104.24304 | [-108.18591, -100.44866] |
| congested_bucket_16 | maxweight | event_deadline_miss | 0.24535 | [0.23491, 0.25557] |
| congested_bucket_16 | maxweight | jain_service_share | 0.23701 | [0.22705, 0.24694] |
| congested_bucket_16 | pf | mean_aoi_s | 0.94619 | [0.93237, 0.95987] |
| congested_bucket_16 | pf | event_deadline_miss | -0.06250 | [-0.06579, -0.05978] |
| congested_bucket_16 | pf | jain_service_share | -0.18092 | [-0.18313, -0.17868] |
| congested_bucket_2 | aoi_gain | mean_aoi_s | -1.34862 | [-1.37831, -1.32085] |
| congested_bucket_2 | aoi_gain | event_deadline_miss | 0.15837 | [0.15437, 0.16185] |
| congested_bucket_2 | aoi_gain | jain_service_share | 0.07460 | [0.07164, 0.07765] |
| congested_bucket_2 | edf | mean_aoi_s | -6.61740 | [-6.95567, -6.35104] |
| congested_bucket_2 | edf | event_deadline_miss | 0.16231 | [0.15867, 0.16551] |
| congested_bucket_2 | edf | jain_service_share | 0.10977 | [0.10625, 0.11331] |
| congested_bucket_2 | fifo | mean_aoi_s | 1.22049 | [1.20904, 1.23202] |
| congested_bucket_2 | fifo | event_deadline_miss | -0.33272 | [-0.33596, -0.32981] |
| congested_bucket_2 | fifo | jain_service_share | 0.10282 | [0.09956, 0.10585] |
| congested_bucket_2 | maxweight | mean_aoi_s | -104.24304 | [-108.18591, -100.44866] |
| congested_bucket_2 | maxweight | event_deadline_miss | 0.24535 | [0.23491, 0.25557] |
| congested_bucket_2 | maxweight | jain_service_share | 0.23701 | [0.22705, 0.24694] |
| congested_bucket_2 | pf | mean_aoi_s | 0.94619 | [0.93237, 0.95987] |
| congested_bucket_2 | pf | event_deadline_miss | -0.06250 | [-0.06579, -0.05978] |
| congested_bucket_2 | pf | jain_service_share | -0.18092 | [-0.18313, -0.17868] |
| congested_bucket_4 | aoi_gain | mean_aoi_s | -1.34862 | [-1.37831, -1.32085] |
| congested_bucket_4 | aoi_gain | event_deadline_miss | 0.15837 | [0.15437, 0.16185] |
| congested_bucket_4 | aoi_gain | jain_service_share | 0.07460 | [0.07164, 0.07765] |
| congested_bucket_4 | edf | mean_aoi_s | -6.61740 | [-6.95567, -6.35104] |
| congested_bucket_4 | edf | event_deadline_miss | 0.16231 | [0.15867, 0.16551] |
| congested_bucket_4 | edf | jain_service_share | 0.10977 | [0.10625, 0.11331] |
| congested_bucket_4 | fifo | mean_aoi_s | 1.22049 | [1.20904, 1.23202] |
| congested_bucket_4 | fifo | event_deadline_miss | -0.33272 | [-0.33596, -0.32981] |
| congested_bucket_4 | fifo | jain_service_share | 0.10282 | [0.09956, 0.10585] |
| congested_bucket_4 | maxweight | mean_aoi_s | -104.24304 | [-108.18591, -100.44866] |
| congested_bucket_4 | maxweight | event_deadline_miss | 0.24535 | [0.23491, 0.25557] |
| congested_bucket_4 | maxweight | jain_service_share | 0.23701 | [0.22705, 0.24694] |
| congested_bucket_4 | pf | mean_aoi_s | 0.94619 | [0.93237, 0.95987] |
| congested_bucket_4 | pf | event_deadline_miss | -0.06250 | [-0.06579, -0.05978] |
| congested_bucket_4 | pf | jain_service_share | -0.18092 | [-0.18313, -0.17868] |

## 不利结果

negative_results.csv 保存全部不利均值方向；区间跨零的比较表示方向尚不明确。以下列出三项主要指标的前 30 条记录。

| 场景 | 对照 | 指标 | FUD−对照 | 95% CI |
|---|---|---|---:|---|
| congested_bucket_16 | aoi_gain | event_deadline_miss | 0.15837 | [0.15437, 0.16185] |
| congested_bucket_16 | debt | mean_aoi_s | 0.45684 | [0.43869, 0.47351] |
| congested_bucket_16 | debt | jain_service_share | -0.10571 | [-0.10840, -0.10309] |
| congested_bucket_16 | edf | event_deadline_miss | 0.16231 | [0.15867, 0.16551] |
| congested_bucket_16 | fifo | mean_aoi_s | 1.22049 | [1.20904, 1.23202] |
| congested_bucket_16 | fud_no_age | event_deadline_miss | 0.41137 | [0.40696, 0.41581] |
| congested_bucket_16 | fud_no_urgency | mean_aoi_s | 1.26785 | [1.25246, 1.28205] |
| congested_bucket_16 | maxweight | event_deadline_miss | 0.24535 | [0.23491, 0.25557] |
| congested_bucket_16 | pf | mean_aoi_s | 0.94619 | [0.93237, 0.95987] |
| congested_bucket_16 | pf | jain_service_share | -0.18092 | [-0.18313, -0.17868] |
| congested_bucket_16 | priority | event_deadline_miss | 0.46365 | [0.45950, 0.46750] |
| congested_bucket_16 | rr | mean_aoi_s | 1.19025 | [1.17435, 1.20540] |
| congested_bucket_16 | rr | jain_service_share | -0.09086 | [-0.09434, -0.08770] |
| congested_bucket_16 | wrr | mean_aoi_s | 1.04990 | [1.03427, 1.06542] |
| congested_bucket_16 | wrr | jain_service_share | -0.12546 | [-0.12906, -0.12190] |
| congested_bucket_2 | aoi_gain | event_deadline_miss | 0.15837 | [0.15437, 0.16185] |
| congested_bucket_2 | debt | mean_aoi_s | 0.45684 | [0.43869, 0.47351] |
| congested_bucket_2 | debt | jain_service_share | -0.10571 | [-0.10840, -0.10309] |
| congested_bucket_2 | edf | event_deadline_miss | 0.16231 | [0.15867, 0.16551] |
| congested_bucket_2 | fifo | mean_aoi_s | 1.22049 | [1.20904, 1.23202] |
| congested_bucket_2 | fud_no_age | event_deadline_miss | 0.41137 | [0.40696, 0.41581] |
| congested_bucket_2 | fud_no_urgency | mean_aoi_s | 1.26785 | [1.25246, 1.28205] |
| congested_bucket_2 | maxweight | event_deadline_miss | 0.24535 | [0.23491, 0.25557] |
| congested_bucket_2 | pf | mean_aoi_s | 0.94619 | [0.93237, 0.95987] |
| congested_bucket_2 | pf | jain_service_share | -0.18092 | [-0.18313, -0.17868] |
| congested_bucket_2 | priority | event_deadline_miss | 0.46365 | [0.45950, 0.46750] |
| congested_bucket_2 | rr | mean_aoi_s | 1.19025 | [1.17435, 1.20540] |
| congested_bucket_2 | rr | jain_service_share | -0.09086 | [-0.09434, -0.08770] |
| congested_bucket_2 | wrr | mean_aoi_s | 1.04990 | [1.03427, 1.06542] |
| congested_bucket_2 | wrr | jain_service_share | -0.12546 | [-0.12906, -0.12190] |

## 统计定义

event_deadline_success/miss/late 的分母为主观察生成 cohort 内已经判定的事件数；pending 单列。overflow/expiration 的分母为该 cohort 全部事件。状态成功率按已完成发送尝试计算，替换率按状态生成数计算。
Service Share 使用观察窗口内实际占用的抽象服务 slots，含失败尝试；加权 Jain 使用 service_slots/weight。每条配置流均进入资源向量，全零向量 Jain=0。
pdr、event_miss、jain_pdr、jain_delivery、latency_s 和 cohort_goodput_bps 保留 legacy v1 保护区口径；新版业务指标使用不同字段。状态替换率和资源利用率作为描述量，不作单向优劣排序。
事件时延/P95 条件于成功交付；Goodput 按主 cohort 的最终交付 payload 字节除以主观察时长。尾窗交付与成本另存 metrics.json。
summary.csv 保存各策略均值与区间；per_flow.csv 保存分类指标、QoS、资源份额；runs/ 保存逐包生命周期与决策。
