# Phase 2：执行 S2/S3 三态机会筛查

Status: open
Assignee: unassigned
Labels: wayfinder:grilling
Parent: [Agentic-KV：从 fresh C1 到证据收口的 Phase 0–7 八阶段推进地图](../MAP.md)
Blocked by: [Phase 1：冻结 baseline-only calibration 并裁决 S1](02-phase-1-baseline-freeze-and-s1.md)

## Question

在 S1 存活且所有统计与 workload 字段已冻结后，如何最小化地规划 sticky-reuse workload、publication-mass witness、pressure/fairness witnesses 和 fresh-store paired runs，使 S2 `PUBLICATION_COST_ENVELOPE` 与 S3 `CAPACITY_EXTERNALITY` 能分别得到 `SIGNAL / VALID_FALSE / INCONCLUSIVE`，并严格执行双 valid-false、remote Get≈0、sticky mass 不足或 X* 消除机会时的 pre-implementation STOP？

规划必须明确：此阶段只能观察 stock publication activity 与 queue/resource/TTFT、roomy/small capacity 与 query-time availability 的关系；没有 behavior hook 和受控 treatment 时，不能声称 `decision → physical Put → resource → endpoint` 因果链已经闭合。

## Comments

<!-- 认领后再开始；答案在 resolution comment 中记录。 -->
