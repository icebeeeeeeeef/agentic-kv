# G0 环境部署合同

> 状态：**OWNER-DECIDED DEPLOYMENT CONTRACT / NON-AUTHORITY / 无运行时证据**（2026-08-12）。
> 用途：记录首次目标 Linux CUDA C0 的最小物理边界、租机日检查与 C1 分界；它本身不授权租机、部署、改源码或开始 G0。
> 权威顺序：[PROJECT_PLAN.md](../project/PROJECT_PLAN.md) Gate/STOP > [STATUS.md](../../STATUS.md) 实际状态 > [TASKS.md](../../TASKS.md) > implementation contracts > decisions。

当前只有 pinned source/release identity 是 `SOURCE_VERIFIED`；目标 Linux build/API、external Store、A Put → cold B Get 和任何网络/性能现象均没有 runtime artifact。D18 取代 D17 对首次 C0 前置范围的裁决：先做 correctness-only C0，随后按真实 blocker 增量 harden，不预建云端实验平台。

## 1. 首次 C0 的唯一问题

```text
stock A Put terminal
  → fresh external C
  → locally-cold fresh B
  → fresh B-no-L3 control
  → RESTORE_PATH_PASS ∧ REMOTE_VALUE_SURVIVES
```

Docker/OCI、TTFT、容器重启、Store aggregate traffic 或人工摘要均不能替代 token-level oracle、B cold certificate、A→C→B join、fresh B-no-L3 control 和 deterministic output oracle。

本文件不处理 Kubernetes、Terraform、ACR/custom image、PD disaggregation、RDMA/GDR/NIXL、trace、hook、candidate 或大规模 benchmark。租机日 region、AZ、价格、库存、quota、image ID 和实例 ID 是当日输入，不能在文档中伪装为已验证事实。

## 2. 最小逻辑拓扑与物理边界

| 角色 | 必须满足 | 不要求 / 不可外推 |
|---|---|---|
| Worker A | stock pinned build；worker `global_segment_size=0`；达到实际 write condition 并取得 Put terminal | 不要求与 B 同时运行；不证明 production writer |
| Worker B-L3 | A 退出后创建的 fresh PID；空 request ledger、独立 writable state、无 persistent local cache；worker zero-segment | 不要求另一块物理 GPU；不证明 cross-GPU/multi-host |
| Worker B-no-L3 | 另一个 fresh PID；相同 request/config；L3 明确 disabled | 不与 B-L3 共享本地状态 |
| Store C | 独立 external Store lifecycle；fresh/unique keyspace；唯一 nonzero bounded L3 segment | master/metadata 可与 C 共置；不新增控制面 |

首次 C0 允许 A、B-L3、B-no-L3 在同一块兼容 GPU 上顺序运行。必须保存 A exit、后续 fresh PID、无进程重叠与独立 state 证据。该拓扑只支持 cross-worker-process restore claim。

C 与 worker 使用同一私有 VPC 的记录 endpoint；Store data port 不得向公网开放。C 或 worker 是否拥有受限管理公网入口，不影响 correctness，关键是数据面走私网且 Store port 不公开。same-AZ、延迟/吞吐和 NIC/CPU fairness 后置到 C1/性能阶段。

## 3. 租机前与租机后的严格分界

### 3.1 租机前必须物化

1. 内容寻址 input bundle：exact SGLang source、Mooncake wheel/source/build input、model、tokenizer、request template 与 checksums；target 待执行的 TCP/cold-isolation/topology command template 由独立 owner-reviewed runbook SHA 绑定，运行前必须核对并留证。
2. 单次 runbook：target admission probe、C start、A fixed trigger、A exit、fresh B-L3、fresh B-no-L3、raw capture、bundle/checksum 与 off-host copy。

OCI archive 或 OSS 可以是选定的传输实现，但不是 C0 correctness Gate；不要求 mutable registry、完整 OSS object re-list/readback、独立 collector/classifier、remote orchestrator、scheduler 或 C1 runner。目标 host 在使用前核对 input bundle checksum 即可防止输入漂移。

