# G0 讨论留档与未决实现问题

> 状态：**HISTORICAL DISCUSSION / NON-AUTHORITY**（不是实现计划、源码事实或 runtime 证据）
> 当前总裁决与下一动作：以 [STATUS.md](../../STATUS.md) 为准。
> 路由：已由 owner 确认、会约束实现或 claim 的决议写入
> [DECISIONS.md](../project/DECISIONS.md)；本文件只保留其讨论缘由，以及尚须由 source/runtime artifact 回答的实现问题。

不要在本文重新选择 D1/D9/D10/D12/D14/D15/D16/D17/D18，也不要在此追加新的“决议”。项目宪法仍是
[PROJECT_PLAN.md](../project/PROJECT_PLAN.md)，实际完成状态仍是
[STATUS.md](../../STATUS.md)。本文不能单独升级 claim state、改变 Gate/STOP 或授权实现。

## 已经固定，不重新选择

| 项目 | 结论 | 依据 / 含义 |
|---|---|---|
| 唯一行为变化 | L2 DMA ack 后、`write_storage` 前的 L3 `ADMIT_TO_L3` / `DROP` | 已在 pinned SGLang `b058dc…` 源码核对；不修改 L1/L2、读路径、eviction 或路由。 |
| 首轮 substrate | external pinned SGLang checkout + external pinned Mooncake checkout，小型独立 patch series | 不 vendor、不建 submodule、不建 policy framework。 |
| Mooncake 首轮候选身份 | `v0.3.12.post1` / `6041a609a8c3af35e778f70db344f145c2914980` | 这是待验证组合，而不是“已兼容版本”。 |
| 首轮拓扑边界 | 2 个独立 worker lifecycle（A/B）+ 1 个 TCP external Store（C） | 仅 C 有非零、有界 storage segment；A/B 为零 segment。首次 C0 可在 A 退出后顺序复用同一物理 GPU，只支持 cross-process claim。 |
| G0 不做的工作 | `VALUE_DENSITY`、L1/L2 或 L3 eviction、router、RDMA/GDR/NIXL、第二 backend、模拟器 | 这些不是解决当前 blocker 的简单办法。 |
| hook 的失败语义 | policy 异常必须 fail-open 回到 upstream write path | 这是 G0 正确性合同，不是可选“高可用功能”。 |

## 已决项路由（不重新讨论）

