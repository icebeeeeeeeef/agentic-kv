# 最终结论独立反方审计

> **历史评审归档（pre-D14 / NON-AUTHORITY）：**本文审计的是早期 local retention/eviction、offload、FP8 项目 framing。它保留反方攻击与方法论证据，不定义当前执行；当前唯一机制、范围、Gate 与 STOP 以 [PROJECT_PLAN.md](../../project/PROJECT_PLAN.md)、D14 和 [STATUS.md](../../../STATUS.md) 为准。

审计对象：`outputs/agent-prefix-cache-project-selection-review-2026-08-04.md`

审计日期：2026-08-04

## Verdict

**REVISE**

- **P0：0 项。** 没有发现编造已完成结果、把 RFC 动机当成本地实验事实、擅自改变用户冻结项目内核，或足以推翻整个方向的事实错误。
- **P1：5 项。** 当前方向判断基本成立，但 ownership 门槛、Gate 0、基线公平性和执行分支仍会让最终立项裁决失真；修完后才能冻结为 `select/stop` 决策依据。

一句话反方结论：**可以批准这个题进入短期证伪阶段，但当前草案把“必须做出一个新 policy patch”设得过硬，同时没有把 Fermi 容量预算和“单卡数据必须产出结构性裁决”写成真正的门；因此现在只能批准 Gate 0，不能把完整项目或 86 分潜力一并预授权。**

## P1-1：把 engine policy patch 误设成 ownership 的唯一合格形态

### 证据位置

- L18、L34、L147、L216、L226、L310、L335、L352、L429、L449、L462 都把最终强项目收敛到“一个 owned policy/decision/diff”。
- L448 又说负结果也是合格交付；但 L457 规定没有“真实 owned decision”就拒绝立项。
- L262 要求候选在线信号“没有被库存策略等价表达”，容易把“有新概念”误当成通过门槛。

### 为什么是 P1

这比用户新增的项目选择 SOP 更严格，也偏离了本项目真正可防守的 ownership 定义。该 SOP 允许以下三者至少一项形成核心 ownership：

1. 自建、可验证的测量/回放/生命周期仪器；
2. 对真实框架源码路径的独立归因；
3. 能改变工程决策的机制边界分析。

因此，**科学上成立的负结果不要求硬凑一个新 eviction policy**。同样，复现/移植已有 RFC 或 prior art，再验证其单卡边界，也不因概念不新而失格。真正应拒绝的是“只开现成开关、画命中率曲线、没有自建仪器或机制归因”，而不是“没有新 policy”。

当前文本会产生两种错误：

- Gate 0 没发现 gap 时，一边要求诚实停止，一边又把没有 policy patch 的项目判为 ownership 不足；这会反向激励为简历强行制造策略。
- 已有 priority/TTL/RFC 思路即使尚未在 pinned commit 上被独立复现，也可能因“不是新信号”被提前淘汰，重新引入近似学术 novelty 门槛。

### 必须怎么改

把成功路径明确拆成两条，二者都允许成为主项目，但证据标准不同：

- **机制改动路径**：实现/移植/复现一个局部 policy，要求 A/B、ablation、删除测试和代价闭环；不要求概念原创。
- **仪器与机制裁决路径**：自建真实引擎内的 lifecycle trace/replay/oracle 或低扰动 instrumentation，给出源码归因、结构性边界、库存策略选择结论和负结果；不要求 policy patch，但不能退化为外部压测脚本加曲线。

相应修改 L34、L147、L216、L262、L352、L443–458、L462。尤其把 L262 改成类似：

> 新工作不能只是翻转一个已有开关；允许复现/移植 prior art，也允许以自建仪器和机制边界为主贡献。若做 candidate，其输入信息预算必须与公平基线区分清楚。

86/100 只能绑定到**完成后的证据包**，不能只绑定到“单策略 patch”。

## P1-2：Gate 0 缺少先于实验基础设施的 Fermi 可行性门

### 证据位置

- L251–262 从“固定 commit/model/backend/GPU”直接进入实机测量。
- L332–334 把容量压力和 oracle 推迟到 Week 3。
- 全文没有在开工前计算该模型在 24GB 卡上的 KV bytes/token、可用 cache tokens、block/page 取整损耗、预期 working set 和压测运行时预算。

### 为什么是 P1

单卡能否对 eviction 做出真实裁决，首先是容量算术问题，不是框架选择问题。若所选模型在留出权重、workspace 和运行时 buffer 后只有很小或极不稳定的 KV 区间，或者需要不现实的 session/token 数才能触发淘汰，那么两周后才发现这一点会直接吃掉 8–10 周预算。

至少需要在 Day 1 前后完成：

```text
KV bytes/token
  ~= 2 × num_layers × num_kv_heads × head_dim × dtype_bytes

usable cache tokens
  ~= framework 实测可分配 KV bytes / 实际 KV bytes/token
  （再考虑 block/page 粒度、量化 scale、hybrid attention 与预留显存）

pressure ratio
  = active reusable working set / usable KV capacity
```

还应估算最小/典型/高压三个 cell 需要的 session 数、prefix 增长和总运行时间，确认正式重复实验在预算内完成。

