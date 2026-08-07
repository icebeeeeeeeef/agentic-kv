# R6 — prefix closure、fail-open 与异步终态

**结论：INCONCLUSIVE。** seam 位置、first-miss、ack cleanup 与 detach cleanup 已核对；policy
不存在，因而 prefix hole、fail-open、ALWAYS_DROP 与 async-drain 都不能通过。

## SOURCE_VERIFIED 与 inference 边界

L2 DMA ack 后先记录 CPU store event，才调用 `write_backup_storage`；在它创建
`StorageOperation` 之前返回可从源码上避开 L3 queue/ongoing backup/protection。remote lookup
在 first missing physical component 停止。由此推出的 prefix closure、exception fail-open 和
ALWAYS_DROP 行为是**待实现的 patch contract**，不是 upstream 已实现功能。

## 后续 test 条件

只接受 root/anchor + ordered hashes 的显式 decision group；首个 DROP 以后 suffix 强制 DROP。
同时验证故意 hole、一次 policy exception 的 upstream Put terminal、DROP 的零 L3 state，及
success/dedup/failure/shutdown 后 queue/ack/ongoing/protection 回 baseline。不能观察 terminal
就保持 `INCONCLUSIVE`；只有 process exit 看到清理则为 `STOP` runtime policy experiments。
