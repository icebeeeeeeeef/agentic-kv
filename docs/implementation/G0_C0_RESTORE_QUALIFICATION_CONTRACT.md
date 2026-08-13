# G0 C0 Restore Qualification Contract

> 状态：**OWNER-DECIDED CONTRACT / 非运行时证据**（2026-08-12）
> 权威：本合同实现 [G0 execution plan Task 1](G0_EXECUTION_PLAN.md#task-1-establish-stock-external-store-recovery-and-prefill-survival) 的输入、控制和观测要求；不得改变 [PROJECT_PLAN.md](../project/PROJECT_PLAN.md) 的 Gate/STOP。
> 结论边界：C0 通过只能称为 **restore qualification / S1 input**，不是 S1 通过、T5 完成、G0 完成、性能结论或进入 D1/T6/T7 的授权。

## 1. 目的和状态边界

C0 分别裁决两个 predicate，不能互相替代：

```text
RESTORE_PATH_PASS
  = A Put terminal ∧ A→C attribution ∧ B local cold
    ∧ B remote Get / loaded pages ∧ output_L3 = output_no_L3

REMOTE_VALUE_SURVIVES
  = RESTORE_PATH_PASS
    ∧ cached_tokens_details.storage > 0
    ∧ uncached_prompt_tokens_L3 < uncached_prompt_tokens_no_L3
```

`uncached_prompt_tokens = prompt_tokens - cached_tokens`。TTFT、Store NIC/CPU 和任何单次“命中”日志都只可作为诊断；它们不能替代 token-level oracle。

截至本合同写入时，SGLang 在 pinned source 暴露 storage-cached token accounting 是 `SOURCE_VERIFIED`；目标 Linux build、A Put、B Get、local coldness 和所有 predicate 均无 runtime artifact，保持 `UNRESOLVED`。

首次 C0 的执行入口服从 [D18](../project/DECISIONS.md#d18--首次-c0-的-correctness-only-入口与-evidence-driven-hardening)：
租机前只物化内容寻址输入与单次 runbook/raw capture/off-host handoff；target host 的 build/API/config、实际
write condition、GPU、Store 和 private TCP 事实只能在租机后检查。无论入口多薄，本节两个 predicate 和下文的
分类表都不能被 OCI/Docker、TTFT、容器重启、Store aggregate 流量或人工摘要替代。

实际 write condition 不是预想风险：pinned source 已 [SOURCE_VERIFIED](G0_SOURCE_RUNTIME_AUDIT.md#verified-sglang-write-path)
`_inc_hit_count` 只有达到 threshold 才调用 `write_backup`。因此首次 C0 只增加一个目标 runtime config/threshold probe
和对应的最小固定 A 请求序列；它不解锁完整 X* audit 或通用 preflight。

## 2. 请求和 identity 合同

| 项目 | 合同 | artifact |
|---|---|---|
| 模型 | 候选 `Qwen/Qwen2.5-1.5B-Instruct`、BF16、revision `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`；A/B 必须看到同一 model 与 tokenizer 文件 hash。该候选尚未 runtime 验证。 | model revision、file hash、served model name |
| 输入 | 以固定 template revision 在 worker 外渲染一次，形成唯一 raw prompt payload；A、B-L3、B-cold control 发送相同字节，不让服务端二次 chat-template 渲染。 | template id/hash、raw-prompt SHA-256、完整 request body 的脱敏 hash |
| token identity | 同一 tokenizer 对 raw payload 的 token-ID 序列必须相同。 | tokenizer revision/hash、token-ID SHA-256、token count |
| page alignment / write trigger | probe 后取得实际 page size `P` 和 stock write policy/threshold，令共享 prefix token 数 `N mod P = 0`；选择能以最小固定 A 请求序列触发非零 Put/Get 的最小 `N`，不得猜测 `P`、阈值或硬编码 8K。 | `write_trigger.json`：`P`、`N`、alignment、policy/threshold echo、A sequence、prompt/token hashes |
| decode | API probe 后使用确定性 greedy decode，固定所有 generation 参数并至少取得一个可比较的 completion token。 | request config、actual completion count、output UTF-8 SHA-256；可取得时另存 completion-token-ID hash |

如果 target API 无法保证相同 raw-prompt 语义、确定性可比输出或可比 token accounting，不能用近似请求替代。
若在请求链开始前发现，记 `BLOCKED_BEFORE_C0`；若在真实请求后才发现证据不足，记 `INCONCLUSIVE`。

## 3. 隔离和执行顺序

每个 C0 run 使用唯一 `run_id`、fresh C 实例或可证明空 keyspace 的等价隔离。`extra_backend_tag` 只能是辅助标签；它本身不证明 Store 容量或对象状态已隔离。

1. **target admission probe**：核验输入 hash；记录 SGLang SHA、Mooncake tag/full SHA/wheel-or-build hash、model/tokenizer hashes、实际 GPU UUID、API request/response fields、cache implementation、page size、stock write policy/threshold、C health/nonzero bounded segment 和 private endpoint。任何失败都停在 `BLOCKED_BEFORE_C0`。
2. **fresh C / unique keyspace**：创建 fresh C 或证明等价的空隔离 keyspace；A 是 tested `config_prefix`/model KV objects 的唯一 writer。唯一允许的例外是 pinned stock client 启动时使用 `sglang_mooncake_store_warmup_key` + UUID 的 warmup object：它不经过 `_tag_keys`，而测试 page key 必须经过 `config_prefix`；A/B-L3 均须保留 warmup 成功与 config-prefix 日志。除此之外不得允许 B 写 tested key。只启动 metadata/master 或使用 zero-sized segment 不合格。
3. **A Put**：A 按 probe 后冻结的最小请求序列触发已核验的 stock write condition，最后写入与 B 请求相同的 page-aligned prefix，并等待 terminal Put。没有 Put terminal 时停在 `BLOCKED_BEFORE_C0`，不得把未形成的 A→C premise 判成 C0 `FAIL`。
4. **A→C→B join**：fresh C/unique keyspace、A 对 tested config-prefix/model KV objects 的 sole-writer、已留证且 namespace 分离的 stock warmup 例外、A Put terminal、相同 token hash 和随后 B 的 remote Get/load 共同闭合最小 join。若 stock C 直接暴露 request/key identity 则保存；不能只凭 aggregate NIC/Store 流量归因，也不为 C0 提前实现 trace patch。
5. **B cold certificate**：保存 A terminal 后退出/销毁的证据，再创建 fresh B-L3 process；B 在请求前完成第 4 节 cold certificate。A/B 可以顺序使用同一物理 GPU，但不得重叠运行或共享可写/persistent local state。
6. **B L3 request**：B 对同一 raw prompt 发请求；保留 Get/loaded-page、token source accounting、输出和配置。
7. **fresh B-cold no-L3 control**：销毁 B-L3，启动新的 B process，L3 明确 disabled，再发完全相同请求；保留同类 token/output/config artifact。
8. **evidence handoff**：在实例释放前生成 raw bundle 与 checksum，并复制到 off-host 持久位置；人工摘要不是 retained evidence。

C1 必须在自己的 fresh cohort 重做这个 preflight；C0 的 retained artifact 证明合同曾被执行，不能替代 C1 的 runtime eligibility。

## 4. B local-cold 的充分证据

“重启进程”这一个字段不是充分条件。C0 要求同一 cold certificate 同时包含：

- B PID、start time、binary/config hash、`CUDA_VISIBLE_DEVICES` 与实际 GPU UUID；
- B 在目标请求前没有任何 request ledger entry；
- `--skip-server-warmup` 禁止 model/API warmup request；Mooncake client 的固定 namespace warmup 不是请求 ledger entry，必须按第 3 节单独留证；
- A Put terminal 后 A 已退出，B 是此后创建的新 PID，且没有继承 A/B-L3 的 writable state；
- B 的 `global_segment_size=0`、无可复用 persistent local cache path，且连接的是 manifest 记录的 C；
- 若 stock 暴露直接的 L1/L2 empty/resident/match metric/log，则一并保存，但它不是首次 C0 的唯一入口。

PID/start、空 request ledger、独立 writable state、无 persistent local cache、`global_segment_size=0` 中任一项缺失，
都不能以“理论上 B 没访问过”补足：coldness 为 `INCONCLUSIVE`。A/B 使用同一 GPU UUID 本身不是失败；只有
进程重叠或状态继承才破坏首次 C0 隔离。

## 5. 必需观测和 retained artifacts

| 观察 | 最小内容 | 支持的 predicate |
|---|---|---|
| admission / trigger | input/build/API/config identity、page size、write policy/threshold、A fixed sequence、GPU/C/private endpoint | 是否进入 C0；不支持 predicate 本身 |
| C pre/post state | config、`/get_all_segments` raw/已确认 schema 与 exact nonzero segment、fresh C or unique keyspace、启动日志 | A→C attribution、freshness |
| stock warmup exception | pinned adapter hash/source proof、A/B-L3 warmup success、相同 tested config prefix | 排除唯一允许的非测试 writer object |
| A Put | request/token identity、terminal result、stock write completion、A config、A exit | `RESTORE_PATH_PASS` |
| B cold certificate | 第 4 节全部项目 | `RESTORE_PATH_PASS` |
| B Get/load | remote Get 与 loaded logical storage pages 的 stock evidence，能关联 B request | `RESTORE_PATH_PASS` |
| token accounting | `prompt_tokens`、`cached_tokens`、`cached_tokens_details.storage`、推导 `uncached_prompt_tokens` | `REMOTE_VALUE_SURVIVES` |
| output | raw UTF-8 output hash、至少一个 completion token、可选 token-ID hash | 功能等价 |
| realized identity | source/build/model/tokenizer/GPU/config/network endpoint | 可复核性与公平性 |
| off-host bundle | raw artifact inventory、bundle checksum、copy destination/confirmation | 短命实例释放后的可复核性 |

所需 artifact 以 raw log/response 为主；人工摘要不能代替其中任一项。不得记录 prompt/token 明文，只记录必要的不可逆 hash、长度和已批准的配置摘要。

## 6. 执行状态与判定表

`execution_status` 先于 C0 outcome：

- input/build/API/config、write condition/Put terminal、GPU、C segment/health 或 private TCP admission 未满足：
  `execution_status=BLOCKED_BEFORE_C0`，两个 predicate=`NOT_EVALUATED`，不产生 C0 Gate outcome；
- 只有 A Put terminal 已成立且 A→C→B 请求链实际开始，才进入 `execution_status=EXECUTED` 并使用下表。

| 观察结果 | `RESTORE_PATH_PASS` | `REMOTE_VALUE_SURVIVES` | C0 outcome |
|---|---|---|---|
| 所有 required joins 成立；`storage>0`；`uncached_L3 < uncached_control` | PASS | PASS | PASS：仅 restore qualification |
| 缺 token breakdown、字段语义未确认，或 Get/load 不可关联 | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE |
| B coldness 不可证明 | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE |
| fixed-decode output 不同 | FAIL | 不适用 | FAIL；主线 next action=`STOP`，不以 token 数差异挽救 |
| 已证明 Get/load，但 verified accounting 显示 `storage=0` 或未减少 uncached/prefill tokens | PASS | FAIL | FAIL；主线 next action=`STOP`，不进入 D1/T6/T7 |
| L3 control 的 prompt、model/tokenizer、decode、worker assignment 或状态不可比 | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE |

每次实际执行的 C0 outcome 只能是一个值。上表两种 `FAIL` 都要求停止主线并由 owner 决定是否针对真实原因重试；
`STOP` 是 next action，不是与 `FAIL` 并列写入同一个 `gate_outcome` 的第二个值。

“remote Get 但无 prefill reduction”只能说明路径可能到达，不能成为 shared-L3 value 的阳性。C 留有无法排除的旧对象、prefix byte/token hash 不同、或只见无关 Store object，均不能形成 A→C→B 的有效 join。

## 7. 冻结时点

| 可在租机前冻结 | 必须在 target runtime probe 后冻结 | 只能在 C1 baseline-only calibration 后冻结 |
|---|---|---|
| 两个 predicate、private Store-port boundary、fresh C/B discipline、deterministic-output rule、artifact/判定表、模型候选 revision | exact source/build identity、API serialization、page size/`N`、write policy/threshold 与 A sequence、request fields、model/tokenizer hashes、C0 segment、namespace semantics、stock cold/Get/load fields | C1 topology/same-AZ、S1 target coordinates、endpoint SLO、`delta`、remote-Get mass floor、load/knee、capacity axes、repeat budget、interval method |

## 8. 对抗检查

- **本地 cache 泄漏**：以 fresh PID/start、空 request ledger、独立 writable state、无 persistent cache 和 worker zero-segment 的合取证明；stock direct local metric 若存在则增强证据。
- **错误 prefix 等价**：同时核验 raw prompt hash、token-ID hash、page alignment 与 request config。
- **无关 Store object / C 遗留状态**：以 fresh C/unique keyspace、A 对 tested config-prefix/model KV objects 的 sole-writer、唯一 stock warmup-key 例外的 source/日志隔离证据、A Put terminal、相同 token hash 与 B Get/load 的 join 排除。
- **模型或 tokenizer 漂移**：A/B file hash、served model name 与 tokenizer identity 必须相同。
- **A/B 生命周期混用**：以 A exit、B fresh PID、无进程重叠和独立 writable state 证明；同一物理 GPU 的顺序复用不冒充 cross-GPU 证据。
- **TTFT-only 假阳性**：TTFT 不进入 predicate；token source accounting 与 B-cold no-L3 control 才有裁决权。
