# 仿真实验结果（metric version 2）
共 6500 次运行。每个场景使用共同到达与信道轨迹；配置、源码摘要与软件环境见 manifest.json。
主窗口到达 cohort 追踪至公共尾窗结束；AoI 和 Service Share 仅统计主观察窗口。

## FUD 场景表现


| 场景 | 状态 AoI(s) | 事件 miss(v2) | Jain Service Share | 加权 Jain | Goodput(bit/s) |
|---|---:|---:|---:|---:|---:|
| bad_to_good_0.05 | 9.91731 | 0.29745 | 0.97996 | 0.69631 | 1298.79771 |
| bad_to_good_0.1 | 8.58163 | 0.19789 | 0.97992 | 0.69637 | 1482.53257 |
| bad_to_good_0.25 | 7.69248 | 0.11162 | 0.97996 | 0.69641 | 1638.98514 |
| bitrate_12800 | 7.11504 | 0.04870 | 0.97991 | 0.69649 | 1765.81486 |
| bitrate_3200 | 7.35747 | 0.26053 | 0.97098 | 0.67324 | 1595.68457 |
| bitrate_6400 | 7.11504 | 0.04870 | 0.97991 | 0.69649 | 1765.81486 |
| bucket_slots_16 | 7.11504 | 0.04870 | 0.97991 | 0.69649 | 1765.81486 |
| bucket_slots_2 | 7.11071 | 0.05134 | 0.97995 | 0.69637 | 1764.05943 |
| bucket_slots_4 | 7.11504 | 0.04870 | 0.97991 | 0.69649 | 1765.81486 |
| bucket_slots_8 | 7.11504 | 0.04870 | 0.97991 | 0.69649 | 1765.81486 |
| dt_0.025 | 7.30058 | 0.04624 | 0.98207 | 0.70461 | 1741.38514 |
| dt_0.05 | 7.17814 | 0.05308 | 0.98342 | 0.69675 | 1745.84686 |
| dt_0.1 | 7.11504 | 0.04870 | 0.97991 | 0.69649 | 1765.81486 |
| duty_0.4 | 7.18444 | 0.13718 | 0.97926 | 0.68977 | 1687.25943 |
| duty_0.8 | 7.11504 | 0.04870 | 0.97991 | 0.69649 | 1765.81486 |
| duty_1.0 | 7.11504 | 0.04870 | 0.97991 | 0.69649 | 1765.81486 |
| good_to_bad_0.01 | 7.71067 | 0.11964 | 0.97990 | 0.69637 | 1638.03429 |
| good_to_bad_0.025 | 8.58163 | 0.19789 | 0.97992 | 0.69637 | 1482.53257 |
| good_to_bad_0.1 | 11.87529 | 0.42270 | 0.97994 | 0.69614 | 1064.00914 |
| rate_0.015 | 7.11504 | 0.04870 | 0.97991 | 0.69649 | 1765.81486 |
| rate_0.04 | 3.16950 | 0.15463 | 0.97439 | 0.80960 | 3855.50629 |
| rate_0.1 | 3.50460 | 0.63152 | 0.81870 | 0.95527 | 3904.14629 |
| success_0.55 | 12.31140 | 0.45267 | 0.97991 | 0.69619 | 1019.17257 |
| success_0.8 | 8.53069 | 0.19659 | 0.97991 | 0.69633 | 1484.94629 |
| success_0.95 | 7.11504 | 0.04870 | 0.97991 | 0.69649 | 1765.81486 |

## 配对比较

差值为 FUD − 对照，区间为对 seed 配对差值进行 2,000 次 bootstrap 的 95% CI。AoI/miss 越低越好，Service Share Jain 越高越均衡。完整比较见 paired_differences.csv。