### 3.2 租机后、首个 request 前检查

- 输入 hash、SGLang/Mooncake build/API identity、model/tokenizer/config echo；
- actual cache implementation、page size、stock write policy/threshold 与最小 A trigger sequence；
- 一块支持目标 build/model 的 x86_64 CUDA/BF16 full-passthrough GPU；实际 UUID/driver/runtime；
- C 的 health/nonzero bounded segment、worker zero-segment、private TCP 与 Store-port exposure；
- A/B lifecycle 与 writable/persistent-state 隔离方法。

任何缺失均为：

```text
execution_status = BLOCKED_BEFORE_C0
RESTORE_PATH_PASS = NOT_EVALUATED
REMOTE_VALUE_SURVIVES = NOT_EVALUATED
```

它只说明该 host/release/配置没有进入实验，不是 C0 `FAIL`/`STOP`，也不是 shared-L3 premise 结论。

## 4. 平台、模型与容量

不在租机前冻结具体云实例 family。租机日只选择满足第 3.2 节且成本最低的完整拓扑：一台单 GPU worker host 即可，外加一台能提供目标 bounded RAM segment 的 C host。若一个 host 无法运行 pinned build/model，记录显式 blocker 后再换规格；不因“未来 benchmark 可能需要”预租双 GPU、更大 NIC 或额外节点。

首轮候选模型仍是 `Qwen/Qwen2.5-1.5B-Instruct` revision `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`、BF16。A/B 必须看见相同 model/tokenizer file hash。候选身份是 owner decision，不是 pinned SGLang compatibility 或 runtime evidence。

C0 shared prefix 的 `N` 在 target probe 后选择：`N mod actual_page_size = 0`，并且最小 A trigger sequence 能产生非零 Put/Get。没有 8K hard floor。decode 使用固定 deterministic greedy 参数并至少取得一个可比较 completion token；没有“恰好 32 token”要求。

C0 只需一个 nonzero bounded C segment。S3 的 `small`/`roomy` 容量必须等 C1 baseline-only calibration 后按 D14 合同冻结，不能为了首次 C0 预建容量矩阵。

## 5. C0 执行、证据与释放

执行顺序与判定完全服从 [C0 Restore Qualification Contract](G0_C0_RESTORE_QUALIFICATION_CONTRACT.md)：

1. fresh C / unique keyspace，A 是 tested config-prefix/model KV objects 的 sole writer；唯一例外是 source-proved、单独留证且不经过 `_tag_keys` 的 stock startup warmup key；
2. A 以实际 threshold 对应的最小固定请求序列取得 terminal Put；
3. A 退出，fresh B-L3 对 identical raw prompt/token hash 执行 Get/load；
4. fresh B-no-L3 执行 identical request；
5. owner 依据 raw identity/config/log/response、cold/join、token accounting 与 output hash 手工裁决两个 predicate；
6. 释放前生成 artifact inventory/checksum，复制到 off-host 持久位置，并验证复制后的 checksum。

首次 C0 不要求 automatic deadline、operator finalizer、`UPLOAD_COMPLETE/ABORTED` 状态机、quarantine、terminal marker、三角色 RAM prefix-isolation 或 retention policy。若 off-host copy 尚未核验，不释放持有唯一证据的实例；这是一条人工操作约束，不是平台建设授权。

## 6. C1 与 formal-cohort 边界

首次 C0 `PASS` 只提供 restore qualification。C1 必须：

```text
fresh cohort + fresh Store/worker state
  → redo full C0
  → finite X* source/runtime audit
  → baseline-only calibration and checksum freeze
  → S1
  → sticky-reuse S2/S3
```

