# 仿真实验结果（自动生成）

共 3900 次运行。数据来自离散时隙网络模型，配置、源码版本与环境见 manifest.json。

## FUD 场景表现

| 场景 | 状态AoI(s) | 事件miss | PDR | Jain(PDR) |
|---|---:|---:|---:|---:|
| budget_100 | 7.1150 | 0.0488 | 0.9444 | 0.9990 |
| budget_40 | 7.1844 | 0.1374 | 0.9026 | 0.9970 |
| bursty | 5.5926 | 0.1815 | 0.7872 | 0.9882 |
| congestion | 3.5046 | 0.6318 | 0.3145 | 0.8184 |
| equal_weights | 7.1172 | 0.0514 | 0.9435 | 0.9990 |
| long_delay | 7.5170 | 0.2329 | 0.8828 | 0.9887 |
| lossless | 6.7927 | 0.0009 | 0.9925 | 0.9998 |
| markov_link | 8.5816 | 0.1982 | 0.7929 | 0.9951 |
| mixed_sizes | 7.2339 | 0.0974 | 0.9203 | 0.9977 |
| nodes_48 | 7.2122 | 0.0979 | 0.9161 | 0.9980 |
| nodes_8 | 7.0359 | 0.0552 | 0.9461 | 0.9990 |
| nodes_96 | 8.0956 | 0.8539 | 0.5270 | 0.7519 |
| normal | 7.1150 | 0.0488 | 0.9444 | 0.9990 |
| unequal_rates | 5.2985 | 0.0478 | 0.9307 | 0.9980 |
| weak_link | 12.3114 | 0.4524 | 0.5452 | 0.9821 |

## 主要配对比较

以下差值为 FUD − FIFO；负值有利于AoI/miss。CI为按seed配对的95%bootstrap区间，采用探索性比较。

| 场景 | 指标 | 差值 | 95% CI |
|---|---|---:|---|
| bursty | mean_aoi_s | -0.00394 | [-0.03330, 0.02285] |
| bursty | event_miss | -0.15811 | [-0.16678, -0.14935] |
| congestion | mean_aoi_s | 1.22049 | [1.20904, 1.23202] |
| congestion | event_miss | -0.33240 | [-0.33565, -0.32948] |

## 负面结果示例（全部记录见negative_results.csv）

| 场景 | 对照 | 指标 | FUD−对照 |
|---|---|---|---:|
| budget_100 | debt | event_miss | 0.00118 |
| budget_100 | edf | event_miss | 0.00019 |
| budget_100 | fud_no_age | event_miss | 0.00060 |
| budget_100 | fud_no_urgency | mean_aoi_s | 0.00075 |
| budget_100 | priority | event_miss | 0.00019 |
| budget_40 | aoi_gain | event_miss | 0.04435 |
| budget_40 | aoi_gain | jain_pdr | -0.00102 |
| budget_40 | debt | event_miss | 0.03123 |
| budget_40 | debt | jain_pdr | -0.00102 |
| budget_40 | edf | event_miss | 0.06927 |
| budget_40 | edf | jain_pdr | -0.00095 |
| budget_40 | fud_no_age | event_miss | 0.08118 |
| budget_40 | fud_no_age | jain_pdr | -0.00069 |
| budget_40 | fud_no_debt | mean_aoi_s | 0.00026 |
| budget_40 | fud_no_debt | jain_pdr | -0.00001 |
| budget_40 | fud_no_urgency | mean_aoi_s | 0.02750 |
| budget_40 | pf | event_miss | 0.00266 |
| budget_40 | pf | jain_pdr | -0.00026 |
| budget_40 | priority | event_miss | 0.08153 |
| budget_40 | priority | jain_pdr | -0.00057 |
| bursty | aoi_gain | event_miss | 0.04300 |
| bursty | debt | jain_pdr | -0.00554 |
| bursty | edf | event_miss | 0.08482 |
| bursty | fud_no_age | event_miss | 0.12615 |
| bursty | fud_no_debt | mean_aoi_s | 0.00072 |

## 指标解读

PDR 按生成 cohort 统计，并区分状态替换、队列丢弃与链路损失。公平性按每流 PDR 计算，时延按交付包统计。节点数量实验同时改变总负载。模型采用已知时间戳、固定反馈时延与有效服务率。

summary.csv 保存各方法均值与区间；paired_differences.csv 保存全部配对差值；per_flow.csv 提供每流服务水平；runs/ 保存逐包结局和调度决策。