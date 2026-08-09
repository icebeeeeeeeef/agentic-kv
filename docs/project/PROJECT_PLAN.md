# 多轮 Agent 负载下共享 KV Pool 的 L3 写入准入

> 文档性质：项目总体规划、证据合同与统一口径  
> 统一版本：2026-08-09
> 当前裁决：**Conditional Select（有条件立项）**  
> 当前 claim state：SGLang 接缝及 Mooncake `v0.3.12.post1` candidate source 为 SOURCE_VERIFIED；其 runtime compatibility 仍 UNRESOLVED。负载、探针、conditional ledger、hook 与策略均仍是 ROADMAP，尚无 IMPLEMENTED_UNVALIDATED 或 EXPERIMENTALLY_VALIDATED 的个人产出
> 本版不做时间排期。所有阶段按证据依赖排序，不按周数排序。
>
> 方法论关系：本计划是 [PROJECT_EVALUATION_SOP.md](PROJECT_EVALUATION_SOP.md) 在本项目上的具体化。SOP 约束选题、能力信号、证据与主张边界；本计划定义当前唯一机制、Gate、STOP 与实验合同。两者发生方法论冲突时，修订本计划而非降低 SOP 标准；实际完成状态仍以 [STATUS.md](../../STATUS.md) 为准。

---

## 0. 一页结论

### 0.1 项目正式口径

**规划期标题：**

> 多轮 Agent 负载下共享 KV Pool 的 L3 写入准入边界与策略评估

**只有通过 G3 的预注册 TARGET_HELD_OUT 在线正结果后，公开标题才升级为：**

> 多轮 Agent 负载下共享 KV Pool 的价值感知写入准入

G2 机会闸门通过后，VALUE_DENSITY 也只能成为 ROADMAP candidate，不能升级公开标题。项目最终可以得到性能正结果、仅流量/容量效率正结果，也可以得到“静态 second-hit 已经足够”的负结果。

### 0.2 一句话定义

在 SGLang HiCache + Mooncake shared L3 上，固定 L1/L2 的算法、容量、配置与 write policy，同时固定路由、远端淘汰和传输实现，只拥有一个在线决策：

> 一个已经完成 L1 → L2 备份的、满足前缀闭包的 KV 段，是否继续写入共享 L3：ADMIT_TO_L3 或 DROP。

多轮 Agent Prefix-DAG 负载生成器、KV evidence correlator / lifecycle trace collector 和 A/B runner 是回答这个问题的必需自建仪器。conditional admission ledger 只是 G2a 通过后才允许实现的候选拒绝工具，不是 G1、Runtime backbone 或 Flagship evidence closure 的默认交付物。

### 0.3 核心可证伪问题

在相同请求序列、worker 分配、L2 write-through、缓存容量和 Mooncake 后端下：

> 相比 ADMIT_ALL 与 calibration set 上调优后冻结的简单静态准入规则，利用决策时已经可见的复用价值信号，能否在预注册 TARGET_HELD_OUT Agent workload 上改善 Goodput@TTFT-SLO，或在 Goodput 不劣的前提下显著减少 `new_physical_put_bytes` 与无效写入？

如果最强静态规则已经吃掉全部稳定空间，项目必须承认“复杂策略不值得”，不能继续包装成优化成功。

### 0.4 项目的真实归类

这个项目不是“只研究 prefix cache”，也不是“重做 Mooncake”。

- **Prefix-DAG**：负载结构和复用语义。
- **SGLang HiCache**：生产级推理框架与分层 KV 生命周期底座。
- **Mooncake**：跨 worker 共享 L3 KV pool。
- **本项目拥有的机制**：L3 写入准入。
- **最终指标**：Goodput@TTFT-SLO、TTFT 分布、Mooncake KV payload Put/Get 字节、有效恢复与重算。

因此它面向的是 KV cache 存储组中的“引擎—共享缓存池边界、准入与容量效率”画像，而不是 CUDA 算子组、纯推理调度组或存储引擎内核组。

---

## 1. 本版取代哪些旧结论

旧文档把以下内容并列或融合成主线：

1. 本地 GPU/CPU prefix retention 或 victim ordering；
2. Mooncake metadata HA、快照、恢复和故障语义；
3. remote-recoverability-aware 本地淘汰；
4. 本地策略与远端恢复的双项目融合。

本版全部取消。原因不是这些问题没有价值，而是它们分别拥有不同的决策面、基线、故障模型和裁决指标。并行主张会让项目无法回答“收益到底来自哪里”。

本版统一为：

| 项目元素 | 本版地位 |
|---|---|
| 多轮 Agent Prefix-DAG | workload 和测量输入 |
| L1/L2 prefix cache | 固定 upstream 算法、容量、配置与 write policy |
| L3 shared KV pool | 被写入和读取的 upstream substrate |
| L3 写入准入 | 唯一 owned mechanism |
| conditional admission ledger | 仅在 G2a 通过后实现；用于给定 eligibility stream 的 action/payload 对账、敏感性分析与候选 rejection filter |
| 双 worker 在线实验 | 端到端裁决层 |
| Mooncake metadata HA | 明确排除 |
| L1/L2 淘汰策略 | 明确排除 |
| 远端淘汰策略 | 明确排除 |

以后若要重新引入被排除项，必须先证明“当前单决策项目为什么无法闭环”，不能仅以“它也很重要”为理由增项。

---

## 2. 术语与层级统一

### 2.1 缓存层级

本文统一使用：

| 层级 | 含义 | 本项目是否修改 |
|---|---|---:|
| L1 | GPU KV cache / HiRadix 中的设备侧缓存 | 否 |
| L2 | Host DRAM KV cache | 否，固定 write-through |
| L3 | Mooncake 提供的跨 worker 共享 KV pool | 只控制是否写入，不修改存储实现 |

如果后续部署中的 Mooncake Store 底层使用本地内存或其他介质，那是 L3 backend 的实现细节；本文的“远端”特指跨 worker 可复用的共享 L3 语义，不泛指任意 SSD 冷存储。

“固定 L2”不等于不同 treatment 下每一时刻的 L2 内容绝对相同：L3 hit/miss 会因果性地改变后续 L2 fill。这里固定的是 L2 算法、容量、配置、L1 → L2 write-through 和 eviction 实现，策略不得直接修改它们。

### 2.2 Prefix cache 与 KV cache

- **KV cache** 是被存储和搬运的数据。
- **Prefix cache** 是按 token prefix 组织、查找和复用 KV 的语义与索引方式。
- 项目使用 prefix 结构构造可复用 workload，但优化对象不是 radix tree 查找本身，而是共享 L3 的写入准入。

### 2.3 Offload

项目经过现有分层 offload 数据路径：

    L1 GPU → L2 Host DRAM → L3 Mooncake shared pool

但项目不自称“实现了 offload 系统”。它只在既有 L2 → L3 边界加入准入门。DMA、序列化、网络传输、远端落盘或内存管理均属于 upstream。

### 2.4 Admission 与 Eviction

- **Admission**：数据是否进入 L3。
- **Eviction**：L3 已有数据在容量压力下由谁被移除。

本项目只研究前者。不能把写入减少带来的容量污染下降叙述成“我实现了更好的远端淘汰”。

### 2.5 Value-aware 的含义

这里的“价值”不是未来真值，也不是不可解释的模型预测，而是：

> 决策时合法可见的复用可能性 × 可节省的 prefill 成本 ÷ 经对账校准的预期 KV payload 字节。

具体信号必须在 pinned source 上证明可获得；任何使用未来 next-use 的策略只能作为给定 eligibility stream 的条件式离线上界，不能成为在线候选或机会闸门。

---

## 3. Project Charter

| 字段 | 统一定义 |
|---|---|
| 观察对象 | 多轮 Agent workload 中长共享前缀、分支会话、工具结果插入与跨 worker 再访问 |
| 唯一决策 | ADMIT_TO_L3 或 DROP |
| 控制变量 | L1/L2 算法、容量、配置与 write policy，路由结果、Mooncake 容量与淘汰、模型、tokenizer、请求序列 |
| 主基线 | ADMIT_ALL 与调优后冻结的最强简单静态 L3 准入规则 |
| 主结果指标 | Goodput@TTFT-SLO |
| 机制指标 | KV payload Put/Get bytes、not-read-within-H、有效恢复字节、重算 token、adapter availability；L3 occupancy/eviction 仅作 conditional-ledger modeled 指标 |
| owned mechanism | L3AdmissionPolicy + SGLang 窄 hook |
| 自建仪器 | 必需：Prefix-DAG generator、trace collector/correlator、A/B runner；条件性：G2a 通过后的 conditional admission ledger |
| losing condition | 最强静态规则与候选差异落入噪声，或候选只在 calibration workload 上有效 |
| 非目标 | router、L1/L2 eviction、remote eviction、Mooncake 数据面、量化、稀疏化、RDMA/GDR、HA |

### 3.1 初始假设

多轮 Agent 负载可能同时包含：

- 高频复用的长 system/tool prefix；
- 只被消费一次的分支和工具结果；
- 局部 worker 上已热、但其他 worker 随后需要的 prefix；
- 大小和未来复用价值不成比例的 KV 段。

因此 ADMIT_ALL 可能产生写后未读和容量污染；纯 second-hit/frequency 阈值又可能错过“第一次跨 worker 复用就很值钱”的长前缀。

这是待验证假设，不是项目结论。

#### 候选收益因果链契约

在当前 owned action 与 Goodput@TTFT-SLO 目标范围内，选择性 L3 admission 只有两条允许的正向性能因果链。它们都是待验证候选，不是已成立事实：

| 候选链 | 从 action 到最终指标 | 通过所需的运行时证据 | 断裂条件 | 最大允许主张 |
|---|---|---|---|---|
| A：写成本 / 资源争用 | DROP 低价值写入 → 减少 `new_physical_put_bytes` 与实际 Put 工作 → 降低 backup queue、CPU、内存、NIC 或 Store 侧争用 → 改善 TTFT-SLO / Goodput | 同一 arm 的 decision → pre-collapse Put terminal → queue/dwell 归因闭合，且 paired 在线实验中相应压力与 Goodput/TTFT 同向变化；CPU/NIC 只作辅助诊断 | exists/dedup 已消除大部分新写、异步 Put 完全隐藏、资源宽松，或瓶颈位于 read/GPU/L2 | 中介证据和端到端结果同时成立时，只能声称固定测床上的局部写路径争用收益；若只有 bytes 下降，只能声称 payload efficiency |
| B：容量竞争 / 查询时可用性 | DROP 低价值写入 → 减少有限 L3 中的无效竞争 → 提高高价值 KV 的 query-time availability 与 useful Get → 减少 recomputed/prefill tokens → 改善 TTFT-SLO / Goodput | 固定 backend 与 remote eviction，在 roomy/knee/overloaded 容量坐标下，各 arm 自身 trace 的 query-time availability、useful Get、computed prefill/recompute 与 paired Goodput/TTFT 形成同向链条 | 容量宽松、对象几乎都高价值、`REMOTE_VALUE_SURVIVES` 不成立、固定 eviction/静态规则已吃掉空间，或 false negative 抵消收益 | 只能声称容量敏感的 availability/recompute 效应；在没有 SOURCE_VERIFIED eviction telemetry 时，不能声称观察到具体 occupancy、victim 或 eviction reason |

