# 仿真实验结果（自动生成）

共 52 次运行。数据来自离散时隙网络模型，配置、源码版本与环境见 manifest.json。

## FUD 场景表现

| 场景 | 状态AoI(s) | 事件miss | PDR | Jain(PDR) |
|---|---:|---:|---:|---:|
| congestion | 4.1423 | 0.9096 | 0.1920 | 0.6065 |
| normal | 6.6897 | 0.2241 | 0.8585 | 0.9427 |

## 主要配对比较

以下差值为 FUD − FIFO；负值有利于AoI/miss。CI为按seed配对的95%bootstrap区间，采用探索性比较。

| 场景 | 指标 | 差值 | 95% CI |
|---|---|---:|---|
| congestion | mean_aoi_s | 0.62220 | [0.43679, 0.80761] |
| congestion | event_miss | -0.09044 | [-0.09091, -0.08997] |

## 负面结果示例（全部记录见negative_results.csv）

| 场景 | 对照 | 指标 | FUD−对照 |
|---|---|---|---:|
| congestion | aoi_gain | event_miss | 0.23130 |
| congestion | aoi_gain | jain_pdr | -0.10028 |
| congestion | debt | event_miss | 0.09395 |
| congestion | debt | jain_pdr | -0.27508 |
| congestion | edf | event_miss | 0.14788 |
| congestion | edf | jain_pdr | -0.06690 |
| congestion | fifo | mean_aoi_s | 0.62220 |
| congestion | fifo | jain_pdr | -0.01826 |
| congestion | fud_no_age | event_miss | 0.44873 |
| congestion | fud_no_debt | mean_aoi_s | 0.00546 |
| congestion | fud_no_debt | event_miss | 0.00346 |
| congestion | fud_no_debt | jain_pdr | -0.00411 |
| congestion | fud_no_urgency | mean_aoi_s | 0.89371 |
| congestion | maxweight | event_miss | 0.33731 |
| congestion | pf | mean_aoi_s | 0.45727 |
| congestion | pf | event_miss | 0.07827 |
| congestion | pf | jain_pdr | -0.36517 |
| congestion | priority | event_miss | 0.45047 |
| congestion | rr | mean_aoi_s | 0.89040 |
| congestion | rr | event_miss | 0.00696 |
| congestion | rr | jain_pdr | -0.25512 |
| congestion | wrr | mean_aoi_s | 0.53094 |
| congestion | wrr | event_miss | 0.03293 |
| congestion | wrr | jain_pdr | -0.26767 |
| normal | aoi_gain | event_miss | 0.09030 |

## 指标解读

PDR 按生成 cohort 统计，并区分状态替换、队列丢弃与链路损失。公平性按每流 PDR 计算，时延按交付包统计。节点数量实验同时改变总负载。模型采用已知时间戳、固定反馈时延与有效服务率。

summary.csv 保存各方法均值与区间；paired_differences.csv 保存全部配对差值；per_flow.csv 提供每流服务水平；runs/ 保存逐包结局和调度决策。