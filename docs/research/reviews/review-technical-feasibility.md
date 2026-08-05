# 技术命题与 8–10 周可行性对抗评审

> 评审日期：2026-08-04（Asia/Shanghai）  
> 适用范围：用户已固定的项目内核；本评审不建议改项目方向，只审查命题是否成立、范围能否闭合、以及什么证据足以支持简历叙事。  
> 证据纪律：框架行为以官方文档、当前源码、官方 RFC/PR 为主；论文只用于证明工作负载类别，不把多卡数据中心结果外推到单张 24GB 消费卡。

## 1. 结论先行

**对原始宽口径方案的裁决：RESHAPE（缩窄后继续），不是 SELECT，也不是 REJECT。**

项目与推理 serving / KV cache 岗位高度相关，但原始表述把至少四个独立研究问题揉在一起：工作负载测量、淘汰策略、CPU offload、FP8 KV cache。8–10 周内同时拥有这些实现，既不可证伪，也很难说明个人所有权。更关键的是，部分“创新前提”已经被当前上游实现或 RFC 削弱：

- vLLM 当前不是笼统的“近似 LRU”，而是**只在 `ref_cnt == 0` 的可驱逐块上执行固定块 LRU，并在同一访问时刻下优先驱逐更深/更靠尾的块**。
- SGLang 当前不是“只有 Radix Tree + LRU”：源码已有 LRU、LFU、FIFO、MRU、FILO、SLRU、priority；驱逐从可驱逐叶节点开始，活动路径由引用锁保护。
- SGLang 已合入 session radix cache，用于 session 结束时批量回收；因此“给缓存增加 session 生命周期”不能再作为新贡献。尚未被它解决的是**暂停但仍存活的 session 在下一次恢复前是否被错误驱逐**。
- vLLM 已有开放的 agent-aware KV eviction RFC，提出 token-range priority 和 TTL。把“为 vLLM 新增 priority/TTL API”作为主贡献，存在明显重复和上游竞速风险。

因此，8–10 周可守住的项目核心应是下面这个**可证伪命题**，它不改变用户给定的项目内核，只把实验边界钉死：

> 在 token 前缀完全一致、GPU KV 容量相同的多轮 agent 合成工作负载中，inter-turn gap 与并发是否会让 stock SGLang LRU 驱逐近期将恢复的 live-session prefix？若会，一个只利用现有 cache-priority 接口、根据 session 下一次使用线索赋值的最小适配器，能否减少 `computed prefill tokens` 和 p95 TTFT，同时不造成超过 5% 的吞吐或 p95 TPOT 退化？

**默认实现载体：条件性选择 SGLang；vLLM 只做 1 天观测性复核，不做双框架主实验。** 原因不是 SGLang 一定更好，而是它当前已有多种淘汰基线和 priority seam，最有机会把自有改动压到一个小适配层。这个选择必须通过 Gate 0：如果固定版本不能只改变 cache priority 而不改变请求调度，或者最小改动超过约 200–300 行，则不应硬做该策略。

FP8 仍可保留为用户要求的附带实验轴，但必须后置到硬件/后端 smoke test 之后；CPU offload 只能使用框架现成能力做可选 2×2 观察，**不得与自研淘汰策略并列为第二套自研机制**。

## 2. 已核实事实、待验证假设、Gate

