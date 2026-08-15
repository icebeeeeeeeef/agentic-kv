# Phase 4：验证 fail-open hook 与 forced actions

Status: open
Assignee: unassigned
Labels: wayfinder:grilling
Parent: [Agentic-KV：从 fresh C1 到证据收口的 Phase 0–7 八阶段推进地图](../MAP.md)
Blocked by: [Phase 3：建立 trace-only 路径归因](04-phase-3-trace-only-path-attribution.md)

## Question

在 trace-only non-interference 通过后，如何规划最小 behavior-changing seam，使 `ALWAYS_ADMIT`、`ALWAYS_DROP` 与 `POLICY_ERROR_FAIL_OPEN` 在 L2 ack 后、`StorageOperation` 前生效，并以独立于 trace non-interference 的 equivalence/correctness oracle 验证 L2 不变量、prefix all-or-none closure、无 L3 async state 的 DROP、dedup/race、fail-open、shutdown/detach 与 terminal cleanup？

forced-action 实验应证明哪些 manipulation：`decision → operation/Put` 的控制能力、链 A 的必要中介，以及为什么 `ALWAYS_DROP` 不能单独证明链 B 的选择性 composition 收益？真实 failure injector 不可得时如何保留 `INCONCLUSIVE` 而不伪造完整 G0？

## Comments

<!-- 认领后再开始；答案在 resolution comment 中记录。 -->
