# 仿真实验结果（metric version 2）

共 78 次运行。每个场景使用共同到达与信道轨迹；配置、源码摘要与软件环境见 manifest.json。

主窗口到达 cohort 追踪至公共尾窗结束；AoI 和 Service Share 仅统计主观察窗口。

## FUD 场景表现

| 场景 | 状态 AoI(s) | 事件 miss(v2) | Jain Service Share | 加权 Jain | Goodput(bit/s) |

|---|---:|---:|---:|---:|---:|

| markov_check | 3.91432 | 0.75451 | 0.75543 | 0.87050 | 3228.44444 |

| tail_check | 3.72613 | 0.62887 | 0.75082 | 0.89439 | 4096.00000 |

| total_036_nodes_8 | 2.30728 | 0.06273 | 0.88317 | 0.56234 | 1649.77778 |

## 配对比较

差值为 FUD − 对照，区间为对 seed 配对差值进行 2,000 次 bootstrap 的 95% CI。AoI/miss 越低越好，Service Share Jain 越高越均衡。完整比较见 paired_differences.csv。

| 场景 | 对照 | 指标 | 差值 | 95% CI |

|---|---|---|---:|---|

| markov_check | aoi_gain | mean_aoi_s | -2.13394 | [-2.27663, -1.99125] |

| markov_check | aoi_gain | event_deadline_miss | 0.18656 | [0.16556, 0.20755] |

| markov_check | aoi_gain | jain_service_share | 0.09250 | [0.08051, 0.10449] |

| markov_check | edf | mean_aoi_s | -2.41941 | [-2.44889, -2.38993] |

| markov_check | edf | event_deadline_miss | 0.19997 | [0.19868, 0.20126] |

| markov_check | edf | jain_service_share | 0.12407 | [0.09973, 0.14841] |

| markov_check | fifo | mean_aoi_s | 1.30920 | [1.26424, 1.35417] |

| markov_check | fifo | event_deadline_miss | -0.19997 | [-0.20126, -0.19868] |

| markov_check | fifo | jain_service_share | 0.04668 | [0.03882, 0.05455] |

| markov_check | maxweight | mean_aoi_s | -3.33811 | [-4.11097, -2.56524] |

| markov_check | maxweight | event_deadline_miss | 0.18472 | [0.09272, 0.27673] |

| markov_check | maxweight | jain_service_share | 0.18074 | [0.15193, 0.20955] |

| markov_check | pf | mean_aoi_s | 0.82377 | [0.72316, 0.92437] |

| markov_check | pf | event_deadline_miss | -0.03609 | [-0.05960, -0.01258] |

| markov_check | pf | jain_service_share | -0.19821 | [-0.21010, -0.18632] |

| tail_check | aoi_gain | mean_aoi_s | -1.45405 | [-1.48229, -1.42580] |

| tail_check | aoi_gain | event_deadline_miss | 0.16140 | [0.15723, 0.16556] |

| tail_check | aoi_gain | jain_service_share | 0.07768 | [0.05401, 0.10135] |

| tail_check | edf | mean_aoi_s | -2.13024 | [-2.16913, -2.09135] |

| tail_check | edf | event_deadline_miss | 0.18127 | [0.15723, 0.20530] |

| tail_check | edf | jain_service_share | 0.11945 | [0.11809, 0.12081] |

| tail_check | fifo | mean_aoi_s | 1.46724 | [1.44087, 1.49361] |

| tail_check | fifo | event_deadline_miss | -0.32230 | [-0.33333, -0.31126] |

| tail_check | fifo | jain_service_share | 0.04207 | [0.01123, 0.07291] |

| tail_check | maxweight | mean_aoi_s | -3.84134 | [-4.03569, -3.64698] |

| tail_check | maxweight | event_deadline_miss | 0.08574 | [0.03311, 0.13836] |

| tail_check | maxweight | jain_service_share | 0.26828 | [0.24937, 0.28718] |

| tail_check | pf | mean_aoi_s | 1.20670 | [1.16420, 1.24920] |

| tail_check | pf | event_deadline_miss | -0.08062 | [-0.08176, -0.07947] |

| tail_check | pf | jain_service_share | -0.23437 | [-0.24209, -0.22665] |

| total_036_nodes_8 | aoi_gain | mean_aoi_s | -0.00094 | [-0.00200, 0.00011] |

| total_036_nodes_8 | aoi_gain | event_deadline_miss | 0.00000 | [0.00000, 0.00000] |

| total_036_nodes_8 | aoi_gain | jain_service_share | 0.00000 | [0.00000, 0.00000] |

| total_036_nodes_8 | edf | mean_aoi_s | -0.01950 | [-0.03389, -0.00511] |

| total_036_nodes_8 | edf | event_deadline_miss | 0.02273 | [0.00000, 0.04545] |

| total_036_nodes_8 | edf | jain_service_share | 0.00281 | [0.00000, 0.00561] |

| total_036_nodes_8 | fifo | mean_aoi_s | 0.10356 | [0.06922, 0.13789] |

| total_036_nodes_8 | fifo | event_deadline_miss | 0.00000 | [0.00000, 0.00000] |