| 类型 | 命题 | 当前结论 | 对项目的约束 |
|---|---|---|---|
| 已核实事实 | vLLM 的 eviction 是“近似 LRU” | 表述不准确。当前 V1 在可驱逐的 `ref_cnt == 0` 块队列上按 LRU 取队首；相同访问时刻用更深的 block-chain tail 作为 tie-break | 简历/报告应写“reference-aware fixed-block LRU with tail/depth tie-break”，不能把错误复述源码当洞察 |
| 已核实事实 | SGLang 只有 LRU，可自行补 LFU/SLRU/priority | 已失效。当前源码已有 LRU/LFU/SLRU/priority 等策略 | 禁止把实现这些策略本身当个人贡献；它们只能做 stock baseline |
| 已核实事实 | SGLang 尚无 session lifecycle | 已部分失效。session radix cache 已支持 session close 时回收，但普通可驱逐语义不变，不会保护暂停的 live session | 研究缺口必须限于 live-session retention / near-future reuse，而非“session-aware cache”泛化口号 |
| 已核实事实 | vLLM 没有 agent-aware eviction 方向 | 已失效。开放 RFC 已提出 token-range priority/TTL，且宣称有早期 ReAct 实验；仍非发布功能 | 不应把通用 priority/TTL API 作为自有主贡献；RFC 数据只能标为作者声称 |
| 已核实事实 | hit rate 提升会直接降低 TTFT | 因果表述过强。命中只减少未缓存 prefill；TTFT 还包含排队、调度、恢复、首 token 等 | 必须同时记录 cached/computed prefill tokens、prefill time、queue time、TTFT；不能只报 hit rate |
| 已核实事实 | eviction 与 CPU offload 是同一优化链 | 否。eviction 决定谁失去 GPU residency；offload 决定失去 residency 后走 CPU 保存/恢复还是重算 | 两者可独立成功或失败；8–10 周只拥有一个机制实现 |
| 已核实事实 | FP8 KV 在任意 24GB 消费卡上都能带来性能收益 | 否。具体 GPU、算力版本、attention backend、head dimension、scale/calibration 都会改变可用性和收益 | FP8 是 Gate 后实验，允许得到“不支持/容量增但延迟无收益”的负结果 |
| 待验证假设 | 目标 workload 中精确 token prefix 占比足够高 | 尚无证据 | 先做序列化后的 token 级一致性审计；若多数 resume 已漂移，淘汰策略不是主要矛盾 |
| 待验证假设 | 单卡压力下 LRU 会驱逐近期将恢复的 live session | 尚无本机数据 | 必须先用压力扫描复现“因 eviction 而 miss”，再写策略 |
| 待验证假设 | priority 可只影响 cache eviction，不改变调度顺序 | 当前源码存在 seam，但固定 release/CLI 行为仍需验证 | Gate 0 失败则停止该实现路径，不能用调度收益冒充缓存收益 |
| 待验证假设 | 改善缓存 residency 能穿透到 TTFT | 尚无证据 | 固定到达序列、输出长度和引擎参数，建立中介链路并做重复试验 |

## 3. 六个技术命题的对抗审查

### 3.1 vLLM 与 SGLang 的 prefix cache 不能做“框架孰优”的主 A/B

#### vLLM 当前语义

在 vLLM 当前 V1 源码中：

1. 只有 `ref_cnt == 0` 的块进入 free/eviction queue；命中并 `touch` 后会从队列移除并增加引用。
2. 队首是 least recently used block。
3. 若多个块拥有相同 last-access epoch（常见于同一请求的一条 block chain），队列会把拥有更多 hash tokens、即链条更深/更靠尾的块放在更前面，先牺牲后缀以保留更公共的前缀。
4. 当前版本还引入 `prefix_match_unit` 与 partial-block cache 路径；因此“vLLM 只能按完整物理 block 命中”也不能作为不加版本限定的结论。

这是一种**工作负载无感但并非朴素的 LRU**。可研究的缺口是它不知道 session 的 near-future reuse，而不是它没有引用保护、没有前缀结构 tie-break。

### 3.2 SGLang 的优势不是简单的“Radix Tree 比 block hash 更懂结构”

SGLang radix cache 的节点记录 `last_access_time`、`hit_count`、`priority` 和 `lock_ref`。当前 eviction heap 只从可驱逐叶节点开始：叶子删除后，若父节点成为无锁叶子，再把父节点放入候选。这保证了树结构上的 leaf-to-root 驱逐；活动请求路径由引用锁保护。

当前源码已有：

- LRU：以最后访问时间排序；
- LFU：以命中次数、再以最后访问时间排序；
- SLRU：probation/protected 分段；
- priority：以显式 priority、再以最后访问时间排序；
- 以及 FIFO、MRU、FILO。

所以以下原始假设应被删除：

- “实现 LFU/SLRU 是项目创新”；
- “SGLang 只会全局 LRU，不保护共享树结构”；
- “为节点加 priority 字段就是新贡献”。

真正仍可能成立的问题是：stock priority 是否能通过一个**不影响调度器**的 session-state adapter 获得可靠 near-future 信号，以及这个信号在单卡真实压力下是否值得。

