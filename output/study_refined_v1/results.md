# 仿真实验结果（metric version 2）
共 3900 次运行。每个场景使用共同到达与信道轨迹；配置、源码摘要与软件环境见 manifest.json。
主窗口到达 cohort 追踪至公共尾窗结束；AoI 和 Service Share 仅统计主观察窗口。

## FUD 场景表现


| 场景 | 状态 AoI(s) | 事件 miss(v2) | Jain Service Share | 加权 Jain | Goodput(bit/s) |
|---|---:|---:|---:|---:|---:|
| budget_100 | 7.11504 | 0.04870 | 0.97991 | 0.69649 | 1765.81486 |
| budget_40 | 7.18444 | 0.13718 | 0.97926 | 0.68977 | 1687.25943 |
| bursty | 5.59262 | 0.18127 | 0.98177 | 0.75897 | 2262.67429 |
| congestion | 3.50460 | 0.63152 | 0.81870 | 0.95527 | 3904.14629 |
| equal_weights | 7.11725 | 0.05127 | 0.98000 | 0.98000 | 1764.13257 |
| long_delay | 7.51703 | 0.23321 | 0.97030 | 0.66694 | 1650.61486 |
| lossless | 6.79274 | 0.00093 | 0.97987 | 0.69647 | 1855.70743 |
| markov_link | 8.58163 | 0.19789 | 0.97992 | 0.69637 | 1482.53257 |
| mixed_sizes | 7.23393 | 0.09742 | 0.89173 | 0.62738 | 2558.97600 |
| nodes_48 | 7.21219 | 0.09781 | 0.98156 | 0.70488 | 3385.19771 |
| nodes_8 | 7.03593 | 0.05512 | 0.98631 | 0.69010 | 587.41029 |
| nodes_96 | 8.09558 | 0.85370 | 0.74444 | 0.64789 | 3904.51200 |
| normal | 7.11504 | 0.04870 | 0.97991 | 0.69649 | 1765.81486 |
| unequal_rates | 5.29850 | 0.04806 | 0.69547 | 0.46608 | 1874.79771 |
| weak_link | 12.31140 | 0.45267 | 0.97991 | 0.69619 | 1019.17257 |

## 配对比较

差值为 FUD − 对照，区间为对 seed 配对差值进行 2,000 次 bootstrap 的 95% CI。AoI/miss 越低越好，Service Share Jain 越高越均衡。完整比较见 paired_differences.csv。

| 场景 | 对照 | 指标 | 差值 | 95% CI |
|---|---|---|---:|---|
| bursty | aoi_gain | mean_aoi_s | -0.06908 | [-0.08909, -0.05205] |
| bursty | aoi_gain | event_deadline_miss | 0.04294 | [0.03720, 0.04870] |
| bursty | aoi_gain | jain_service_share | 0.00097 | [-0.00016, 0.00213] |
| bursty | edf | mean_aoi_s | -0.45893 | [-0.49124, -0.42590] |
| bursty | edf | event_deadline_miss | 0.08470 | [0.07901, 0.09020] |
| bursty | edf | jain_service_share | 0.00836 | [0.00649, 0.01043] |
| bursty | fifo | mean_aoi_s | -0.00394 | [-0.03330, 0.02285] |
| bursty | fifo | event_deadline_miss | -0.15786 | [-0.16643, -0.14917] |
| bursty | fifo | jain_service_share | 0.00663 | [0.00426, 0.00937] |
| bursty | maxweight | mean_aoi_s | -0.41823 | [-0.47856, -0.35682] |
| bursty | maxweight | event_deadline_miss | -0.04147 | [-0.05595, -0.02607] |
| bursty | maxweight | jain_service_share | 0.00357 | [0.00134, 0.00579] |
| bursty | pf | mean_aoi_s | 0.05376 | [0.04024, 0.06740] |
| bursty | pf | event_deadline_miss | -0.07438 | [-0.07984, -0.06883] |
| bursty | pf | jain_service_share | -0.00948 | [-0.01108, -0.00785] |
| congestion | aoi_gain | mean_aoi_s | -1.34862 | [-1.37831, -1.32085] |
| congestion | aoi_gain | event_deadline_miss | 0.15837 | [0.15437, 0.16185] |
| congestion | aoi_gain | jain_service_share | 0.07460 | [0.07164, 0.07765] |
| congestion | edf | mean_aoi_s | -6.61740 | [-6.95567, -6.35104] |
| congestion | edf | event_deadline_miss | 0.16231 | [0.15867, 0.16551] |
| congestion | edf | jain_service_share | 0.10977 | [0.10625, 0.11331] |
| congestion | fifo | mean_aoi_s | 1.22049 | [1.20904, 1.23202] |
| congestion | fifo | event_deadline_miss | -0.33272 | [-0.33596, -0.32981] |
| congestion | fifo | jain_service_share | 0.10282 | [0.09956, 0.10585] |
| congestion | maxweight | mean_aoi_s | -104.24304 | [-108.18591, -100.44866] |
| congestion | maxweight | event_deadline_miss | 0.24535 | [0.23491, 0.25557] |
| congestion | maxweight | jain_service_share | 0.23701 | [0.22705, 0.24694] |
| congestion | pf | mean_aoi_s | 0.94619 | [0.93237, 0.95987] |
| congestion | pf | event_deadline_miss | -0.06250 | [-0.06579, -0.05978] |
| congestion | pf | jain_service_share | -0.18092 | [-0.18313, -0.17868] |
| normal | aoi_gain | mean_aoi_s | -0.01016 | [-0.03353, 0.01612] |
| normal | aoi_gain | event_deadline_miss | -0.00041 | [-0.00254, 0.00149] |
| normal | aoi_gain | jain_service_share | -0.00011 | [-0.00034, 0.00011] |
| normal | edf | mean_aoi_s | -0.06858 | [-0.11385, -0.02676] |
| normal | edf | event_deadline_miss | 0.00019 | [-0.00247, 0.00268] |
| normal | edf | jain_service_share | -0.00000 | [-0.00032, 0.00032] |
| normal | fifo | mean_aoi_s | -0.03266 | [-0.07409, 0.00552] |
| normal | fifo | event_deadline_miss | -0.00045 | [-0.00339, 0.00225] |
| normal | fifo | jain_service_share | 0.00009 | [-0.00016, 0.00033] |
| normal | maxweight | mean_aoi_s | -0.07115 | [-0.13002, -0.02338] |
| normal | maxweight | event_deadline_miss | -0.00370 | [-0.00768, -0.00070] |
| normal | maxweight | jain_service_share | 0.00006 | [-0.00020, 0.00030] |
| normal | pf | mean_aoi_s | -0.01972 | [-0.03888, 0.00022] |
| normal | pf | event_deadline_miss | -0.00530 | [-0.00858, -0.00254] |
| normal | pf | jain_service_share | -0.00019 | [-0.00042, 0.00005] |

