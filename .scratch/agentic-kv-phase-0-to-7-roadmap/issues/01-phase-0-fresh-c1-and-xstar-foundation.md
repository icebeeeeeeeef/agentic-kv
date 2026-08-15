# Phase 0：固化 fresh C1 与 X* 基础

Status: open
Assignee: unassigned
Labels: wayfinder:grilling
Parent: [Agentic-KV：从 fresh C1 到证据收口的 Phase 0–7 八阶段推进地图](../MAP.md)
Blocked by: none

## Question

在不复用 first-C0 r6 的 Store、worker state、coldness、ledger 或 predicate artifact，也不预建 OCI、通用 runner、自动 classifier/finalizer 或依赖平台的前提下，Phase 0 的最小 execution-ready 规划是什么：如何把已观察 blocker 写入新的 C1 runbook/admission，完成 fresh C1 C0，并在 C1 双 predicate `PASS` 后对 X* 的 `write_through_selective` semantics、quota/adapter wiring、metrics/prefetch threshold 和相关 upstream 变化做有限 source/runtime audit？

本 ticket 还必须决定 Phase 0 是否真的需要独立 Wayfinder 子地图；若现有 canonical contract 已足够清楚，则应直接给出最小执行 handoff，而不是为规划而规划。无论哪种情况，关闭本 ticket 前都必须建立或链接 Phase 0 的 terminal ruling task，并把 Phase 1 的 blocker 重连到该 terminal，而不是把“规划完成”当作 Phase 0 runtime 通过。

## Comments

<!-- 认领后再开始；答案在 resolution comment 中记录。 -->
