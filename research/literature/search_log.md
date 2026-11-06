# 文献检索与版本记录

日期：2026-11-06。

## 检索主题

- AoI scheduling、throughput constraints、unknown channel、soft deadlines。
- QoS provisioning、shared gateway scheduling、MaxWeight、service debt。
- Proportional fairness、DRR、GPS、queue delay。
- MPTCP/MPQUIC scheduling、P4、dynamic wireless networks。
- 2025–2026 年的异构更新与实际 AoI 调度。

## 资料组织

采用论文标题、作者、发表年份、出版物、DOI 和版本号组织书目。出版元数据来自 Crossref 与出版页面；正文资料来自出版平台、作者稿和 arXiv。

[网络调度论文](networking_papers.md)整理十篇网络实现与资源调度研究，[Related Work](related_work.md)整理十四篇理论与代表性方法，[总书目](bibliography.md)提供统一引用入口。

## 访问记录

全文资料包括 P01、P02、P03、P04、R02、R03、R05、R06、R13、R14。其余条目的访问状态按摘要、出版元数据和待补充正文分别记录。

本地原始下载与查询响应位于用户缓存目录 ~/.cache/netadapt-iot/literature。项目目录保存可编辑的阅读笔记和文献矩阵。

## 版本核对

P03 使用 DOI 10.23919/comex.2023COL0002；P04 出版年为 2023。P06 分别记录预印本与出版版本。P10 按会议、作者列表和 DOI 区分同题条目。R02 为 2021 年综述。arXiv 条目保留对应版本号。

## 更新命令

reading_notes.json 为阅读笔记输入，执行以下命令更新文献矩阵、主题笔记与总书目：

    .venv/bin/python scripts/build_literature.py
