# 网络通信与资源调度论文

按共享资源、应用需求、网络实现与多路径传输组织十篇研究。

## P01. An Accurate Platform for Investigating TCP Performance in Wi-Fi Networks

Shunji Aoyagi; Yuki Horie; Do Thi Thu Hien; Thanh Duc Ngo; Duy-Dinh Le; Kien Nguyen; Hiroo Sekiya。2023，Future Internet。DOI：10.3390/fi15070246；[原始来源](https://doi.org/10.3390/fi15070246)。

- 资料状态：全文（19页；§2–5）。

- 背景：Wi-Fi端到端TCP性能需要结合链路与传输行为评估。

- 问题：构建低成本评估平台并检验一致性。

- 网络模型：Mininet-WiFi、真实Wi-Fi，瓶颈和多流。

- 方法：仿真与实网交叉检验；14种TCP CCA。

- 比较方法：14种CCA、不同缓存和链路/流数设置。

- 实验环境：Mininet-WiFi及真实网络，ping/iperf/tcpdump。

- 指标：RTT、吞吐、Jain公平性。

- 结果：特定条件下平台趋势一致；不同CCA优势随条件变化。

- 讨论与后续：作者未来工作：扩展到802.11n/ax等实网验证。

- 项目关联：后续以实际链路时序校准服务模型。

## P02. Fine-grained QoS provisioning with micropayments in wireless networks

Hideya Masaki; Kien Nguyen; Hiroo Sekiya。2023，Nonlinear Theory and Its Applications, IEICE。DOI：10.1587/nolta.14.50；[原始来源](https://doi.org/10.1587/nolta.14.50)。

- 资料状态：全文（16页；§3–5）。

- 背景：细粒度服务需要资源保障。

- 问题：按流/用户提供带宽或时延服务。

- 网络模型：客户端—AP—OVS—服务器；SDN控制器。

- 方法：SQI：SDN队列配置与IOTA交易。

- 比较方法：无保障时段、单流/多流、公链/私链。

- 实验环境：Mininet-WiFi、POX、IOTA1.5；iperf/ping。

- 指标：RTT、带宽、交易处理时长。

- 结果：给定场景达到请求服务；私链减轻交易等待。

- 讨论与后续：作者：带宽与时延同时保障及移动网络仍待扩展。

- 项目关联：项目关注混合状态/事件业务的 AoI 与公平性。

## P03. QoE Provisioning System for VoIP and Video Streaming Using Software-Defined Networking and IOTA Micropayment

Jiayang Chen; Hideya Masaki; Kien Nguyen; Hiroo Sekiya。2023，IEICE Communications Express。DOI：10.23919/comex.2023col0002；[原始来源](https://doi.org/10.23919/comex.2023col0002)。

- 资料状态：全文（4页；§2–5）。

- 背景：应用体验与传统QoS指标不同。

- 问题：流级VoIP/视频QoE保障。

- 网络模型：客户端、802.11n AP、OVS、服务器。

- 方法：QmV2：用loss/delay计算MOS并配置队列。

- 比较方法：未启用保障的相同应用。

- 实验环境：Mininet-WiFi、POX0.7、OVS2.16、DITG/VLC。

- 指标：MOS、loss/delay作为输入。

- 结果：给定loss场景中保障机制维持较高MOS。

- 讨论与后续：作者讨论视频MOS下降可能与入队速度或估计有关。

- 项目关联：不同业务分别采用新鲜度与及时交付指标。

## P04. An implementation and evaluation of MPTCP-based IoT router

Taichi Tsuru; Mikio Hasegawa; Yozo Shoji; Kien Nguyen; Hiroo Sekiya。2023，Multimedia Tools and Applications。DOI：10.1007/s11042-023-14781-8；[原始来源](https://pmc.ncbi.nlm.nih.gov/articles/PMC9983533/)。

- 资料状态：全文（PMC；§3–5）。

- 背景：网关出口需弹性与带宽。

- 问题：在低成本IoT设备上实现多路径路由器。

- 网络模型：RPi3B+/4，两Wi-Fi接口及两AP。

- 方法：MPTCP内核、source routing、常规/backup模式。

- 比较方法：单路径TCP；同硬件，CCA并不完全相同。

- 实验环境：真实静态与移动Wi-Fi，iperf3重复10次。

- 指标：吞吐、链路质量、功耗/效率。

- 结果：展示聚合与切换收益，受硬件和路径条件影响。

- 讨论与后续：作者未来工作：其他scheduler/path manager/CCA、异构无线技术、更多AP及操作模式。

- 项目关联：共享出口调度与事务能耗分别设计实验。

## P05. Implementation of P4-Based Schedulers for Multipath Communication

Hiroaki Motohashi; Phi Le Nguyen; Kien Nguyen; Hiroo Sekiya。2022，IEEE Access。DOI：10.1109/access.2022.3192539；[原始来源](https://doi.org/10.1109/access.2022.3192539)。

- 资料状态：书目核实；正文待补充。

- 背景：多路径调度需要可编程网络。

- 问题：P4中的多路径调度实现。

- 网络模型：正文待补充，具体拓扑待补充。

- 方法：标题确认P4调度实现；算法细节待补充。

- 结果：结果信息待补充全文。

- 讨论与后续：讨论与后续工作待补充全文。

- 项目关联：项目关联：P4部署非现有硬件的必要部分。

## P06. FQ-SAT: A fuzzy Q-learning-based MPQUIC scheduler for data transmission optimization

Thanh Trung Nguyen; Minh Hai Vu; Thi Ha Ly Dinh; Thanh Hung Nguyen; Phi Le Nguyen; Kien Nguyen。2024，Computer Communications。DOI：10.1016/j.comcom.2024.107924；[原始来源](https://doi.org/10.1016/j.comcom.2024.107924)。

- 资料状态：出版商摘要；正文待补充，SSRN下载403。

- 背景：异构路径随时间变化。

- 问题：优化MPQUIC传输。

- 网络模型：异构无线多路径；细节待全文。

- 方法：FQ-SAT：fuzzy逻辑调节Q-learning。

- 比较方法：摘要称state-of-the-art；具体实现待补充。

- 实验环境：摘要确认仿真与实网；参数待补充。

- 指标：下载时间、网页资源和视频及时率。

- 结果：出版摘要报告传输收益，复现实验列为后续任务。

- 讨论与后续：未取得全文，作者局限待补充。

- 项目关联：按 SSRN 2023 与出版 2024 分别记录结果版本。

## P07. MuLeS: A Multi-Client Learning-Based MPQUIC Scheduler

Thanh Trung Nguyen; Minh Hai Vu; Thi Ha Ly Dinh; Phi Le Nguyen; Kien Nguyen。2024，2024 IEEE 21st Consumer Communications &amp; Networking Conference (CCNC)。DOI：10.1109/ccnc51664.2024.10454897；[原始来源](https://dblp.org/rec/conf/ccnc/NguyenVDNN24)。

- 资料状态：出版书目；正文待补充。

- 背景：多客户端共享网络。

- 问题：MPQUIC多客户端调度。

- 网络模型：具体拓扑待补充。

- 方法：MuLeS；仅由题名确认learning-based。

- 结果：性能结果待补充全文。

- 项目关联：用于多流竞争场景与后续基线扩展。

## P08. LoGra: an LSTM-DDPG Integrated MPQUIC Scheduler for Mobile Video Streaming

Minh Hai Vu; Thanh Trung Nguyen; Thi Ha Ly Dinh; Phi Le Nguyen; Kien Nguyen。2024，2024 IEEE 100th Vehicular Technology Conference (VTC2024-Fall)。DOI：10.1109/vtc2024-fall63153.2024.10757478；[原始来源](https://doi.org/10.1109/vtc2024-fall63153.2024.10757478)。

- 资料状态：Crossref 出版元数据；正文待补充。

- 背景：移动视频业务的路径变化。

- 问题：视频MPQUIC调度。

- 网络模型：具体拓扑待补充。

- 方法：LoGra；题名为LSTM-DDPG结合。

- 项目关联：后续在传输栈环境中扩展 DRL 基线。

## P09. Evaluating MPQUIC schedulers in dynamic wireless networks with 2D and 3D mobility

Minh Hai Vu; Thanh Trung Nguyen; Thi Ha Ly Dinh; Thanh-Hung Nguyen; Phi Le Nguyen; Kien Nguyen; Hiroo Sekiya。2025，Computer Networks。DOI：10.1016/j.comnet.2025.111689；[原始来源](https://doi.org/10.1016/j.comnet.2025.111689)。

- 资料状态：Crossref+出版商摘要；正文待补充。

- 背景：二维移动模型不足以代表三维。

- 问题：比较动态移动MPQUIC调度。

- 网络模型：2D/3D移动无线网络；参数待补充。

- 方法：比较评估方法；具体调度集合待全文。

- 实验环境：实验平台待补充全文。

- 结果：摘要支持需检验移动维度，具体幅度待补充。

- 项目关联：按网络拓扑与移动模型分别评估。

## P10. Overlapping Channel Bonding Allocation for Dense WLANs under Imbalanced Traffic Demands

Hong-Nhat Hoang; Kien Nguyen; Hiroo Sekiya; Chang-Hong Lee; Dong-Hyun Kim; Jong-Deok Kim。2023，2023 IEEE 97th Vehicular Technology Conference (VTC2023-Spring)。DOI：10.1109/vtc2023-spring57618.2023.10199705；[原始来源](https://doi.org/10.1109/vtc2023-spring57618.2023.10199705)。

- 资料状态：Crossref 出版元数据；正文待补充。

- 背景：稠密WLAN需求不平衡。

- 问题：重叠信道绑定资源分配。

- 网络模型：稠密WLAN；其余待全文。

- 方法：具体算法待全文。

- 项目关联：同题名在出版书目出现另一APNOMS作者条目，本条只指VTC版本。

## 版本记录

P03 采用 DOI 10.23919/comex.2023COL0002；P04 出版年为 2023。P06 按预印本与出版版本分别记录。P10 按会议、作者列表与 DOI 区分同题条目。
