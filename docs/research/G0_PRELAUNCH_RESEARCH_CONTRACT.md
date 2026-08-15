# G0 启动前调查合同

> 状态：**ROADMAP（调查任务说明，不是调查结论）**
> Historical prelaunch verdict: **G0-SOURCE BLOCKED**（2026-08-06 的调查入口，不是当前 runtime 状态）
> 面向对象：接手 G0 部署与验证前的独立 research agent
> Canonical plan：[PROJECT_PLAN.md](../project/PROJECT_PLAN.md)；实际状态：[STATUS.md](../../STATUS.md)。如本文件与前二者冲突，以前二者为准。当前 active pre-D1 contract 是 D14 的 S1–S3；D12 仅保留窄 payload/resource 例外，旧 one-shot sentinel 不得由本调查合同重新启用。
> Runtime follow-up：first-C0 r6 后续已 scoped 验证 stock restore qualification；本 prelaunch contract 的 R0–R6 仍只描述其当时缺失的 source/runtime evidence，不能替代或降低 fresh C1、S1–S3 的要求。

## 1. 目的和边界

本合同列出启动 G0 runtime plan 前仍需取得的一级证据。它不授权实现
`VALUE_DENSITY`、修改 L1/L2、添加 remote metadata/read path、vendor upstream、创建
submodule，或把任何候选版本称为“已兼容”。

