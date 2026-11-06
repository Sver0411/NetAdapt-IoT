# Related Work

十四篇理论与代表性方法覆盖 AoI、QoS、公平分配与队列管理。

## R01. Real-time status: How often should one update?

Sanjit Kaul; Roy Yates; Marco Gruteser。2012，2012 Proceedings IEEE INFOCOM。DOI：10.1109/infcom.2012.6195689；[原始来源](https://doi.org/10.1109/infcom.2012.6195689)。

- 资料状态：出版元数据及可检索正文；正文待补充。

- 方法：AoI定义与FCFS队列，产生率并非越高越好；本项目固定流量而不优化采样。。

- 讨论与后续：按正文与版本记录补充。

- 项目关联：项目方法关联见 related_work.md。

## R02. Age of Information: An Introduction and Survey

Roy D. Yates; Yin Sun; D. Richard Brown; Sanjit K. Kaul; Eytan Modiano; Sennur Ulukus。2021，IEEE Journal on Selected Areas in Communications。DOI：10.1109/jsac.2021.3065072；[原始来源](https://doi.org/10.1109/jsac.2021.3065072)。

- 资料状态：全文PDF（综述）。

- 方法：覆盖AoI度量、排队、采样和网络调度；用于统一定义，用于模型定义与方法分类。。

- 讨论与后续：按正文与版本记录补充。

- 项目关联：项目方法关联见 related_work.md。

## R03. Scheduling Policies for Minimizing Age of Information in Broadcast Wireless Networks

Igor Kadota; Abhishek Sinha; Elif Uysal-Biyikoglu; Rahul Singh; Eytan Modiano。2018，IEEE/ACM Transactions on Networking 26(6):2637–2650。DOI：10.1109/TNET.2018.2873606；[原始来源](https://doi.org/10.1109/TNET.2018.2873606)。

- 资料状态：全文PDF；模型/策略/数值章节。

- 方法：不可靠广播链路；Greedy、随机、MaxWeight、Whittle及理论界。作者将随机到达、时变信道、多跳列为扩展；项目采用外生到达与混合业务。。

- 讨论与后续：按正文与版本记录补充。

- 项目关联：项目方法关联见 related_work.md。

## R04. Optimizing Age of Information in Wireless Networks with Throughput Constraints

Igor Kadota; Abhishek Sinha; Eytan Modiano。2018，IEEE INFOCOM 2018 - IEEE Conference on Computer Communications。DOI：10.1109/infocom.2018.8486307；[原始来源](https://doi.org/10.1109/infocom.2018.8486307)。

- 资料状态：出版商正文引言+MIT库摘要；本地PDF链接404。

- 方法：联合AoI与及时吞吐要求，含随机/MaxWeight/Whittle；提供 AoI 与吞吐联合建模依据，数值实验细节待补充全文。。

- 讨论与后续：按正文与版本记录补充。

- 项目关联：项目方法关联见 related_work.md。

## R05. Scheduling Policies for Age Minimization in Wireless Networks With Unknown Channel State

Rajat Talak; Igor Kadota; Sertac Karaman; Eytan Modiano。2018，arXiv:1805.06752; 预印本版本。DOI：arXiv 版本见原始来源；[原始来源](https://arxiv.org/abs/1805.06752)。

- 资料状态：全文arXiv预印本（11页）。

- 方法：当前信道不可见但统计已知；虚拟队列与age-based策略；本项目采用 EWMA 反馈和时变链路。。

- 讨论与后续：按正文与版本记录补充。

- 项目关联：项目方法关联见 related_work.md。

## R06. A Theory of QoS for Wireless

I-Hong Hou; Vivek S. Borkar; P. R. Kumar。2009，IEEE INFOCOM:486–494。DOI：10.1109/INFCOM.2009.5061954；[原始来源](https://doi.org/10.1109/INFCOM.2009.5061954)。

- 资料状态：全文PDF（10页）；模型/仿真/结论。

- 方法：准入可行性与两种最大欠账优先，比较random/DCF；作者明确同到达周期及统一deadline假设限制。。

- 讨论与后续：按正文与版本记录补充。

- 项目关联：项目方法关联见 related_work.md。

## R07. Stability properties of constrained queueing systems and scheduling policies for maximum throughput in multihop radio networks

L. Tassiulas; A. Ephremides。1992，IEEE Transactions on Automatic Control。DOI：10.1109/9.182479；[原始来源](https://doi.org/10.1109/9.182479)。

- 资料状态：出版元数据+大学作者技术报告摘要。

- 方法：可行激活集合下吞吐稳定性最优；吞吐稳定性、AoI 与截止期分别评价；单跳 MaxWeight 按当前模型实现。。

- 讨论与后续：按正文与版本记录补充。

- 项目关联：项目方法关联见 related_work.md。

## R08. Efficient fair queueing using deficit round robin

M. Shreedhar; George Varghese。1995，Proceedings of the conference on Applications, technologies, architectures, and protocols for computer communication。DOI：10.1145/217382.217453；[原始来源](https://doi.org/10.1145/217382.217453)。

- 资料状态：Crossref书目；正文待补充。

- 方法：DRR为字节公平提供经典参考。本轮主包长相同采用WRR；异包长实验分别记录包服务份额与字节份额。。

- 讨论与后续：按正文与版本记录补充。

- 项目关联：项目方法关联见 related_work.md。

## R09. Rate control for communication networks: shadow prices, proportional fairness and stability

F P Kelly; A K Maulloo; D K H Tan。1998，Journal of the Operational Research Society。DOI：10.1057/palgrave.jors.2600523；[原始来源](https://doi.org/10.1057/palgrave.jors.2600523)。

- 资料状态：Crossref+可检索原论文正文；本地下载TLS失败。

- 方法：比例公平与网络效用优化的理论依据；本项目PF是无线在线调度适配，采用当前共享出口模型实现。。

- 讨论与后续：按正文与版本记录补充。

- 项目关联：项目方法关联见 related_work.md。

## R10. A generalized processor sharing approach to flow control in integrated services networks: the single-node case

A.K. Parekh; R.G. Gallager。1993，IEEE/ACM Transactions on Networking。DOI：10.1109/90.234856；[原始来源](https://doi.org/10.1109/90.234856)。

- 资料状态：Crossref书目；正文待补充。

- 方法：GPS给出理想公平共享参照；为分组服务公平性提供参照。。

- 讨论与后续：按正文与版本记录补充。

- 项目关联：项目方法关联见 related_work.md。

## R11. Controlling Queue Delay

Kathleen Nichols; Van Jacobson。2012，Queue。DOI：10.1145/2208917.2209336；[原始来源](https://doi.org/10.1145/2208917.2209336)。

- 资料状态：出版元数据+可检索原论文正文；本地站点403。

- 方法：CoDel以排队驻留时间区分持久排队与突发；TCP 反馈闭环作为后续拥塞控制扩展。。

- 讨论与后续：按正文与版本记录补充。

- 项目关联：项目方法关联见 related_work.md。

## R12. Scheduling With Soft Age-of-Information Deadlines

Chengzhang Li; Qingyu Liu; Shaoran Li; Yongce Chen; Y. Thomas Hou; Wenjing Lou; Sastry Kompella。2025，IEEE Internet of Things Journal。DOI：10.1109/jiot.2024.3496113；[原始来源](https://doi.org/10.1109/jiot.2024.3496113)。

- 资料状态：IEEE出版商摘要；正文待补充。

- 方法：AoI软deadline及违约容忍和可调度性已被研究；分别记录 packet deadline 与 AoI deadline，具体实验证据待全文。。

- 讨论与后续：按正文与版本记录补充。

- 项目关联：项目方法关联见 related_work.md。

## R13. Optimizing Age of Information in Networks with Large and Small Updates

Zhuoyi Zhao; Vishrant Tripathi; Igor Kadota。2025，arXiv:2503.23658v1; 预印本。DOI：arXiv 版本见原始来源；[原始来源](https://arxiv.org/abs/2503.23658)。

- 资料状态：全文arXiv HTML v1；§II–VII。

- 方法：不同大小更新、切换/非切换随机策略与MaxWeight；包含理论及仿真。本项目按包长与资源预算分析服务变化。。

- 讨论与后续：按正文与版本记录补充。

- 项目关联：项目方法关联见 related_work.md。

## R14. Toward Practical Age-of-Information Scheduling in 5G Cellular

Zhuoyi Zhao; Igor Kadota。2026，arXiv:2605.13012v1; 预印本。DOI：arXiv 版本见原始来源；[原始来源](https://arxiv.org/abs/2605.13012)。

- 资料状态：全文arXiv HTML v1；§II–V。

- 方法：5G gNB可观测性限制；低复杂度估计+MW-LC，NetSim/MATLAB验证；作者设计仍需长期流量参数、包身份及Bernoulli近似；本项目有显式时间戳和理想仿真ACK。。

- 讨论与后续：按正文与版本记录补充。

- 项目关联：项目方法关联见 related_work.md。

## 方法关联

AoI 提供状态更新目标，QoS 研究提供截止期与服务欠账机制，公平分配研究提供多流服务指标，队列管理研究提供拥塞与延迟分析。项目将这些方法用于共享出口实验。
