# Interview Defense Collection

本文件是 `agentic-kv` 的面试防守集合。它只压缩已存在的项目决策和证据，不是新的项目权威，也不允许升级 claim state。

## Claim-state vocabulary

- `ROADMAP`：只有计划或设计，尚未实现。
- `SOURCE_VERIFIED`：在明确固定版本的一手源码中核对过的事实。
- `IMPLEMENTED_UNVALIDATED`：代码存在，但要求的运行时或实验 Gate 尚未通过。
- `EXPERIMENTALLY_VALIDATED`：在明确 manifest、commit、raw log 和统计方法下可复现。

`gate_outcome`（`PASS` / `FAIL` / `INCONCLUSIVE` / `STOP`）与上述 claim state 正交；一次 scenario 的
PASS 只能支持它实际覆盖的主张，不能自动升级完整 G0 或性能 claim。

回答时必须明确主语：哪些是 upstream SGLang/Mooncake 提供，哪些是本项目集成、实现、测量或验证。没有 artifact 支撑的内容不得使用完成时。

## Current defense boundary

当前唯一可以确认的个人产出是仓库组织、规划材料和 G0 源码审计；L3 admission hook、instrumentation、workload generator、conditional ledger、在线策略和性能收益仍未完成。固定 SGLang source 上的接缝，以及 Mooncake `v0.3.12.post1` 的 release metadata 属于 `SOURCE_VERIFIED`；该候选与 pinned SGLang adapter 的 build/runtime compatibility、exact build hash 和跨 worker runtime path 仍未解决，因此当前 verdict 仍是 `G0-SOURCE BLOCKED`。

权威细节见：

- [PROJECT_PLAN.md](PROJECT_PLAN.md)
- [STATUS.md](../../STATUS.md)
- [implementation evidence](../implementation/)
- [durable decisions](DECISIONS.md)

## Required current questions

### Q: 这会不会只是一个 `decide()` 函数加参数扫描？

**Claim state：** `SOURCE_VERIFIED + ROADMAP`

**短回答：** 不把策略收益作为工程完成前提。最低交付是独立的 trace-only correlation、pre-collapse
payload observation、L2 ack 后的 fail-open seam、prefix closure 与 async terminal oracle；它们都在真实
SGLang→Mooncake 生命周期上，并要求 focused test、patch provenance 和 run artifact。当前这些 owned
patch 尚未实现，因此不能说已经拥有 runtime 工程成果。

**证据：** [runtime backbone contract](PROJECT_PLAN.md#32-三层完成定义)、
[minimum ownership/deletion oracle](PROJECT_PLAN.md#34-工程最低交付与反向删除测试)。

**反例与 trade-off：** 如果删除 benchmark 后只剩阈值函数，R 层即失败；解决办法不是增加 policy
framework，而是完成已有生命周期与观测合同。

**不能声称：** “已经实现了分层 KV cache / Mooncake transfer”或“策略已带来收益”。

### Q: 为什么 trace-only 必须先于 admission hook？

**Claim state：** `SOURCE_VERIFIED + ROADMAP`

**短回答：** source 只证明 seam 的位置，不能证明异步 operation、batch、physical object terminal 的运行时
关联。先加 behavior hook 会混淆观测回归与机制回归；所以先在不计算/应用 action 的条件下，用 opaque
`observation_id` 证明 trace-disabled/trace-enabled 行为等价，之后才允许写 `ALWAYS_*` hook。

**证据：** [trace-first order](PROJECT_PLAN.md#212-唯一正确的下一动作顺序)、
[trace-only acceptance](../implementation/G0_EXECUTION_PLAN.md#task-2-add-trace-only-correlation-and-prove-it-is-inert)。

**反例与 trade-off：** trace 改变 key、队列、Put/Get result、输出或 cleanup 时，必须 STOP/revert trace
patch；不能用 policy 绕过不可信 telemetry。

**不能声称：** 目前没有 trace-disabled/enabled artifact，不能说关联链已经正确或无开销。

### Q: 你如何证明“减少写入”不是 dedup 或 two-writer race？

**Claim state：** `SOURCE_VERIFIED + ROADMAP`

**短回答：** adapter 的 `put_result=0` 会把真正新 Put 与 `OBJECT_ALREADY_EXISTS` race 合并为 success，
不能作为新物理写入。D1 因此只授权在 Mooncake 归约前增加严格 trace-only observation；只有它的
non-interference artifact 通过后，`new_physical_put_bytes` 才能用作 payload 分子。

**证据：** [D1](DECISIONS.md#d1--保留-new-put-payload-指标并授权最小观察-patch)、
[race limitation](../implementation/G0_SOURCE_RUNTIME_AUDIT.md#race-observation-limitation)。

**反例与 trade-off：** 观测不到原始原因码或观测改变行为时，payload 分支 STOP，不用模糊的
`completed_put_bytes` 替代。

**不能声称：** 目前尚无 observation patch/test，不能给出 new-Put 字节或 payload-efficiency 数字。

### Q: 为什么 prefix group 必须 all-or-none，而不做更细的按页规则？

**Claim state：** `SOURCE_VERIFIED + ROADMAP`

**短回答：** remote lookup 在第一个缺失 page 停止。若 ancestor DROP 而 descendant ADMIT，后者不可达。
G0 选择 root/known-resident anchor 加有序 logical pages 的完整 group 一次性 ADMIT 或 DROP；这用最少状态
满足可达性，不引入 remote metadata、read-path repair 或逐页策略。

**证据：** [D9](DECISIONS.md#d9--g0-的-prefix-group-一律-all-or-none)、
[prefix closure contract](PROJECT_PLAN.md#54-前缀闭包不变量)。

**反例与 trade-off：** callback 不能证明完整可达 group 时必须整体 DROP，可能牺牲更细粒度收益；不能以
“整个 suffix 一起写”猜测闭包。

**不能声称：** 规则尚无 runtime artifact，不能说任何真实 workload 已验证 closure。

### Q: 取消、failure 或 late completion 怎么处理？

**Claim state：** `SOURCE_VERIFIED + ROADMAP`

**短回答：** DROP 在 `StorageOperation` 之前返回，不新增 async owner；admitted path 继续使用 upstream
ack/detach cleanup。项目必须验证 success、dedup、race、fail-open、shutdown/detach 的终态；真实 failure
injector 不可得时只能是 `INCONCLUSIVE`，不能靠 mock 或进程退出声称 G0 validated。

**证据：** [D10](DECISIONS.md#d10--failureasync-合同保持严格不伪造覆盖)、
[async source facts](../implementation/G0_SOURCE_RUNTIME_AUDIT.md#async-cleanup-facts)。

**反例与 trade-off：** 若 detach 后观察到 residual protection、late ack 或 leak，这是 G0 FAIL/STOP，
不是新增 cancellation registry/epoch state machine 的理由。

**不能声称：** 当前未运行 G0 matrix，不能声称这些终态已经全部通过。

## Question template

新增问题时使用以下最小结构：

### Q: 追问问题

**Claim state：** `ROADMAP | SOURCE_VERIFIED | IMPLEMENTED_UNVALIDATED | EXPERIMENTALLY_VALIDATED`

**Gate outcome（如存在 run artifact）：** `PASS | FAIL | INCONCLUSIVE | STOP`；没有 artifact 时明确写“无”。

**短回答：** 先给结论，明确 ownership 和边界。

**证据：** 固定 commit、测试、run manifest、raw log 或统计产物的路径。

**反例与 trade-off：** 什么时候失效，最强简单基线是什么，失败时如何按 Gate/STOP 收口。

**不能声称：** 当前证据尚不支持的扩大表述。