另外，SGLang 的 page size 默认可很细，但具体 attention backend 可能要求更大的 page。page size 会同时影响可复用粒度和 kernel 性能，必须记录并固定；不能把不同 page/block 粒度下的结果归因于 eviction policy。

### 3.3 “agent workload 存在结构性 gap”是条件命题，不是先验事实

公开证据足以证明这种工作负载类别存在：

- TokenCake 将外部工具调用刻画为 temporal idle，并在 idle 时段 offload KV；
- KVFlow 指出普通 LRU 不具备 workflow future knowledge，并利用 agent-step graph 做保留/预取；
- vLLM × Mooncake 的公开 agent traces 显示多轮、长 context、较长 inter-turn delay 与高 input:output ratio。

但这些证据**不能证明你的单卡实验一定出现 gap**，更不能把多卡/分布式收益数字外推到 24GB 单卡。单卡 gap 只有在以下条件同时满足时才成立：

1. resume 输入保留了完全相同的 token prefix；chat template、tool definition、时间戳、随机盐、消息重排和截断均未破坏前缀。
2. 并发和 inter-turn delay 足以让前缀变为可驱逐并遭遇真实容量压力。
3. 后续 resume 确实再次包含此前 token，而不是摘要/截断后的新上下文。
4. 能把 miss 归因到 eviction，而不是 hash/prefix mismatch、backend page constraints 或服务重启。

相应的边界反例：

- 全部 session 都能同时放入 KV：没有 eviction gap，任何策略都不应改善。
- 提示词每轮前部都会变化：没有 exact prefix，eviction 再聪明也救不了。
- 所有 session 的 reuse distance 相同或压力极端：priority 无可利用信息。
- 输出 decode 占主导：即使缓存 prefill 改善，端到端延迟也可能几乎不变。

项目应把这些反例纳入实验，而不是只选能赢的 workload。

### 3.4 hit rate → TTFT 不是直接因果

正确的中介链路应写成：

> policy → victim/residency → resume 时 cached tokens → computed prefill tokens / prefill time → queue interaction → TTFT

近似分解为：

> TTFT = frontend/tokenization + queue wait + scheduling + restore（若有）+ uncached prefill + first-token work

因此：

- 主指标不是请求级“命中/未命中”，而是 token-weighted cached ratio、`request_prefill_kv_computed_tokens`、prefill time、queue time、TTFT。
- 固定 prompt、到达序列/随机种子、GPU KV bytes、模型、attention backend、输出长度与引擎配置。
- 每个 cell 至少 3 个重复/seed，报告分布与置信区间或 bootstrap 区间，不只给单次均值。
- 同时报告吞吐、p95 TPOT/ITL 作为代价。若 hit 增加但 computed prefill 或 TTFT 没变，应明确判定“缓存指标改善未转化为用户收益”。

vLLM 官方 APC 文档也明确指出：APC 只减少 prefill；当输出生成占主导或不存在共享前缀时，不会加速。

### 3.5 eviction 与 CPU offload 必须拆成两个假设

两者分别回答：

- eviction：GPU 容量不够时，哪个可驱逐 prefix 失去 residency？
- offload：失去/暂停 GPU residency 后，是写入 CPU 并 H2D 恢复，还是未来重算？传输能否与计算重叠？

它们可出现四种组合：策略选对 victim 但 PCIe 恢复过慢；策略一般但 offload 避免了大段重算；二者都有利；二者都无利。因此把“自研 eviction + 自研分层 offload”当成一个项目，会让结果无法归因。

当前 vLLM 已有 KV offloading connector/CPU tier；SGLang 已有 HiCache/hierarchical cache 参数。8–10 周内的纪律是：

- 自有实现只放在 eviction/session adapter；
- offload 只允许调用 stock path 做一个边界 cell；
- 若必须改 offload I/O、异步流水线或 allocator 才能跑，立即砍掉该轴；
- 不能把 stock offload 的框架实现包装成个人贡献。

### 3.6 FP8 KV cache：24GB 不是能力证明，具体 GPU 才是

FP8 可以降低 KV storage bytes，但“容量更大”“attention 更快”“端到端更快”是三个不同命题。