G2a 只要求其中至少一条获得运行时中介证据与端到端结果共同支持，不要求两条都成立。TTFT/Goodput 的变化不能单独识别中介机制；`new_physical_put_bytes`、CPU/NIC 计数器或 modeled occupancy 中任一单项也不能使性能链通过。两条链都不成立时，停止 Goodput/TTFT 策略方向；如果仅有可复现的 new-Put payload 节省，则只能进入 payload-efficiency 终局。

`ADMIT_ALL + fixed remote eviction` 是必须保留的强反例，而不是预设为弱支配选择性准入：只有在写成本隐藏、容量宽松，或 eviction 确实拥有不弱于 admission 的信息并能保护高价值对象时，才预期 ADMIT_ALL 最好或持平。普通 eviction “决策更晚”本身不证明它掌握更强信息。

#### D1 投资前的 stock survival sentinels

`REMOTE_VALUE_SURVIVES` 通过后，不立即开发 D1。先用未打任何本项目 patch 的 pinned SGLang + Mooncake 做两个
低成本投资筛查；它们不构成新的 Gate，也不复用 pre-launch research 已占用的 `R1/R2/R3` 名称：

| Sentinel | 固定问题与最小对照 | 继续 D1 的粗粒度信号 | 不能推出什么 |
|---|---|---|---|
| `WRITE_COST_SENTINEL` | zero-reuse / one-shot workload、roomy L3、相同模型/请求/worker，在 baseline service-curve knee 附近比较 stock L3 enabled 与 L2_ONLY；同时保留低负载 sanity cell | L3 arm 有可识别的 Store NIC/CPU 活动，且 paired-run 相对 Goodput 退化的预注册单侧区间下界越过物质性阈值 | backend 开/关同时改变 Put 与 lookup/miss，只能说明最坏浪费下的整条 L3 path cost 可见，不能归因到写成本；NIC/CPU 或 submitted bytes 单独不能证明 admission 会改善性能，也不能产生 `new_physical_put_bytes` claim |
| `CAPACITY_PRESSURE_SENTINEL` | backend 恒开，固定复用流 + one-shot fill 流；用两个 fresh、配置完全相同但 `global_segment_size` 为 roomy/small 的 external Store 运行 matched arms，并从 health/segment response 验证每个实际 segment | small arm 的 query-time storage availability/useful Get 下降、uncached/prefill tokens 上升，且 paired-run 相对 Goodput 退化的预注册单侧区间下界越过物质性阈值 | 只能证明容量敏感性；没有 SOURCE_VERIFIED eviction telemetry 时，不能声称观察到 occupancy、victim 或 eviction reason，更不能证明某个 admission policy 有效 |

两个 sentinel 都必须冻结 workload、offered load、arm 顺序、fresh Store 隔离、噪声/物质性阈值并至少做 3 个
paired repeats。`global_segment_size` 的配置合同绑定 pinned source；roomy/small 是否在目标 build 中实际生效，必须由
各自 fresh Store 的 runtime response 证明，不能假设原地改容量或仅凭配置文件成立。

在查看任一 treatment arm 结果前，必须先完成一份带 checksum 的 stock-sentinel preregistration，执行顺序固定为
`CALIBRATE_BASELINE → FREEZE_CONTRACT → RUN_PAIRED_ARMS`：

1. `CALIBRATE_BASELINE` 只允许查看 control/baseline 数据。`WRITE_COST_SENTINEL` 的 offered-load grid、低负载
   sanity cell 与 knee 选择规则必须只由 `L2_ONLY` service curve 决定，不能查看 L3-enabled 结果后移动 knee；
2. roomy/small 先按固定 workload 的 reusable working-set 与 one-shot fill 的**预声明 KV payload 估算方法**构造：
   small 应能容纳 reusable set、但不能同时容纳 reusable + fill，roomy 应能容纳完整 distinct set 加预声明安全余量。
   估算方法、余量和配置值在 treatment 前冻结，运行时仍须由 fresh Store response 验证实际 segment；该估算只证明
   intended capacity coordinate，不得包装成已观察到 occupancy、victim 或 eviction；
3. preregistration 必须冻结 TTFT-SLO、唯一主端点 `Goodput@TTFT-SLO`、paired-run 统计单元、效应方向、区间估计方法、
   工程物质性阈值 `delta`、最少/最多重复次数和停止规则。区间方法必须与顺序停止规则兼容；否则必须跑满冻结预算后
   只判定一次。最少 3 对只是执行下限，不自动赋予 null 裁决能力；
4. 定义相对退化 `d_write = (Goodput_L2_ONLY - Goodput_L3) / Goodput_L2_ONLY`，以及
   `d_capacity = (Goodput_roomy - Goodput_small) / Goodput_roomy`。只有压力/隔离/Store 活动等前提成立，要求的中介
   方向同时成立，且预注册单侧区间的下界大于 `delta`，对应 signal 才为 `true`；只有全部前提成立、实验精度足以使
   单侧区间上界小于 `delta`，才可记为有效 `false`；区间跨越 `delta`、达到最大预算仍无排除能力，或任一前提不可证，
   一律为 `INCONCLUSIVE`；任一 control Goodput 分母非正时相对退化无定义，同样不得裁决；
5. “p-value 不显著”“均值接近零”或“只有 3 对重复”都不能单独产生有效 `false`。冻结后若必须改变 workload、knee、
   容量、阈值或统计方法，应创建新 preregistration 版本并保留旧结果，不能静默覆盖后重跑。

preregistration 模板见
[experiments/manifests/g0-stock-sentinels-preregistration.example.json](../../experiments/manifests/g0-stock-sentinels-preregistration.example.json)。

这两个实验只是 admission-specific instrumentation 的**投资筛查**：至少一个按预注册区间规则成为 `true`，才自动继续
D1/trace/hook；即使如此也不等于任一 admission 策略获益。若两项在已确认的 knee/capacity-pressure 坐标下都以区间
上界低于物质性阈值成为有效 `false`，则 Goodput/TTFT 主线在实现前 STOP；此时只能保留 shared-L3 characterization 与方向筛查负结果，不能称为
Runtime backbone（R）或 Flagship evidence closure（F），也不能为了展示工程量自动开发 D1/hook。