| 原讨论号 | 当前状态 | 唯一决议入口 |
|---|---|---|
| D1 / D2 | 已决：保留 `new_physical_put_bytes`，固定严格 trace-only pre-collapse observation 边界；实际施工受 D14 active S1–S3 ruling 或 D12 窄例外约束 | [D1](../project/DECISIONS.md#d1--保留-new-put-payload-指标并授权最小观察-patch) |
| D9 | 已决：complete prefix group all-or-none | [D9](../project/DECISIONS.md#d9--g0-的-prefix-group-一律-all-or-none) |
| D10 | 已决：failure/async 合同严格，failure injector 不可得为 `INCONCLUSIVE` | [D10](../project/DECISIONS.md#d10--failureasync-合同保持严格不伪造覆盖) |
| D12 / D14 | 已决：D12 保留有效-null与两级 payload 例外纪律；D14 以 S1–S3、X* 与 online oracle 收敛 active contract | [D14](../project/DECISIONS.md#d14--shared-l3-publication-admission-收敛与替代攻击) |
| D15 | 已决：C0 request/coldness/token oracle 与 C1 finite-X*/S1–S3 preregistration materialization；不构成 runtime result | [D15](../project/DECISIONS.md#d15--c0c1-实验合同物化) |
| D16 | 已决：大陆 TCP cohort 的 release staging、GPU/network preflight、archive finalizer、interruption/quarantine、retention；不构成 runtime result | [D16](../project/DECISIONS.md#d16--短生命周期-cohort-的租机前执行与证据合同) |
| D17 / D18 | D18 取代 D17 的首次 C0 前置范围：内容寻址输入 + one-shot runbook/raw handoff；host runtime facts 租机后检查；formal lifecycle 仅按真实 blocker 后置 | [D18](../project/DECISIONS.md#d18--首次-c0-的-correctness-only-入口与-evidence-driven-hardening) |

## 历史依赖图（仅解释先后，不授权实现）

```text
D1/D2 payload/race 观测合同（已决）
 └─ Mooncake trace-only patch + non-interference artifact → D8/D10

D3 目标 Linux/GPU 组合 → D4 stock A→B restore → D5 拓扑与隔离
                                                     ↓
                                      D6 trace context → D7 non-interference
                                                     ↓
                                      D8 binary hook → D9 prefix closure
                                                     ↓
                                      D10 cleanup/failure → D11 G0 exit ruling
```

当前执行顺序已由 [G0 execution plan](G0_EXECUTION_PLAN.md) 固定：首次 C0 → fresh C1 重做 C0 → finite X* audit
→ baseline-only freeze + S1 restore-value → sticky-reuse S2/S3 → 条件性 D1 observation → SGLang trace-only → behavior hook。
`D6`–`D10` 只有 active survival ruling 通过后才能实施；S1 STOP 或 S2/S3 都为有效 null 时
按 D14 在实现前 STOP，不满足 R/F，也不得为了展示工程量自动开发 D1。D12 的第一次 payload/resource 例外只允许
observation-only D1/opaque correlation；它不能直接授权 D8 behavior hook。

## 尚待 artifact 回答的实现问题

下列条目不是新的 owner 决策；它们的 Pass/Fail/Inconclusive 必须由对应 G0 artifact 回答。实现边界、
测试与 STOP 以 [G0 execution plan](G0_EXECUTION_PLAN.md) 和 source audit 为准。

### D3 — G0 的目标 Linux GPU 组合和不可替代的版本身份是什么？

**问题：**哪台/哪些机器构成唯一允许的第一轮 runtime 环境，wheel 不可用时是否启动单独的
source-build compatibility 调查？

**推荐：**第一轮只接受 Linux x86_64、CPython 3.11、官方
`mooncake-transfer-engine==0.3.12.post1` wheel（已记录 SHA-256）和固定 SGLang SHA。保存 GPU、
CUDA、driver、glibc、wheel hash、`git status --porcelain` 和启动命令。若该 wheel 不可用，标记
C0 `BLOCKED_BEFORE_C0`，再由该真实 blocker 决定是否另开 source-build compatibility 子调查；不得把 source build
静默称为同一输入。

**通过后解锁：**D4。
**停止条件：**API shape 通过但 adapter 初始化或 A Put 前 admission 失败，仍是 `BLOCKED_BEFORE_C0`；不得写成
C0 `FAIL/STOP`，也不得打 hook。

### D4 — stock A Put → fresh B Get 的最小因果证明如何定义？

**问题：**什么证据足以排除 B 的本地命中、静默重算，以及“成功 Get 但没有替代 prefill”的假通过？

**推荐：**A 完成 Put 后再启动一个从未处理该 prefix 的 B；B 的 L1/L2 配置不变、local segment 为
零。先以 A Put terminal、B 启动/冷态证据、B successful remote Get、B storage-loaded pages 和固定
decode output hash 证明 `RESTORE_PATH_PASS`；再用相同请求的独立 B-cold no-L3 control，证明
`cached_tokens_details.storage > 0` 且 L3 arm 的 uncached/prefill tokens 更少，得到
`REMOTE_VALUE_SURVIVES`。两者都成立才解锁后续；输出正确但没有 remote Get、或 Get 成功但未减少
prefill，均不得当作 PASS。TTFT 在此只作诊断。

**通过后解锁：**D5–D10。
**停止条件：**用减小 L1/L2 容量、复制对象或 worker affinity 来制造“冷态”。

### D5 — external Store 的 key-space 和 scenario 隔离合同如何固定？

**问题：**哪些字段必须 A/B 相同或不同，如何保证一次 run 不读取上一次残留对象？

**推荐：**A/B 固定相同 model/tokenizer revision、served model name、tenant、backend tag、page
size、master/metadata；仅 `local_hostname` 按 worker 唯一。每个 scenario 使用 fresh C Store 或
可证实的 fresh epoch；不能把 `MooncakeStore.clear()` 当作隔离证明。run 前后保存 C 的 health、
segment、epoch/对象状态证据。

**通过后解锁：**可比较的 `ALWAYS_ADMIT`、`ALWAYS_DROP` 与 restore case。
**停止条件：**容量、key-space 或冷态无法证明时，不跑比较型场景。

### D6 — trace context 的最小数据模型和所有权是什么？

**问题：**如何实现 `observation_id → StorageOperation → batch/attempt → adapter result`，又不引入
第二套异步生命周期？

**当前合同：**向 `StorageOperation` 显式传递一个小型不可变 `TraceContext`（`run_id`、
`observation_id`、`operation_id`）；controller 以每 operation 的 batch ordinal 派生 `attempt_id`。只有
后续 behavior patch 才可在同一 record 追加 `decision_id`。
不要用全局 side map：它会复制 operation 生命周期、引入清理泄漏和时间关联猜测。ID 仅用于日志 join，
不进入 key construction、policy 输入、queue ordering、retry、dedup 或 read path。

**依赖：**D4、D5。
**通过后解锁：**D7、D8–D10。
**停止条件：**只能依据 wall-clock、key 字符串或跨进程日志猜测关联。

### D7 — trace-only 不干扰性的比较 oracle 是什么？

**问题：**怎样证明“有 trace”不是改变行为的另一个 treatment？

**推荐：**同一 isolated microcase 下，比较 stock、trace-disabled、trace-enabled（并改变 opaque
ID 字面值）三个 run 的：logical key/hash 顺序、submitted operation 顺序、Put/Get terminal、
output hash、queue/ack/ongoing/protection drain state。性能时延不是此处的 oracle；有任一行为差异即
trace patch `FAIL` 并回退。

**依赖：**D6。
**通过后解锁：**D8。

### D8 — G0 行为 hook 的 API 与 fail-open 范围是什么？

**问题：**怎样保持它是单一二元准入门，而不是提前形成 policy framework？

**推荐：**在已构造完整 group 输入、尚未调用 `write_storage` 的 seam 同步调用一个窄接口：
`decide(group) -> ADMIT_TO_L3 | DROP`。G0 只实现 `ALWAYS_ADMIT`、`ALWAYS_DROP` 和
`POLICY_ERROR_FAIL_OPEN`；不提供动态加载、RPC、策略注册表或未来信号。异常捕获后执行原 upstream
write path 并记录 reason code。

**依赖：**D7。
**通过后解锁：**D9、D10。
**停止条件：**hook 在 L2 ack 前、`StorageOperation` 创建后，或任何 trace 字段参与决策。

### D9 — prefix-closure group 的 runtime oracle

此项已由 [D9](../project/DECISIONS.md#d9--g0-的-prefix-group-一律-all-or-none) 决定为 complete
group all-or-none。剩余问题只是在 runtime artifact 中证明 anchor/order 可观测、partial input 被拒绝，
而不是重新选择 suffix 规则或增加 remote metadata/read path。

### D10 — failure/async 的 runtime oracle

此项已由 [D10](../project/DECISIONS.md#d10--failureasync-合同保持严格不伪造覆盖) 决定。剩余问题只是在
G0 matrix 中取得 success/dedup/race/fail-open/shutdown-detach terminal artifact，并如实把不可注入的
failure 标为 `INCONCLUSIVE`；不得在此重新讨论 mock、process-exit 或新 cancellation owner。

### D11 — G0 的最终通过声明究竟要求哪些 retained artifacts？

**问题：**什么是功能 smoke，什么才允许写 `G0-RUNTIME VALIDATED`？

**推荐：**保留原严格定义：每个 required scenario 有 immutable run bundle，含 source/build hashes、
A/B/C 配置和日志、health/segment 前后响应、trace JSONL、output hashes、drain snapshots、
manifest、checksums 和 `PASS/FAIL/INCONCLUSIVE/STOP` 结果。`make check` 仅是仓库检查，不能替代
runtime artifact。D1 已保留 payload metric；若其 trace-only observation 不能通过 non-interference，必须按
[D1 翻案条件](../project/DECISIONS.md#d1--保留-new-put-payload-指标并授权最小观察-patch) 停止该 payload
分支并修改 canonical plan，不能使用原 `G0-RUNTIME VALIDATED` 结论。

**依赖：**D1–D10。
**通过后解锁：**G0 的诚实状态升级，或保留可复核的 STOP/负结果。

## 使用规则

- 新的 owner-confirmed constraint 只能在用户确认后写入 [DECISIONS.md](../project/DECISIONS.md)，并同步
  canonical plan/status；不要在本文件追加“决议”。
- source/runtime finding 应进入 [source audit](G0_SOURCE_RUNTIME_AUDIT.md) 或 retained run artifact；它不能
  自动改变 owner decision。
- 当前可执行下一步由 [TASKS.md](../../TASKS.md) 与 [STATUS.md](../../STATUS.md) 给出；本文件不再提供
  “下一题”。
