# Phase 1：冻结 baseline-only calibration 并裁决 S1

Status: open
Assignee: unassigned
Labels: wayfinder:grilling
Parent: [Agentic-KV：从 fresh C1 到证据收口的 Phase 0–7 八阶段推进地图](../MAP.md)
Blocked by: [Phase 0：固化 fresh C1 与 X* 基础](01-phase-0-fresh-c1-and-xstar-foundation.md)

## Question

在 Phase 0 已获得 fresh C1 restore qualification 与可实际构造的 X* 后，如何只使用 control/baseline 结果完成 treatment-blind calibration，冻结 workload split、target coordinate、Goodput@TTFT-SLO、materiality delta、load knee、capacity、paired interval、repeat budget、arm order 与 fresh-store isolation，并用 S1 `RESTORE_VALUE_REGION` 对“restore 是否在目标区域优于 recompute且具有物质 remote value”作出 `SURVIVES / STOP / INCONCLUSIVE` 裁决？

规划必须保持 token-level prefill substitution 是必要路径证据、paired endpoint 是最终裁决；不得以 first-C0、TTFT-only、偶发 Get 或未冻结阈值替代 S1。

## Comments

<!-- 认领后再开始；答案在 resolution comment 中记录。 -->
