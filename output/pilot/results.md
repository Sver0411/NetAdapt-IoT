# 仿真实验结果（自动生成）

共 52 次运行。数据来自离散时隙网络模型，配置、源码版本与环境见 manifest.json。

## FUD 场景表现

| 场景 | 状态AoI(s) | 事件miss | PDR | Jain(PDR) |
|---|---:|---:|---:|---:|
| congestion | 3.7605 | 0.6417 | 0.3008 | 0.7698 |
| normal | 6.7781 | 0.1505 | 0.8967 | 0.9505 |

## 主要配对比较

以下差值为 FUD − FIFO；负值有利于AoI/miss。CI为按seed配对的95%bootstrap区间，采用探索性比较。

| 场景 | 指标 | 差值 | 95% CI |
|---|---|---:|---|
| congestion | mean_aoi_s | 1.50182 | [1.45311, 1.55054] |
| congestion | event_miss | -0.32518 | [-0.33218, -0.31818] |

## 负面结果示例（全部记录见negative_results.csv）

| 场景 | 对照 | 指标 | FUD−对照 |
|---|---|---|---:|
| congestion | aoi_gain | event_miss | 0.15654 |
| congestion | debt | mean_aoi_s | 0.72549 |
| congestion | debt | jain_pdr | -0.13199 |
| congestion | edf | event_miss | 0.17924 |
| congestion | fifo | mean_aoi_s | 1.50182 |
| congestion | fud_no_age | event_miss | 0.46430 |
| congestion | fud_no_debt | event_miss | 0.00519 |
| congestion | fud_no_urgency | mean_aoi_s | 1.64854 |
| congestion | maxweight | event_miss | 0.19115 |
| congestion | pf | mean_aoi_s | 1.19520 |
| congestion | pf | jain_pdr | -0.20528 |
| congestion | priority | event_miss | 0.45911 |
| congestion | rr | mean_aoi_s | 1.43172 |
| congestion | rr | jain_pdr | -0.11752 |
| congestion | wrr | mean_aoi_s | 1.33738 |
| congestion | wrr | jain_pdr | -0.11826 |
| normal | aoi_gain | event_miss | 0.06020 |
| normal | aoi_gain | jain_pdr | -0.00950 |
| normal | debt | mean_aoi_s | 0.08805 |
| normal | debt | event_miss | 0.03261 |
| normal | debt | jain_pdr | -0.00891 |
| normal | edf | event_miss | 0.03261 |
| normal | edf | jain_pdr | -0.00451 |
| normal | fifo | jain_pdr | -0.00865 |
| normal | fud_no_age | event_miss | 0.02174 |

## 指标解读

PDR 按生成 cohort 统计，并区分状态替换、队列丢弃与链路损失。公平性按每流 PDR 计算，时延按交付包统计。节点数量实验同时改变总负载。模型采用已知时间戳、固定反馈时延与有效服务率。

summary.csv 保存各方法均值与区间；paired_differences.csv 保存全部配对差值；per_flow.csv 提供每流服务水平；runs/ 保存逐包结局和调度决策。