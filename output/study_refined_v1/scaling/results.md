# 仿真实验结果（metric version 2）
共 1040 次运行。每个场景使用共同到达与信道轨迹；配置、源码摘要与软件环境见 manifest.json。
主窗口到达 cohort 追踪至公共尾窗结束；AoI 和 Service Share 仅统计主观察窗口。

## FUD 场景表现


| 场景 | 状态 AoI(s) | 事件 miss(v2) | Jain Service Share | 加权 Jain | Goodput(bit/s) |
|---|---:|---:|---:|---:|---:|
| total_036_nodes_24 | 7.24231 | 0.05122 | 0.98236 | 0.70690 | 1737.94743 |
| total_036_nodes_48 | 14.05040 | 0.05456 | 0.96575 | 0.69326 | 1747.09029 |
| total_036_nodes_8 | 2.45431 | 0.05037 | 0.96759 | 0.57632 | 1710.15314 |
| total_036_nodes_96 | 27.47482 | 0.05329 | 0.93091 | 0.66943 | 1749.86971 |

## 配对比较

差值为 FUD − 对照，区间为对 seed 配对差值进行 2,000 次 bootstrap 的 95% CI。AoI/miss 越低越好，Service Share Jain 越高越均衡。完整比较见 paired_differences.csv。

| 场景 | 对照 | 指标 | 差值 | 95% CI |
|---|---|---|---:|---|
| total_036_nodes_24 | aoi_gain | mean_aoi_s | -0.01325 | [-0.03141, 0.00529] |
| total_036_nodes_24 | aoi_gain | event_deadline_miss | -0.00098 | [-0.00417, 0.00230] |
| total_036_nodes_24 | aoi_gain | jain_service_share | -0.00012 | [-0.00026, 0.00000] |
| total_036_nodes_24 | edf | mean_aoi_s | -0.02647 | [-0.05165, -0.00035] |
| total_036_nodes_24 | edf | event_deadline_miss | -0.00146 | [-0.00432, 0.00136] |
| total_036_nodes_24 | edf | jain_service_share | -0.00004 | [-0.00020, 0.00012] |
| total_036_nodes_24 | fifo | mean_aoi_s | -0.01614 | [-0.03980, 0.00571] |
| total_036_nodes_24 | fifo | event_deadline_miss | 0.00170 | [-0.00054, 0.00406] |
| total_036_nodes_24 | fifo | jain_service_share | 0.00007 | [-0.00006, 0.00018] |
| total_036_nodes_24 | maxweight | mean_aoi_s | -0.02805 | [-0.05985, 0.00106] |
| total_036_nodes_24 | maxweight | event_deadline_miss | -0.00256 | [-0.00580, 0.00049] |
| total_036_nodes_24 | maxweight | jain_service_share | 0.00000 | [-0.00022, 0.00027] |
| total_036_nodes_24 | pf | mean_aoi_s | 0.00671 | [-0.00799, 0.02183] |
| total_036_nodes_24 | pf | event_deadline_miss | -0.00391 | [-0.00722, -0.00064] |
| total_036_nodes_24 | pf | jain_service_share | -0.00025 | [-0.00043, -0.00009] |
| total_036_nodes_48 | aoi_gain | mean_aoi_s | -0.02076 | [-0.05621, 0.01551] |
| total_036_nodes_48 | aoi_gain | event_deadline_miss | 0.00132 | [-0.00266, 0.00552] |
| total_036_nodes_48 | aoi_gain | jain_service_share | -0.00017 | [-0.00035, 0.00001] |
| total_036_nodes_48 | edf | mean_aoi_s | -0.03781 | [-0.09779, 0.02016] |
| total_036_nodes_48 | edf | event_deadline_miss | 0.00109 | [-0.00315, 0.00554] |
| total_036_nodes_48 | edf | jain_service_share | -0.00012 | [-0.00034, 0.00010] |
| total_036_nodes_48 | fifo | mean_aoi_s | -0.01505 | [-0.07200, 0.03806] |
| total_036_nodes_48 | fifo | event_deadline_miss | 0.00295 | [-0.00051, 0.00614] |
| total_036_nodes_48 | fifo | jain_service_share | -0.00008 | [-0.00029, 0.00011] |
| total_036_nodes_48 | maxweight | mean_aoi_s | -0.00064 | [-0.06931, 0.07096] |
| total_036_nodes_48 | maxweight | event_deadline_miss | -0.00153 | [-0.00446, 0.00137] |
| total_036_nodes_48 | maxweight | jain_service_share | 0.00002 | [-0.00016, 0.00021] |
| total_036_nodes_48 | pf | mean_aoi_s | 0.01942 | [-0.00531, 0.04589] |
| total_036_nodes_48 | pf | event_deadline_miss | -0.00365 | [-0.00680, -0.00046] |
| total_036_nodes_48 | pf | jain_service_share | -0.00034 | [-0.00054, -0.00013] |
| total_036_nodes_8 | aoi_gain | mean_aoi_s | -0.00511 | [-0.00989, -0.00084] |
| total_036_nodes_8 | aoi_gain | event_deadline_miss | -0.00027 | [-0.00259, 0.00179] |
| total_036_nodes_8 | aoi_gain | jain_service_share | 0.00013 | [-0.00007, 0.00033] |
| total_036_nodes_8 | edf | mean_aoi_s | -0.01589 | [-0.02536, -0.00691] |
| total_036_nodes_8 | edf | event_deadline_miss | 0.00225 | [-0.00011, 0.00448] |
| total_036_nodes_8 | edf | jain_service_share | -0.00010 | [-0.00031, 0.00013] |
| total_036_nodes_8 | fifo | mean_aoi_s | -0.01038 | [-0.02059, 0.00213] |
| total_036_nodes_8 | fifo | event_deadline_miss | 0.00212 | [-0.00118, 0.00554] |
| total_036_nodes_8 | fifo | jain_service_share | 0.00165 | [0.00127, 0.00202] |
| total_036_nodes_8 | maxweight | mean_aoi_s | -0.01042 | [-0.01815, -0.00351] |
| total_036_nodes_8 | maxweight | event_deadline_miss | -0.00278 | [-0.00524, -0.00054] |
| total_036_nodes_8 | maxweight | jain_service_share | 0.00190 | [0.00130, 0.00252] |
| total_036_nodes_8 | pf | mean_aoi_s | -0.00671 | [-0.01198, -0.00076] |
| total_036_nodes_8 | pf | event_deadline_miss | -0.00172 | [-0.00437, 0.00088] |
| total_036_nodes_8 | pf | jain_service_share | 0.00076 | [0.00030, 0.00118] |

