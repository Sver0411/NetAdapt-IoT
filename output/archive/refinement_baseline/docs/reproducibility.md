# 复现与数据字典

## 环境与命令

参考实验使用 Mac 本地 Python 虚拟环境。`requirements-lock.txt`记录本机解析出的依赖版本；跨环境复现时按 pyproject.toml 安装，并记录 Python、NumPy 与依赖版本。

```sh
.venv/bin/python -m pytest -q
.venv/bin/python run.py run --config configs/study.json --out output/reproduction --workers 4
.venv/bin/python run.py analyze --out output/reproduction
.venv/bin/pio run -d hardware/firmware
```

只运行一个小实验时复制 `configs/pilot.json` 并删减场景/seed/方法，使用新输出目录。配置更新后生成对应的新实验目录与 hash。workers控制进程并发，调度决策不依赖运行完成顺序；摘要表排序固定。

## 数据文件

| 路径 | 含义 |
|---|---|
| manifest.json | 完整场景/seed/方法、Python与NumPy版本、src代码hash、模型标签 |
| completion.json / failures.json | 实际与期望次数、耗时及失败信息；失败令CLI退出非零 |
| runs/{scenario}/{seed}/{policy}/config.json | 单次完整参数 |
| metrics.json | 全部指标、每流统计、trace/config hash、预算审计 |
| packets.jsonl.gz | 每包id/flow/generated/size、started/received/finished、最终互斥状态 |
| decisions.jsonl.gz | 每次非抢占服务起点、包和持续时间 |
| all_runs.csv / per_flow.csv | 所有运行与每流数据 |
| summary.csv | 各方法seed均值、n和95% bootstrap CI |
| paired_differences.csv | 每seed相同条件下FUD减基线的差值与CI |
| negative_results.csv | FUD均值方向更差的全部比较，包括消融，并保留配对区间 |

`generated`、`started`、`received`、`finished`的单位均为slot，乘配置dt得到秒；payload单位字节。`received`为空表示没确认交付。`cohort_status_counts`的和应等于评估cohort生成数，`status_counts`的和应等于全部输入包数。

互斥状态：queued（截至观察末仍排队）、inflight（尚未反馈）、replaced、overflow、expired、link_loss、delivered、late。状态替换的包计入 PDR 分母，按 replaced、overflow、expired 与 link_loss 分解原因，并同时记录 AoI。

`event_miss`统计cohort内事件生成包未及时交付的比例；没有事件时为null。`mean_aoi_s`统计warmup后全部slot的状态流平均AoI；与cohort并非同一统计对象。`cohort_goodput_bps`按cohort生成窗口归一化，`observation_goodput_bps`按实际观察时间窗口到达字节统计。两个字段分别对应生成 cohort 与接收观察窗口。

`jain_pdr`按每流PDR归一化，排除无生成流；全零取0。`jain_delivery`按交付包数，更偏向高产生率；两者回答不同问题。latency/P95 按交付包统计，miss 与 PDR 提供对应的交付水平。

## 配对随机与统计

每seed一次生成完整到达与潜在信道结果，全部方法读取同一Trace。链路结果按发送绝对slot与flow索引，调度器读取历史反馈状态。文件中的trace_hash同时含counts、success、config和seed；同一scenario/seed跨policy必须唯一。

置信区间用20个seed配对差值进行2000次bootstrap，固定分析seed20261106。以 seed 为重复单位，报告点差值和区间。完整比较集采用探索性分析。

pilot seeds 0、1用于实现检查，正式评估使用100–119。修订记录、对应源码与各版本完整数据按实验目录保存。

## macOS Python 3.14启动入口

本次发现虚拟环境中的editable .pth被文件系统hidden标志标记，Python3.14跳过该文件，导致包导入失败。已清除该标志，并提供根目录run.py显式加载src，因此建议使用上面的run.py命令；测试也显式配置src路径。run.py 为源码目录提供统一启动入口。

## 文档版本与计算指纹

manifest.json 保留实验执行时的完整源码 hash。后续报告文字整理记录在 documentation_revision.json；该记录保存原始 hash、当前 hash 与计算代码的 AST 指纹。audit_study.py 使用这些版本记录核对计算实现，并重放代表场景。

## 仓库数据结构

仓库保存汇总 CSV、每流统计、图表、实验配置与运行环境。逐包日志位于本地 output/**/runs/，源码快照和完整原始校验文件也保留在本地。重跑配置生成 output/reproduction 后，执行以下命令审计完整数据：

    .venv/bin/python scripts/audit_study.py output/reproduction