- RTX 4090 属于 Ada、compute capability 8.9，硬件具有 FP8 Tensor Core input；但能否走原生高效路径仍取决于框架、attention backend、head dimension、scale 与 kernel。
- RTX 3090 属于 Ampere、compute capability 8.6，不支持原生 FP8 Tensor Core input。FP8 作为存储格式可能经反量化/fallback 跑通，但不能承诺性能收益。
- vLLM 官方 2026 FP8 KV cache 优化报告主要验证 H100/Hopper 和 B200/Blackwell；其中还记录了长上下文精度、`head_dim=256` prefill、短序列小于约 7K、sliding window 与 calibration 等边界。不能把这些性能数字外推到消费卡。
- SGLang 虽暴露 `fp8_e4m3` / `fp8_e5m2`，但 scale 文件/校准常是必要条件；缺失时 scale=1.0 可能损害准确性。部分路径仍是 FP8 存储后反量化到 BF16/FP16 attention，收益可能主要体现为容量。

公平的 FP8 子实验必须分两组：

1. **等 token capacity**：BF16/FP16 vs FP8，隔离 dtype/kernel/量化开销和质量。
2. **等 HBM bytes**：让 FP8 实际容纳更多 tokens，测系统层容量、eviction 和 TTFT 效果。

每组都要记录准确性/确定性输出守门、实际 cached tokens、eviction 数与延迟。若 smoke test 不支持，正确结论是“本硬件/后端下不可执行”；若容量增加但延迟不降，也是一条合格负结果。

## 4. 被当前上游状态否定或显著削弱的原始假设

| 原始假设/潜在叙事 | 反证 | 处理 |
|---|---|---|
| vLLM 只是粗糙近似 LRU | 当前源码有 ref-count 候选集与同 epoch 的 tail/depth-first tie-break | 改成准确实现描述；研究“无 future/session signal” |
| SGLang 只有 LRU | 当前源码已有 LFU/SLRU/priority 等 | 这些只能做 baseline，不实现 |
| 实现 session-aware cache 是空白 | session radix cache 已在 2026-06 合入，解决 close 后回收 | 只研究 paused/live session retention，不声称发明 session lifecycle |
| 给 vLLM 加 priority/TTL 是独立创新 | vLLM issue #37003 已提出 token-range priority + TTL | 避免以通用 API 为主交付，除非明确做 RFC 复现/验证且不声称原创 |
| 框架 A 比 B 的 hit/TTFT 更好即可证明策略 | 两框架同时差异在缓存结构、粒度、调度、attention backend、chunked prefill、指标实现 | 拒绝双框架性能主结论；固定一个框架做同构 A/B |
| FP8 让 24GB 卡“一定翻倍容量并加速” | backend/硬件/校准决定路径，消费卡缺少当前官方等价性能证据 | 只声明理论 storage reduction；实际收益以 smoke/A-B 为准 |

## 5. Gate 0：3–5 天内必须完成的可行性证明

### G0：硬件与版本清单（半天）

固定并记录：GPU 型号与 compute capability、driver/CUDA、框架 commit/release、模型、dtype、attention backend、block/page size、KV budget、head dimension。运行 BF16 基线与 FP8 10–30 分钟 smoke test，确认是否真的创建 FP8 KV、有没有 fallback/error、输出是否明显异常。

### G1：exact-prefix 真值表（半天）

至少四个请求对：

1. 完全相同 append-only prefix，应复用；
2. 前缀首部改变 1 token，应不复用；
3. 只追加 assistant/tool result，应复用此前公共前缀；
4. 改 chat template/tool schema 顺序，应观察 token 差异与命中变化。

同时核对框架指标与 token 级离线比较，防止“业务上相同但 token 不同”。

### G2：先证明 stock LRU 的压力缺口（1–2 天）

用 4–8 个 session、三档 KV 压力和两档 inter-turn gap 扫描。必须找到至少一个可重复 cell，能够展示：

- prefix 曾被插入且当时可命中；
- session idle 后变为可驱逐；
- 它因容量压力成为 victim；
- resume 时产生额外 computed prefill，而非 prefix mismatch。

找不到这个 cell，项目就不应进入策略实现。

### G3：验证最小干预 seam（1 天）

在固定 SGLang 版本上验证：

