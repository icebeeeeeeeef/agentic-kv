# R4 — SGLang runtime 配置、冷态与 cross-worker attribution

> Historical prelaunch finding. It records no runtime artifact of its own. The later first-C0 r6 artifact scoped-validates A Put→cold B Get and token survival; current state is [STATUS.md](../../../../STATUS.md).

**历史结论：INCONCLUSIVE。** source 提供了 first-miss query、storage-loaded-token 的记账与响应暴露路径；
没有 A Put → cold B Get 的真实链和 B-cold no-L3 token control，不能声称 shared-L3 restore 或 prefill
survival。

## 已知边界

`_storage_hit_query` 逐 batch 查询，任何未完整命中立即 break；prefetch 完成后
`loaded_from_storage` 是 completed minus already matched host prefix。scheduler 将它写入 request 的
`storage_hit_length`，随后形成 `cached_tokens_details.storage`；finished-request metrics 将实际未缓存输入记为
`uncached_prompt_tokens = prompt_tokens - cached_tokens`。这些是 stock runtime 可用的 token-level oracle，
但不会自行证明 B local-cold、remote Get、output equality 或对照公平。

## 可接受的 PASS artifact

同一 `run_id` 可 join：A completed Put、B fresh/cold proof、B per-object Get terminal、
B storage-loaded pages、同 token/hash request 与固定 decode output hash，形成 `RESTORE_PATH_PASS`；另保留
相同请求的独立 B-cold no-L3 control，并证明 L3 arm 的 `cached_tokens_details.storage > 0` 且
uncached/prefill tokens 更少，形成 `REMOTE_VALUE_SURVIVES`。没有 successful remote Get 时，输出正确只能
标为 `recompute`、`local hit` 或 `unobservable`；Get 成功但没有减少 prefill 也不能解锁后续实现。
