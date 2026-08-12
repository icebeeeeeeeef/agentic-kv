# Research provenance

## Research status and routing

- [JOB_MARKET_FIT.md](JOB_MARKET_FIT.md)：岗位与团队匹配调查。它是市场证据，不是当前工程范围；其中 FP8、local eviction/offload 的早期建议已不构成任务授权。
- [PROJECT_SELECTION_REVIEW.md](PROJECT_SELECTION_REVIEW.md)：候选方向对抗式选择记录。它保留“为什么收窄”的反例与岗位判断，但其中 local retention/eviction/FP8 项目设计已被当前 L3 write-admission contract 取代。
- G0_PRELAUNCH_RESEARCH_RESULTS.md：G0 固定源码调查、逐包结论与 runtime blockers

当前唯一工程机制是 D14 定义的 **Shared-L3 Publication Admission**；其 active sequence 是 S1 restore-value、sticky-reuse S2/S3、X* 替代攻击和后续 online oracle stop bound。项目选择、能力信号、证据与叙事方法必须先从
[PROJECT_EVALUATION_SOP.md](../project/PROJECT_EVALUATION_SOP.md) 读取；当前机制、Gate、claim 与已决边界再从
[PROJECT_PLAN.md](../project/PROJECT_PLAN.md)、[STATUS.md](../../STATUS.md) 和
[DECISIONS.md](../project/DECISIONS.md) 读取。研究材料不能升级 claim state、降低 SOP 标准或恢复被排除的 scope。

## Evidence ledgers

The evidence directory contains the three required signal classes and upstream prior-art review:

- signal-a-jds.md
- signal-b-interviews.md
- signal-c-team-actions.md
- upstream-prior-art-review.md

## Historical adversarial reviews

The reviews directory preserves independent attacks on market fit, technical feasibility, interview defensibility and final conclusions. Some files predate the final single-mechanism L3 write-admission scope.

Use them to recover rejected arguments, not to override docs/project/PROJECT_PLAN.md.

## Source material

The source-material directory contains earlier kv-lab reports. The private subdirectory is deliberately ignored by Git because it contains a user-provided company direction note that must not be treated as a public citation.