双 null 后的唯一例外由 [D12](DECISIONS.md#d12--两个-stock-sentinel-有效-null-时在实现前-stop-payload-例外分两级授权)
约束：owner 必须在 D1 结果未知时另行冻结真实 payload/resource 目标、资源预算、物质性判据与有界的 observation-only
证据计划；第一次授权只允许 D1 pre-collapse observation 和完成 stock payload 归因所需的最小 opaque correlation，
不允许 behavior hook。只有该 artifact 证明超过阈值、可映射回资源目标的 new-Put 与写后未读浪费，才进行第二次
owner review 决定是否解锁最小静态 hook。没有这份 resource-objective record 时，双 null 直接按 pre-implementation
STOP 收口。无法证明负载拐点、实际 segment size、远端读来源或公平对照时，结果只能是 `INCONCLUSIVE`，不能
当成“无机会”。

### 3.2 三层完成定义

项目不以“调出一个更好的 threshold”作为完成条件。完成物分三层，后层不是前层的自动推论：

| 层 | 名称 | 最小交付 | 不意味着什么 |
|---|---|---|---|
| R | **Runtime backbone** | 在真实 SGLang→Mooncake 路径上，独立 trace-only correlation、最小 fail-open admission seam、all-or-none closure 与生命周期 oracle 都有 focused test 和可复现 run artifact；A Put→cold B Get 能被路径真值解释，且 stock restore 确实替代非零 prefill | 不意味着 G0 已完整通过，更不意味着某个策略有效或有性能收益 |
| F | **Flagship evidence closure** | R 层已经满足，且 G0/G1 的 required artifacts、workload/trace、在线机会裁决与明确 Gate ruling 齐全；若 G2a 通过，才额外要求 G2b conditional ledger artifact | 不意味着 VALUE_DENSITY 必须存在，也不意味着可升级公开性能标题；D1 前的方向筛查 STOP 不属于 F，G2a STOP 也不要求为了补交付物实现 ledger |
| P | **Optional policy-positive** | 仅在 G2a 证明可行动 residual 后，实现最简单候选并经 G2b/G3 的 TARGET_HELD_OUT 在线裁决 | 不意味着 runtime backbone 的复杂度来自该 policy，失败时不得反向否定已完成的工程证据 |

R 层是防止项目退化为“一个 `decide()` 函数 + 参数扫描”的最低工程线：删除 benchmark/分析脚本后，审查者仍必须能看到 upstream patch series、focused tests、异步终态 oracle、trace schema 和 stock/trace/forced-action 对照。R 层的实现证据可使对应组件成为 `IMPLEMENTED_UNVALIDATED`；只有每个具体 Gate 场景有 retained runtime artifact 才能升级该场景的 claim，D10 的真实 failure 缺失仍会使完整 G0 结论为 `INCONCLUSIVE`。

R 是“若要称为 runtime flagship，最低必须完成什么”，不是无条件施工承诺。若 D12 的双-null STOP 在任何 owned
patch 前触发，项目应诚实保留方向筛查 artifact 并停止或重选；不能用“负结果也有价值”把未达到 R 的结果升级为 F。

### 3.3 预注册的判断与剪枝顺序

项目深度来自可反驳的工程选择，不来自候选数量。执行必须按下列 A→B→C 顺序留下证据：

| 判断 | 候选与已选项 | 为什么这样剪枝 | 何时翻案 |
|---|---|---|---|
| A：behavior seam 放在哪里 | L1→L2 前 / **L2 ack 后、`write_storage` 前** / Mooncake Put 后 | 前者污染 L2 生命周期，后者已支付 L3 成本；中间 seam 是唯一只改变 L3 admission 的位置 | pinned runtime 证明该 seam 无法保持 L2 或 async 不变量，则 STOP，不迁移到其他层 |
| B：先改变行为还是先取得路径真值 | 只靠 source / **trace-only 先行** / 直接加 behavior hook | source 不能证明异步终态与 physical-object attribution；先加行为会把观测回归和机制回归混在一起 | trace-only 不能通过 non-interference，就停止 trace/payload 分支，不用 policy 绕过 |
| C：是否值得复杂策略 | ADMIT_ALL / SECOND_HIT / STATIC_FREQ* / **仅在 G2a 后的 VALUE_DENSITY** | 先证明 shared L3、ADMIT_ALL waste 和静态规则 residual，再允许复杂候选；静态规则胜出就是有效负结论 | G2a residual 不达预注册阈值，删除 VALUE_DENSITY，不进入 G2b/G3 候选开发 |

### 3.4 工程最低交付与反向删除测试

R 层必须同时满足以下最小所有权，不允许以 policy 参数实验替代其中任一项：

1. **路径实现**：独立 trace-only patch 在不改变 key、队列、重试、Put/Get、输出或 cleanup 的条件下，关联 observation/operation/batch/attempt/object terminal；D1 的 pre-collapse Mooncake observation 另行证明 non-interference。
2. **行为实现**：在已验证 trace 的同一 source seam 上，实现 `ALWAYS_ADMIT`、`ALWAYS_DROP` 与 `POLICY_ERROR_FAIL_OPEN`，且 DROP 不创建 L3 async state。
3. **正确性实现**：完整 group 的 all-or-none closure、success/dedup/race/fail-open/shutdown-detach 终态和真实 failure 的可得性都写入 scenario oracle；不可得 failure 只能留下 `INCONCLUSIVE`。
4. **可审查实现**：[patch provenance](../../patches/README.md)、focused tests、manifest 和原始事件可定位到固定 upstream SHA；不把 upstream shared cache、transfer 或 restore 计为 owned code。`PLANNED` series 只固定未来补丁边界，不能当作 patch 或实现证据。

反向删除必须至少回答：

- 删除 behavior hook：`ALWAYS_DROP` 的无 L3 operation/queue/protection/Put 性质消失，路径退回 upstream always-write；
- 删除 trace-only patch：serving 仍可运行，但不能再把任何 decision→physical terminal 数字作为证据；
- 删除本项目全部 patch：stock A→Mooncake→cold B restore 仍成立，明确 shared pool/transfer/read lifecycle 属于 upstream。

这些是 ownership oracle，不是要求为了展示复杂度另造插件框架或第二数据面。

---

## 4. 数据路径与因果边界

### 4.1 在线路径

    固定请求与 worker assignment
                │
                ▼
       SGLang prefix lookup / scheduler
                │
          L1 GPU cache
                │
       upstream L1 → L2 backup
                │
       L2 DMA completion acknowledged
                │
                ▼
       [唯一 owned hook]
       ADMIT_TO_L3 | DROP
          │               │
          ▼               └── 保留 L2，不创建 L3 写入状态
    upstream Mooncake Put
          │
          ▼
    shared L3 pool / later Get

读路径、remote lookup、Mooncake Get 和恢复后的继续执行保持 upstream 原样。

### 4.2 为什么 hook 必须在这里

如果在 L1 → L2 之前决定，策略会同时改变 L2 命中与 L3 写入，无法归因。

如果在 Mooncake Put 之后再过滤，已经支付传输和写入成本，失去 admission 的意义。

因此唯一允许的接缝是：

> L2 备份已经完成、即将调用 L3 write_storage 之前。

DROP 必须满足：

- L2 数据仍然可用；
- 不进入 backup queue；
- 不创建 ongoing_backup；
- 不增加 protect_host；
- 不调用 Mooncake Put；
- 不改变读路径、L2 eviction 实现或配置；不要求不同 treatment 的 L2 内容和 eviction event sequence 相同。
- policy 本身异常时 fail-open 为 ADMIT_TO_L3，不能让实验机制破坏 serving 正确性。

---

## 5. Pinned Source 与源码接缝

### 5.1 固定版本

首轮事实验证固定在 SGLang commit：

**b058dc910619c9d4bce9e9e24117104ffc491fa6**

Mooncake `v0.3.12.post1` candidate 的 exact source commit 已固定为
`6041a609a8c3af35e778f70db344f145c2914980`（SOURCE_VERIFIED）；其 target-Linux wheel/build identity、
API/build probe 与与该 SGLang adapter 的 runtime compatibility 仍 UNRESOLVED，必须在 G0 部署时与镜像/二进制 hash 一并记录。不得只写“最新版”，也不得把 tag/source audit 误写成 runtime compatible。

首轮使用普通 dense model，并固定：

- Unified Radix Tree：关闭；
- TP / PP / DP / DCP：均为 1；
- 模型、tokenizer、page size、L1/L2/L3 容量：写入 manifest。

未经重新做 source audit，不把其他 commit 的行为当成本版事实。

### 5.2 已定位的写路径

在 pinned commit 上，待验证的窄路径为：

    _inc_hit_count
      → write_backup
      → _finish_write_through_ack
      → write_backup_storage
      → HiCacheController.write_storage
      → backup thread
      → MooncakeStore.batch_set_v1

推荐 hook 位于 HiRadixCache.write_backup_storage 内：完成 keys、host_indices 与 prefix_keys 构造之后，调用 HiCacheController.write_storage 之前。此时 L2 DMA 已 ack，但尚未创建 StorageOperation。

这里的“唯一 hook”专指唯一 **behavior-changing seam**。为了把异步 backend 结果关联回 prospective seam 和后续 admission decision，纯观测 instrumentation 允许最小触及：

1. 在 prospective seam 生成 opaque run_id / observation_id；behavior patch 完成后才在同一记录追加 decision_id；
2. 将 opaque ID 随 StorageOperation 传播，不参与 queue、batch、retry 或读写语义；
3. controller 形成 batch 时生成 attempt_id，并记录 batch_id → operation/logical keys；
4. adapter 记录 batch_id / attempt_id → physical keys、buffer_size 与逐 object result；
5. collector 通过这些 ID 做确定性 join，而不是依赖 wall clock 或仅靠 key 猜测。

如果不修改 StorageOperation 接口，也必须在 controller 建立等价的 batch correlation map。无论采用哪种方式，instrumentation patch 与 admission policy patch 要分 commit、分测试，证明 trace ID 的存在不会改变运行行为。

首轮 source audit 必须逐项确认：

1. callback 的粒度是 node、page 还是连续 segment；
2. 能获得哪些在线合法信号；
3. payload 的逻辑字节和实际 Mooncake buffer 字节；
4. DROP 是否完全绕开 L3 状态；
5. 异步 ack、引用保护和失败回调是否保持配对；
6. remote lookup 的前缀闭包要求。
7. sequential dedup、跨 worker race 与 Put failure 如何进入 trace；固定上游未实现 partial success，不把它误写成已覆盖语义。
8. observation_id（及 behavior patch 后的 decision_id）/ batch_id / attempt_id 如何从 seam 传播到 adapter result。

### 5.3 运行时正确性不变量

1. **L2 不变量**：admission 不改变 L2 DMA ack、CPU cache 可用性、write-through、refcount 或 eviction 实现。
2. **upstream 等价不变量**：ALWAYS_ADMIT 的 keys、host indices、顺序、完成结果与 cross-worker hit 行为必须和未打 patch 的 pinned commit 对齐。
3. **异步生命周期不变量**：成功、sequential dedup、two-writer race、policy exception fail-open 与 shutdown/detach 后，queue、ongoing_backup、host protection 与 buffer reference 都回到基线。若没有真实、非侵入式 failure evidence，failure coverage 只能是 `INCONCLUSIVE`，不得报告 `G0-RUNTIME VALIDATED`；固定上游未实现 partial success，不能用 mock 将它包装成已覆盖语义。
4. **key-space 不变量**：两个 worker 使用相同 model/tokenizer revision、served model name、page size、tenant、extra_backend_tag 与存储配置；不同 run 隔离状态。
5. **serving correctness 不变量**：admission 只影响是否产生 L3 副本；固定解码下生成 token、请求成功性和 L1/L2 命中正确性不变。

### 5.4 前缀闭包不变量

remote prefix lookup 会在第一个缺失 page 处停止。因此策略不能制造：

> ancestor 被 DROP，但 descendant 单独写入、实际永远不可达的 prefix hole。

G0 的最小实现采用以下规则（[D9](DECISIONS.md#d9--g0-的-prefix-group-一律-all-or-none)）：

- admission 只能作用于从 root 或“本次操作可证明已驻留”的 anchor 开始、含有有序 logical pages 的完整连续 prefix group；
- 一个 group 只能整体 `ADMIT_TO_L3` 或整体 `DROP`；G0 不实现 group 内首个 DROP 后的逐页 suffix 规则；
- 如果 callback 只给出一个 descendant suffix，且无法从同一次操作证明完整 group/ancestors 可达，则整体 DROP；不能仅因“整个 suffix 一起写”就假设 closure 成立；
- 不为了逐 page 精细 admission 新增远端 metadata RPC；
- 将后续 upstream-induced unavailability 与 policy-induced hole 分开；只有存在 SOURCE_VERIFIED telemetry 时才进一步归因为 remote eviction，否则只报告 query-time unavailable。本项目只要求 admission 时不主动制造新 hole。

若 pinned source 无法在不增加新控制面的情况下满足这个不变量，直接触发 STOP，不扩展成“顺便实现一套远端目录”。

### 5.5 一级来源

- [SGLang HiCache design](https://docs.sglang.io/docs/advanced_features/hicache_design)
- [HiRadixCache pinned source](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/hiradix_cache.py)
- [CacheController pinned source](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/managers/cache_controller.py)
- [MooncakeStore adapter pinned source](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/storage/mooncake_store/mooncake_store.py)
- [KV events pinned source](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/disaggregation/kv_events.py)
- [MooncakeStore deployment README](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/storage/mooncake_store/README.md)
- [SGLang HiCache roadmap issue #21846](https://github.com/sgl-project/sglang/issues/21846)

源码与 roadmap 只能证明问题域真实、接缝存在；不能证明本候选策略有效。

---

## 6. Ownership Contract

### 6.1 我亲手拥有的代码

| 模块 | 必须由项目实现 | 删除后发生什么 |
|---|---|---|
| Prefix-DAG workload generator | 生成确定性的多轮、分支、工具结果插入与跨 worker reuse trace | 无法重复同一 workload，也无法做公平 A/B |
| KV evidence correlator | 复用 upstream L1/L2 事件，只补齐 decision → StorageOperation → batch → adapter result 的 correlation 与缺失 L3 观测 | 无法解释“为什么赢或输” |
| Mooncake payload-byte validator | 在 adapter 展开 physical K/V object 后，对账 Put/Get buffer_size 与完成结果 | 只能报估算字节，失去裁决权 |
| Conditional admission ledger（仅 G2a PASS 后） | 对具名 source-run eligibility stream 回放 action、reason code、payload、fixed-H demand coverage 与 modeled sensitivity | 失去 G2b 的条件式对账、阈值 frontier 与 candidate rejection filtering；不影响 G1 仪器可信、G2a 在线机会裁决或 G3 在线因果裁决 |
| L3AdmissionPolicy | 实现 ADMIT_TO_L3 / DROP 与静态基线 | 删除后退回 upstream always-write |
| SGLang narrow behavior hook | 在固定 L2 后调用 policy，并保持异步状态正确 | candidate 无法在线生效 |
| A/B runner + manifest | 固定版本、配置、顺序、清池和重复实验 | 结果不可复现 |
| Analysis + evidence pack | 生成原始数据、图表、负结果和 commit 对应关系 | 简历数字无法追溯 |

### 6.2 Upstream 提供的能力

- SGLang 请求执行、scheduler、radix tree 与 prefix match；
- L1 GPU cache 与 L2 Host cache；
- L1 → L2 数据搬运和异步完成协议；
- remote lookup 与 L3 restore；
- Mooncake Put/Get、传输、存储、容量与淘汰；
- 模型执行、prefill、decode 和基础 metrics。

叙事必须使用“集成、插入准入门、测量、验证”，不能使用“实现了 SGLang 分层缓存”或“实现了 Mooncake KV pool”。

L1/L2 原始生命周期、event 产生和实际数据运动仍属于 upstream；本项目只拥有 collector、跨异步层 correlation、缺失的 L3 adapter instrumentation 与分析 schema。

### 6.3 Ownership 删除测试

本节的具体 R 层 oracle 以 [3.4](#34-工程最低交付与反向删除测试) 为准。候选策略若存在，另须将 decision 固定为 `ADMIT_ALL`：选择性收益消失且退化为 stock write-through + Mooncake 行为。

如果删除一小段阈值判断后项目几乎没有任何 owned depth，说明 R 层 tracer/hook/lifecycle oracle 没有完成；这不是增加 policy 框架的理由。删除 Mooncake 后 shared L3 消失；删除 SGLang HiCache 后 L1/L2 生命周期与 L3 lookup 消失；删除本项目后只应消失“选择性 L3 admission + 可复现实验和证据”。

---

## 7. Workload Contract

### 7.1 为什么用参数化 Prefix-DAG

真实 Agent 系统的动态决策会使不同策略走向不同工具分支，破坏 A/B 的同输入条件。首轮项目不运行“会被策略影响的真实 Agent 大脑”，而是生成固定 Prefix-DAG 和固定 token 序列。

这不是弱化真实性，而是获得因果裁决权：

- 相同 arrival timestamps；
- 相同 request/token sequence；
- 相同 worker assignment；
- 相同 branch structure；
- 唯一差异是 L3 admission。

真实 trace 以后只用于外部效度验证，不替代受控 workload。

### 7.2 必须覆盖的结构

生成器至少支持：

1. 长共享 system prefix；
2. 多轮历史持续增长；
3. 同一父 prefix 的多分支会话树；
4. 工具调用结果插入造成的长短不等分支；
5. 跨 worker 再访问；
6. 热 prefix、一次性 prefix 与周期性复用混合；
7. 固定并发与可控 offered load。

### 7.3 主要参数轴

| 参数轴 | 需要回答的问题 |
|---|---|
| 复用价值分布 | 高价值 prefix 是否与简单频次排序一致 |
| 跨 worker reuse 比例 | shared L3 何时真正有用 |
| L3 容量 / working-set 比 | admission 在何种压力下才产生差异 |
| prefix token 与 KV payload 字节 | 大 prefix 的收益是否覆盖写入成本 |
| reuse distance | second-hit、recency 与未来复用何时失效 |
| offered load | admission 收益能否传导到 TTFT SLO |
| branch fan-out / depth | Agent 树结构是否增加写后未读 |

参数空间用于寻找边界，不用于穷举所有组合。最终只保留能区分机制的代表性坐标。

### 7.4 Manifest

每次运行必须保存：

- SGLang/Mooncake commit；
- 模型与 tokenizer hash；
- workload seed 与 DAG 描述；
- worker assignment；
- cache page size 与三级容量；
- policy 名称、参数与参数来源；
- offered load 与 TTFT SLO；
- 清池方式、运行顺序与重复编号。

---

## 8. Trace 与测量合同

### 8.1 逻辑事件

至少记录：

- request/session/turn/worker 标识；
- parent prefix 和 token length；
- L1/L2/L3 lookup、hit、miss；
- L1 → L2 backup 完成；
- eligible write group、admission decision、输入信号和 reason code；
- StorageOperation enqueue、Mooncake Put submitted、dedup/race、Put/Get terminal、失败与耗时；
- restore token/byte；
- 因 miss 而重算的 token；
- TTFT、TPOT、完成状态。

不得记录用户明文 prompt；prefix 使用不可逆 hash 与长度描述。

### 8.2 Mooncake KV payload 字节

ADMIT 不等于实际写入。证据链必须完整区分：

    eligible
      → ADMIT / DROP
      → StorageOperation enqueued
      → Put submitted
      → dedup / race / partial result
      → Put completed

在 MooncakeStore.batch_set_v1、batch_get_v1 与 batch_exists 中，于 _batch_preprocess 展开 logical page 之后记录：

- 由 opaque ID 传播得到的 run、worker、request、decision、batch、operation 与 attempt 标识；
- logical storage key 和展开后的 physical K/V keys；
- 每个 physical object 的 buffer_size；
- 每个 object 的 adapter-visible success / exists / missing / failure；
- worker-local monotonic sequence 与开始/结束时间。

要将“新物理 Put”与 race 区分，另在 Mooncake `OBJECT_ALREADY_EXISTS -> success` 归约前由独立
trace-only observation patch 记录原始原因码。该 patch 的授权、不可变行为边界与停止条件由
[D1](DECISIONS.md#d1--保留-new-put-payload-指标并授权最小观察-patch) 固定；其未实现或未通过
non-interference proof 时，不能产生 new-Put payload claim。

至少保留以下量，不能混用：

| 字段 | 含义 |
|---|---|
| logical_kv_bytes | 按 tensor shape/dtype 计算的 KV 逻辑大小 |
| eligible_payload_bytes | 符合 upstream L3 write eligibility 的 payload |
| admitted_payload_bytes | policy 决定 ADMIT 的 payload |
| submitted_payload_bytes | 去重检查后实际提交 Put 的 payload |
| new_physical_put_bytes | 仅由 pre-collapse 原因码确认、确由当前 writer 新建物理 object 的 payload |
| race_existing_bytes | precheck 未见对象、但 Put 在归约前确认竞争对象已存在的 payload |
| exists_skip_bytes | precheck 已存在而未提交 Put 的 payload |
| failed_put_bytes | Put 未获得成功或 race-existing 终态的 payload |
| completed_get_bytes | 后端确认成功的 Get payload |
| dedup_or_race_skipped_bytes | `exists_skip_bytes + race_existing_bytes`；仅作派生汇总，不能替代两者 |

batch_exists 只产生可用性事件，数据 payload bytes 记为 0。简历中的“减少写入 X%”默认指
`new_physical_put_bytes`；如果只能拿到 adapter-visible offered/submitted bytes，必须明确降级措辞。
不得把一个未区分 race 的 success 汇总命名为 `completed_put_bytes`。

这些量是 adapter trace 或 D1 pre-collapse observation 可归属的 **KV payload bytes**，不是 NIC/wire bytes：它们不含协议头、metadata、复制和重试的全部网络开销。不得把它们包装成“真实网络流量”。

### 8.3 派生指标

- useful restored bytes：被后续成功 Get 且实际避免 prefill 的数据；
- not-read-within-H bytes：成功写入后，在预注册 horizon H 内没有 useful Get 的 payload；
- closed-DAG unused bytes：仅当 workload DAG 与 reuse schedule 完整闭合、测量后包含 drain phase 时，才把全程未读写入计为 unused；
- recomputed tokens：本可由 L3 命中避免、但因缺失而重算的 token；
- policy overhead：决策 CPU 时间、队列等待和额外 metadata；
- SGLang backup queue depth / dwell time；
- Put/Get latency、错误、dedup/race 与 partial result；
- p50/p95/p99 TTFT 仅作为诊断，不能挑一个最有利分位数充当唯一结论。

测量窗口尾部仍可能在未来被读的对象是 right-censored：从 unused numerator 中排除，或单独做 survival-censored 报告。H、warm-up、measurement、drain 与尾部归属必须在运行前冻结。

写放大可定义为：

    new physical Put payload bytes / useful completed L3 Get payload bytes

分母为 0 时分别报告两个绝对值，不制造无意义比率。

### 8.4 Mooncake 内部状态的观测边界

当前已定位的 adapter seam 只能证明 Put/Get/exists 请求与逐 object 结果，不能直接看到 Mooncake master 内部的精确 occupancy、eviction time、victim reason 或 wire traffic。

因此本版默认：

- 在线只报告 adapter-visible Put/Get、query-time availability、queue 和 SLO；其中 new physical Put
  仅在 D1 observation patch 已通过 non-interference proof 后报告；
- 一次 exists=false 只称“查询时不可用”，不能仅凭它断言发生 eviction；
- occupancy/eviction 只在 conditional ledger 中标为 modeled；
- 若 G0 后续找到并 pin 官方 Mooncake metrics/event API，才可新增一列 SOURCE_VERIFIED upstream telemetry；在此之前不以精确在线 eviction 作为验收条件。

---

## 9. Replay 的职责与边界

### 9.0 Activation gate

本章冻结的是 **G2a 通过后** conditional ledger 的最小合同，不授权提前实现。G1 只验收真实运行所需的
workload replayability、trace/correlation、non-interference、payload reconciliation 与 workload split；它不要求
policy replay、modeled resident set 或 future-aware upper bound。只有 G2a 用各 arm 自身的在线 lifecycle trace
证明 shared L3 价值、可行动浪费与静态规则 residual 后，才允许实现本章工具并进入 G2b。

Prefix-DAG generator 的确定性重放和在线 trace 的解析/关联不是 conditional ledger，不能因本章后移而从 G1
删除。反过来，也不能以“先做工具更方便”为由，在 G2a 前构建 policy simulator 或 conditional resident-state model。

### 9.1 Replay 实际是什么

本项目不实现完整 L1/L2/L3 闭环 simulator。Replay 的准确名称是：

> 给定某个具名 source run 的 observed eligible-candidate stream，对 L3 admission action 与 KV payload 做条件式账本回放。

它可以：

- 在同一 eligible stream 上运行 policy interface，检查 action、reason code 和阈值 frontier；
- 计算 conditional admitted/dropped/submitted payload；
- 用冻结的未来 request/prefix demand annotation 计算 conditional useful-demand coverage 与 not-read-within-H；
- 在明确标为 modeled 的容量/eviction 规则下做 sensitivity；
- 用多个 source arm 的 eligibility stream 检查候选是否对 source-run 选择极度敏感。

它不能把某一 arm 的 eligibility stream 当作其他 policy 的真实反事实。Admission 会改变 L3 hit、后续 L2 fill、recompute 和新的 write eligibility；因此 replay 不输出跨策略 causal hit、recompute、TTFT 或“真实最优策略排序”。

### 9.2 Replay 不做什么

Replay 不模拟完整 GPU scheduler、CUDA 执行、真实网络竞争或最终 TTFT。因此：

- replay 只做 action/payload 正确性、条件式机会描述与候选 rejection filtering；
- 任何端到端性能主张必须由双 worker 在线实验确认；
- replay 条件账本即使显示候选更好，也不能证明候选可上线或优于 STATIC_FREQ*；
- online A/B 与每个 arm 自己演化出的 eligibility/lifecycle trace 是唯一策略裁决；
- 若 Mooncake eviction 规则/对象粒度无法 source-pin 并用 microcase 校准，replay 只能裁决无限容量或 no-eviction 条件下的 payload ledger；所有 bounded-capacity occupancy、eviction 与 conditional demand coverage 降级为 modeled sensitivity，不得充当 G2 的生产事实。

### 9.3 正确性验证

- 用手工 tiny eligible stream 验证每个 action 与 payload 变化；
- 对很小的有界 conditional ledger 使用 exhaustive oracle 验证实现；
- 对每种 policy 独立推进 modeled capacity/eviction state machine；
- 用 no-eviction microcase 对齐 runtime 的 action、eligible/submitted/new-physical bytes（D1 可用时）与 dedup；
- 只有获得 SOURCE_VERIFIED eviction 规则或 telemetry 后，才要求 bounded-capacity replay 与 runtime 对齐；
- 每份 eligibility stream 必须记录 source policy/run，不能隐去 treatment 来源；
- 不把 conditional exact/upper bound 写成系统级“最优策略”。

### 9.4 Future-aware upper bound

上界可以读取给定 eligibility stream 的未来 next-use，只用来回答“在这个条件式账本上最多还有多少 action/payload 空间”；它绝不能：

- 进入在线候选；
- 充当 G2 机会闸门或 G3 的公平击败基线；
- 被称为可部署 oracle；
- 向在线策略泄露 TARGET_HELD_OUT 的 future。

---

## 10. Policy 与 Baseline Ladder

### 10.1 统一接口

    decision = policy.decide(segment, online_context)
    decision ∈ {ADMIT_TO_L3, DROP}

online_context 只能包含决策时已经存在且能从 pinned path 合法获得的信息。首轮优先使用：

- 当前累计 hit/reuse count；
- 距上次访问的 age/recency；
- continuous prefix length；
- 经 byte reconciliation 校准的 expected KV payload bytes；
- 由独立 calibration 得到的 prefill-cost lookup table。

不新增远端查询，不运行预测模型，不依赖未来请求。

### 10.2 因果基线梯子

所有因果 A/B 都固定 L2 write-through：

| 层级 | 策略 | 作用 |
|---|---|---|
| S0 | L2_ONLY | 系统级参考：完全关闭 L3 lookup/write，回答 shared L3 本身是否值得 |
| B0 | L3_ENABLED + DROP_ALL | 同一 treatment 下界：保留 L3 lookup 与 hook 固定开销，但不产生新 Put |
| B1 | L3_ADMIT_ALL | 同一 hook 的全写基线，暴露写放大和污染 |
| B2 | L3_SECOND_HIT | 在同一 hook 内只按二次访问写 L3 |
| B3 | STATIC_FREQ* | 在 calibration set 调优、随后冻结的最强简单阈值 |
| C1 | VALUE_DENSITY | 条件候选，仅在机会闸门通过后实现 |
| A1 | C1 去掉关键 signal 或 threshold frontier | 多信号候选做 deletion；单阈值候选只画 frontier，不伪造 ablation |
| U1 | conditional future-aware upper bound | 仅检查给定 eligibility stream 的 action/payload 空间，不做系统级因果基线 |

星号表示参数只能在 calibration workload 上选择，不能看 TARGET_HELD_OUT 结果后回调。

### 10.3 Stock selective 的正确地位

SGLang stock write_through_selective 可以作为**外部整系统参考**，但不能混入 L3-only 因果基线：它不是本项目“固定 L2 write-through 后再做 L3 gate”的同一 treatment，会改变上游 L2/L3 写入语义。

必须明确区分：

- L3_SECOND_HIT：本项目在固定 L2 后实现的可归因基线；
- stock write_through_selective：upstream whole-system reference。

### 10.4 条件候选

只有 G2a 在 STATIC_FREQ* 自己的在线 lifecycle trace 中测出超过噪声的可行动 residual，才进入最简单候选：

    value_density
      = estimated_reuse_probability(hit_count, recency)
      × calibrated_saved_prefill_ms(prefix_length)
      ÷ validated_expected_payload_bytes

当 value_density ≥ frozen threshold 时 ADMIT，否则 DROP。

约束：

- probability 可以是单调 bucket/table，不引入 ML；
- prefill cost curve 独立测量并冻结；
- threshold 只在 calibration set 选择；
- 决策以 prefix-closed segment 为单位；
- 若 STATIC_FREQ* 已经足够，停止，不为了“有算法”继续堆复杂度。

---

## 11. 部署口径

### 11.1 最小可信拓扑

推荐三个逻辑节点：

| 节点 | 角色 |
|---|---|
| GPU Worker A | 产生或写入可复用 KV |
| GPU Worker B | 清空本地缓存后，从 shared L3 恢复同一 prefix |
| CPU Storage Node | Mooncake master/metadata + 注册非零、固定容量 storage segment 的 external store service；首轮使用 TCP |

workload driver 可与 CPU Storage Node 共置；若观测到干扰，再拆为第 4 台。第 5 台不是默认需求。

运行约束：

- A、B 使用相同 pinned SGLang/Mooncake/model/tokenizer 配置；
- 显式设置 SGLANG_ENABLE_UNIFIED_RADIX_TREE=0，并从启动日志断言实际 cache implementation 是 HiRadixCache；
- 每个 worker 固定 TP=PP=DP=DCP=1，使用 dense、非 hybrid cache 模型；
- A、B 的 Mooncake global_segment_size=0，避免把 worker host memory 误算成 shared L3；
- C 必须实际注册非零、bounded storage segment；只启动 master/metadata 不算 shared L3；
- master/metadata 等辅助进程可共置在 C，但均属于 upstream 依赖；
- 跨节点事件用 request/op id 与 worker-local sequence 合并，不依赖三台机器 wall clock 的严格全序。

### 11.2 为什么必须双 worker

单 worker 的远端命中容易和本地 L1/L2 命中混淆。最小关键证明是：

1. Worker A 成功写入 L3；
2. Worker B 对同 prefix 的 L1/L2 为冷；
3. Worker B 从 shared L3 完成 Get；
4. Get 产生非零、可归因的 storage-cached tokens，并相对同请求的 B-cold no-L3 control 实际减少 uncached/prefill tokens。

如果这条链不能稳定成立，shared KV pool 项目没有立项基础。

这里必须分开两个结果：

- `RESTORE_PATH_PASS`：A Put、B 本地冷、B remote Get 与固定解码输出一致性全部可关联，只证明链路正确；
- `REMOTE_VALUE_SURVIVES`：在前者之上，pinned runtime 报告 `cached_tokens_details.storage > 0`，且相同 prompt 下 `uncached_prompt_tokens = prompt_tokens - cached_tokens` 小于 B-cold no-L3 control，证明 L3 KV 实际替代了 prefill。

G0 只有两者都成立才继续。TTFT 在这里仅作诊断：它可能因 TCP restore 成本而不改善，不能替代 token-level survival oracle，也不在此阶段构成性能 claim。

### 11.3 明确不用的部署

- 不做 Prefill/Decode disaggregation；
- 不引入 Kubernetes 或 GPUStack；
- 不以 RDMA/GDR 为前提；
- 不搭建五节点 HA metadata 集群；
- 不把 Redis/Dragonfly 作为第二套远端中间件；
- 不增加本地 SSD L4。

这些部署都不能帮助隔离 L3 admission 的因果效应。

### 11.4 A/B 隔离

策略 arm 必须顺序运行，不共享一个持续变化的 L3 pool：

- 每个 arm 使用 freshly restarted、verified-cleared 或真正容量隔离的 store；
- extra_backend_tag 只能避免 key collision，不能消除容量与 eviction 历史；
- 不把 MooncakeStore.clear() 当成单实验安全清理原语；在 pinned 版本确认其全局 remove_all 语义后，默认用新 store/restart；
- 固定 workload 和 worker assignment；
- 使用随机顺序或 ABBA 顺序抵消温度/背景漂移；
- 每轮记录 warm-up、稳定区间和异常请求；
- 运行前用 probe 验证 L1/L2/L3 的冷热状态。

---

## 12. 实验矩阵

### 12.1 Gate 场景：先证明链路

| 场景 | 目的 | 必须观察 |
|---|---|---|
| CROSS_WORKER_RESTORE | 分别证明 stock restore 链路正确与机制存活 | `RESTORE_PATH_PASS`：Mooncake Put/Get、B 本地冷、输出一致；`REMOTE_VALUE_SURVIVES`：`cached_tokens_details.storage > 0`，且同请求 B-cold L3 arm 的 uncached/prefill tokens 少于 no-L3 control |
| WRITE_COST_SENTINEL | 在 D1 前筛查最坏浪费下的 stock L3 path cost 是否能传导到前台 | zero-reuse、roomy L3、service-curve knee 下，L3 enabled/L2_ONLY 的 Store 活动与 paired TTFT-SLO/Goodput；该对照含 lookup/miss，单独 NIC/CPU 增长不算性能信号 |
| CAPACITY_PRESSURE_SENTINEL | 在 D1 前筛查 bounded L3 容量是否影响有价值 KV 的 query-time availability | 两个 fresh Store 的实际 roomy/small segment response、复用请求的 storage-cached/useful Get、uncached/prefill tokens 与 paired TTFT-SLO/Goodput |
| ALWAYS_DROP | 证明 DROP 不碰 L2 控制面且无 L3 Put | L2 write-through 路径、配置、refcount 正确性与 eviction 实现不变；不要求内容或 eviction 事件序列相同；`admitted_payload_bytes = submitted_payload_bytes = 0`，且无 L3 operation/queue/protection/Put |
| ALWAYS_ADMIT | 证明 hook 等价于 stock write-through path | correctness、bytes、TTFT 落在等价区间 |
| PREFIX_CLOSURE | 证明策略不制造不可达 descendant | remote lookup 无 policy-induced hole |
| BYTE_RECONCILE | 证明 trace 对账 KV payload | adapter physical-object buffer 与 trace 聚合一致；D1 pre-collapse 原因码区分 new/race/exists-skip/failure |
| DEDUP_RACE_FAILURE | 证明 ADMIT 与完成写入被正确区分 | sequential dedup、two-writer race、Put failure（可取得时）全部进入 DecisionTrace；failure injector 不可得时为 `INCONCLUSIVE`，不能升级 G0 |

### 12.2 离线边界矩阵

对以下轴做受控组合：

- cross-worker reuse：低 / 中 / 高；
- L3 capacity pressure：roomy / knee / overloaded；
- L3 write path：隐藏 / queue pressured；
- branch fan-out：低 / 高；
- prefix size：短 / 长 / 混合；
- reuse distance：短 / 长 / bimodal；
- value-frequency correlation：正相关 / 弱相关 / 反相关。

离线矩阵只用于找出代表性 sentinel，不追求所有组合全覆盖。

### 12.3 在线 sentinel

| Sentinel | 预期裁决 | 候选若不符合意味着什么 |
|---|---|---|
| MIXED_PRESSURE | 候选可能优于 ADMIT_ALL 与静态规则 | 核心机会不存在或信号无效 |
| NO_L3_VALUE | DROP_ALL/L2_ONLY 应最好或不劣 | 策略在制造无意义远端开销 |
| ALL_VALUABLE_ROOMY | ADMIT_ALL 应最好或持平 | 策略过度过滤高价值 KV |
| TARGET_HELD_OUT | 与目标分布同族、未参与调参与筛选；正结果必须保留收益 | 只拟合 calibration/conditional-replay-validation workload |
| OOD_SHIFT | 有意改变热点、reuse distance 或 fan-out；允许候选失败 | 稳定失败用于界定 losing boundary，不能帮助正结果通过 G3 |

一个可信策略不仅要有“赢的场景”，还要在应当输的场景按预期输。

### 12.4 主指标与判定

**主在线指标：Goodput@TTFT-SLO。**

- TTFT-SLO 在看候选结果前预注册；
- offered load 选择在 baseline service curve 的可区分区域；
- p50/p95/p99 TTFT 为诊断指标；
- `new_physical_put_bytes`、not-read-within-H / closed-DAG unused、useful restore 和 recompute 是机制解释；`new_physical_put_bytes` 仅在 D1 observation 已通过 non-interference 后可报告；
- 所有 candidate overhead 计入端到端结果。

候选可以通过两种方式成立：

1. 在相近 L3 写入预算下，提高 Goodput@TTFT-SLO；
2. 在预注册的不劣 Goodput 范围内，显著减少 `new_physical_put_bytes`。

“显著”的统计和工程阈值必须在 calibration 后、TARGET_HELD_OUT 前冻结；不能事后按图挑阈值。

D1 前 sentinel 使用更严格的投资裁决：`true` 要求预注册效应区间下界越过物质性阈值；有效 `false` 要求上界已低于
该阈值。区间仍跨阈值时只能是 `INCONCLUSIVE`。两项有效 `false` 才能触发 D12；“未检出显著差异”本身不能触发 STOP。

### 12.5 公平性规则

- 同一请求序列、token、arrival、worker assignment；
- 同一模型和所有三级容量；
- 同一 Mooncake backend 和远端淘汰；
- baseline 允许合理调优，但只能在 calibration set；
- candidate 与 baseline 使用相同清池、warm-up、重复和统计方法；
- 以独立 run 为统计单元，不能把同一 run 内相关请求伪装成独立样本；
- headline cell 至少做 5 个 paired repeats，其他核心 cell 至少 3 个；若测床噪声要求更多，以预注册 power/noise 结果为准；
- 对 D1 前 stock sentinel，最少重复数只是下限；若效应区间仍跨越物质性阈值，必须按冻结的最大重复预算继续，预算耗尽仍
  不能排除物质性效应时记为 `INCONCLUSIVE`，不得用“不显著”生成有效 null；
- 固定解码下输出 token 一致，request error、hang、queue/ref leak 为零容忍；
- 报告所有 sentinel，不只报告赢的 workload；
- 保存 raw logs，不只保存聚合图。

### 12.6 预注册 losing conditions

以下不是“实验失败后找理由”，而是项目开始前就接受的反例：

- L3 容量大于活跃 working set、写带宽无压力：ADMIT_ALL 应最好或持平；
- 几乎所有对象都高 fan-out 且跨 worker 复用：选择性准入的 false negative 会伤害命中；
- one-shot，或复用只发生在同 worker 的 L2 保留期内：L2_ONLY / DROP_ALL 应最好；
- 短 prefix 的远端写读成本不低于重算；
- 热点变化快于历史窗口：旧热度造成 false positive / false negative；
- Mooncake dedup 已消除大部分重复 Put：可优化的 `new_physical_put_bytes` 很小；
- 瓶颈位于 read、GPU compute 或 L2，而不是 L3 write/capacity；
- 异步 Put 被完全隐藏：可能只有 payload/capacity 收益，没有 Goodput 收益；
- STATIC_FREQ* 自己的在线 trace 中，unused-put 与 dropped-then-demanded residual 均低于物质性阈值：动态候选没有存在必要；
- policy CPU/queue 开销抵消节省；
- calibration 赢、TARGET_HELD_OUT 反向：不得称为目标分布上的成功。

---

## 13. Gate / STOP 流程

### G0：源码与运行时真相

通过条件：

- pinned commit 可运行；
- hook 的前后状态、异步 ack 和 DROP 语义被测试证明；
- Worker A → L3 → fresh Worker B 同时满足 `RESTORE_PATH_PASS` 与 `REMOTE_VALUE_SURVIVES`：链路稳定、storage-cached tokens 非零，且相对 B-cold no-L3 control 实际减少 uncached/prefill tokens；
- prefix closure 可在不增加远端控制面的情况下保证；
- Mooncake KV payload bytes 可对账，且 D1 pre-collapse trace 可区分 new Put、race-existing、exists-skip 与 failure；
- ALWAYS_ADMIT 与未改 upstream 对齐，ALWAYS_DROP 的 admitted/submitted payload bytes 为 0，且无 L3 operation；
- duplicate/race 能关联到 decision trace；真实 Put failure 必须有 runtime evidence，否则该项为 `INCONCLUSIVE`，不得称 G0 validated；
- 输出一致且无 hang、queue/ref leak。

STOP：

- 找不到只影响 L3 的窄 hook；
- DROP 会改变 L2 或破坏引用状态；
- remote restore 在目标条件下不减少任何 prefill；
- 必须新增远端 metadata/read path 才能保证可达。

### G1：仪器可信

通过条件：

- generator 可完全重放；
- tiny trace 的 observation、operation、batch/attempt、adapter terminal 与后续 Get/recompute 可手工对账；
- trace 与 Mooncake adapter bytes 对账；
- D1 可用时，new/race/exists/failure 原因与 eligible/submitted/new-physical payload 对账；
- online feature 只来自 decision 时可见状态，不读取未来 trace；
- calibration、TARGET_HELD_OUT 与 OOD_SHIFT workload 在调参前冻结；
- online trace 能解释各 arm 自己的一次 Put 到后续 Get/recompute 的完整生命周期。

STOP：

- 事件丢失或跨 worker 无法关联；
- 只能估算、无法测量关键 KV payload 字节；
- trace/payload reconciliation 遗漏 dedup、race 或实际 object 粒度；
- workload 无法确定性重放，或 trace-enabled 改变在线行为；
- 在线 policy 读取未来 trace；
- 在线 lifecycle 无法关联 Put、query-time availability、Get/recompute 与 terminal cleanup。

### G2a：机会生存闸门

通过条件：

- shared L3 对至少一个受控 Agent 坐标有稳定净价值；
- ADMIT_ALL 存在非噪声级 not-read-within-H / closed-DAG unused payload，或可观测的 query-time unavailability；
- “写成本 / 资源争用”或“容量竞争 / 查询时可用性”两条候选收益因果链中，至少一条由各 arm 自身的运行时中介证据与 paired Goodput@TTFT-SLO 结果共同支持；
- STATIC_FREQ* 自己的在线 lifecycle trace 同时留下可观的 admitted-but-not-read 与 dropped-then-demanded residual；
- 可在线获得的信号与该 gap 有可解释关系。

链 A 不能只用 NIC/CPU 计数器或 submitted bytes 通过，必须闭合 decision → `new_physical_put_bytes` → queue/resource pressure → Goodput/TTFT；链 B 不能只用 modeled occupancy 通过，必须闭合 decision → query-time availability/useful Get → computed prefill/recompute → Goodput/TTFT。若两条链都没有通过，G2a 对性能策略为 STOP；只有 new-Put payload 节省时，最多保留 payload-efficiency 分支。

其中：

- admitted-but-not-read：该 arm 实际完成 Put，但在固定 H 内无 useful Get；
- dropped-then-demanded：该 arm 实际 DROP 后，同 key/prefix 在固定 H 内出现需求，且当时 adapter-visible 为 unavailable 并发生对应 prefill；
- 两者都是 STATIC_FREQ* 自身运行的观察，不伪装成另一个 policy 的反事实结果。

dropped-then-demanded 只是 opportunity marker，不证明“当时若 ADMIT 就一定能命中”：Put 延迟、dedup、容量变化和后续 eviction 仍可能让它不可用。它只能允许候选进入拒绝筛选，最终价值必须由 G3 在线 treatment 证明。

建议在实验前预注册“可行动 residual”阈值；例如 STATIC_FREQ* own-arm residual value 达到约 10% 且跨重复稳定。具体定义、归一化与数字必须在 calibration 前冻结；这里不是当前结果。

STOP / 降级：

- L3 本身无价值：停止策略项目；
- 两条候选收益因果链都缺少“运行时中介 + 端到端结果”的共同证据：停止 Goodput/TTFT 策略方向；仅有 new-Put payload 节省时降级到 payload-efficiency；
- ADMIT_ALL 几乎无浪费：只保留链路 characterization；
- dedup 已经消除绝大多数实际重复 Put：降级为负结果；
- STATIC_FREQ* 的 own-arm residual 低于物质性阈值：结论为“简单规则足够”，不实现复杂候选；
- gap 只由 future information 产生：不得上线。

### G2b：Conditional replay rejection filter

只有 G2a 通过后，才允许实现最小 conditional ledger，并在其中实现 VALUE_DENSITY，将其保持为 ROADMAP candidate。runtime hook 尚不启用候选。实现前先冻结 calibration、conditional-replay-validation、TARGET_HELD_OUT 与 OOD_SHIFT 的边界；ledger 输出必须携带 source policy/run，且不能声称跨策略 causal ranking。

ledger 自身通过条件：

- 手工 tiny eligibility stream 的 action、reason code 与 payload 逐项一致；
- no-eviction microcase 能复现其 source arm 的 eligible/submitted/new-physical bytes（D1 可用时）与 dedup；
- 每个 policy 独立演化 modeled resident set，future-aware upper-bound feature 与 online feature 结构性隔离；
- 只有获得 SOURCE_VERIFIED eviction 规则或 telemetry 后，bounded-capacity replay 才可升级为 runtime 对齐；否则始终标为 modeled sensitivity。

不被拒绝的条件：

- candidate 参数只在 calibration set 选择并冻结；
- 在多个具名 source-run eligibility stream 上不被简单静态规则条件式支配；
- candidate 与 STATIC_FREQ* 的不同动作覆盖足够的 eligible payload mass，而非只发生在边角流量；
- action/payload 与 conditional useful-demand coverage 的变化方向可解释；
- 不使用 future-aware feature。

STOP：

- ledger 遗漏 dedup、race、实际 object 粒度或无法对账 source arm 的 action/payload；
- 把某一 arm 的 eligibility stream 当成其他 policy 的真实反事实；
- 在未获得 SOURCE_VERIFIED eviction seam 时，把 modeled occupancy/eviction 冒充在线事实；
- 只在 calibration 赢；
- 动作差异不足以产生可测在线 effect；
- 只有依赖未经验证 eviction model 才能赢；
- decision overhead 的保守估计已超过收益。

G2b 只能拒绝明显不值得上线测试的候选，不能证明 candidate 胜出。未被拒绝后才实现并启用 runtime candidate；此时状态是 IMPLEMENTED_UNVALIDATED，公开标题仍不升级。

### G3：在线因果验证

通过条件：

- candidate 在 MIXED_PRESSURE 对最强公平基线有稳定收益；
- 在 NO_L3_VALUE 和 ALL_VALUABLE_ROOMY 按预期退化；
- 在预注册 TARGET_HELD_OUT 上相对 STATIC_FREQ* 达到性能阈值，或达到 Goodput 非劣条件下的 payload 节省阈值；
- OOD_SHIFT 只用于复现失效边界，不替代 TARGET_HELD_OUT 正结果；
- 各 arm 自己的 online lifecycle trace 能闭合 decision → Put/Get → prefill/SLO 因果链；conditional ledger 只核对该 arm 的 action/payload 账；
- policy overhead 未吃掉收益。

STOP / 负结果：

- 只赢 ADMIT_ALL，不赢调优静态基线；
- 只在 calibration/conditional ledger 上看似有利，TARGET_HELD_OUT 不成立；
- 收益来自 workload/worker assignment 改变；
- 清池或顺序效应解释了结果；
- 置信区间覆盖噪声区；
- 机制字节改善不能传导到端到端 SLO，且原因无法解释。

如果异步写入被完全隐藏、候选稳定减少 `new_physical_put_bytes` 但 Goodput 无变化，则只能降级为 **traffic-efficiency / capacity-efficiency** 结论；不能把流量下降换算成 TTFT 提升。

### G4：证据封装

通过条件：

- 每个简历数字可回到 manifest、raw log、analysis commit；
- upstream / owned / experimental 三层清晰；
- 正结果与负结果都保留；
- 提供复现实验和最小 source patch；
- 完成 issue/PR 前先确认结论不依赖本地私有假设。

---

## 14. 当前 Evidence Ledger

### 14.1 Claim state 与 Gate outcome 是正交字段

SOURCE_VERIFIED 与个人实现状态不是同一条线性状态机；Gate outcome 也不是 claim state。每个结论或
artifact 必须同时写清它们，不能用一个 PASS 掩盖另一项尚未实现或 `INCONCLUSIVE` 的事实。

| 字段 | 回答的问题 | 合法值 | 规则 |
|---|---|---|---|
| `claim_state` | 这条主张被何种证据支持？ | `ROADMAP`、`SOURCE_VERIFIED`、`IMPLEMENTED_UNVALIDATED`、`EXPERIMENTALLY_VALIDATED` | 仅随对应 source/code/runtime evidence 升级；一个 Gate 的 PASS 只升级它所支持的具体 claim |
| `gate_outcome` | 这次 scenario / Gate 执行发生了什么？ | `PASS`、`FAIL`、`INCONCLUSIVE`、`STOP` | 每份 run bundle 都必须有；`INCONCLUSIVE` 不是 PASS，也不能提升完整 Gate 或 performance claim |

规划、决议和运行结果应各自保持位置：`DECIDED` 是决议文件的状态，不是上述任何 claim state；例如 D1 可为
`DECIDED` 且其 new-Put attribution 仍为 `ROADMAP/STOP`。

本文强制使用以下 claim-state 词典：

| 状态 | 允许措辞 | 禁止措辞 |
|---|---|---|
| ROADMAP | 计划实现、验收条件、待测假设 | 支持、解决、降低、提升 |
| SOURCE_VERIFIED | 在 pinned commit 的具体函数/文档中观察到某事实 | 把 upstream 当个人贡献，或推导测床必然有效 |
| IMPLEMENTED_UNVALIDATED | 代码、单测、forced allow/drop 已存在 | 跨 worker 有效、性能提升、线上成立 |
| EXPERIMENTALLY_VALIDATED | 在明确 topology/workload/commit 下得到可复现观察 | production-ready、普适收益、大集群外推 |

`EXPERIMENTALLY_VALIDATED` 再区分：

1. **功能正确性**：ALLOW/DROP 只改变 L3 Put，L2、输出和 ref/queue 生命周期正确，Worker A 写后 Worker B 可真实读取。
2. **效率结果**：固定 cohort、paired order、重复实验、raw logs、置信区间与 TARGET_HELD_OUT 都齐备；进一步区分 payload/capacity efficiency 与 Goodput/TTFT performance。

功能正确不自动推出性能有效；一个 `G0-RUNTIME VALIDATED` 也不自动推出 G1/G2/G3。

### 14.2 当前账本

| Claim | 当前状态 | 当前证据 | 允许措辞 |
|---|---|---|---|
| SGLang HiCache 存在 L1/L2/L3 分层路径 | SOURCE_VERIFIED | 官方文档与 pinned source | “源码验证了分层路径” |
| L2 ack 后、L3 write_storage 前存在候选接缝 | SOURCE_VERIFIED，待 runtime test | pinned source audit | “已定位接缝，待运行时验证” |
| Mooncake adapter 支持 shared L3 路径 | SOURCE_VERIFIED，待本地部署验证 | adapter/README | “计划以 Mooncake 验证跨 worker 复用” |
| SGLang 社区把 HiCache 准入/策略视作持续演进问题 | SOURCE_VERIFIED | roadmap issue | “官方 roadmap 证明问题域真实” |
| Prefix-DAG generator、trace、hook、policy | ROADMAP | 尚未在本项目实现 | 只能说“计划实现” |
| Conditional admission ledger | ROADMAP，gated behind G2a | 尚未在本项目实现；G1 与 G2a 不要求它 | 只能说“若 G2a 通过，计划在 G2b 实现候选拒绝工具” |
| Agent Prefix-DAG 会造成 ADMIT_ALL 浪费 | ROADMAP hypothesis | 尚无项目数据 | 只能说“待测假设” |
| stock L3 path-cost envelope 或 bounded-capacity pressure 可传导到 Goodput/TTFT | ROADMAP hypothesis | `WRITE_COST_SENTINEL` / `CAPACITY_PRESSURE_SENTINEL` 尚未运行 | 只能说“D1 前计划筛查两类粗粒度性能机会”；前者尚未隔离 write contribution |
| STATIC_FREQ* own-arm trace 留有可行动 residual | ROADMAP | 尚无数据 | 禁止当作事实 |
| VALUE_DENSITY 优于静态规则 | ROADMAP | 尚无数据 | 禁止写进简历 |
| 双 worker 下减少 new physical Put payload 且 Goodput 非劣 | ROADMAP | 尚无数据；D1 observation patch 尚未实现 | 只能留 X 占位 |
| 双 worker 下改善 Goodput@TTFT-SLO | ROADMAP | 尚无数据 | 只能留 Y 占位 |

本表必须随实验更新。任何升级为 EXPERIMENTALLY_VALIDATED 的 claim，都要附运行 ID、commit、原始日志与统计方法。

---

## 15. 结果分叉与诚实终局

### 终局 A1：性能正结果

条件：

- 过 G0–G3；
- 赢最强公平静态基线；
- TARGET_HELD_OUT 上 Goodput@TTFT-SLO 达到预注册改善阈值；
- 失败边界清楚。

可叙述为：

> 我固定 L2 和远端实现，只修改 L3 写入准入；在指定 Agent workload 坐标下获得 X/Y，并证明收益来自哪些在线信号。

### 终局 A2：仅 payload / capacity efficiency 正结果

条件：

- TARGET_HELD_OUT 上 `new_physical_put_bytes` 达到预注册下降阈值；
- Goodput 满足预注册 non-inferiority，但没有统计与工程上可信的提升；
- 收益不是 dedup、清池、顺序或错误计数造成；
- 明确报告“未观察到 TTFT/Goodput 改善”。

可叙述为：

> 候选在固定 SLO 表现下减少了 Mooncake new physical Put payload 与 not-read-within-H；异步写入被隐藏，因此没有声称 TTFT/Goodput 提升。

### 终局 B：简单规则已经足够

条件：

- ADMIT_ALL 有浪费；
- 但 L3_SECOND_HIT 或 STATIC_FREQ* 的 own-arm residual 已低于预注册物质性阈值。

这是合格负结果：

> 我用双 worker 在线 lifecycle trace 发现，调优静态规则的 own-arm residual 低于物质性阈值，因此按 G2a 停止，未实现 conditional ledger 或复杂 value-aware policy；静态规则在该负载族上是更好的工程选择。

不得为了简历继续加 signal。

### 终局 C：共享 L3 在目标坐标无净价值

可能原因：

- cross-worker reuse 太低；
- 远端恢复慢于重算；
- working set 太小，L1/L2 已覆盖；
- prefix 太短；
- offered load 未到 SLO knee。

可保留 characterization 和边界图，但不再声称优化 L3 admission。若该结论由 D1 前两个 stock sentinel 的有效
null 触发，它是 **pre-implementation direction STOP**：不满足 R/F，也不能作为已完成的 runtime flagship。只有
先前已经满足 R、随后在 G2/G3 得到无净价值结论时，才可能作为 F 层的工程负结果收口。

### 终局 D：实验系统无裁决权

如果 Mooncake KV payload 字节不可测、prefix closure 不可守、A/B 隔离失败或 source seam 不成立，项目停止。不能用离线 simulator 数字替代生产框架结果。

---

## 16. 与目标岗位的映射

### 16.1 直接命中的 KV cache 组关键词

- KV Cache / Prefix Cache；
- hierarchical KV cache / L1-L2-L3；
- KV offload data path；
- shared / distributed KV cache pool；
- cache admission / capacity efficiency；
- cross-worker KV reuse；
- SGLang / Mooncake source integration；
- KV lifecycle observability；
- workload characterization；G2a 通过后可增加 conditional trace replay 作为候选拒绝工具；
- TTFT / SLO / Goodput；
- distributed systems performance trade-off。

### 16.2 项目最适合的团队

优先匹配：

- shared KV cache / KV storage platform；
- inference serving 中的 cache lifecycle 与容量策略；
- engine-storage boundary；
- hierarchical cache / remote cache integration；
- MaaS serving 的跨 worker reuse 与成本效率。

部分匹配：

- 通用推理引擎组：有源码集成、prefix reuse 和 TTFT，但不改 scheduler/kernel；
- 存储系统组：有 admission、bytes、capacity 和远端池，但不改底层引擎。

弱匹配：

- CUDA/Triton kernel；
- 编译器/MLIR；
- RDMA/GDR/NIXL 数据面；
- 模型量化与 sparse attention；
- storage durability / consensus / HA。

### 16.3 面试中的准确定位

一句话：

> 我做的不是新的 KV 存储后端，而是生产推理框架到共享 KV pool 的写入控制面：用 Agent Prefix-DAG 重放和 Mooncake KV payload 探针判断哪些 KV 值得进入远端池，再用双 worker 端到端验证它是否真正改善 TTFT SLO。

---

## 17. 面试防守面

### 17.1 45 分钟追问必须能打开

1. 一次请求如何命中 L1、L2、L3；
2. L2 ack 与 L3 Put 的具体源码路径；
3. DROP 为什么不破坏 L2；
4. prefix closure 为什么是正确性/可达性约束；
5. logical KV bytes、Mooncake physical-object payload bytes 与 NIC/wire bytes 为什么不同；
6. stock selective 为什么不是公平 L3-only baseline；
7. Worker B 如何证明不是本地命中；
8. replay 为什么不能直接预测 TTFT；
9. 最强静态基线如何调优和冻结；
10. 哪个 sentinel 应该让候选输；
11. 删除哪段 owned code 后收益消失；
12. 哪些结论是 upstream、SOURCE_VERIFIED、ROADMAP、IMPLEMENTED_UNVALIDATED 或 EXPERIMENTALLY_VALIDATED。

### 17.2 四类攻击的预案

**“这不就是 second-hit？”**

先把 second-hit 实现为公平在线基线。如果它自身 trace 的 admitted-but-not-read 与 dropped-then-demanded residual 都低于物质性阈值，项目结论就是“不需要更复杂”。只有 residual 在 value-frequency 失配坐标下稳定存在，才引入 value density。

**“为什么不改远端淘汰？”**

准入和淘汰是两个决策面。首轮固定远端淘汰，才能裁决写入过滤本身。远端淘汰只有在 admission 已闭环且出现新证据时另立项目。

**“为什么不加本地 SSD？”**

本项目研究共享 L3 的跨 worker 复用；本地 SSD 会增加一个本机冷层和新的成本模型，不能帮助回答当前单一问题。

**“为什么不用 RDMA/GDR？”**

本问题先裁决结构性的 admission 与 reuse；首轮 TCP 足以验证方向。数据面传输优化依赖硬件，是另一个项目，不能把其收益混进 policy。

**“为什么不做量化/稀疏化？”**

它们改变 KV 表示、精度和容量，是独立机制。当前项目固定 KV 表示，避免把“少写数据”和“每份数据变小”混为一个收益。

---

## 18. 明确排除项及拒绝理由

| 被拒绝方向 | 为什么不进入本项目 |
|---|---|
| L1/L2 victim ordering / retention | 改变本地命中，导致无法隔离 L3 admission |
| remote-recoverability-aware eviction | 同时依赖本地淘汰与远端状态，重新变成双决策 |
| Mooncake metadata HA / recovery | 目标是故障正确性与 RTO，不是准入和 SLO |
| remote eviction policy | 与 admission 相关但不是同一决策 |
| router / consistent hashing | 改变 worker assignment 和复用机会，污染 workload 控制变量 |
| Redis 两级中间件 | 重造已有 shared cache substrate，ownership 密度低 |
| 纯离线算法评测 | 没有生产框架在线验证，无法声称 TTFT/Goodput 收益 |
| custom FIFO log / storage engine | 深但正交，回答的是介质写放大而非 KV admission |
| Backup Request / 慢节点识别 | 通用分布式长尾组件，不是 KV 生命周期核心机制 |
| KV FP8 / 量化 | 改变表示与精度，形成第二优化主线 |
| sparse KV | 改变 token/head 保留语义，形成第二优化主线 |
| RDMA / GDR / NIXL | 数据面与硬件条件型问题，不帮助隔离 policy |
| 本地 SSD L4 | 新增层级、介质与 eviction/admission 决策 |
| PD disaggregation | 改变拓扑与调度，不是验证 shared L3 admission 的必要条件 |
| Kubernetes / GPUStack | 部署工程量不增加核心机制证据 |
| vLLM / 第二个 cache backend | 会复制 source seam 与集成工作，不能增强当前单问题的因果证据 |
| TP>1、hybrid cache、Unified Radix Tree 泛化 | 首轮 source contract 明确不覆盖；只有核心结论成立后才能另做兼容性验证 |
| coherence / invalidation / consistency protocol | shared L3 的 upstream 语义，不是本项目 admission 决策 |
| 通用 policy DSL、动态 RPC policy service、插件平台 | 为假想扩展提前造框架，删除后不影响核心实验 |

---

## 19. 交付物

最终仓库应能独立审查以下内容：

1. **Problem contract**：本文件、层级定义、单一问题和 STOP 条件；
2. **Pinned source note**：commit、源码路径、hook 与 upstream 边界；
3. **Workload package**：Prefix-DAG spec、generator、seed、manifest；
4. **Instrumentation package**：event schema、opaque trace-ID propagation、collector/correlation、payload-byte validator；
5. **Conditional ledger package（仅 G2a PASS 后）**：policy interface、给定 eligibility stream 的 payload ledger/upper bound、tiny-case correctness tests；若 G2a STOP，该包明确不交付；
6. **Runtime patch**：最小 behavior hook、policy interface、reason codes，以及不改变语义的 StorageOperation/controller/adapter trace correlation；
7. **Deployment package**：双 worker + Mooncake TCP 拓扑、健康检查和清池验证；
8. **Experiment package**：sentinel、A/B runner、raw logs、统计脚本；
9. **Evidence report**：正结果、负结果和边界图；只有 G2a PASS 并进入 G2b 时，才增加 conditional-ledger 与 source arm 的 action/payload 对账；
10. **Community artifact**：可复现 issue、RFC 或最小 PR；是否提交由证据决定。

核心交付不是大而全平台，而是一条可删除、可 A/B、可追溯的机制链。

---

## 20. 简历与项目叙事模板

### 20.1 证据尚未完成前

> 基于 SGLang HiCache 与 Mooncake 设计多轮 Agent Prefix-DAG workload 和 KV 证据关联探针，固定 L2 write-through 并探索 shared L3 的写入准入边界；当前处于跨 worker 恢复链与 stock opportunity screen 验证阶段，conditional ledger 仅在 G2a 通过后进入实现。

### 20.2 只有性能正结果完成后

> 基于 SGLang HiCache 构建多轮 Agent Prefix-DAG 负载与 KV 证据关联探针，在固定 L2 write-through 的前提下实现 shared L3 写入准入，并在 2 Worker + 1 Mooncake Store 环境中对比 ADMIT_ALL、second-hit 与调优静态阈值；在 TARGET_HELD_OUT workload 下将 new physical L3 Put payload bytes 降低 X%，Goodput@TTFT-SLO 提升 Y%，并给出低复用、宽松容量和远端恢复过慢时的失效边界。

### 20.3 只有 payload / capacity efficiency 成立

> 基于 SGLang HiCache + Mooncake 实现固定 L2 后的 shared L3 写入准入；在 TARGET_HELD_OUT workload 上，相对调优静态阈值将 new physical Put payload bytes 降低 X%，Goodput@TTFT-SLO 保持在预注册 non-inferiority 范围内；未观察到可信 TTFT/Goodput 提升，并量化异步写入被隐藏时的适用边界。

### 20.4 如果静态规则胜出

> 构建 SGLang HiCache + Mooncake 的双 worker 在线 lifecycle trace 与 A/B，量化 Agent Prefix-DAG 下 shared L3 准入的收益边界；实验发现调优静态 second-hit/frequency 规则的 own-arm residual 低于物质性阈值，因此按 G2a 停止、未实现 conditional ledger 或复杂 value-aware policy，并给出该结论的成立坐标。

所有 X/Y 在 EXPERIMENTALLY_VALIDATED 前必须保持占位，不得写入简历。

---

## 21. 当前裁决与下一动作

### 21.1 当前裁决

**Conditional Select。**

选择它的理由：

- 有真实生产级 substrate 和可定位的窄源码接缝；
- owned mechanism 单一，可做公平删除测试；
- Prefix-DAG、trace 与双 worker 在线 A/B 能形成核心分析闭环；G2a 通过后，conditional ledger 只增加候选拒绝能力；
- 数据以请求结构、复用和 Mooncake KV payload 字节为主，不要求大集群才能有裁决权；
- 直接命中 KV cache pool、hierarchical cache、admission、lifecycle 与 TTFT/SLO；
- 正结果和负结果都可交付，不依赖论文级 novelty。

仍然“有条件”的理由：

- 尚未运行时证明 DROP 不修改 L2 路径、配置、refcount 正确性与 eviction 实现；
- 尚未证明跨 worker Mooncake restore 在目标模型上有稳定净价值；
- 尚未测出 ADMIT_ALL 在固定 horizon 下的 not-read payload 或其他可行动浪费；
- 尚未证明最强静态基线的 own-arm lifecycle trace 中存在可行动 residual；
- 尚无任何 X/Y 可用于简历。

### 21.2 唯一正确的下一动作顺序

1. 固定 source、模型、tokenizer 与三级容量；
2. 打通 Worker A Put → fresh Worker B Get，并分别证明 `RESTORE_PATH_PASS` 与 token-level `REMOTE_VALUE_SURVIVES`；成功 Get 或单次 TTFT 变化不能替代 prefill 减少；
3. 在 stock、无补丁系统上先做 baseline-only calibration、冻结带 checksum 的 preregistration，再跑 `WRITE_COST_SENTINEL` 与 `CAPACITY_PRESSURE_SENTINEL`；至少一个信号区间下界越过物质性阈值才自动继续 D1；只有两者区间上界都低于阈值才按 D12 作为有效双 null 在实现前 STOP，不能称为 R/F；区间跨阈值只能 `INCONCLUSIVE`；
4. 双 null 后只有 owner 在 D1 结果未知时另行冻结真实 payload/resource 目标、预算、物质性判据和有界 observation-only 计划，才可例外继续；该第一次授权不包含 behavior hook；
5. 只有正常 pre-D1 ruling 或 D12 第一次例外授权允许继续时，才实施 Mooncake pre-collapse trace-only observation，并以 trace-disabled/trace-enabled oracle 证明不干扰；在此前不运行 `BYTE_RECONCILE`，不作 new-Put payload claim；
6. 再实现完成 stock payload 归因所需的 SGLang trace-only correlation，证明 observation→operation→batch/attempt→adapter terminal 的 join 与 stock 等价；
7. 正常 sentinel-positive 分支在 trace-only 通过后可实现 ALWAYS_ADMIT / ALWAYS_DROP / POLICY_ERROR_FAIL_OPEN 最小 hook；双-null payload 例外分支必须先证明超过预注册阈值且映射回资源目标的 new-Put/写后未读浪费，并取得第二次 owner ruling，才解锁同一最小 hook；
8. 验证 prefix closure、dedup/race、fail-open 与 async/shutdown-detach 终态；真实 failure 不可得时保留 `INCONCLUSIVE`，不得称 G0 validated；
9. 用受控 Prefix-DAG 跑 G2a opportunity test；
10. 只有 G2a 通过，才实现最小 conditional ledger，并在其中实现和冻结 VALUE_DENSITY；否则以静态规则足够或无机会收口，不为补交付物建设 ledger；
11. 只有 candidate 未被 G2b conditional replay rejection filter 拒绝，才实现 runtime candidate，并标为 IMPLEMENTED_UNVALIDATED；
12. 只有 G3 TARGET_HELD_OUT 在线结果通过，才升级公开标题和对应的效率/性能 claim state。

这份规划的核心纪律是：

> 先证明 shared L3 可恢复且确实替代 prefill，再用 stock sentinel 判断两条性能机会是否值得投入；只有投资筛查存活，或 D12 的真实资源目标第一次例外成立，才允许证明 trace 不干扰。双-null 例外还必须经过 observation artifact 的第二次裁决才能进入 forced admission；其后才裁决 ADMIT_ALL 浪费、静态规则 residual 与价值感知准入。
