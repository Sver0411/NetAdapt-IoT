"""Build topic-based bibliography and reading documents from curated notes."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'research/literature'
rows = json.loads((P / 'reading_notes.json').read_text())

with (P / 'literature_matrix.csv').open('w', newline='') as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

def citation(row):
    return (f"{row['authors']}。{row['year']}，{row['venue']}。"
            f"DOI：{row['doi'] or 'arXiv 版本见原始来源'}；"
            f"[原始来源]({row['original_url']})。")

labels = {
    'access_status': '资料状态', 'background': '背景', 'problem': '问题',
    'network_model': '网络模型', 'method': '方法', 'baselines': '比较方法',
    'environment': '实验环境', 'metrics': '指标', 'results': '结果',
    'discussion': '讨论与后续', 'project_questions': '项目关联',
}
network = ['# 网络通信与资源调度论文',
           '\n按共享资源、应用需求、网络实现与多路径传输组织十篇研究。']
related = ['# Related Work',
           '\n十四篇理论与代表性方法覆盖 AoI、QoS、公平分配与队列管理。']
bibliography = ['# 网络资源调度参考文献',
                '\n按题名、作者、年份、出版物和 DOI 组织项目使用的 24 篇文献。',
                '\n| 编号 | 年份 | 论文 | 资料状态 |', '|---|---|---|---|']
for row in rows:
    bibliography.append(f"| {row['id']} | {row['year']} | [{row['title']}]({row['original_url']}) | {row['access_status']} |")
    target = network if row['id'].startswith('P') else related
    target += [f"\n## {row['id']}. {row['title']}", '\n' + citation(row)]
    for key, label in labels.items():
        value = row.get(key, '')
        if value and value != '待补充':
            target.append(f'\n- {label}：{value}。')
network += ['\n## 版本记录',
            '\nP03 采用 DOI 10.23919/comex.2023COL0002；P04 出版年为 2023。P06 按预印本与出版版本分别记录。P10 按会议、作者列表与 DOI 区分同题条目。']
related += ['\n## 方法关联',
            '\nAoI 提供状态更新目标，QoS 研究提供截止期与服务欠账机制，公平分配研究提供多流服务指标，队列管理研究提供拥塞与延迟分析。项目将这些方法用于共享出口实验。']
(P / 'networking_papers.md').write_text('\n'.join(network) + '\n')
(P / 'related_work.md').write_text('\n'.join(related) + '\n')
(P / 'bibliography.md').write_text('\n'.join(bibliography) + '\n')
print(f'{len(rows)} references rendered')
