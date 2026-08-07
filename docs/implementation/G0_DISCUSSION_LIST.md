# G0 决策讨论列表

> 状态：**DISCUSSION DRAFT**（不是实现计划、源码事实或 runtime 证据）
> 当前总裁决：**G0-SOURCE BLOCKED**
> 目的：在启动 G0 前，逐项收敛会改变 G0 合同、最小 patch、运行时验收或 STOP 处理的决策。
> 讨论方式：严格按本文顺序一次只解决一题；每题结论必须写明采用项、拒绝项、理由和对后续题目的影响。

本清单使用 `grill-me` 的原则：能由 pinned source 或既有 canonical contract 回答的，
不假装成用户选择；真正的分歧才进入讨论。项目宪法仍是
[PROJECT_PLAN.md](../project/PROJECT_PLAN.md)，实际完成状态仍是
[STATUS.md](../../STATUS.md)。本文不能单独升级 claim state，也不能绕过其中的 STOP。

## 已经固定，不重新选择

| 项目 | 结论 | 依据 / 含义 |
|---|---|---|
| 唯一行为变化 | L2 DMA ack 后、`write_storage` 前的 L3 `ADMIT_TO_L3` / `DROP` | 已在 pinned SGLang `b058dc…` 源码核对；不修改 L1/L2、读路径、eviction 或路由。 |
| 首轮 substrate | external pinned SGLang checkout + external pinned Mooncake checkout，小型独立 patch series | 不 vendor、不建 submodule、不建 policy framework。 |
| Mooncake 首轮候选身份 | `v0.3.12.post1` / `6041a609a8c3af35e778f70db344f145c2914980` | 这是待验证组合，而不是“已兼容版本”。 |
| 首轮拓扑边界 | 2 个独立 GPU worker（A/B）+ 1 个 TCP external Store（C） | 仅 C 有非零、有界 storage segment；A/B 为零 segment。 |
| G0 不做的工作 | `VALUE_DENSITY`、L1/L2 或 L3 eviction、router、RDMA/GDR/NIXL、第二 backend、模拟器 | 这些不是解决当前 blocker 的简单办法。 |
| hook 的失败语义 | policy 异常必须 fail-open 回到 upstream write path | 这是 G0 正确性合同，不是可选“高可用功能”。 |

## 讨论顺序与决策树

```text
D1 payload/race 观测合同
 ├─ 保留 new-Put bytes → D2 Mooncake trace-only patch 授权 → D8/D10
 ├─ 删除该 claim       → canonical plan 改写 → 不能按原口径宣称 G0-RUNTIME VALIDATED
 └─ 不接受任一路径     → G0 停止

D3 目标 Linux/GPU 组合 → D4 stock A→B restore → D5 拓扑与隔离
                                                     ↓
                                      D6 trace context → D7 non-interference
                                                     ↓
                                      D8 binary hook → D9 prefix closure
                                                     ↓
                                      D10 cleanup/failure → D11 G0 exit ruling
```

`D1` 和 `D3` 可以在事实收集上并行，但不能跳过 `D1` 后就声称 payload 结果；
`D6`–`D10` 只有 `D3`–`D5` 的 stock runtime 证据通过后才能实施。

## 待讨论项

### D1 — 是否保留“新完成 Put payload bytes”这一 G0 验收目标？

**需要裁决的事实：**当前 Mooncake contract 将 `OBJECT_ALREADY_EXISTS` 与新的 Put 都归约为
Python success `0`。所以 `precheck-miss + put=0` 不能证明“此 writer 产生了新物理写入”。

**可选项：**

1. 授权只读、trace-only 的 Mooncake 观测，在 duplicate-to-success 归约**之前**保留原因码；
2. 修改 canonical plan，停止 `completed_new_put_bytes`、dedup/race 新写归因与 payload-efficiency
   claim；
3. 不接受上述两项，停止 G0。

**推荐：选项 1。**它不改变 Put、Get、去重、重试、队列或存储行为，只补回被上游 API
抹平的事实。选项 2 会使原 G0 的 payload-byte 通过条件失效，不能悄悄将模糊的成功字节改名。

**通过后解锁：**D2、D10、`BYTE_RECONCILE` 与原 G0 exit contract。
**拒绝 / 停止条件：**没有选项 1 的授权时，不得实施 Mooncake patch；若同时不改 canonical plan，
G0 保持 `G0-SOURCE BLOCKED`。

### D2 — 若保留该指标，允许的 Mooncake trace-only patch 精确边界是什么？

**问题：**如何让 trace 在归约前区分 `new_put`、`already_exists_race`、`exists_skip`、
`put_failure`，且不改变原有 return code？

**推荐：**只在 pinned Mooncake checkout 的 duplicate-to-success 归约点之前，向一个独立的
append-only trace sink 发出 opaque `attempt_id` + physical-object key hash + 原始原因码。不得改
API return、object key、lock、retry、batch 顺序、网络协议或 Store 状态；SGLang trace 与此 patch
分 commit、分测试。若无法在不改变行为的前提下取得原因码，应停止 payload 分支，而不是扩展 backend。

**依赖：**D1 选项 1。
**通过后解锁：**D10 的 race/dedup/bytes 分类。
**需要留下的反证：**trace-disabled 与 trace-enabled 的物理 Put/Get 结果和输出相同。

