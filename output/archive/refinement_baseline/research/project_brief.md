# NetAdapt-IoT 项目说明

## 项目目标

构建多业务 IoT 网络资源调度平台，研究共享通信出口下的信息时效、截止期交付和设备公平性。

## 核心问题

状态更新、紧急事件和普通遥测共享同一出口时，调度策略如何随负载、链路质量和可用预算变化？不同机制分别改善哪些指标，又会增加哪些服务成本？

## 技术组成

- Python 离散时隙网络模型与可重复流量生成。
- FIFO、RR、WRR、EDF、Priority、MaxWeight、PF、AoI-gain、Debt 基线。
- Freshness–Urgency–Debt（FUD）调度与三个分量消融。
- JSON 实验配置、随机种子、逐包日志与自动统计。
- ESP32-S3/E220 双端固件与 PC 逻辑流重放工具。

## 当前成果

完成 15 个场景、20 个评估种子、13 种方法，共 3,900 次仿真；34 项软件测试通过。两种固件角色均构建通过，物理链路实验进入下一阶段。

## 相关项目

AdaptiveSense 研究源端采样，SensorTrust 研究传感器健康，EventGuard-LoRa 研究关键事件冗余。NetAdapt-IoT 固定源端产生行为，研究网络级共享服务顺序。

## 交付结构

README 提供项目入口；research 保存方法、文献与实验方案；src 保存仿真实现；output 保存实验数据；hardware 保存固件和采集工具；docs 保存架构、复现和开发记录。
