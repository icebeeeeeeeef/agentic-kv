# R4 — SGLang runtime 配置、冷态与 cross-worker attribution

**结论：INCONCLUSIVE。** source 提供了 first-miss query、storage-loaded-token 的记账位置；
没有 A Put → cold B Get 的真实链，不能声称 shared-L3 restore。

## 已知边界

`_storage_hit_query` 逐 batch 查询，任何未完整命中立即 break；prefetch 完成后
`loaded_from_storage` 是 completed minus already matched host prefix。它们可成为 B restore
trace 的字段，但不会自行证明 B local-cold、remote Get 或 output equality。

## 可接受的 PASS artifact

同一 `run_id` 可 join：A completed Put、B fresh/cold proof、B per-object Get terminal、
B storage-loaded pages、同 token/hash request 与固定 decode output hash。没有 successful
remote Get 时，输出正确只能标为 `recompute`、`local hit` 或 `unobservable`，不是 restore。