| total_036_nodes_8 | fifo | jain_service_share | 0.00281 | [0.00000, 0.00561] |

| total_036_nodes_8 | maxweight | mean_aoi_s | 0.06800 | [-0.00300, 0.13900] |

| total_036_nodes_8 | maxweight | event_deadline_miss | 0.02273 | [0.00000, 0.04545] |

| total_036_nodes_8 | maxweight | jain_service_share | 0.00694 | [0.00561, 0.00827] |

| total_036_nodes_8 | pf | mean_aoi_s | -0.00989 | [-0.02389, 0.00411] |

| total_036_nodes_8 | pf | event_deadline_miss | 0.00000 | [0.00000, 0.00000] |

| total_036_nodes_8 | pf | jain_service_share | 0.00000 | [0.00000, 0.00000] |

## 不利结果

negative_results.csv 保存全部不利均值方向；区间跨零的比较表示方向尚不明确。以下列出三项主要指标的前 30 条记录。

| 场景 | 对照 | 指标 | FUD−对照 | 95% CI |

|---|---|---|---:|---|

| markov_check | aoi_gain | event_deadline_miss | 0.18656 | [0.16556, 0.20755] |

| markov_check | debt | mean_aoi_s | 0.35370 | [0.11521, 0.59219] |

| markov_check | debt | event_deadline_miss | 0.00860 | [-0.03311, 0.05031] |

| markov_check | debt | jain_service_share | -0.09423 | [-0.09692, -0.09153] |

| markov_check | edf | event_deadline_miss | 0.19997 | [0.19868, 0.20126] |

| markov_check | fifo | mean_aoi_s | 1.30920 | [1.26424, 1.35417] |

| markov_check | fud_no_age | event_deadline_miss | 0.43155 | [0.40397, 0.45912] |

| markov_check | fud_no_debt | jain_service_share | -0.01169 | [-0.02973, 0.00634] |

| markov_check | fud_no_urgency | mean_aoi_s | 1.45076 | [1.31111, 1.59042] |

| markov_check | maxweight | event_deadline_miss | 0.18472 | [0.09272, 0.27673] |

| markov_check | pf | mean_aoi_s | 0.82377 | [0.72316, 0.92437] |

| markov_check | pf | jain_service_share | -0.19821 | [-0.21010, -0.18632] |

| markov_check | priority | event_deadline_miss | 0.42857 | [0.41060, 0.44654] |

| markov_check | rr | mean_aoi_s | 1.21295 | [1.15368, 1.27222] |

| markov_check | rr | jain_service_share | -0.15171 | [-0.16171, -0.14170] |

| markov_check | wrr | mean_aoi_s | 0.95590 | [0.75083, 1.16097] |

| markov_check | wrr | jain_service_share | -0.15154 | [-0.18151, -0.12157] |

| tail_check | aoi_gain | event_deadline_miss | 0.16140 | [0.15723, 0.16556] |

| tail_check | debt | mean_aoi_s | 0.66578 | [0.61743, 0.71413] |

| tail_check | debt | jain_service_share | -0.14453 | [-0.15284, -0.13622] |

| tail_check | edf | event_deadline_miss | 0.18127 | [0.15723, 0.20530] |

| tail_check | fifo | mean_aoi_s | 1.46724 | [1.44087, 1.49361] |

| tail_check | fud_no_age | event_deadline_miss | 0.43586 | [0.42138, 0.45033] |

| tail_check | fud_no_urgency | mean_aoi_s | 1.63177 | [1.52087, 1.74267] |

| tail_check | maxweight | event_deadline_miss | 0.08574 | [0.03311, 0.13836] |

| tail_check | pf | mean_aoi_s | 1.20670 | [1.16420, 1.24920] |

| tail_check | pf | jain_service_share | -0.23437 | [-0.24209, -0.22665] |

| tail_check | priority | event_deadline_miss | 0.43950 | [0.40881, 0.47020] |

| tail_check | rr | mean_aoi_s | 1.41747 | [1.34833, 1.48660] |

| tail_check | rr | jain_service_share | -0.15632 | [-0.18931, -0.12334] |

## 统计定义

event_deadline_success/miss/late 的分母为主观察生成 cohort 内已经判定的事件数；pending 单列。overflow/expiration 的分母为该 cohort 全部事件。状态成功率按已完成发送尝试计算，替换率按状态生成数计算。

Service Share 使用观察窗口内实际占用的抽象服务 slots，含失败尝试；加权 Jain 使用 service_slots/weight。每条配置流均进入资源向量，全零向量 Jain=0。

pdr、event_miss、jain_pdr、jain_delivery、latency_s 和 cohort_goodput_bps 保留 legacy v1 保护区口径；新版业务指标使用不同字段。状态替换率和资源利用率作为描述量，不作单向优劣排序。

事件时延/P95 条件于成功交付；Goodput 按主 cohort 的最终交付 payload 字节除以主观察时长。尾窗交付与成本另存 metrics.json。

summary.csv 保存各策略均值与区间；per_flow.csv 保存分类指标、QoS、资源份额；runs/ 保存逐包生命周期与决策。
