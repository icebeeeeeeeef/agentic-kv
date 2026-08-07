# Interview Defense Collection

本文件是 `agentic-kv` 的面试防守集合。它只压缩已存在的项目决策和证据，不是新的项目权威，也不允许升级 claim state。

## Claim-state vocabulary

- `ROADMAP`：只有计划或设计，尚未实现。
- `SOURCE_VERIFIED`：在明确固定版本的一手源码中核对过的事实。
- `IMPLEMENTED_UNVALIDATED`：代码存在，但要求的运行时或实验 Gate 尚未通过。
- `EXPERIMENTALLY_VALIDATED`：在明确 manifest、commit、raw log 和统计方法下可复现。

回答时必须明确主语：哪些是 upstream SGLang/Mooncake 提供，哪些是本项目集成、实现、测量或验证。没有 artifact 支撑的内容不得使用完成时。

## Current defense boundary

当前唯一可以确认的个人产出是仓库组织、规划材料和 G0 源码审计；L3 admission hook、instrumentation、workload generator、conditional ledger、在线策略和性能收益仍未完成。固定 SGLang source 上的接缝，以及 Mooncake `v0.3.12.post1` 的 release metadata 属于 `SOURCE_VERIFIED`；该候选与 pinned SGLang adapter 的 build/runtime compatibility、exact build hash 和跨 worker runtime path 仍未解决，因此当前 verdict 仍是 `G0-SOURCE BLOCKED`。

权威细节见：

- [PROJECT_PLAN.md](PROJECT_PLAN.md)
- [STATUS.md](../../STATUS.md)
- [implementation evidence](../implementation/)

## Question template

新增问题时使用以下最小结构：

### Q: 追问问题

**Claim state：** `ROADMAP | SOURCE_VERIFIED | IMPLEMENTED_UNVALIDATED | EXPERIMENTALLY_VALIDATED`

**短回答：** 先给结论，明确 ownership 和边界。

**证据：** 固定 commit、测试、run manifest、raw log 或统计产物的路径。

**反例与 trade-off：** 什么时候失效，最强简单基线是什么，失败时如何按 Gate/STOP 收口。

**不能声称：** 当前证据尚不支持的扩大表述。
