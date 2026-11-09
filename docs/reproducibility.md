# 复现与数据字典

## 环境与命令

Python 3.11+；依赖及本机版本见 pyproject.toml、requirements-lock.txt 和每组 manifest。项目根目录执行：

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,hardware]'
python -m pytest -q
python run.py run --config configs/refined_v1/pilot.json --out output/reproduction_pilot --workers 4
python run.py analyze --out output/reproduction_pilot
python scripts/audit_refined.py output/reproduction_pilot
```

开发例子为 78 次运行，正式矩阵分别运行到四个新目录：

```sh
python run.py run --config configs/refined_v1/main.json --out output/reproduction_v2 --workers 6
python run.py run --config configs/refined_v1/scaling.json --out output/reproduction_v2/scaling --workers 6
python run.py run --config configs/refined_v1/sensitivity.json --out output/reproduction_v2/sensitivity --workers 6
python run.py run --config configs/refined_v1/bucket_load.json --out output/reproduction_v2/bucket_load --workers 6
python run.py analyze --out output/reproduction_v2
python run.py analyze --out output/reproduction_v2/scaling
python run.py analyze --out output/reproduction_v2/sensitivity
python run.py analyze --out output/reproduction_v2/bucket_load
python scripts/audit_refined.py output/reproduction_v2
python scripts/audit_refined.py output/reproduction_v2/scaling
python scripts/audit_refined.py output/reproduction_v2/sensitivity
python scripts/audit_refined.py output/reproduction_v2/bucket_load
pio run -d hardware/firmware -e sender -e receiver
```

`scripts/run_refined.py` 顺序执行以上完整矩阵、分析和独立审计，输出默认使用 output/study_refined_v1；本轮已生成的结果通过相同源码/config/trace hash 恢复。每次实现或配置改变时选择新输出目录。workers 只改变并发，不改变调度结果。

配置可由 `python scripts/make_refined_configs.py` 重建。全部审计完成后运行 `python scripts/finalize_refined.py`，生成跨参数配对效应、源端 AoI 对照、A–K 报告、双语 README 和最终证据索引。分析只接受 metric_version=2；v1 复现使用发布提交 `1b302342` 的源码和 configs/study.json，原始报告与数据继续位于 output/study/。

## 数据文件

| 文件 | 内容 |
|---|---|
| manifest.json | 完整配置、seed、方法、metric_version、源码 hash、依赖与平台 |
| completion.json / failures.json | 实际/期望次数、耗时和失败记录；失败使运行器退出非零 |
| runs/{scenario}/{seed}/{policy}/config.json | 单次完整配置 |
| metrics.json | v2 分类指标、legacy 字段、每流 QoS/资源份额、主/尾窗口和结局 |
| packets.jsonl.gz | id、flow、generated、size、started、received、finished、主截止点快照和最终状态 |
| decisions.jsonl.gz | 服务起点、业务流、包 id、完整服务成本 |
| all_runs.csv / per_flow.csv | 全部运行和业务流的标量指标 |
| summary.csv | 每个场景/策略/指标的 seed 均值、n、95% CI |
| paired_differences.csv | FUD−对照的 seed 配对差值和区间 |
| negative_results.csv | 指标均值朝不利方向变化的全部比较；描述量不作单向排序 |
| overview.png / ablations.png / results.md | 主指标图、机制消融图和自动报告 |
| audit.json | 原始日志独立重算、共享轨迹、确定性重放与源码核对 |
| source_snapshot.zip | 本轮执行源码快照，本地保存 |

时间单位为 slot，乘 dt 得秒；payload 单位为字节，服务资源为抽象 slots。完整数学定义与分母见 [metrics-v2.md](metrics-v2.md)。

## 随机性和统计

每个 seed 用三个独立 RNG 流产生到达、潜在成功结果和 Markov 转移。同一配置/seed 的全部策略共享 Trace；发送的绝对 slot/flow 决定读取的潜在结果。Trace hash 包含到达、信道、配置和 seed。

固定总负载实验在不同节点规模下保持分类到达时刻及包数相同，之后按类均匀拆分。其他节点规模实验固定每流速率，因此总到达量随流数改变。

以 seed 为统计重复单位，20 个 seed 均值及配对差值各进行 2,000 次 bootstrap，分析 seed 为 20261106。CI 为探索性逐项区间，完整比较集和不利方向均保留。

## 版本与完整性

原结果目录、manifest、配置、审计及报告不作改写。第一轮修改前的文件摘要见 docs/validation/refined_v1/baseline_inventory.json，原 README/研究报告/协议副本见 output/archive/refinement_baseline/。历史文案修订指纹仍位于 documentation_revision.json，适用于 v1。

v2 manifest 的 code_hash 对 src 下全部 Python 源文件逐字节计算。审计要求当前源码与 manifest 一致，并重放代表性 FUD 和 PF 运行；后续代码变化可使用该批次源码快照恢复执行环境。

仓库保存汇总 CSV、报告、配置、图表和审计。原始压缩逐包日志和源码快照位于本地 output/**/runs/ 与 source_snapshot.zip，按配置运行可重新生成。