### 必须怎么改

在 Gate 0 前新增 **Gate -1 / Fermi gate**，产物只需一页 capacity sheet 加一次框架实测校准：

- 模型与 dtype 的理论/实测 KV bytes/token；
- 权重和非 KV 运行时占用后，可控的 KV budget 区间；
- 预计发生 eviction 的 working-set/cache 区间；
- 低压负对照和高压主场景都能在同一张卡上稳定复现；
- 预计总请求/token/重复次数不超出 8–10 周计算预算。

若算术不成立，只调整模型大小、cache budget 和 workload scale 这些冻结内核允许的实验参数；不要以此偷换项目方向。

## P1-3：“两格或一条 held-out trace”不能保证单卡数据有结构性裁决权

### 证据位置

- L238、L301 已列出 working-set/cache ratio、reuse distance、branching、arrival，方向正确。
- 但 L260 的正式通过标准只是“至少两个压力 cell 或一个 held-out trace 有稳定 headroom”。
- L288、L337 把 held-out replay 当验证，但没有要求它验证哪条结构关系。

### 为什么是 P1

单张卡不能证明生产规模，但它必须回答可迁移的结构性问题，例如：

- gap 在 `working set / usable KV capacity` 的哪一侧出现；
- reuse distance 相对容量跨过什么区间后，LFU/SLRU/候选排序发生反转；
- branching 是独立原因，还是只通过共享比例与 working set 改变结果；
- 何时应启用/禁用策略，何时增大 cache 或用 FP8 已足够。

两个孤立 cell 可以是挑点，一条 held-out trace 也只能证明一个样本可复现，不能自动产生结构性裁决。当前门槛仍可能放行“在一个恰好有利的点提升”的项目。

### 必须怎么改

保持简单，不做全因子网格，只冻结两个主坐标：

1. `ρ = reusable working set / usable KV capacity`；
2. `D = reuse distance（按 block/token）/ usable KV capacity`。

branching/arrival 作为生成这两个坐标的 workload 参数和少量 matched control。Gate 0 的数据门改为：

- 在连续、机制一致的区间发现 headroom，而不是两个任意 cell；
- 明确至少一个 break-even/ordering/losing boundary；
- 用独立 trace family 或 held-out replay 验证该边界方向，而不只是复现单点数字；
- 输出一个实际决策：选哪种库存策略、何时不做 candidate、何时 FP8/增加容量已经吃掉 headroom。

这才满足“单卡数据有结构性裁决权”，又不会把矩阵扩大成笛卡尔积。

## P1-4：`priority` 被硬编码为强基线，但在默认输入下可能只是 LRU 的别名

### 证据位置

- L123、L131、L258、L309、L366、L372、L408 多次把 SGLang `priority` 与 LFU/SLRU 并列为必须打过的库存强基线。

### 源码核对

- SGLang 当前公开 server 参数只把 `lru/lfu/slru/priority` 暴露为 radix eviction choices：[server_args.py](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/server_args.py)。
- RadixCache 插入时读取 `getattr(req, "priority", 0) or 0`，并沿路径传播 priority：[radix_cache.py](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/radix_cache.py)。
- priority eviction 的排序键是显式 priority，再以 recency 打破平局：[evict_policy.py](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/evict_policy.py)。

因此，若 replay 请求没有合法的 priority 输入，所有节点 priority 都为 0，`priority` 会退化为 recency/LRU。若为了让它变强而用未来 reuse 赋 priority，它又变成 oracle，不是公平在线库存基线。

### 必须怎么改

不要写死“至少 LRU/LFU/SLRU/priority”，改为三类：

- **无额外 metadata 的库存基线**：在 pinned commit 上端到端可选且语义相关的策略，通常至少 LRU/LFU/SLRU；
- **带 workload 合法在线 metadata 的 stock-priority 基线**：只有 trace 本来就有可在请求到达时得到的 priority，或预注册一个不读未来的映射时才纳入；同时公开映射规则；
- **future-aware priority**：只能归入 A5 oracle，不能进在线 A2。

候选与 priority baseline 必须比较“输入信息预算”，不能只比较策略名字。

## P1-5：执行 DAG 自相矛盾，失败分支仍会进入不存在的 2×2

### 证据位置

- L251 标题写 Gate 0 是前 7–14 天；L332–334 却到 Week 3 才完成强基线/oracle并作 Gate 0 决策。
- L35、L264–273、L334 规定无 headroom 就停止 candidate。
- L197–203、L338 却无条件安排 `stock × candidate` 与 `BF16 × FP8` 的 2×2；无 candidate 时该矩阵不存在。
- L259 的“埋点差异足够小”也没有预注册 overhead/effect margin，执行时容易事后解释。

### 必须怎么改

画成最小分支即可：

```text
Gate -1 Fermi 可行
  -> Gate 0（最迟 Week 2 或明确改名为前三周）
     -> 有结构性 headroom：机制改动路径，Week 8 可做 2×2
     -> 无 headroom：仪器/机制裁决路径，只做 stock BF16-vs-FP8 容量实验或跳过 FP8
```