- priority/SLRU CLI 与源码行为一致；
- session-derived priority 只进入 cache eviction；请求 scheduler 顺序保持一致；
- 能打印/导出 session→node/victim/hit 的最小证据；
- 自有改动预计不超过约 200–300 行，不触碰 attention kernel、allocator、offload pipeline。

只有 G0–G3 全部通过，才选择 SGLang 作为实现框架。若 G3 不通过，保留测量项目和 stock-policy 反例研究，但不要伪装成“完成了新策略”。

## 6. Kill conditions：出现即停止扩张

1. 在 0.6×、1.0×、1.2–1.5× working-set / KV-capacity 压力扫描下，stock LRU 的 token hit 始终 ≥95%，或 computed prefill 差异 <5% 且 TTFT 变化落在重复噪声内。
2. 真实/合成 trace 序列化后，可精确复用的 prefix token 占目标输入低于 70%；这时主要问题是 prompt construction，而非 eviction。
3. 到第 2 周仍无法区分 prefix mismatch、eviction、queueing 与 prefill compute，或无法获得 session/victim 证据。
4. priority 同时改变请求调度，且无法用小改动隔离；或需要重写 cache manager/超过约 200–300 行才能干预。
5. 改进只靠长期 pinning 赢得命中，却让吞吐、p95 TPOT 或无关 session 的 p95 TTFT 退化超过预先声明的 5%。
6. FP8 在具体 GPU/backend 上 smoke 失败，或准确性守门失败：停止 FP8 性能叙事，保留“不支持/失败边界”的记录，不阻塞主线。
7. offload 需要自研 I/O、DMA overlap、allocator 或协议才能成立：立即 defer offload 轴。

这些阈值必须在正式跑数前写入实验协议，不能看完结果后移动门槛。

## 7. 最小反例矩阵

### 7.1 主矩阵

固定：单框架、单模型、单 attention backend、单 page/block size、相同 KV bytes、相同到达序列、短输出 16–32 tokens。

策略仅三档：

1. stock LRU；
2. stock 最强相关基线（SLRU 或 static priority，Gate 后二选一）；
3. proposed live-session next-use/deadline priority adapter。

工作负载 2×2×2：

| 轴 | 低/正例 | 高/反例 |
|---|---|---|
| prefix stability | 完全稳定 append-only | 前部突变 1 token，验证策略无法救 prefix drift |
| KV pressure | working set 约 0.6–0.7× capacity，应几乎无 eviction | working set 约 1.2–1.5× capacity，制造可归因 pressure |
| reuse distance / gap | 短 gap | 长 gap，live session 可能被冷数据挤出 |

总计 8 cells × 3 policies × 3 seeds = 72 次。先用一个主 prefix length 完成闭环，再对 4K/8K/12K 三点做敏感性补充，避免一开始指数爆炸。

每个 cell 至少输出：token cached ratio、computed prefill tokens、prefill time、queue time、TTFT p50/p95、吞吐、TPOT/ITL p95、eviction victim/lifetime/reuse-gap、实验失败数。另做一个 decode-heavy 输出作为“不应明显改善 TTFT”的负控。

### 7.2 FP8 最小矩阵（主线闭环之后）

- stock LRU，选一个已证明会 thrash 的 cell；
- BF16/FP16 与 FP8；
- 等 token capacity、等 HBM bytes 两种公平口径；
- 各 3 次重复；
- 若时间仍有余，只加一个 proposed+FP8 interaction 确认，不展开全矩阵。

### 7.3 offload 最小矩阵（只有提前完成时）

仅使用 stock HiCache/offload：`LRU vs proposed` × `offload off vs on`，只跑一个边界 cell、3 次重复。它用于证明 eviction 与 offload 的独立/交互关系，不作为第二个实现交付。

## 8. 8–10 周落地计划

| 周 | 交付 | 退出标准 |
|---|---|---|
| 1 | Gate 0：硬件/版本锁定、FP8 smoke、exact-prefix 真值表、policy seam | G0/G1/G3 可复现；否则缩为测量研究 |
| 2 | workload generator、token/metrics truth、压力扫描 | 复现至少一个由 eviction 引发的 resume miss；否则触发 kill |
| 3 | stock LRU/SLRU/priority baseline 与 victim trace | 能解释每次关键 hit/miss 的路径 |
| 4–5 | 最小 session priority adapter、单元/集成测试 | 调度顺序不变，改动边界清楚，负控通过 |
| 6–7 | 72-run 主矩阵、重复/区间、负例与代价 | 结论可证伪；无论赢输都有边界图 |
| 8 | 可复现脚本、raw logs、图表、源码 diff、报告 | 第三方可一键复跑核心 cell |
| 9 | FP8 等 token / 等 bytes 子实验 | 明确支持矩阵、容量/延迟/质量三分法 |
| 10 | 缓冲、复跑异常、面试证据包；仅提前时做 stock offload 2×2 | 不再增加新机制 |