| 场景 | 对照 | 指标 | 差值 | 95% CI |
|---|---|---|---:|---|
| bad_to_good_0.05 | aoi_gain | mean_aoi_s | -0.01058 | [-0.05781, 0.04025] |
| bad_to_good_0.05 | aoi_gain | event_deadline_miss | -0.00101 | [-0.00692, 0.00476] |
| bad_to_good_0.05 | aoi_gain | jain_service_share | -0.00004 | [-0.00026, 0.00014] |
| bad_to_good_0.05 | edf | mean_aoi_s | -0.05017 | [-0.13009, 0.03361] |
| bad_to_good_0.05 | edf | event_deadline_miss | 0.00042 | [-0.00565, 0.00688] |
| bad_to_good_0.05 | edf | jain_service_share | 0.00004 | [-0.00024, 0.00033] |
| bad_to_good_0.05 | fifo | mean_aoi_s | -0.06791 | [-0.16990, 0.03844] |
| bad_to_good_0.05 | fifo | event_deadline_miss | -0.00177 | [-0.00671, 0.00298] |
| bad_to_good_0.05 | fifo | jain_service_share | 0.00014 | [-0.00009, 0.00037] |
| bad_to_good_0.05 | maxweight | mean_aoi_s | -0.11556 | [-0.20457, -0.02684] |
| bad_to_good_0.05 | maxweight | event_deadline_miss | -0.00447 | [-0.00940, 0.00071] |
| bad_to_good_0.05 | maxweight | jain_service_share | -0.00016 | [-0.00042, 0.00009] |
| bad_to_good_0.05 | pf | mean_aoi_s | -0.03348 | [-0.07356, 0.01126] |
| bad_to_good_0.05 | pf | event_deadline_miss | -0.00358 | [-0.00942, 0.00219] |
| bad_to_good_0.05 | pf | jain_service_share | -0.00002 | [-0.00019, 0.00015] |
| bad_to_good_0.1 | aoi_gain | mean_aoi_s | -0.01898 | [-0.04779, 0.01182] |
| bad_to_good_0.1 | aoi_gain | event_deadline_miss | 0.00057 | [-0.00362, 0.00452] |
| bad_to_good_0.1 | aoi_gain | jain_service_share | -0.00005 | [-0.00028, 0.00016] |
| bad_to_good_0.1 | edf | mean_aoi_s | -0.08790 | [-0.15079, -0.02236] |
| bad_to_good_0.1 | edf | event_deadline_miss | 0.00216 | [-0.00216, 0.00627] |
| bad_to_good_0.1 | edf | jain_service_share | 0.00000 | [-0.00031, 0.00033] |
| bad_to_good_0.1 | fifo | mean_aoi_s | -0.03848 | [-0.10291, 0.02816] |
| bad_to_good_0.1 | fifo | event_deadline_miss | -0.00077 | [-0.00438, 0.00272] |
| bad_to_good_0.1 | fifo | jain_service_share | 0.00010 | [-0.00016, 0.00035] |
| bad_to_good_0.1 | maxweight | mean_aoi_s | -0.10064 | [-0.17581, -0.02393] |
| bad_to_good_0.1 | maxweight | event_deadline_miss | -0.00199 | [-0.00522, 0.00126] |
| bad_to_good_0.1 | maxweight | jain_service_share | -0.00014 | [-0.00042, 0.00016] |
| bad_to_good_0.1 | pf | mean_aoi_s | -0.00467 | [-0.03700, 0.02894] |
| bad_to_good_0.1 | pf | event_deadline_miss | -0.00228 | [-0.00740, 0.00269] |
| bad_to_good_0.1 | pf | jain_service_share | -0.00019 | [-0.00041, 0.00004] |
| bad_to_good_0.25 | aoi_gain | mean_aoi_s | -0.01730 | [-0.04469, 0.01106] |
| bad_to_good_0.25 | aoi_gain | event_deadline_miss | -0.00038 | [-0.00456, 0.00314] |
| bad_to_good_0.25 | aoi_gain | jain_service_share | -0.00008 | [-0.00031, 0.00012] |
| bad_to_good_0.25 | edf | mean_aoi_s | -0.07132 | [-0.12181, -0.02251] |
| bad_to_good_0.25 | edf | event_deadline_miss | -0.00167 | [-0.00588, 0.00253] |
| bad_to_good_0.25 | edf | jain_service_share | 0.00004 | [-0.00030, 0.00040] |
| bad_to_good_0.25 | fifo | mean_aoi_s | -0.03948 | [-0.09435, 0.01559] |
| bad_to_good_0.25 | fifo | event_deadline_miss | -0.00371 | [-0.00795, 0.00056] |
| bad_to_good_0.25 | fifo | jain_service_share | 0.00014 | [-0.00014, 0.00041] |
| bad_to_good_0.25 | maxweight | mean_aoi_s | -0.04690 | [-0.08976, -0.00950] |
| bad_to_good_0.25 | maxweight | event_deadline_miss | -0.00588 | [-0.01056, -0.00158] |
| bad_to_good_0.25 | maxweight | jain_service_share | -0.00010 | [-0.00039, 0.00016] |
| bad_to_good_0.25 | pf | mean_aoi_s | -0.00183 | [-0.02041, 0.01563] |
| bad_to_good_0.25 | pf | event_deadline_miss | -0.00430 | [-0.00878, -0.00032] |
| bad_to_good_0.25 | pf | jain_service_share | -0.00012 | [-0.00032, 0.00008] |

## 不利结果

negative_results.csv 保存全部不利均值方向；区间跨零的比较表示方向尚不明确。以下列出三项主要指标的前 30 条记录。

