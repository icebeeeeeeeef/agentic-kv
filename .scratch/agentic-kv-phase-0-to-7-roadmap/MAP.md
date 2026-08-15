# Agentic-KV：从 fresh C1 到证据收口的 Phase 0–7 八阶段推进地图

Status: open
Assignee: unassigned
Labels: wayfinder:map

## Destination

形成一条 owner 可逐阶段裁决的项目推进路线：从当前 first-C0 证据出发，在不预设正结果的前提下，把每个阶段规划到可执行、可停止、可诚实收口，并最终到达 pre-implementation STOP、runtime negative、payload-only、static-sufficient 或 held-out policy result 中与证据相符的终局。

本地图完成的含义是 Phase 0–7 八个阶段的决策路线都已清楚、每个仍需展开的阶段都有独立规划地图或被证明无需子地图；它不表示这些阶段已经执行或通过。

## Notes

- 权威顺序固定为 `PROJECT_EVALUATION_SOP.md → PROJECT_PLAN.md → STATUS.md → TASKS.md → implementation evidence → INTERVIEW_QA.md`。本地图只做导航和规划索引，不能修改 Gate、STOP、claim state 或实际完成状态。
- 顶层使用 Wayfinder 的 planning mode。每个阶段 ticket 只回答“该阶段怎样规划到 execution-ready”；实际执行仍须由 canonical contract 和用户明确授权的 `TASKS.md` 承载。
- 阶段 ticket 到达 frontier 后，先判断是否仍有超过一次会话的 fog：有则为该阶段 chart 独立 Wayfinder map；没有则直接产出最小执行 handoff，不为了目录完整性强建子地图。
- 阶段规划 ticket 的关闭不能机械解锁下一阶段：若创建了子地图，关闭前必须把 successor 的 `Blocked by` 从当前规划 ticket 重连到子地图中最终记录 `PASS / STOP / INCONCLUSIVE / owner ruling` 的 terminal ticket；若无需子地图，则创建或链接一个最小 terminal ruling task 后再重连。只有 canonical entry condition 与该 terminal ruling 同时满足，successor 才属于 frontier。
- 当前事实锚点：first-C0 r6 只完成 scoped restore qualification；fresh C1、S1–S3、D1、trace、behavior hook、candidate 和性能收益均未完成。
- Phase 0–7 低分辨率路线：`Phase 0 fresh C1 + X* foundation → Phase 1 baseline-only freeze + S1 → Phase 2 S2/S3 survival screen → Phase 3 trace-only path attribution → Phase 4 fail-open hook + forced actions → Phase 5 causal closure + candidate ruling → Phase 6 minimal candidate + held-out A/B → Phase 7 failure/tradeoff/evidence closeout`。
- 这不是无条件线性流水线：Phase 1 的 S1 是 hard veto；Phase 2 的双 valid-false、remote Get≈0、sticky-reuse mass 不足或 X* 消除机会会 STOP；`INCONCLUSIVE` 留在当前阶段修复前提或精度，不能解锁后续阶段。
- Phase 3 只能做 path attribution 与 hypothesis narrowing，不能在受控 treatment 前宣称 RCA 完成。Phase 4 的 forced arms 先证明 actuator/correctness/manipulation；容量链的选择性因果闭合仍属于 Phase 5。
- Phase 5 只有在 own-arm runtime mediator、paired `Goodput@TTFT-SLO`、STATIC_FREQ* residual 与 O1-vs-X* 均未停止方向后，才允许新的 owner decision 定义最小 candidate；conditional ledger 也不能提前实现。
- 若某阶段产生 STOP，关闭或撤销所有因此越过 Destination 的下游 ticket，并把终局写入 Out of scope；不能让“blocker ticket 被关闭”机械地把下游阶段变成可执行 frontier。

## Decisions so far

<!-- 尚无已关闭阶段规划 ticket。决定只在对应 ticket 中保留详情；本节以后只追加一行 gist 和链接。 -->

## Not yet specified

- Phase 0 runtime 后才能确定的 X* 实际 component 集合，以及由 source/runtime evidence 排除的 stock controls。
- Phase 1 calibration 后才能冻结的 target coordinates、SLO、materiality delta、interval method、repeat budget、load knee 与 capacity values。
- Phase 2 outcome 后才能精确拆分的 D1 observation、opaque correlation 和 non-interference 子问题。
- Phase 4 forced-action 结果后才能确定的链 A / 链 B residual、最强选择性静态对照和 Phase 5 子地图结构。
- Phase 5 owner ruling 前不可命名的 candidate signals、公式、参数和实现切片。
- 最终正结果、payload-only、static-sufficient、shared-L3-no-value 或 no-adjudication-power 终局分别需要哪些最小 Phase 7 evidence；只能由实际前序 outcome 决定。

## Out of scope

- 把项目改造成通用性能优化平台、自动 RCA 系统或 benchmark 平台。
- L1/L2 eviction、remote eviction、router、affinity、load balancing、SSD L4、第二 cache backend 或 vLLM 平行实现。
- RDMA/GDR/NIXL、KV 量化/稀疏化、kernel、metadata HA、PD disaggregation、Kubernetes/GPUStack。
- 通用 policy DSL、动态 RPC policy service、为未来 candidate 预建的插件框架。
- 用 offline replay、conditional ledger、单 arm correlation、CPU/NIC 计数器或 modeled occupancy 代替在线 treatment 的因果裁决。
- 在 runtime evidence 前把 ROADMAP、DECIDED、SOURCE_TO_REVERIFY 或 first-C0 qualification 包装成工程完成或性能收益。