资源纪律：真实外部工具不必接入；用可复现 arrival delay 模拟工具等待即可。若使用公开 agent trace，只取 turn length / inter-turn gap / session concurrency 分布来参数化，并标为 trace-informed synthetic workload。

## 9. 框架选择建议

### 条件默认：SGLang

选择理由：

- Radix cache 的 leaf-to-root eviction、lock/ref 保护和多种 stock policy 已存在，适合把工作限制在一个小的 session signal adapter；
- 可用 LRU、SLRU/priority 做同实现内的公平基线；
- session close reclaim 已存在，能明确把本项目边界限定在 paused/live session。

主要风险：

- current `main` 的策略不一定全部出现在你最终固定的 release/CLI；
- `req.priority` 可能与调度 priority 共享语义，必须证明没有 scheduler confound；
- 若只是调用已有 priority 而没有测量、归因、反例和最小 adapter，所有权会偏弱。

### vLLM 的角色

vLLM 的可观测指标更丰富，适合用一天做“相同 synthetic sequence 是否也出现 eviction gap”的外部有效性复核。但不建议把它放进主性能 A/B，也不建议在 8–10 周内重做 #37003 的 priority/TTL plumbing。若最终选择 vLLM，前提是能找到同样小且隔离的 policy seam，并显式说明与 RFC 的差异；否则 scope 风险高于 SGLang。

## 10. Rubric 评分

采用 100 分、并带硬门槛的工程项目 rubric。分数衡量“当前方案能否作为可辩护项目”，不是市场流行度。

| 维度 | 权重 | 原始宽口径方案 | Gate 后缩窄方案（条件预测） | 说明 |
|---|---:|---:|---:|---|
| 岗位相关性 | 15 | 14 | 14 | serving/KV/cache/latency 高度相关 |
| 个人所有权 | 15 | 7 | 12 | 原方案混入框架现成策略/offload；缩窄后可由 workload、instrumentation、adapter 构成清晰 owned diff |
| 技术深度 | 20 | 13 | 16 | 原方案主题多但因果浅；缩窄后能深入 prefix semantics、residency、queue/prefill 中介 |
| 证据质量 | 25 | 12 | 20 | 当前尚无单卡数据；完成反例矩阵后才可能得分 |
| 可复现性 | 10 | 7 | 9 | 参数化 generator、固定版本、raw logs 可闭环 |
| 取舍与负结果 | 10 | 7 | 9 | kill conditions、负控、FP8 不支持均可成为证据 |
| 沟通与边界 | 5 | 4 | 4 | 必须避免“框架胜负”“通用 agent-aware”过度声明 |
| **总分** | **100** | **64** | **84（仅在 Gate 与实验完成后）** | 当前不能把 84 当已实现成绩 |

硬门槛：

- 真实问题：**条件通过**，公开证据证明 workload 类别，但单卡实例尚未证明；
- 可证伪性：原方案部分通过，缩窄命题通过；
- 所有权清晰：原方案不通过，缩窄后待 G3；
- 资源可行性：原方案不通过，单机制 + 后置 FP8 条件通过。

最终裁决：**RESHAPE**。若 G2 无法证明 stock LRU gap，或 G3 无法隔离 cache priority，则对“策略改进”子命题应 **REJECT**，但仍可保留诚实的行为测量与负结果报告；不要用更多机制挽救一个未成立的问题。

## 11. 可说与不可说的项目叙事

可以说（完成证据后）：