已完成的 SGLang 源码事实不需要重复审计：在
[`b058dc910619c9d4bce9e9e24117104ffc491fa6`](https://github.com/sgl-project/sglang/commit/b058dc910619c9d4bce9e9e24117104ffc491fa6)
中，唯一 behavior-changing seam 已定位在 `HiRadixCache.write_backup_storage`：L2
DMA ack 后、`HiCacheController.write_storage(...)` 前。精确行号、队列和 host
protection 事实见 [G0 source audit](../implementation/G0_SOURCE_RUNTIME_AUDIT.md)。

本调查的产出只能升级各条目的证据状态；不能仅因为 API 名称存在、服务能启动或
smoke test 成功，就把 G0 升级为 `G0-RUNTIME VALIDATED`。

## 2. 统一证据纪律

每个调查包必须使用固定 checkout、官方 release、官方文档、固定 commit 源码或实际
运行 artifact。README 描述、Python `hasattr`、服务启动日志和端到端 trace 的证据等级
不同，报告中必须分列。

每个包交付一个独立目录（不提交原始运行输出），至少包含：

- `finding.md`：问题、结论，且结论只能是 `PASS`、`FAIL`、`INCONCLUSIVE` 或 `STOP`；
- `evidence.md`：每项 SOURCE_VERIFIED 事实对应固定 URL/commit/path/line，或原始命令与原始输出的 hash；
- `manifest.json`：SGLang SHA、Mooncake tag/full SHA、包版本、wheel/source-build SHA-256、Python/CUDA/driver、硬件、日期；
- 原始 stdout/stderr、配置文件、精确命令和校验和；
- 未解决项与其阻止的下一步。不得以推测填补空项。

除非各自标准明确允许，`INCONCLUSIVE` 不得被记录为 `PASS`。任何 `STOP` 都保留
artifact 并停止对应分支，不通过扩大 scope 来规避。

## 3. 调查包 R0：Mooncake 精确版本与 pinned adapter 兼容性

### 目标

确认候选 `mooncake-transfer-engine==0.3.12.post1` 能否作为 SGLang
`b058dc910619c9d4bce9e9e24117104ffc491fa6` 的**第一轮固定输入**，而非确认
“Mooncake 最新版可用”。

在这份 prelaunch contract 写入时，仅 SOURCE_VERIFIED：官方 release `v0.3.12.post1`、release commit 前缀
`6041a60`，以及 Linux x86_64 CPython 3.11 wheel SHA-256
`8b73bf8a4f1de741a73f04f32f1e73549c60bfbf7ee73710141ef1f8ea324439`。
该候选与 pinned adapter 的兼容性当时仍是未决 blocker；后续 r6 只为其记录的 stock target-Linux 组合提供 scoped runtime evidence。

### 必答问题

1. `v0.3.12.post1` tag 实际解析到哪个完整 Git SHA？其 SHA 是否以 `6041a60` 开头？
2. 安装的 distribution 名称和版本是否精确为 `mooncake-transfer-engine 0.3.12.post1`？二进制/wheel 或 source build 的 SHA-256 是什么？
3. 该环境中的 `MooncakeDistributedStore` 是否能被 pinned SGLang adapter import，并提供 `setup`、`register_buffer`、`batch_is_exist`、`batch_put_from`、`batch_get_into`？
4. adapter 初始化和最小 Put/Get probe 是否在该组合中完成，且没有 API 签名、ABI、CUDA 或动态库错误？
5. 若官方 wheel 不适用，官方 source build 的**实际**依赖、CMake 参数、编译器/CUDA 版本和产物 hash 是什么？这必须作为新的候选组合，不可与 wheel probe 混称。

### 允许证据与通过标准

| 检查 | 通过（全部必须满足） | 失败 / 不确定 / 停止 |
|---|---|---|
| Source identity | SGLang `rev-parse HEAD` 精确等于 pinned SHA；Mooncake `rev-parse HEAD` 是 tag 解析出的完整 SHA，且该 tag/release 由官方来源交叉确认。 | SHA、tag 或 checkout 不一致：`FAIL`。无法获取 official tag：`INCONCLUSIVE`，不打 patch。 |
| Binary identity | Python metadata 显示 `0.3.12.post1`；实际 wheel/source artifact SHA-256 被保存。首轮 wheel 必须等于上列 SHA。 | 包版本/哈希不符：`FAIL`。目标平台无该 wheel：`STOP` 当前 wheel 分支；不得静默换包。 |
| API contract | 在真实安装环境 import 成功；五个 API 全部存在，且 pinned adapter 的最小初始化、Put 与 Get 获得正常 terminal。 | `hasattr` 通过但 adapter/probe 失败：`FAIL`。服务未就绪导致无法 probe：`INCONCLUSIVE`。 |
| Compatibility conclusion | 上三项均通过，并保存原始 probe，才可写“该精确组合通过 G0 compatibility probe”。 | 绝不可由 tag、release date 或 API shape 单独写“compatible”。 |

### 必交付物

- 官方 release URL、tag 的完整 SHA、`git status --porcelain`、安装命令与 `pip show`/metadata 输出；
- wheel 文件名与 SHA-256，或 source checkout SHA、构建命令、编译日志和产物 SHA-256；
- adapter import、初始化、最小 Put/Get 的原始日志；
- 对 SGLang adapter 调用的 API/签名对照表。源码入口是
  [`MooncakeStore.batch_set_v1`](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/storage/mooncake_store/mooncake_store.py#L1059-L1115)。

## 4. 调查包 R1：external Mooncake Store 的 TCP 与 bounded-segment 合同

### 目标

验证 G0 所需的唯一 L3 拓扑能够成立：两个独立 GPU worker A/B 使用 TCP 访问一个
external Mooncake Store C，且仅 C 提供非零、有上界的 global storage segment。

### 必答问题

1. fixed Mooncake 版本中 master、metadata、external Store 的官方启动方式、配置字段和 health/segment 查询接口是什么？
2. `protocol: "tcp"`、`device_name: ""`、`local_buffer_size: 0`、非零整数 `global_segment_size` 在 external Store 上是否被接受并实际生效？
3. A/B 的同一 backend config 中 `global_segment_size: 0` 是否真的使它们不贡献 L3 storage？
4. tenant、`extra_backend_tag`、model name、page size 与各 hostname 哪些必须一致/唯一，才能让 A 写入、B 找到同一 key-space？
5. Store 的 segment capacity、已用量和健康状态能否在 run 前后留存为原始响应？

### 通过标准

| 结论 | PASS | FAIL | INCONCLUSIVE / STOP |
|---|---|---|---|
| TCP external topology | A/B 是独立进程；C 的 Store 成功注册并报告非零、bounded segment；A/B 均报告零 segment；三者均为 TCP。 | worker 贡献 L3 memory、C 无 segment、fallback 到别的 transport 或角色混淆。 | 接口不可达：`INCONCLUSIVE`。只能靠 RDMA/GDR/NIXL 才能启动：`STOP`，不扩展 G0 数据面。 |
| Key-space contract | A/B 使用相同 model/tokenizer revision、served model name、tenant、backend tag、page size 和 metadata/master；仅 hostname 按角色不同。 | 任一 key-space 输入漂移，或靠手工复制数据达到命中。 | 文档与源码无法确定字段语义：`INCONCLUSIVE`，先做 fixed-source audit。 |
| Observability | 保存启动配置、health/segment 原始响应和 A/B/C 完整日志。 | 仅有汇总监控、无可保存的配置/response。 | 无 endpoint：`STOP` payload/capacity 分支；不得用猜测的容量数替代。 |

### 必交付物

- 官方 fixed-version deployment 文档与源码 URL；
- C 的完整 JSON 配置、A/B backend config（删除凭据后）、启动命令和 health/segment response；
- topology manifest，写明 host/IP、端口、角色、segment 大小和 transport；
- 一张 key-space 字段表，注明 `same on A/B`、`unique per worker` 或 `unknown`。

Pinned SGLang README 已证明 TCP 与 external segment 是上游支持路径，但尚未证明本地部署成功：
[deployment README](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/storage/mooncake_store/README.md#L34-L78)。

## 5. 调查包 R2：Mooncake 写入终态、dedup、race 与失败语义

### 目标

确定真实 object 级写入语义，避免把“对象已存在”、并发竞争、部分成功和真正新写入混为一个
模糊的 completed Put 指标。D1 已固定若进入 payload 归因时唯一允许的 Mooncake pre-collapse 只读
observation；是否实际施工还受 canonical pre-D1 ruling 与 D12 约束。该 patch 完成前，new-Put payload
仍不可报告。

### 必答问题

1. `batch_is_exist`、exists-filter、`batch_put_from` 的返回值在 fixed version 中分别代表什么？
2. 两个 writer 对同一 physical key 并发执行时，哪些 terminal 状态可能出现？是否原子？是否有错误码？
3. 一个 logical page 展开为 K/V（或 split-head）physical objects 时，部分 object 成功如何向 adapter 归约？
4. 支持哪些受控 Put failure 方法；若没有 injector，哪些自然失败路径可观测且不会误伤环境？
5. failed/partial batch 后 SGLang backup queue、ack queue、`ongoing_backup`、host protection 的实际终态是什么？

### 通过标准

| 检查 | PASS | FAIL | INCONCLUSIVE / STOP |
|---|---|---|---|
| State classification | 每个 physical object 都可区分 exists-skip、race/existing、successful new Put、Put failure，且能关联回 logical page/operation。 | dedup 被计为新 Put，或 terminal 不可区分。 | 后端不暴露一项：`INCONCLUSIVE`；该项不得进入 payload claim。 |
| Failure lifecycle | success、dedup、可获得的 failure、shutdown/detach 均可观察到 queue/ref/protection 回到基线。 | 泄漏、hang、无终态或只有进程退出掩盖状态。 | failure injector 不可用：`INCONCLUSIVE`，仅限 failure coverage；不能宣称 failure 已覆盖。 |
| Partial semantics | fixed Mooncake + adapter 的 page/object result reduction 被源码和 runtime artifact 同时证明。 | 只凭 controller bool 推断每 object 结果。 | 上游没有足够 telemetry：`STOP` byte-reconciliation / partial-failure claim，不改造 backend。 |

### 必交付物

- Mooncake fixed-source 的函数链接、精确行号与 API 返回值表；
- sequential dedup、two-writer overlap、可控/自然 failure 的 raw trace；
- 每个 case 的 queue/ack/`ongoing_backup`/host-protection baseline 与 drain 后快照；
- 明确的限制：SGLang controller 当前对 partial success 的处理不完整，不能将 bool result 伪装为 per-object 成功。

SGLang 已验证的 adapter 顺序是 exists 检查 → 过滤 → Put → logical page 归约；详情见
[source audit](../implementation/G0_SOURCE_RUNTIME_AUDIT.md#mooncake-adapter-and-observation-seam)。这不是 Mooncake race/atomicity 的证明。

## 6. 调查包 R3：payload-byte 定义、逐 object 对账与实验隔离

### 目标

证明 G0 可以测量 `new_physical_put_bytes`（当前 writer 新建的 Mooncake physical-object payload），并证明每个 run
不受上一次残留对象污染。

### 必答问题

1. fixed adapter 在何处得到 logical hash、physical object key、pointer、`buffer_size`、exists 结果与 Put result？
2. `new_physical_put_bytes` 应精确定义为哪些 physical object 的 `buffer_size` 之和？race-existing、exists-skip、失败、Get bytes 是否分别记账？
3. 该定义与 logical KV bytes、NIC/wire bytes 的边界是什么？
4. `MooncakeStore.clear()`、namespace、tenant/tag 或 Store restart 在 fixed version 中各自清除什么？怎样证明 fresh run？

### 通过标准

| 检查 | PASS | FAIL | INCONCLUSIVE / STOP |
|---|---|---|---|
| Byte reconciliation | 对每个 decision，logical page → physical object → terminal 一一可 join；pre-collapse 确认新 Put 的 physical `buffer_size` 之和等于报告的 `new_physical_put_bytes`。 | unmatched object/byte、混合 logical/physical/wire 定义、dedup/race 被加为新写入。 | backend 无 per-object terminal：`STOP` 任何 payload-efficiency claim。 |
| Get separation | Get、Put、dedup 与 failure 分别有字段和独立总计。 | 使用一个“bytes”字段混合读写。 | 缺少 Get terminal：`INCONCLUSIVE` restore payload 分析。 |
| Run isolation | 每次 scenario 使用 fresh Store，或有 fixed-version source + before/after evidence 证明 namespace/cleanup 的等价隔离。 | 仅调用 `clear()` 且无语义/状态证据。 | 清理语义无法确认：`STOP` comparative run；采用 fresh Store/restart。 |

### 必交付物

- 字节词典（字段、层级、分子、排除项、产生点）；
- 一个 tiny Put/Get/dedup case 的 object-level JSONL 与手算对账；
- cleanup/source audit 或 fresh-store procedure，含 before/after segment、object state 或启动 epoch 证据。

## 7. 调查包 R4：SGLang runtime 配置、冷态与 cross-worker attribution

### 目标

让 “A Put → fresh B Get → non-zero prefill substitution” 是可证伪的因果链，而不是 B 输出正确、
成功 Get 或 cache hit 计数上升的间接猜测。

### 必答问题

1. 目标 dense model 是否支持 pinned SGLang HiCache Mooncake path，且 A/B 的 model/tokenizer revision/hash 是否可固定？
2. 从启动输出和配置中如何确认 `HiRadixCache` 被选中、Unified Radix Tree 关闭、TP=PP=DP=DCP=1、page size/L1/L2 固定？
3. B 在 probe 前如何证明 local-cold？禁止通过改动 L1/L2 容量或配置实现冷态。
4. 请求 token/hash、A Put、B Get、B storage-loaded pages、storage-cached token breakdown、输出 hash 如何形成同一 run 的确定性关联？
5. 如何用相同请求的独立 B-cold no-L3 control 证明 L3 arm 实际减少 uncached/prefill tokens？若 B 成功输出但无 successful remote Get，如何区分重算和本地命中？

### 通过标准

| 检查 | PASS | FAIL | INCONCLUSIVE / STOP |
|---|---|---|---|
| Fixed runtime | A/B 的 model、tokenizer、cache config、transport、backend tag/tenant 相同且记录；启动日志确认 HiRadix。 | fallback cache、hybrid model、不同 tokenizer/model/config，或用不同 L1/L2 实现作实验变量。 | 启动日志不足：`INCONCLUSIVE`，补 source/config audit 后再运行。 |
| `RESTORE_PATH_PASS` | A completed Put、B successful remote Get、B storage-loaded pages、B local-cold evidence 和输出 equality 全部可关联。 | B 无 remote Get 而重算，B 已热，或输出不同。 | 缺任一证据：`INCONCLUSIVE`，不得称 shared-L3 restore。 |
| `REMOTE_VALUE_SURVIVES` | 前一行已通过，`cached_tokens_details.storage > 0`，且 L3 arm 的 uncached/prefill tokens 少于相同请求的独立 B-cold no-L3 control。 | Get 成功但不减少任何 uncached/prefill tokens；按 G0 STOP，不以 TTFT 偶然变化挽救。 | cache-source breakdown、token count 或公平 control 不可得：`INCONCLUSIVE`，不得进入 D1/trace/hook。 |

### 必交付物

- A/B launch commands、startup logs、model/tokenizer hashes、完整 fixed cache config；
- cold-state procedure 和证据；
- 一个 stock（无 patch）A→B exact-prefix trace，含 Put/Get/output joins、cache-source breakdown，以及相同请求 B-cold no-L3 control 的 token accounting；
- 对失败时的明确归因：`local hit`、`recompute`、`remote unavailable` 或 `unobservable`。

## 8. 调查包 R5：trace-only 传播与行为不干扰性

### 目标

在行为 hook 之前证明最小观测链可实现且不会改变 upstream path：

```text
observation_id → StorageOperation operation_id → batch_ordinal / attempt_id
               → adapter logical/physical object terminal
```

行为 hook 完成后才可在同一 record 追加 `decision_id`；R5 不计算或应用 admission action。

### 必答问题

1. `StorageOperation`、backup batching 与 adapter 的最小加字段/side map 位置是什么？
2. 哪些字段必须记录以支持 byte、dedup、failure、Get 与 output join？
3. 如何证明 opaque ID 不会进入 key construction、queue ordering、retry、dedup、read path 或 admission？
4. trace-disabled/trace-enabled stock-equivalent microcase 的等价 oracle 是什么？

### 通过标准

| 检查 | PASS | FAIL | INCONCLUSIVE / STOP |
|---|---|---|---|
| Deterministic correlation | 无 wall-clock 猜测；每个 eligible decision 可唯一关联 operation、每个 controller batch 和 adapter terminal。 | missing/duplicate join，或只能由 key/time heuristic 关联。 | 上游对象边界不可观测：`STOP` policy，不在不可信 telemetry 上实现。 |
| Non-interference | 改变 opaque ID 字面值或关闭 trace 后，keys、order、Put/Get result、output、queue/ref terminal 与 stock 相同。 | ID 改变 key-space、顺序、dedup、retry 或行为。 | 无 matched artifact：`INCONCLUSIVE`。 |
| Scope | trace patch 与 admission patch 分文件、分测试、分 commit。 | 合并 patch，或 trace 字段参与 policy/行为。 | `STOP`，先拆分。 |

### 必交付物

- source map 与字段 schema；
- trace-disabled / trace-enabled paired raw artifact；
- 一个 ID 改变但行为恒等的 test report；
- 明确写出不记录 prompt/token 内容，仅记录 hash 和 opaque IDs。

## 9. 调查包 R6：prefix closure、fail-open 与异步终态的可验证性

### 目标

将已经确认的 L2 ack→L3 seam 转换为可测不变量，确认无需新增 remote control plane。

### 必答问题

1. 一个 admission decision group 的 root/known-resident anchor、ordered logical hashes 和 split-chain 重建方式是什么？
2. 如何在 decision point 判断并拒绝 “ancestor DROP、descendant ADMIT” 的 hole？
3. policy exception 的 fail-open 如何证明回到未改 upstream `write_storage` path？
4. `ALWAYS_DROP` 如何同时证明 L2 CPU event 完成、零 L3 operation/queue/protection/Put？
5. success、dedup、failure、shutdown/detach 后哪些异步状态必须回到 baseline？

### 通过标准

| 检查 | PASS | FAIL | INCONCLUSIVE / STOP |
|---|---|---|---|
| Prefix closure | 一个 root/known-resident anchor 与 ordered hashes 构成的完整 group 只取得一个 action：完整 group `ADMIT`，或完整 group `DROP`；故意 partial-group hole / descendant-only group 被决策边界拒绝；B lookup 在 first miss 停止。 | policy 产生 partial-group admission，或通过新增 metadata/read path 修补。 | anchor/order 不可见：`STOP`，不做细粒度 policy。 |
| Fail open | 人为抛出一次 policy exception，记录 `POLICY_ERROR_FAIL_OPEN` 后出现 upstream Put terminal 与正常 cleanup。 | 请求失败、意外 DROP、L2 受影响。 | exception terminal 无法观察：`INCONCLUSIVE`。 |
| ALWAYS_DROP | L2 event/output 正确；无 `StorageOperation`、backup queue、`ongoing_backup`、host protection、Mooncake Put，且 `admitted_payload_bytes = submitted_payload_bytes = 0`。 | 任一 L3 mutation、ref/protection 变化或 L2 异常。 | 缺少任一状态证据：`INCONCLUSIVE`，不能由 aggregate metric 推零 Put。 |
| Async drain | delay/success/dedup/failure/shutdown 后 backup queue、ack queue、`ongoing_backup` 和 protection 均回基线且无 hang。 | leak、residual ref 或 hang。 | 只有 process exit 可见：`STOP` runtime policy experiments。 |

### 必交付物

- group/anchor 数据模型与三组手工 case：完整 group `ADMIT`、完整 group `DROP`、descendant-only / 无法重建的 split chain 被整体拒绝；
- fail-open、ALWAYS_DROP、drain snapshots 的 raw traces；
- 对每个无法注入 failure 的 case 标为 `INCONCLUSIVE`，不以理论替代。

## 10. 调查结果如何决定下一步

| 调查包结果 | 可以进入的下一步 | 禁止动作 |
|---|---|---|
| R0 PASS，R1 PASS | 运行 stock external-store A→B restore（R4）。 | 尚不实现 policy。 |
| R0 FAIL / STOP | 保持本 prelaunch source branch 的 `G0-SOURCE BLOCKED` 结论，记录候选不兼容。 | 不换“最新版”继续宣称同一 pin。 |
| R1 FAIL / STOP | 收口为部署不可用或环境不满足。 | 不改为 RDMA/GDR/NIXL、同进程伪双 worker 或 worker-local L3。 |
| R2 或 R3 STOP | 保留 restore/correctness 调查；停止 payload-efficiency / byte claim。 | 不用 aggregate 指标或 simulator 补齐 physical payload。 |
| R4 PASS | 只形成首次 C0 qualification；随后必须在 fresh C1 cohort 重做 C0，再 finite source/runtime-audit X*、完成 baseline-only freeze、S1 `RESTORE_VALUE_REGION` 与 sticky-reuse S2/S3。只有 S1 存活、target remote Get 非近零、sticky-reuse publication mass 达到冻结阈值且 S2/S3 至少一个 signal，才自动继续 D1 observation 与 R5 trace-only；双 valid-false 后仅有符合 D12、在 D1 结果未知时冻结真实资源目标/预算/物质性判据的第一次 owner 例外可解锁 observation-only R5。 | 不复用首次 C0 状态/artifact 证明 C1 eligibility；不把 stock restore、one-shot negative control 或粗粒度 Store activity 当作 policy 效果；S1 STOP、remote Get≈0、sticky-reuse mass 过小或 S2/S3 双 valid-false 均在 owned patch 前 STOP，不满足 R/F，第一次例外也不授权 behavior hook。 |
| R5 PASS | 在 active D14-surviving branch 中实现最小 fail-open binary hook，并执行 R6；D12 第一次例外本身不授权此步骤。 | 不建设通用 policy framework、Agent hint 或 VALUE_DENSITY candidate。 |
| R6 PASS | 运行 G0 matrix：ALWAYS_ADMIT、ALWAYS_DROP、closure、bytes、race/failure、cleanup；之后才可进入 G2a/O1 的独立 Gate。 | 不自动实现 candidate、conditional ledger 或 G3。 |

## 11. 研究报告验收清单

交付审核时逐项回答：

- [ ] 是否每个版本、二进制与配置都有可复现 identity？
- [ ] 是否每个 SOURCE_VERIFIED 事实都能定位到固定 source/release，而非惯例？
- [ ] 是否把 adapter API shape 与 runtime compatibility 分开？
- [ ] 是否能分别解释 logical KV、physical-object payload、dedup、failure 与 Get？
- [ ] 是否能证明 B 是 local-cold 且确实完成 remote Get？
- [ ] 是否 trace ID 完全不参与行为？
- [ ] 是否对 hole、fail-open、async leak 和 partial/failure 诚实标记 PASS/FAIL/INCONCLUSIVE/STOP？
- [ ] 是否没有引入 L1/L2 改动、remote metadata/read path、第二 backend 或策略框架？

只有全部相关调查项满足其明确 PASS 标准，才允许执行
[G0 runtime execution plan](../implementation/G0_EXECUTION_PLAN.md) 的对应步骤。即使全部调查
PASS，G0 仍须完成该计划中的完整 runtime matrix 并保留 artifacts，才可能升级为
`G0-RUNTIME VALIDATED`。
