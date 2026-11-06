# 仿真实验结果（自动生成）

共 3900 次运行。数据来自离散时隙网络模型，配置、源码版本与环境见 manifest.json。

## FUD 场景表现

| 场景 | 状态AoI(s) | 事件miss | PDR | Jain(PDR) |
|---|---:|---:|---:|---:|
| budget_100 | 7.1150 | 0.0488 | 0.9444 | 0.9990 |
| budget_40 | 7.3943 | 0.4468 | 0.7648 | 0.9570 |
| bursty | 5.8748 | 0.4509 | 0.6522 | 0.9681 |
| congestion | 4.0045 | 0.8981 | 0.1964 | 0.6674 |
| equal_weights | 7.2086 | 0.1894 | 0.8846 | 0.9939 |
| long_delay | 7.6017 | 0.5057 | 0.7817 | 0.9325 |
| lossless | 6.8692 | 0.1060 | 0.9427 | 0.9974 |
| markov_link | 8.7095 | 0.2955 | 0.7477 | 0.9912 |
| mixed_sizes | 7.2599 | 0.1921 | 0.8843 | 0.9838 |
| nodes_48 | 7.6449 | 0.6437 | 0.6531 | 0.8882 |
| nodes_8 | 7.0289 | 0.0575 | 0.9431 | 0.9988 |
| nodes_96 | 11.7566 | 1.0000 | 0.3286 | 0.5595 |
| normal | 7.2158 | 0.1505 | 0.8951 | 0.9962 |
| unequal_rates | 5.4050 | 0.0995 | 0.8859 | 0.9953 |
| weak_link | 12.2438 | 0.5297 | 0.5152 | 0.9788 |

## 主要配对比较

以下差值为 FUD − FIFO；负值有利于AoI/miss。CI为按seed配对的95%bootstrap区间，采用探索性比较。

| 场景 | 指标 | 差值 | 95% CI |
|---|---|---:|---|
| bursty | mean_aoi_s | -0.07222 | [-0.11188, -0.03301] |
| bursty | event_miss | -0.09853 | [-0.10422, -0.09236] |
| congestion | mean_aoi_s | 0.54369 | [0.52117, 0.56731] |
| congestion | event_miss | -0.10158 | [-0.10332, -0.09986] |

## 负面结果示例（全部记录见negative_results.csv）

| 场景 | 对照 | 指标 | FUD−对照 |
|---|---|---|---:|
| budget_100 | debt | event_miss | 0.00118 |
| budget_100 | edf | event_miss | 0.00019 |
| budget_100 | fud_no_age | event_miss | 0.00060 |
| budget_100 | fud_no_urgency | mean_aoi_s | 0.00075 |
| budget_100 | priority | event_miss | 0.00019 |
| budget_40 | aoi_gain | event_miss | 0.21897 |
| budget_40 | aoi_gain | jain_pdr | -0.03512 |
| budget_40 | debt | event_miss | 0.10952 |
| budget_40 | debt | jain_pdr | -0.02649 |
| budget_40 | edf | event_miss | 0.23877 |
| budget_40 | edf | jain_pdr | -0.03566 |
| budget_40 | fud_no_age | event_miss | 0.34850 |
| budget_40 | fud_no_age | jain_pdr | -0.03147 |
| budget_40 | fud_no_urgency | mean_aoi_s | 0.06760 |
| budget_40 | maxweight | event_miss | 0.01619 |
| budget_40 | pf | event_miss | 0.10484 |
| budget_40 | pf | jain_pdr | -0.02662 |
| budget_40 | priority | event_miss | 0.34803 |
| budget_40 | priority | jain_pdr | -0.02470 |
| bursty | aoi_gain | event_miss | 0.16683 |
| bursty | aoi_gain | jain_pdr | -0.01363 |
| bursty | debt | event_miss | 0.05854 |
| bursty | debt | jain_pdr | -0.01649 |
| bursty | edf | event_miss | 0.13411 |
| bursty | edf | jain_pdr | -0.01380 |

## 指标解读

PDR 按生成 cohort 统计，并区分状态替换、队列丢弃与链路损失。公平性按每流 PDR 计算，时延按交付包统计。节点数量实验同时改变总负载。模型采用已知时间戳、固定反馈时延与有效服务率。

summary.csv 保存各方法均值与区间；paired_differences.csv 保存全部配对差值；per_flow.csv 提供每流服务水平；runs/ 保存逐包结局和调度决策。