C1 可以复用 runbook/launcher code，但不能复用 C0 实例状态、coldness、Store、keyspace 或 artifact 作为 eligibility。C1 的正式 GPU mapping、same-AZ、网络/Store baseline、paired-arm acquisition type 与重复预算在 treatment 前独立冻结；中断的 pair 为 `INCONCLUSIVE`，不得跨 cohort 拼另一 arm。

只有 C0 暴露真实 lifecycle/evidence blocker，或 C1 repeated/formal cohort 明确需要时，才从 D16 中选择最小 hardening：role-scoped access、finalizer、deadline/abort、quarantine、terminal marker 或 retention。未发生的风险不能一次性解锁整套控制面。

## 7. TCP 网络证据的阶段边界

首次 C0 raw bundle 只需保存：transport=`tcp`、逻辑角色、实际 private endpoints、Store-port exposure 检查和 A/B→C 连通性。它们用于证明请求能够走到指定 C，不是网络 benchmark。

C1/S2+ 只有在 endpoint fairness 或 pressure witness 需要时，才保存冻结方法下的 latency/throughput、NIC/CPU/queue 样本。NIC/CPU 既不是 `new_physical_put_bytes`，也不能单独证明 L3 write cost、capacity externality 或 admission 收益；最终裁决仍服从 token oracle 与 paired `Goodput@TTFT-SLO` interval。

## 8. RDMA scope gate

RDMA 当前被 canonical scope 排除，不能用于挽救 TCP 的 `FAIL`、`STOP` 或 `INCONCLUSIVE`。只有以下条件全部满足才可另行讨论：

1. TCP cohort 已有 retained `RESTORE_PATH_PASS` 与 `REMOTE_VALUE_SURVIVES`；
2. 已冻结的性能 cell 有可复核证据把主要 residual 指向 transport，而非 GPU/CPU/queue/Store 等解释；
3. D14 尚未以有效 STOP 收口方向；
4. owner 先修改 canonical scope/decision；
5. 新 RDMA cohort 独立通过 driver/NIC/GDR/Mooncake build preflight，并从依赖起点重跑。

满足条件只允许新讨论，不承诺实施 RDMA，也不能把 TCP/RDMA runs 交叉配对。

## 9. 当前未决与 claim 边界

| 项目 | 状态 | 合法处理 |
|---|---|---|
| input bundle + one-shot runbook/handoff | fail-closed r7 已本地物化并完成 owner review；bundle owner root=`207f866e2bbc83f96207d112a8d10730280fddd91422b59f02e7b858d9b7c477`，独立 runbook owner root=`577588c07b7cb7d5a593f5dd2b0d69a8d733a6c6cc898767374dc7a3b241b4ec`；租机后 C-host probe 已暴露并收窄真实 runtime blockers，尚未完成正式 admission | 继续按最新 root 重跑 C-host/worker admission；不把本地 checksum/test 或 C-host probe 写成 C0 evidence |
| region/AZ、价格、库存、quota、instance/image ID | 租机日 `UNRESOLVED` | 当日选择并记 manifest；same-AZ 不作为 C0 correctness Gate |
| host driver/runtime、build/API、page size、write threshold、GPU UUID | target runtime `UNRESOLVED` | 首个 request 前 probe；失败=`BLOCKED_BEFORE_C0` |
| C segment/private endpoint/Store-port exposure | target runtime `UNRESOLVED` | 首个 request 前 probe；失败=`BLOCKED_BEFORE_C0` |
| Put/Get、B cold、token/output oracle、off-host artifact | runtime `UNRESOLVED` | 仅 retained raw artifact 可升级具体 claim |
| C1 topology/X*/S1–S3 数值与 witnesses | ROADMAP / `UNRESOLVED` | fresh C1 baseline-only 阶段冻结 |

本合同不产生兼容、remote restore、token savings、网络瓶颈、性能或生产适用性结论。`DECIDED` 只代表 owner 选择；`SOURCE_VERIFIED` 只代表 pinned source 事实；runtime claim 只能由对应 retained artifact 更新到 [STATUS.md](../../STATUS.md)。
