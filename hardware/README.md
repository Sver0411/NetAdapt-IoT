# ESP32-S3 + E220 单链路实验

## 平台与进度

平台由两套 ESP32-S3 N16R8 和 E220-400T22S 组成，分别承担发送端 A 与接收端 B。PC 调度多条逻辑业务流，A 发送数据，B 校验并回复 ACK。

发送端与接收端固件均通过 PlatformIO 构建；PC 协议完成模拟串口测试。下一阶段是接线、参数读取、链路校准和物理负载重放。

## 接线

固件目标为 ESP32-S3 DevKitC-1 兼容板，16MB Flash / 8MB OPI PSRAM。按板上 GPIO 标签和模块信号名称连接：

| ESP32 GPIO | E220 信号 | 功能 |
|---|---|---|
| 18 (TX) | RXD | UART 发送 |
| 17 (RX) | TXD | UART 接收 |
| 4 | M0 | 模式选择 |
| 5 | M1 | 模式选择 |
| 6 | AUX | 模块就绪 |
| GND | GND | 公共参考地 |
| 稳压电源 | VCC | 按型号供电规格连接 |

信号电平为 3.3V。ESP32 通过 USB 连接 PC，UART 连接 E220。两端使用相同的地址、信道、空中速率和透明传输设置；固件 UART 配置为 9600 8N1。

参数资料：[制造商资料入口](https://www.ebyte.com/datadown/LoRa.html)与[型号手册](https://www.ebyte.com/Uploadfiles/Files/2021-6-29/2021629114373486.pdf)。连接天线后进行发射实验，记录使用的无线配置。

## 构建与刷写

    .venv/bin/pio run -d hardware/firmware
    .venv/bin/python hardware/run.py ports
    .venv/bin/pio run -d hardware/firmware -e sender -t upload --upload-port /dev/cu.YOUR_SENDER
    .venv/bin/pio run -d hardware/firmware -e receiver -t upload --upload-port /dev/cu.YOUR_RECEIVER
    .venv/bin/python hardware/run.py probe --port /dev/cu.YOUR_SENDER

用枚举出的设备路径替换示例端口。发送板使用 sender，接收板使用 receiver。GPIO 定义位于 hardware/firmware/src/main.cpp。

## 负载重放

    .venv/bin/python hardware/run.py run --port /dev/cu.YOUR_SENDER --config configs/hardware.json --policy fud --seed 100 --out output/hardware/fud-100

分别选择 fifo、rr、edf、aoi_gain、fud_no_debt 等方法，轮换执行顺序，每种至少重复十次。seed 固定 PC 产生的负载；链路条件通过距离、位置、供电、寄存器快照与接收日志记录。

## 协议

数据帧为 NA1,seq,flow,generation_ms,payload_hex,CRC16，ACK 为 AK1,seq,flow,generation_ms,CRC16，以换行分隔。

CRC-16/CCITT-FALSE 使用初值 FFFF、poly 1021；标准向量 123456789 对应 29B1。当前配置采用 64B payload，ASCII 帧长度上限为 200B。

PC 发送 SEND 命令，固件返回 TX 与 ACK。主机按 seq、flow 和生成时间戳匹配反馈。ACK 超时记为 unconfirmed，接收端 RX 日志用于核对实际收到的包。PARAMS 命令读取无线参数，每个数据命令对应一次发送事务。

## 记录指标

host_rtt_s 记录 USB、UART、无线数据和 ACK 的事务往返时间。确认数、未确认数、原始串口行与逐包记录保存到输出目录。

硬件预算按配置服务成本与事务墙钟耗时的较大值扣除。硬件示例采用 1s slot；完成时序校准后生成新的服务率配置。

后续增加独立发送节点及接入协议，开展多节点竞争实验；加入电流采集设备后记录实际事务能耗。
