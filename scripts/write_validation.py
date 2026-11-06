"""Generate software validation notes from experiment logs."""
import csv,json,re
from pathlib import Path

root=Path(__file__).resolve().parents[1];out=root/'output/study'
completion=json.loads((out/'completion.json').read_text())
audit=json.loads((out/'audit.json').read_text())
log=(root/'docs/validation/pytest.log').read_text()
count=int(re.findall(r'(\d+) passed',log)[-1])
assert completion['runs']==completion['expected_runs']==3900 and completion['failures']==0
assert audit['status']=='PASS' and audit['audited_runs']==3900
assert '2 succeeded' in (root/'docs/validation/firmware-build.log').read_text()
negative=len(list(csv.DictReader((out/'negative_results.csv').open())))
rows=list(csv.DictReader((out/'paired_differences.csv').open()))
def row(s,b,m):return next(r for r in rows if (r['scenario'],r['baseline'],r['metric'])==(s,b,m))
text=['# 软件验证记录',
'\n记录日期：2026-11-06。当前里程碑为软件评估与双端固件构建，下一阶段开展物理链路校准。',
'\n| 检查 | 结果 | 证据 |','|---|---|---|',
f'| Python单元/集成测试 | **{count} passed** | [pytest.log](pytest.log) |',
'| 开发用例 | 52次，全部完成 | [pilot completion](../../output/pilot/completion.json) |',
'| 最终模型正式仿真 | **3900 / 3900，0失败** | [completion.json](../../output/study/completion.json)、[failures.json](../../output/study/failures.json) |',
'| 统一随机条件 | 300组scenario/seed，13方法组内trace hash相同 | [audit.json](../../output/study/audit.json) |',
'| 包守恒/资源预算/事件cohort截断 | 全部3900次通过 | audit.json及逐次metrics |',
'| 确定性重放 | normal/congestion/markov_link/mixed_sizes/nodes_96的FUD逐字段一致 | audit.json |',
'| 分数预算可达性 | 单流饱和时0.8预算达到0.8服务利用率 | test_saturated_service_reaches_fractional_budget |',
'| 统计与图表 | 全量CSV、配对CI、负面结果、2张图 | [结果报告](../../output/study/results.md) |',
'| ESP32-S3 N16R8固件构建 | sender / receiver **SUCCESS** | [firmware-build.log](firmware-build.log) |',
'| 串口协议测试 | CRC、帧长度、ACK身份过滤、原始日志及错误反馈通过 | 模拟串口协议检查 |',
'| 物理链路与电流采集 | 下一阶段 | [硬件指南](../../hardware/README.md) |',

f"\n最终批次运行约{completion['seconds']:.0f}秒；不含环境准备、开发、旧批次及分析。全部{negative}条均值方向不利的指标比较保留在negative_results.csv，对应区间记录在配对比较表。",
'\n## 主要假设（最终模型）']
for s in ['congestion','bursty']:
    h1=all(float(row(s,'fifo',m)['ci_high'])<0 for m in ['mean_aoi_s','event_miss'])
    h2=float(row(s,'aoi_gain','event_miss')['ci_high'])<0 or float(row(s,'aoi_gain','jain_pdr')['ci_low'])>0
    h3=float(row(s,'fud_no_debt','jain_pdr')['ci_low'])>0
    text.append(f'\n- {s}：H1（同时降AoI/miss）'+('获支持' if h1 else '未获完整支持')+'；H2（相对纯AoI改善miss或公平性）'+('获局部支持' if h2 else '不受支持')+'；H3欠账公平性效应'+('区间支持为正' if h3 else ('区间支持为负' if float(row(s,'fud_no_debt','jain_pdr')['ci_high'])<0 else '证据有限'))+'。')
text+=['\n各场景的效应大小与配对区间见[技术报告](../../research/REPORT.md)。',
'\n## 版本记录',
'\n开发过程中修订了 event 接收时间戳与预算桶容量。最终模型统一四 slot 桶，历史模型按版本归档。见[实现修正](implementation_correction.md)、[预算模型敏感性](budget_model_comparison.md)。各版本采用相同 FUD 公式、系数与评估种子。',
'\n本地构建采用espressif32 6.9.0、Arduino ESP32 2.0.17框架系列、16MB Flash/8MB OPI PSRAM配置。默认 GPIO 与接线、参数读取和校准流程见[硬件指南](../../hardware/README.md)。']
(root/'docs/validation/status.md').write_text('\n'.join(text))
print(f'acceptance: {count} tests, {completion["runs"]} runs, {negative} negative metric comparisons')