同时给 A0/A1 一个预注册的 observer-effect 判据，例如端到端主指标差异的 CI 落在预设非劣区间、事件丢失率和 CPU 开销低于固定门槛；不要保留“足够小”这种事后口径。

## 已核对、无需作为阻断项的问题

1. **没有违反冻结项目内核。** 单框架、测量驱动、淘汰/offload 二选一、FP8 作为附带轴仍在原方向内部；只是应允许仪器/机制裁决成为合法完成路径。
2. **上游动机与本地事实大体分开了。** L61–76、L140–147、L474–475 明确把 RFC/发布方数字当问题空间证据，不当本地收益；这符合新增 SOP 中“官方公开动作证明问题真实且尚未统一解决”的意图。
3. **SGLang 的 leaf eviction 事实成立。** 当前 `evict()` 从 `evictable_leaves` 建 heap，删除叶后才把成为叶的父节点加入：[radix_cache.py](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/radix_cache.py)。但 L123 应补这个直接链接，现有两个链接只覆盖策略工厂/排序键。
4. **vLLM reverse free/tail-first 描述有源码依据。** 当前 manager 明确要求 reverse order 使尾部 block 先被淘汰；草案没有把它夸成通用最优策略。
5. **RFC 状态表述保守。** SGLang #24656 被写作 closed/inactive，vLLM #37003 的实现/早期结果明确写成 RFC 作者“声称”，没有伪装为本地验证。

## 冻结前最小修改清单

只需做以下五处结构修改，不需要扩写更多背景：

1. 把 ownership 从“必须有新 policy”改为“机制改动”或“自建仪器 + 源码归因 + 结构性裁决”两条等价路径。
2. 在 Day 1 加一页 Fermi capacity gate。
3. 把 Gate 0 的单点门改为 `ρ/D` 两坐标上的边界门，并要求 held-out 验证边界方向。
4. 重写 priority 基线，按在线信息预算区分 stock、metadata-aware 和 oracle。
5. 对齐 7–14 天/Week 3 时间口径，并给“有 candidate/无 candidate”两条 FP8 分支。

完成这些修改后，我的预期 verdict 是：

> **PASS：批准先做 Fermi gate + 最多两周的 Gate 0；Gate 0 之后，根据证据选择“机制改动”或“仪器/机制裁决”完成路径。prior art 复现与边界扩展允许通过，不以学术 novelty 或一定产出 engine patch 为门槛。**

## 2026-08-04 修订后复核记录

### 最终状态

**PASS（P0=0，剩余 P1=0）**

已对最新版 `outputs/agent-prefix-cache-project-selection-review-2026-08-04.md` 定向复核，上一轮五个阻断项均已实质关闭：

1. **P1-1 ownership/novelty：已关闭。** L101–109、L159–170、L242–247、L338–349、L441、L589、L594 已明确“机制改动”与“自建仪器 + 源码归因 + 结构性裁决”两条完成路径；允许复现/移植 prior art，不要求 idea novelty，也不再为负结果强制 engine patch。
2. **P1-2 Fermi gate：已关闭。** L295–325 新增 KV bytes/token、cache capacity、`rho` 压力估算、实机 smoke 与 kill condition；执行表在 Day 1–5 先过 Gate F，不再到 Week 3 才发现单卡不可达。
3. **P1-3 结构性裁决：已关闭。** L278–293 定义 `rho/D/S/F/R`，L336 要求相邻压力 cell 的机制一致趋势并用 held-out 分布复核，L379–390 给出有限矩阵；主结论已经从单点百分比改成 break-even/ordering/losing boundary。
4. **P1-4 priority 公平性：已关闭。** L143、L334、L338、L398、L497 已按输入信息预算区分无 metadata 库存策略、合法在线 priority 与 future-aware oracle；不再把全 0 priority 当独立强基线。
5. **P1-5 执行 DAG：已关闭。** Gate F 为 Day 1–5、Gate S 为 Week 2–3；L222–229 与 L427 明确有 candidate 才做 policy x dtype 2x2，无 candidate 时只做 stock dtype 边界或跳过 FP8；A0/A1 也已有预注册 observer-effect 判据。

新增源码断言也已抽查：SGLang PR #27058 确为 2026-06-23 merged，其设计是给普通可淘汰 Radix KV 加 session tag，并在 close 时释放对应独占链；草案将它概括为“session close 后回收”，且与 paused-but-live retention 分开，表述准确。

### 非阻断性收尾

- 开工 pin commit 后，把 GitHub `main` 源码链接换成对应 commit permalink；正文 L606 已承认该漂移风险，因此不阻断当前立项裁决。
- `KVFlow/Continuum` 在 prior-art 表中最好补一级论文链接；目前只承担路线举例，不承载裁决关键数字，因此不升级为 P1。

最终允许冻结的裁决是：

> **批准 Gate F + Gate S 的限时证伪阶段。Gate S 后可以进入局部机制路径，也可以以自建仪器、源码归因和结构边界完成负结果路径；完整项目价值不依赖学术 novelty、必有性能提升或必有 engine patch。**
