# 小容量预算桶模型

该版本采用 B=max_packet_service。默认 duty=0.8、B=1 时，slot 化服务的饱和利用率约为 0.5；异包长场景同时改变桶容量。

study 保存完整 3,900 次结果，pilot 保存开发检查，study.json 保存配置，本地 source_snapshot.zip 保存源码。

后续版本将容量统一为 B=4，饱和服务检查达到 0.8 利用率，并重新运行完整矩阵。两版本使用相同 FUD 公式、分量系数与评估种子。[预算比较](../../../docs/validation/budget_model_comparison.md)汇总利用率、AoI 和事件 miss 的变化。