## 不利结果

negative_results.csv 保存全部不利均值方向；区间跨零的比较表示方向尚不明确。以下列出三项主要指标的前 30 条记录。

| 场景 | 对照 | 指标 | FUD−对照 | 95% CI |
|---|---|---|---:|---|
| total_036_nodes_24 | aoi_gain | jain_service_share | -0.00012 | [-0.00026, 0.00000] |
| total_036_nodes_24 | debt | event_deadline_miss | 0.00011 | [-0.00350, 0.00379] |
| total_036_nodes_24 | debt | jain_service_share | -0.00012 | [-0.00027, 0.00001] |
| total_036_nodes_24 | edf | jain_service_share | -0.00004 | [-0.00020, 0.00012] |
| total_036_nodes_24 | fifo | event_deadline_miss | 0.00170 | [-0.00054, 0.00406] |
| total_036_nodes_24 | fud_no_age | jain_service_share | -0.00016 | [-0.00030, -0.00003] |
| total_036_nodes_24 | fud_no_debt | mean_aoi_s | 0.00003 | [0.00000, 0.00006] |
| total_036_nodes_24 | fud_no_debt | event_deadline_miss | 0.00012 | [0.00000, 0.00037] |
| total_036_nodes_24 | fud_no_urgency | mean_aoi_s | 0.00283 | [-0.00091, 0.00684] |
| total_036_nodes_24 | pf | mean_aoi_s | 0.00671 | [-0.00799, 0.02183] |
| total_036_nodes_24 | pf | jain_service_share | -0.00025 | [-0.00043, -0.00009] |
| total_036_nodes_24 | priority | jain_service_share | -0.00004 | [-0.00020, 0.00012] |
| total_036_nodes_24 | rr | event_deadline_miss | 0.00102 | [-0.00252, 0.00410] |
| total_036_nodes_24 | rr | jain_service_share | -0.00005 | [-0.00021, 0.00012] |
| total_036_nodes_24 | wrr | event_deadline_miss | 0.00170 | [-0.00103, 0.00436] |
| total_036_nodes_24 | wrr | jain_service_share | -0.00002 | [-0.00019, 0.00014] |
| total_036_nodes_48 | aoi_gain | event_deadline_miss | 0.00132 | [-0.00266, 0.00552] |
| total_036_nodes_48 | aoi_gain | jain_service_share | -0.00017 | [-0.00035, 0.00001] |
| total_036_nodes_48 | debt | event_deadline_miss | 0.00277 | [-0.00078, 0.00624] |
| total_036_nodes_48 | debt | jain_service_share | -0.00012 | [-0.00034, 0.00009] |
| total_036_nodes_48 | edf | event_deadline_miss | 0.00109 | [-0.00315, 0.00554] |
| total_036_nodes_48 | edf | jain_service_share | -0.00012 | [-0.00034, 0.00010] |
| total_036_nodes_48 | fifo | event_deadline_miss | 0.00295 | [-0.00051, 0.00614] |
| total_036_nodes_48 | fifo | jain_service_share | -0.00008 | [-0.00029, 0.00011] |
| total_036_nodes_48 | fud_no_age | event_deadline_miss | 0.00154 | [-0.00214, 0.00515] |
| total_036_nodes_48 | fud_no_age | jain_service_share | -0.00014 | [-0.00038, 0.00009] |
| total_036_nodes_48 | fud_no_urgency | jain_service_share | -0.00005 | [-0.00018, 0.00008] |
| total_036_nodes_48 | pf | mean_aoi_s | 0.01942 | [-0.00531, 0.04589] |
| total_036_nodes_48 | pf | jain_service_share | -0.00034 | [-0.00054, -0.00013] |
| total_036_nodes_48 | priority | event_deadline_miss | 0.00109 | [-0.00315, 0.00554] |

## 统计定义

event_deadline_success/miss/late 的分母为主观察生成 cohort 内已经判定的事件数；pending 单列。overflow/expiration 的分母为该 cohort 全部事件。状态成功率按已完成发送尝试计算，替换率按状态生成数计算。
Service Share 使用观察窗口内实际占用的抽象服务 slots，含失败尝试；加权 Jain 使用 service_slots/weight。每条配置流均进入资源向量，全零向量 Jain=0。
pdr、event_miss、jain_pdr、jain_delivery、latency_s 和 cohort_goodput_bps 保留 legacy v1 保护区口径；新版业务指标使用不同字段。状态替换率和资源利用率作为描述量，不作单向优劣排序。
事件时延/P95 条件于成功交付；Goodput 按主 cohort 的最终交付 payload 字节除以主观察时长。尾窗交付与成本另存 metrics.json。
summary.csv 保存各策略均值与区间；per_flow.csv 保存分类指标、QoS、资源份额；runs/ 保存逐包生命周期与决策。