| 场景 | 对照 | 指标 | FUD−对照 | 95% CI |
|---|---|---|---:|---|
| bad_to_good_0.05 | aoi_gain | jain_service_share | -0.00004 | [-0.00026, 0.00014] |
| bad_to_good_0.05 | edf | event_deadline_miss | 0.00042 | [-0.00565, 0.00688] |
| bad_to_good_0.05 | fud_no_age | event_deadline_miss | 0.00009 | [-0.00498, 0.00556] |
| bad_to_good_0.05 | fud_no_debt | mean_aoi_s | 0.00012 | [0.00000, 0.00035] |
| bad_to_good_0.05 | fud_no_urgency | mean_aoi_s | 0.00850 | [0.00198, 0.01635] |
| bad_to_good_0.05 | fud_no_urgency | jain_service_share | -0.00001 | [-0.00018, 0.00016] |
| bad_to_good_0.05 | maxweight | jain_service_share | -0.00016 | [-0.00042, 0.00009] |
| bad_to_good_0.05 | pf | jain_service_share | -0.00002 | [-0.00019, 0.00015] |
| bad_to_good_0.05 | priority | event_deadline_miss | 0.00042 | [-0.00565, 0.00688] |
| bad_to_good_0.05 | rr | mean_aoi_s | 0.00729 | [-0.08198, 0.09703] |
| bad_to_good_0.1 | aoi_gain | event_deadline_miss | 0.00057 | [-0.00362, 0.00452] |
| bad_to_good_0.1 | aoi_gain | jain_service_share | -0.00005 | [-0.00028, 0.00016] |
| bad_to_good_0.1 | debt | event_deadline_miss | 0.00117 | [-0.00189, 0.00408] |
| bad_to_good_0.1 | debt | jain_service_share | -0.00006 | [-0.00037, 0.00027] |
| bad_to_good_0.1 | edf | event_deadline_miss | 0.00216 | [-0.00216, 0.00627] |
| bad_to_good_0.1 | fud_no_age | event_deadline_miss | 0.00155 | [-0.00210, 0.00493] |
| bad_to_good_0.1 | fud_no_age | jain_service_share | -0.00004 | [-0.00035, 0.00027] |
| bad_to_good_0.1 | fud_no_debt | mean_aoi_s | 0.00001 | [-0.00000, 0.00002] |
| bad_to_good_0.1 | fud_no_debt | event_deadline_miss | 0.00000 | [-0.00037, 0.00037] |
| bad_to_good_0.1 | fud_no_urgency | mean_aoi_s | 0.00324 | [-0.00363, 0.01065] |
| bad_to_good_0.1 | fud_no_urgency | jain_service_share | -0.00007 | [-0.00020, 0.00006] |
| bad_to_good_0.1 | maxweight | jain_service_share | -0.00014 | [-0.00042, 0.00016] |
| bad_to_good_0.1 | pf | jain_service_share | -0.00019 | [-0.00041, 0.00004] |
| bad_to_good_0.1 | priority | event_deadline_miss | 0.00216 | [-0.00216, 0.00627] |
| bad_to_good_0.25 | aoi_gain | jain_service_share | -0.00008 | [-0.00031, 0.00012] |
| bad_to_good_0.25 | debt | event_deadline_miss | 0.00042 | [-0.00371, 0.00380] |
| bad_to_good_0.25 | debt | jain_service_share | -0.00011 | [-0.00042, 0.00018] |
| bad_to_good_0.25 | fud_no_age | jain_service_share | -0.00002 | [-0.00034, 0.00030] |
| bad_to_good_0.25 | fud_no_debt | event_deadline_miss | 0.00012 | [0.00000, 0.00037] |
| bad_to_good_0.25 | fud_no_urgency | mean_aoi_s | 0.00157 | [-0.00297, 0.00552] |

## 统计定义

event_deadline_success/miss/late 的分母为主观察生成 cohort 内已经判定的事件数；pending 单列。overflow/expiration 的分母为该 cohort 全部事件。状态成功率按已完成发送尝试计算，替换率按状态生成数计算。
Service Share 使用观察窗口内实际占用的抽象服务 slots，含失败尝试；加权 Jain 使用 service_slots/weight。每条配置流均进入资源向量，全零向量 Jain=0。
pdr、event_miss、jain_pdr、jain_delivery、latency_s 和 cohort_goodput_bps 保留 legacy v1 保护区口径；新版业务指标使用不同字段。状态替换率和资源利用率作为描述量，不作单向优劣排序。
事件时延/P95 条件于成功交付；Goodput 按主 cohort 的最终交付 payload 字节除以主观察时长。尾窗交付与成本另存 metrics.json。
summary.csv 保存各策略均值与区间；per_flow.csv 保存分类指标、QoS、资源份额；runs/ 保存逐包生命周期与决策。
