# R1 — external Store TCP 与 bounded segment

**结论：INCONCLUSIVE。** upstream 支持目标配置，但没有实际 A/B/C 进程、segment health
response 或配置文件，不能把支持路径写成部署成功。

## SOURCE_VERIFIED

- `tcp` 是支持 protocol；external Store 的 `global_segment_size` 可以非零，worker 在至少有
  一个 Store 时可为 `0`。
- `tenant_id`、backend tag 和 model name 影响 shared key-space；A/B 必须一致，
  `local_hostname` 必须按 worker 角色唯一。

## 下一步与停止条件

用一个 C Store（non-zero bounded segment）和两个独立 GPU worker（A/B 各 zero segment）
完成 TCP 真实部署，保留启动配置、A/B/C logs 和 before/after health/segment raw response。
若只能通过 RDMA/GDR/NIXL 成功，结论为 `STOP`，不扩大数据面。