- “在固定 SGLang 版本与单卡 KV budget 下，构造 trace-informed multi-turn workload，定位 exact-prefix、reuse distance 和容量压力的边界。”
- “通过 victim trace 和 computed-prefill 指标证明某类 resume miss 来自 eviction，而非 token drift。”
- “复用现有 eviction priority seam，实现小型 session-state adapter，并用 LRU/SLRU/priority 基线、负控和代价指标评估。”
- “FP8 在具体 GPU/backend 上呈现容量、延迟、质量的分离结果，包括无收益或不支持边界。”

不可说：

- “SGLang/vLLM 原来没有 session-aware/priority eviction，我首次实现了它。”
- “hit rate 提升 X%，所以 TTFT 必然降低 X%。”
- “FP8 在 24GB 消费卡上天然带来 2× 可用容量和加速。”
- “实现了 CPU offload”，如果只是打开框架现成参数。
- “真实 agent workload”，如果实际只是参数化合成；应写 `trace-informed synthetic workload`。

## 12. 第一方/高可信证据索引

### vLLM

- 当前 KV cache / prefix cache 源码：<https://github.com/vllm-project/vllm/blob/cb8104839c141609d99f1254459ef3a4f1bd4263/vllm/v1/core/kv_cache_utils.py>
- 当前 block pool 源码：<https://github.com/vllm-project/vllm/blob/cb8104839c141609d99f1254459ef3a4f1bd4263/vllm/v1/core/block_pool.py>
- APC 官方文档（命中只减少 prefill）：<https://docs.vllm.ai/en/v0.13.0/features/automatic_prefix_caching/>
- 当前 metrics 官方文档：<https://docs.vllm.ai/en/stable/usage/metrics/>
- KV offloading 官方文档：<https://docs.vllm.ai/en/v0.26.0/features/kv_offloading_usage/>
- FP8 KV cache 官方文档：<https://docs.vllm.ai/en/latest/features/quantization/quantized_kvcache/>
- vLLM 官方 FP8 KV cache 工程报告源码：<https://github.com/vllm-project/vllm-project.github.io/blob/main/_posts/2026-04-22-fp8-kvcache.md>
- Agent-aware KV eviction RFC（开放 issue，非已发布功能）：<https://github.com/vllm-project/vllm/issues/37003>
- vLLM × Mooncake agent workload 官方博客：<https://vllm.ai/blog/2026-05-06-mooncake-store>

### SGLang

- Radix cache 当前源码：<https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/radix_cache.py>
- eviction policies 当前源码：<https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/evict_policy.py>
- attention backend / page-size 官方文档：<https://github.com/sgl-project/sglang/blob/main/docs/advanced_features/attention_backend.md>
- server arguments（HiCache、FP8 KV 等）：<https://github.com/sgl-project/sglang/blob/main/docs/advanced_features/server_arguments.md>
- session radix cache 合入 PR：<https://github.com/sgl-project/sglang/pull/27058>
- FP8 path 边界讨论（issue，属于问题报告而非发布保证）：<https://github.com/sgl-project/sglang/issues/10083>

### Agent workload / 硬件能力

- TokenCake（外部调用造成 temporal idle）：<https://arxiv.org/abs/2510.18586>
- KVFlow（workflow future knowledge 与缓存决策）：<https://papers.neurips.cc/paper_files/paper/2025/hash/b7971d31a7d5eb0f1eed2f8f6f368195-Abstract-Conference.html>
- NVIDIA CUDA GPU compute capability 列表：<https://developer.nvidia.com/cuda/gpus>
- NVIDIA CUDA compute capability 功能表：<https://docs.nvidia.com/cuda/cuda-programming-guide/05-appendices/compute-capabilities.html>
- NVIDIA Ada 架构白皮书：<https://images.nvidia.com/aem-dam/Solutions/Data-Center/l4/nvidia-ada-gpu-architecture-whitepaper-v2.1.pdf>

## 13. 本评审的局限性

- 框架 `main` 在 2026-08-04 仍会变化；真正实验必须 pin release/commit，不能把 current-main 能力默认成稳定 CLI 能力。
- 未知用户具体 24GB GPU 型号，因此 FP8 只能给 capability gate，不能先验给性能结论。
- 公开 agent traces 多来自多卡/分布式系统，本文只用它们证明 workload 形态与参数范围，不使用其收益数字预测单卡效果。
- 这是开工前 feasibility review，没有替代 Gate 0 的本机实测；64 分是当前证据评分，84 分只是缩窄方案完成后的条件上限。