## 不利结果

negative_results.csv 保存全部不利均值方向；区间跨零的比较表示方向尚不明确。以下列出三项主要指标的前 30 条记录。

| 场景 | 对照 | 指标 | FUD−对照 | 95% CI |
|---|---|---|---:|---|
| budget_100 | aoi_gain | jain_service_share | -0.00011 | [-0.00034, 0.00011] |
| budget_100 | debt | event_deadline_miss | 0.00118 | [-0.00082, 0.00319] |
| budget_100 | edf | event_deadline_miss | 0.00019 | [-0.00247, 0.00268] |
| budget_100 | edf | jain_service_share | -0.00000 | [-0.00032, 0.00032] |
| budget_100 | fud_no_age | event_deadline_miss | 0.00060 | [-0.00182, 0.00284] |
| budget_100 | fud_no_age | jain_service_share | -0.00000 | [-0.00031, 0.00030] |
| budget_100 | fud_no_urgency | mean_aoi_s | 0.00075 | [-0.00415, 0.00429] |
| budget_100 | fud_no_urgency | jain_service_share | -0.00012 | [-0.00024, -0.00000] |
| budget_100 | pf | jain_service_share | -0.00019 | [-0.00042, 0.00005] |
| budget_100 | priority | event_deadline_miss | 0.00019 | [-0.00247, 0.00268] |
| budget_100 | priority | jain_service_share | -0.00000 | [-0.00032, 0.00032] |
| budget_40 | aoi_gain | event_deadline_miss | 0.04436 | [0.03780, 0.05116] |
| budget_40 | aoi_gain | jain_service_share | -0.00182 | [-0.00250, -0.00117] |
| budget_40 | debt | event_deadline_miss | 0.03105 | [0.02710, 0.03509] |
| budget_40 | debt | jain_service_share | -0.00115 | [-0.00177, -0.00064] |
| budget_40 | edf | event_deadline_miss | 0.06911 | [0.06088, 0.07765] |
| budget_40 | edf | jain_service_share | -0.00058 | [-0.00170, 0.00041] |
| budget_40 | fud_no_age | event_deadline_miss | 0.08100 | [0.07154, 0.09121] |
| budget_40 | fud_no_age | jain_service_share | -0.00043 | [-0.00169, 0.00063] |
| budget_40 | fud_no_debt | mean_aoi_s | 0.00026 | [0.00004, 0.00053] |
| budget_40 | fud_no_urgency | mean_aoi_s | 0.02750 | [0.01014, 0.04391] |
| budget_40 | pf | event_deadline_miss | 0.00275 | [-0.00364, 0.00914] |
| budget_40 | pf | jain_service_share | -0.00183 | [-0.00271, -0.00108] |
| budget_40 | priority | event_deadline_miss | 0.08135 | [0.07170, 0.09118] |
| budget_40 | priority | jain_service_share | -0.00014 | [-0.00141, 0.00097] |
| bursty | aoi_gain | event_deadline_miss | 0.04294 | [0.03720, 0.04870] |
| bursty | debt | jain_service_share | -0.00371 | [-0.00459, -0.00271] |
| bursty | edf | event_deadline_miss | 0.08470 | [0.07901, 0.09020] |
| bursty | fud_no_age | event_deadline_miss | 0.12596 | [0.11730, 0.13534] |
| bursty | fud_no_debt | mean_aoi_s | 0.00072 | [-0.00071, 0.00223] |

## 统计定义

event_deadline_success/miss/late 的分母为主观察生成 cohort 内已经判定的事件数；pending 单列。overflow/expiration 的分母为该 cohort 全部事件。状态成功率按已完成发送尝试计算，替换率按状态生成数计算。
Service Share 使用观察窗口内实际占用的抽象服务 slots，含失败尝试；加权 Jain 使用 service_slots/weight。每条配置流均进入资源向量，全零向量 Jain=0。
pdr、event_miss、jain_pdr、jain_delivery、latency_s 和 cohort_goodput_bps 保留 legacy v1 保护区口径；新版业务指标使用不同字段。状态替换率和资源利用率作为描述量，不作单向优劣排序。
事件时延/P95 条件于成功交付；Goodput 按主 cohort 的最终交付 payload 字节除以主观察时长。尾窗交付与成本另存 metrics.json。
summary.csv 保存各策略均值与区间；per_flow.csv 保存分类指标、QoS、资源份额；runs/ 保存逐包生命周期与决策。