### D3 — G0 的目标 Linux GPU 组合和不可替代的版本身份是什么？

**问题：**哪台/哪些机器构成唯一允许的第一轮 runtime 环境，wheel 不可用时是否启动单独的
source-build compatibility 调查？

**推荐：**第一轮只接受 Linux x86_64、CPython 3.11、官方
`mooncake-transfer-engine==0.3.12.post1` wheel（已记录 SHA-256）和固定 SGLang SHA。保存 GPU、
CUDA、driver、glibc、wheel hash、`git status --porcelain` 和启动命令。若该 wheel 不可用，标记
wheel 分支 `STOP`，另开 source-build compatibility 子调查；不得把 source build 静默称为同一输入。

**通过后解锁：**D4。
**停止条件：**API shape 通过但 adapter 初始化或最小 Put/Get 失败，仍是兼容性 `FAIL`，不得打 hook。

### D4 — stock A Put → fresh B Get 的最小因果证明如何定义？

**问题：**什么证据足以排除 B 的本地命中和静默重算？

**推荐：**A 完成 Put 后再启动一个从未处理该 prefix 的 B；B 的 L1/L2 配置不变、local segment 为
零。一个 PASS 必须同时 join：A Put terminal、B 启动/冷态证据、B successful remote Get、B
storage-loaded pages 和固定 decode output hash。B 输出正确但没有 remote Get 是 `INCONCLUSIVE`，
不是 restore。

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

**问题：**如何实现 `decision_id → StorageOperation → batch/attempt → adapter result`，又不引入
第二套异步生命周期？

**推荐：**向 `StorageOperation` 显式传递一个小型不可变 `TraceContext`（`run_id`、
`decision_id`、`operation_id`）；controller 以每 operation 的 batch ordinal 派生 `attempt_id`。
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

### D9 — prefix-closure 的 decision group 是 all-or-none 还是允许首个 DROP 后强制 suffix DROP？

**问题：**如何确保 first-miss lookup 下不会写入不可达的远端 suffix？

**推荐：**G0 采用更简单的 **root/known-resident anchor + ordered logical pages 的 group all-or-none**。
它天然满足闭包，便于 `ALWAYS_*` oracle 和 trace。将来只有确有按页选择需求且有独立单测时，才讨论
“首个 DROP 后强制所有 suffix DROP”；G0 不需要它。

**依赖：**D8。
**通过后解锁：**`PREFIX_CLOSURE` runtime case。
**停止条件：**靠新 remote metadata、目录 RPC 或 read-path repair 修补 hole。

### D10 — dedup/race/failure 与异步清理的最低验收边界是什么？

**问题：**真实 runtime 必须覆盖哪些终态；没有官方 failure injector 时能否把“未测”写成通过？

**推荐：**必须分别保留 sequential dedup、two-writer overlap、正常成功、policy exception fail-open、
shutdown/detach 的 terminal；每个 admitted path drain 后 `backup_queue`、`ack_backup_queue`、
`ongoing_backup` 和 host protection 回到基线。没有官方、非侵入式 failure injector 时，failure
coverage 只能是 `INCONCLUSIVE`，不能伪造或以进程退出掩盖；若 canonical G0 仍要求该项 PASS，则 G0
不能报告 runtime validated。D1 选项 1 后，race 还必须按 pre-collapse 原因码对账。

**依赖：**D1/D2（针对 race bytes）、D8。
**通过后解锁：**G0 matrix 的清理与失败分支结论。
**停止条件：**通过 mock backend、聚合字节或进程退出声称 runtime failure lifecycle 已覆盖。

### D11 — G0 的最终通过声明究竟要求哪些 retained artifacts？

**问题：**什么是功能 smoke，什么才允许写 `G0-RUNTIME VALIDATED`？

**推荐：**保留原严格定义：每个 required scenario 有 immutable run bundle，含 source/build hashes、
A/B/C 配置和日志、health/segment 前后响应、trace JSONL、output hashes、drain snapshots、
manifest、checksums 和 `PASS/FAIL/INCONCLUSIVE/STOP` 结果。`make check` 仅是仓库检查，不能替代
runtime artifact。D1 若选择取消 payload metric，必须先改 canonical plan 后才能重新定义一个较窄的
G0 functional gate；在此之前不能使用原 `G0-RUNTIME VALIDATED` 结论。

**依赖：**D1–D10。
**通过后解锁：**G0 的诚实状态升级，或保留可复核的 STOP/负结果。

## 每题的结论记录模板

讨论完一题后在该题下追加：

```markdown
### 决议（YYYY-MM-DD）

- 采用：
- 拒绝：
- 理由与反例：
- 需要修改的 canonical / implementation 文档：
- 解锁的下一题：
- 不改变的 scope：
```

没有这六项，讨论只能算观点交换，不能作为 implementation authority。

## 下一题

**D1：你是否授权一个严格 trace-only、pre-collapse 的 Mooncake observation patch，以保留
`new_put` / `race_existing` 的区分并维持原 G0 payload-byte 合同？**

推荐授权，但前提是它只记录原因码与 opaque correlation，完全不改变 Put/Get 结果、对象 key、
队列、重试、传输和 Store 状态。若不授权，下一步不是写 hook，而是修改 canonical plan 或停止 G0。
