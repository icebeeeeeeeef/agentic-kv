# 多轮 Agent KV Cache 项目：面试可防守性与个人 Ownership 对抗评审

> 评审对象：用户已经冻结的项目方向，不重选赛道。  
> 证据基础：`outputs/ai-infra-inference-campus-market-fit-2026-08-04.md` 的岗位、面经和团队动作；面经样本只用于识别追问模式，不视为市场总体概率。  
> 评审状态：项目仍是 roadmap，尚无已实现、已测量或可复现的个人成果。  
> 评审标准：招聘信号优先看角色相关性、个人 ownership、机制深度、证据质量、可复现性和诚实边界，不看技术名词数量或题目新颖度。

## 0. 结论

**总 verdict：`reshape`，不是 `reject`。**

方向与 serving/cache runtime 岗位高度相关，不需要换题；但当前描述仍把五件事放在同一个项目外壳中：workload generator、行为分析、淘汰策略、offload、FP8，以及潜在的 vLLM/SGLang 双框架。它们并不天然形成一条因果链。

必须收敛成：

> **一个框架 + 一个可证伪的原生缓存失配现象 + 一个本人修改的在线策略机制 + 一套可复现的因果实验。**

其中：

- workload generator 与埋点是支撑主线的实验设施，不是默认的核心创新；
- FP8 是用户冻结的独立附带轴，但从主机制移除后核心问题仍成立，所以不能与策略收益混成一个结论；
- offload 只能是现成路径下的对照或主线闭环后的扩展，不能再成为第二个独立 owned mechanism；
- vLLM 与 SGLang 不能同时做深度实现。第二框架从项目中删除后核心问题完全不变，因此双框架只会稀释 ownership。

### 能否撑住 20–45 分钟追问

- **按当前模糊 roadmap 完成一个“生成请求 + 调框架 + 画命中率图”的版本：不能。** 面试通常会在 8–12 分钟内穿透到“你到底改了什么、为什么不是框架原生行为、因果怎么证明”。
- **完成下文的最小可信主线：可以稳定支撑约 20–30 分钟。** 前提是能沿真实数据路径解释代码、基线、指标、ablation 和失败条件。
- **要支撑 35–45 分钟：有条件可以。** 需要额外具备一次真实错误假设或难 bug 的诊断过程、一个可量化的 break-even、一次删除测试、至少一个策略输掉的 workload，以及对单卡结论不能外推到多节点的清楚回答。

报告中的 B 样本支持这个门槛：14 条记录里，严格项目拷打与条件/边界问题各出现于 9 条，系统诊断 10 条，框架机制 8 条，手写代码 10 条。样本有候选人相关性偏差，不能外推概率；但它足以说明面试不会停在“我用了 vLLM/SGLang”。

## 1. 评审 lens

| 项目 | 冻结口径 |
|---|---|
| 目标岗位 | 国内校招/实习的 LLM serving、cache runtime、推理引擎系统侧；kernel/编译/芯片适配不是该项目的直接证据 |
| 候选人级别 | 大三学生，个人项目 |
| 评估者 | 简历筛选者、推理/serving 技术面试官、TL |
| 当前状态 | 全部为 `roadmap`，没有可写成完成态的项目 claim |
| 时间/硬件 | 8–10 周业余时间，单张 24GB 消费级 GPU |
| 数据约束 | 没有真实线上私有流量；可使用参数化合成 workload、公开 trace 或公开统计作校准 |
| 核心缺口 | 目前没有选定框架 commit、原生失配证据、具体代码 seam、单一策略机制与删除测试 |

## 2. 当前 roadmap 分与成功完成预期分

### 2.1 当前 roadmap：58/100，且硬门槛失败

这个分数评的是“现有项目设计”，不是可放简历的完成成果。因为当前没有 shipped artifact，任何性能结果仍是 0 条。

| 维度 | 当前分 | 对抗判断 |
|---|---:|---|
| 角色相关性与问题价值 | 14/15 | 与 KV/cache runtime、框架源码、性能诊断直接相关，企业公开动作也证明问题真实 |
| 个人 ownership | 5/15 | 只说“小范围改进”，没有明确本人负责的状态、决策与真实数据路径；高度可能退化为 glue/config |
| 机制与跨层深度 | 10/20 | 已考虑 workload、cache 和时延，但尚未形成 workload→资源压力→策略决策→系统指标的唯一因果链 |
| 证据与实验严谨性 | 11/25 | 已提出 A/B、TTFT/TPOT、负例，但没有固定 baseline、oracle/headroom、ablation、重复策略和归因方法 |
| 工程完整性与复现 | 5/10 | 有版本、trace、原始数据意识；目前没有第三方可运行的 artifact |
| trade-off 与失败边界 | 8/10 | 明确不扩 RDMA/多机，也要求报告负例；这是当前 roadmap 最强部分之一 |
| 沟通与包装 | 5/5 | 问题边界和诚实口径清楚 |
| **合计** | **58/100** | 数值进入 reshape 区间；ownership、falsifiability、measurement、reproducibility、defensibility 的硬门槛仍未通过 |

### 2.2 窄化主线成功完成：预期 88/100

| 维度 | 成功完成分 | 必须兑现的证据 |
|---|---:|---|
| 角色相关性与问题价值 | 14/15 | 在真实 vLLM 或 SGLang 路径上证明一个多轮 workload 下的原生失配 |
| 个人 ownership | 13/15 | 本人修改在线缓存决策路径，拥有状态、排序/选择逻辑、测试、诊断与回退 |
| 机制与跨层深度 | 17/20 | 能连接请求形态、reuse distance/cache pressure、block 生命周期、调度干扰、GPU 计算与 TTFT/TPOT |
| 证据与实验严谨性 | 22/25 | 原生基线、instrumentation-only、候选策略、oracle/headroom、删除测试、ablation、尾延迟、负例、重复运行齐全 |
| 工程完整性与复现 | 8/10 | 固定 commit、环境清单、一键重放、结构化原始结果、测试和失败 artifact |
| trade-off 与失败边界 | 9/10 | 定量 break-even、输掉 workload、开销、回退与不外推边界 |
| 沟通与包装 | 5/5 | 一句话问题、一个机制、一组条件式结果，claim state 明确 |
| **合计** | **88/100** | 所有硬门槛通过后可 `select` |

两个重要下限：

- 如果最终只有 workload generator、框架调用和图表，即使实验做得整齐，预期约 **65–68/100**，并且 ownership 硬门槛仍失败，不能靠平均分补救。
- 如果策略有正数但没有 instrumentation overhead 对照、删除测试、ablation 和失败 workload，证据门槛仍失败；“提升 X%”不会自动变成强项目。

## 3. 核心问题必须改写成可证伪形式

### 3.1 不够安全的原表述

> 研究多轮 Agent workload 下 prefix/KV cache 复用行为，并做淘汰、offload、FP8 改进。

问题在于：它包含多个能独立成功或失败的目标，无法指出哪项结论被证伪时项目应该停。

### 3.2 可进入实现的主问题

> 在固定的 `[一个框架 commit]`、同一 KV 容量和同一请求 trace 下，先证明原生缓存策略在 `[一个明确的多轮复用模式]` 中存在可重复的错误淘汰或重算 headroom；再检验一个只使用线上可观测历史信息的 `[候选决策信号]`，是否能降低 p95 TTFT/重算量，同时不让 TPOT、goodput、显存和策略开销越过预声明阈值。

这里的 `[候选决策信号]` 不能在开工前凭想象固定。先读源码、跑原生 trace，证明具体失配后再准入策略。可能的信号必须来自真实请求路径可见信息；不能使用 generator 知道的未来 turn、下一次到达时间或未来共享关系。

### 3.3 假设与因果链

```text
[多轮共享、间隔、并发与容量压力]
  -> [原生策略能看到的信息不足，出现特定 block 的错误保留/淘汰]
  -> [本人实现的在线决策信号改变 victim 选择]
  -> [减少后续重算或加载，同时付出元数据/决策开销]
  -> [p95 TTFT 改变；TPOT、goodput、内存与正确性是 guardrail]
```

如果原生策略与离线 oracle 的差距很小，就没有改策略的因果 headroom。此时应停止“为了有改动而改动”，转入负结果路径，而不是调 workload 直到出现胜例。

## 4. 硬门槛逐项判断

| 硬门槛 | 当前判断 | 通过条件 | 一票否决情形 |
|---|---|---|---|
| Target | **通过** | 项目只声称 serving/cache runtime 系统侧证据 | 包装成全栈推理引擎、CUDA kernel 或分布式 KV store |
| Real problem | **部分通过** | 企业动作证明问题真实；还需在自己的选定框架/模型/workload 中观察到可重复失配 | 只引用 Tair/Mooncake，自己的运行中没有现象 |
| Falsifiability | **失败** | 固定一个失配、一个策略机制、主指标、guardrail 和拒绝阈值 | 同时追求命中率、offload、FP8、双框架，任意一项有图就算成功 |
| Ownership | **失败** | 改动真实 block/cache 决策路径，拥有状态/invariant/测试/诊断/回退 | 只发 HTTP 请求、调配置、解析日志或调用框架已有 offload/FP8 |
| Feasibility | **条件通过** | 单框架、单卡、一个策略可做；FP8 先 capability gate | 双框架深改、多节点/RDMA、自建远端 store；硬件不支持仍宣称 FP8 结果 |
| Baseline | **部分通过** | 至少有原生未改、原生+埋点、候选策略；另有离线 oracle 或合理上界证明 headroom | 只与自己挑的弱策略比，或把 no-cache 当唯一 baseline |
| Measurement | **失败** | 固定 trace、cache reset、warmup、重复、随机实验顺序、服务端时间、尾延迟和 guardrail | 只报平均命中率/吞吐，客户端成为瓶颈，或不同策略运行不同请求序列 |
| Reproducibility | **失败** | 固定 commit/环境、单命令重放、原始结构化结果、manifest、测试日志 | 只有截图、Notebook 手工步骤和最终表格 |
| Defensibility | **失败** | 能完成五层 why/alternative/failure/scale 追问及 20 分钟证据演示 | 两条追问链退化成概念八股或“框架就是这样” |
| Credibility | **可通过** | roadmap/shipped/experimentally validated/replay/simulated 分开写 | 把公开 trace 写成真实线上流量，把调用内置 FP8 写成自己的量化实现 |

当前 failed hard gates 决定 verdict 必须是 `reshape`，不能用 58 分或未来预期分绕过。

## 5. Workload generator：什么时候只是脚本

### 5.1 会被面试官判成脚本的版本

- 拼几段 system prompt/user prompt，按固定循环请求 API；
- 只支持“共享前缀长度”和“并发数”两个参数；
- 用客户端 wall-clock 当 TTFT，无法排除客户端排队与网络抖动；
- generator 在每个 A/B 运行中随机生成不同请求；
- 没有 tokenizer 后的真实 prefix ground truth；
- 用“Agent workload”命名，但没有 turn、branch、idle/reuse distance 或工具结果膨胀等区别于普通 batch 的结构；
- 生成器把未来 turn/下一次访问时间直接提供给在线策略，造成信息泄漏。

这种实现不能成为主简历贡献。删掉它、改成固定 JSON trace 后，策略问题仍然成立，说明它只是支撑依赖。

### 5.2 达到可信实验设施的最低条件

1. **语义明确。** trace 至少表示 session、turn、arrival time、tokenized prefix、non-prefix tokens、branch/fan-out、共享关系、模型输出长度或其控制方式。
2. **参数对应机制。** 共享比例、inter-turn gap/reuse distance、并发/到达率、cache pressure/churn、prefix 长度和 branch 结构必须能解释它们如何改变缓存机会。
3. **ground truth 在 token/block 层。** 文本看似相同不等于 tokenizer 后 block 对齐；需要预先计算可复用 token/block 上界。
4. **可重放。** generator 先产出不可变 trace；所有策略重放同一 trace、seed 与到达时间，不在 A/B 过程中重新随机生成。
5. **线上信息边界。** 在线策略只接触真实运行时可见的历史状态；未来访问只用于离线 oracle，不进入候选实现。
6. **服务端观测。** TTFT/TPOT、block alloc/free、hit/eviction/recompute 以服务端事件为主，客户端只负责施压和 E2E 校验。
7. **校准而非冒充。** 用公开 agent trace 或公开统计做分布校准；若只有合成负载，claim 必须写“参数化合成/trace replay”，不写“真实线上 Agent 流量”。
8. **自测 invariants。** 同 seed 生成完全一致的 trace；声明共享 X tokens 时 tokenizer 后 ground truth 一致；到达序列、turn 依赖和 branch 不被并发 driver 打乱。

### 5.3 generator 的删除测试

- 把一次生成的 trace 固化，完全移除 generator 运行时，直接 replay；策略相对原生的效果应在噪声内保持。
- 若删除 generator 后收益消失，优先怀疑 generator 与策略存在信息耦合或特殊 workload 过拟合，不能把收益归因给通用 cache policy。
- 简历主句应从“发现的失配和 owned policy”开始；generator 只作为方法证据出现。

## 6. 双框架：明确 reject

**Reject：同时在 vLLM 和 SGLang 中做策略实现、统一 adapter 或横向性能排名。**

理由不是时间不够这么简单：

1. 两个框架的 block 生命周期、prefix 索引、scheduler、指标与版本变化会引入独立因果变量；“同一个 workload”不等于公平比较。
2. 两套浅 patch 会让面试官无法判断你真正理解哪条数据路径。
3. 为统一两框架写 adapter 是 glue ownership，不会替代缓存决策机制。
4. 删除第二框架后主问题完全不变，按 removal test 它只能是 extension。

允许的最小做法：开工前用短 spike 比较两者的源码 seam、单卡可运行性、可观测事件和 FP8 支持，随后冻结一个框架 commit。主线完成后若仍有时间，可在第二框架只 replay 一条代表 workload 做外部效度观察；不能在简历中暗示两者都做了深度源码改造。

## 7. 策略改动的 admission、删除测试与 ablation

### 7.1 改策略之前的 admission gate

必须先回答：

1. 原生策略在选定 commit 上到底根据什么状态做 victim/保留决策？不能从旧博客或惯例猜。
2. 在固定 trace 下，哪一个 block/prefix 被错误淘汰或错误保留？给出事件时间线。
3. 离线 oracle/上界与原生相差多少？如果没有足够 headroom，不准进入策略实现。
4. 候选信号在线可见吗？它在真实请求中是否存在，还是只有合成 generator 知道？
5. 额外元数据、排序复杂度、锁竞争和决策时间的预算是什么？

### 7.2 最小对照组

| 组 | 目的 |
|---|---|
| A0：未改原生框架 | 库存行为和性能基线 |
| A1：原生策略 + 完整埋点 | 测出 instrumentation 自身开销；若 A1 已改变结论，后续实验无效 |
| A2：候选策略 | 完整机制 |
| A3：候选代码路径但核心信号关闭/固定 | 区分“多了代码/数据结构”与“决策信号”造成的效果 |
| A4：离线 oracle 或可解释上界 | 量化可用 headroom；oracle 不冒充可上线方案 |
| A5：必要时 no-reuse/no-cache 诊断组 | 校验 TTFT 变化确实由重算/复用路径造成，不作为唯一竞争 baseline |

### 7.3 必须做的删除测试

1. **代码删除。** revert 候选策略 commit 或构建时回到原生选择逻辑，独特收益应回到 A1 噪声范围。
2. **信号删除。** 保留候选数据结构和函数调用，只去掉核心决策信号；用于证明收益不是 incidental code-path change。
3. **埋点删除。** 关闭高成本 trace，证明最终性能数字不是 measurement perturbation。
4. **generator 删除。** 固定 trace 直接 replay，证明机制不依赖 generator 的隐藏信息。
5. **压力删除。** 在无 cache pressure 或几乎无复用时，候选策略应没有收益且不应显著退化；否则可能只是改变了其他调度变量。

### 7.4 机制级 ablation

ablation 只能针对最后实际实现的机制，不能预先伪造组件。若候选评分包含 recency、prefix value、estimated reuse 等多个项，则逐项置零或固定，报告：

- 哪一项贡献主要收益；
- 哪一项只在特定 workload 有用；
- 组合是否只是过拟合合成 trace；
- 元数据与决策开销随 active block/session 数如何增长；
- 遇到 in-flight/refcount block、取消请求、异常结束时如何保持不变量和回退。

代码量不是深度指标。几十行真实 victim-selection 改动，只要有源码路径、invariant、诊断、ablation 和边界，也比一千行 adapter 更有 ownership。

## 8. 最小可信实验设计

### 8.1 控制变量

- 策略主实验固定一个框架 commit、GPU、模型、dtype、KV 容量、scheduler 配置和请求 trace。
- 每个实验前按预声明方法重置 cache 与进程状态；记录冷启动与 warmup，不把前一组的热 cache 带入后一组。
- A/B 顺序随机化或交错，至少做多次独立重复并报告分布/置信区间；不能只挑最好一次。
- driver 先证明没有成为瓶颈；以服务端事件和时间为归因主体。
- 先用固定精度完成策略结论。FP8 不与策略第一次 A/B 同时改变，否则无法归因。

### 8.2 最小 workload，而不是笛卡尔积

至少保留五类有机制意义的区域：

1. 中等共享、可形成 headroom 的目标区；
2. 低共享/随机前缀；
3. 高共享但无容量压力；
4. 长 inter-turn gap + 高 churn；
5. 突发并发或 branch/fan-out 使 scheduler 与缓存相互干扰。

每一类先写出预期：原生为何可能输、候选为何可能赢、哪项指标会先退化。不能先看结果再补故事。

### 8.3 指标层次

| 层次 | 指标 | 用途 |
|---|---|---|
| 主结果 | p95 TTFT，或固定 SLO 下的 goodput（二选一为主） | 面向用户/serving 的真实结果 |
| 机制诊断 | token/block hit、eviction、重算 token、occupancy、reuse distance | 解释为什么，不作为唯一成功标准 |
| guardrail | TPOT、E2E、吞吐/goodput、显存、CPU/元数据、策略决策时间 | 防止命中率提高但系统变慢 |
| FP8 独立轴 | 可容纳 token/block、质量/精度、TTFT、TPOT、吞吐、后端兼容 | 不把容量增长自动写成命中/延迟收益 |

## 9. FP8 与 offload 的边界

### 9.1 FP8：保留，但从主机制拆出

FP8 从主问题删除后，淘汰策略问题仍完整，因此它是独立实验轴：

- 先做 capability gate，固定具体 GPU、框架 commit、模型、attention/backend；
- 若可运行，先比较库存策略下 BF16/FP8 的容量、质量与延迟，再决定是否有必要做 `policy × dtype` 的 2×2 交互实验；
- 没有显著 interaction 时，FP8 与策略分别报告，不合并成“FP8 策略提升 X”；
- 调用框架内置 FP8 只能写“评估/验证 FP8 KV cache”，不能写“实现 FP8 量化”或“开发 FP8 kernel”；
- 若消费卡不支持该路径，这是兼容性结果，不得用模拟数字替代，也不应占主简历 bullet。

### 9.2 offload：默认 reject 为第二机制

- 复用框架现成 CPU/offload 路径做“restore 与 recompute”成本对照，可以作为 baseline；
- 自己修改分层放置、prefetch、传输协议或远端 store 会形成第二条独立因果链，应从 8–10 周主项目排除；
- 单卡 CPU/PCIe 结果不能写成 RDMA、多节点或生产级 offload 结论。

## 10. 负结果如何仍形成招聘信号

负结果不是“没做出来”。强负结果必须同时有假设、足够统计功效、因果证据和决策后果。

| 负结果 | 可形成的强信号 | 不能说的话 |
|---|---|---|
| 原生策略接近 oracle，无改进 headroom | 证明你建立了 oracle/上界、没有为了简历硬改；给出哪些 workload 下值得/不值得优化 | “框架已经完美”“所有 Agent workload 都无需新策略” |
| 候选策略只在合成 workload 赢，公开 trace/replay 不赢 | 识别 distribution mismatch，拒绝上线候选机制，说明 generator 过拟合 | 只展示合成胜例并隐藏外部验证 |
| 候选策略命中提高但 TTFT/TPOT 退化 | 量化 metadata/排序/锁开销与 break-even，做出 rollback 决策 | 只报命中率提升 |
| 低压力或长 idle 区间无收益 | 给出容量压力、reuse distance 与收益的 break-even 曲线 | 用平均结果掩盖输区 |
| FP8 在目标消费卡/后端不可用 | 形成可复现 compatibility artifact，保护主线不被错误假设拖垮 | 模拟容量后写成实测，或写“完成 FP8 优化” |
| 重复实验无统计显著差异 | 报告方差、最小可检测效应和停止规则 | 把单次最好结果当提升 |

### 负结果仍能高分的条件

若本人完成真实埋点、候选策略 patch、oracle/headroom、删除测试、重复实验，并最终证伪候选机制，预期仍可达到约 **83–86/100**。个人判断力和证据质量不会因“没有正收益”消失。

若只是没有跑通、没有足够样本或没有找对 benchmark，则不是负结果，而是不完整项目。

## 11. 最可能击穿原叙事的追问

| 追问 | 被击穿的回答 | 可防守证据 |
|---|---|---|
| “你到底改了哪个模块、哪个函数、哪个状态？” | “我在 vLLM/SGLang 上做了 workload 和参数调优。” | 固定 commit 的源码路径图、owned diff、调用/事件时间线 |
| “为什么叫 Agent workload，和普通 prefix batch 有什么机制差异？” | “因为请求是多轮对话。” | turn gap、branch、tool-result 增长、reuse distance、并发交错如何改变 cache pressure |
| “你的策略是否偷看了下一轮什么时候来？” | generator 把 future turn 直接给 policy | 在线可观测字段清单；未来信息只存在于离线 oracle |
| “命中率怎么定义？” | request/token/block hit 混用 | 三种口径、框架事件来源、为何主结果用 TTFT/goodput |
| “为什么不是 scheduler 或 warm cache 造成的？” | 每个版本各跑一次、请求顺序不同 | 同一固定 trace、cache reset、A1 埋点对照、随机顺序和重复实验 |
| “删除你的代码后会怎样？” | 只关一个配置但结果没复现 | revert/deletion test；A1/A2/A3 原始结果 |
| “原生策略真的次优吗？” | 只与 no-cache 或人为弱 baseline 比 | 原生时间线、offline oracle/headroom、具体被错误淘汰的 block |
| “为什么不用现成 HiCache/LMCache/offload？” | “我的更快。” | 层次边界：你研究单机在线 victim 决策；现成系统作为依赖/对照，功能与 claim 分开 |
| “为什么做两个框架？” | “为了更全面、命中更多 JD。” | 正确回答是没有双做；说明 removal test 和 scope 决策 |
| “FP8 为什么提高命中率？” | “容量减半所以必然命中更高。” | 只有发生容量淘汰且后端可用时才可能转化；同时报告质量和 prefill/decode 回归 |
| “策略开销在 10 倍 session/block 下如何？” | 只报小规模均值 | 复杂度、元数据字节、decision latency 随规模曲线；明确单卡外推限制 |
| “并发取消或 in-flight block 被选中怎么办？” | 没考虑 refcount/lifecycle invariant | 单元/集成测试、不可淘汰条件、异常回退 |
| “为什么不做 RDMA/P/D？” | “没时间。” | 第一性约束：单卡无法公平验证网络/拓扑；保留机制理解、不伪造生产证据 |
| “别人如何复现你的 X%？” | “照 README 大概跑。” | 环境 manifest、单命令、固定 trace、raw data、聚合脚本、commit 与结果 hash |

只要其中两条回答退化为框架定义或泛泛经验，20 分钟 defensibility gate 就没有通过。

## 12. 20–45 分钟面试展开结构

| 时间 | 可讲内容 | 必备 artifact |
|---:|---|---|
| 0–4 分钟 | 真实现象、为什么是 serving/cache 问题、核心可证伪问题 | 原生行为 trace + 一张失配时间线 |
| 4–10 分钟 | 选定框架的请求→prefix/block→分配/复用→淘汰路径 | 固定 commit 的源码路径图、事件定义 |
| 10–16 分钟 | workload 参数与 cache opportunity/reuse distance 的关系 | trace schema、ground truth、自测 |
| 16–24 分钟 | owned policy 的状态、invariant、复杂度、替代方案 | diff、测试、最难 bug/错误假设 |
| 24–32 分钟 | baseline、A/B、ablation、删除测试、统计与尾指标 | manifest、raw results、重复分布 |
| 32–38 分钟 | 输掉的 workload、break-even、rollback | negative cases、边界图 |
| 38–45 分钟 | FP8 独立轴、单卡外部效度、为何拒绝双框架/RDMA | capability report、non-goals、claim ledger |

如果缺少第 16–32 分钟的 owned mechanism 与 causal evidence，项目不能靠更多背景知识填满 45 分钟。

## 13. 最小可信实现与里程碑 gate

### M0：冻结选择，不产生简历 claim

- 对两个候选框架只做短期可行性探针；冻结一个 commit、模型、GPU/backend。
- FP8 capability gate 只记录可运行性，不与主线同步调试。
- 交付：版本/环境 manifest、源码数据路径草图、明确 non-goals。

### M1：原生行为与测量可信

- workload 先生成固定 trace，再重放；实现 token/block ground truth。
- 加入 alloc/reuse/evict/recompute 与时延事件；完成 A0/A1 开销对照。
- 交付：可复现原生结果、事件语义测试、至少五类 workload。
- **停止条件：**无法解释指标来源，或 instrumentation 显著改变行为却无法校正。

### M2：策略 admission

- 展示一个具体失配时间线和 oracle/headroom。
- 写清在线可观测信号、候选机制、复杂度、invariant、失败预测。
- **停止条件：**原生与上界几乎无差距，或候选机制依赖未来信息。

### M3：一个 owned policy

- 实现真实决策路径 patch、回退、单元/集成测试。
- 完成 A0–A4、删除测试与机制 ablation。
- 交付：owned diff、测试日志、raw results、一个胜区和一个输区；正结果不是强制条件。

### M4：FP8 独立轴与收口

- 仅在 capability gate 通过后运行；先与原生策略组合，必要时再做 2×2 interaction。
- 锁定 claim ledger；第三方按文档复跑至少一条代表 trace。
- offload 只有主线全部通过且现成路径无需新系统时才作为成本对照。

## 14. Claim state 与简历安全措辞

### 14.1 当前状态

- 项目整体：`roadmap`。
- 市场/团队公开动作：`source-verified`，不是个人成果。
- 性能、策略、FP8 结果：当前均不是 `shipped` 或 `experimentally validated`。

### 14.2 完成后可晋级的 claim

| Claim | 安全状态条件 |
|---|---|
| workload/trace runner | 代码已运行、trace invariants 有测试：`shipped`；只代表参数化/公开 trace replay |
| 原生行为发现 | 固定环境下重复观察并保存 trace：`experimentally validated` |
| policy patch | 真实运行且测试通过：`shipped`；有 A/B 和删除测试后，收益才是 `experimentally validated` |
| offline oracle/simulator | 始终标 `simulated/offline upper bound`，不能写成线上策略 |
| FP8 | 使用框架内置能力时写“评估/验证”；只有自己真正实现 kernel 才能写“实现”，本项目不应做后者 |
| offload | 现成 connector 只能写“接入并对照”；不能写成自研分布式 KV 层 |

### 14.3 正结果简历句式

> 针对 `[选定框架 commit]` 在多轮 Agent `[明确 workload]` 下的 `[具体原生淘汰失配]`，在真实 cache/block 决策路径实现 `[owned policy]`；相对原生策略，在单张 `[GPU]`、`[模型/dtype/容量]` 下将 `[p95 TTFT 或 goodput]` 改善 `[实测值]`，`[TPOT/显存/开销 guardrail]` 为 `[实测值]`，并通过信号 ablation、commit 删除测试和 `[输掉条件]` 验证收益来源与边界。

### 14.4 负结果简历句式

> 在 `[选定框架 commit]` 构建 block 生命周期 trace 与可重放多轮 workload，比较原生策略、`[候选机制]` 与离线 oracle；证实 `[候选机制/原生策略]` 在 `[范围]` 的收益边界为 `[实测 break-even]`，定位 `[元数据开销/误判/无 headroom]` 为限制因素并拒绝默认启用，保留可复现实验、删除测试与负例。

### 14.5 FP8 若独立验证成功

> 在 `[GPU、框架 commit、模型/backend]` 上评估框架内置 FP8 KV cache，相对 `[BF16/FP16]` 测量容量、质量、TTFT/TPOT 与真实 cache pressure 下的命中变化，并报告 `[不支持或回归条件]`。

### 14.6 明确不安全的措辞

- “基于 vLLM 和 SGLang 自研高性能 KV Cache 系统”；
- “实现企业级/生产级 Agent KV cache”；
- “实现 FP8 KV 量化/FP8 kernel”（若只是调用框架能力）；
- “实现分布式 offload/RDMA KV store”（单卡或现成 connector）；
- “命中率提升 X%”但不报告 TTFT/goodput、guardrail 和 workload 条件；
- “真实 Agent 线上 workload”但只有合成数据或公开 trace replay；
- 把 roadmap 的 offload、双框架或 FP8 写入一个已完成 bullet。

## 15. 最终 go/no-go 标准

### Go：足以作为主项目投递

以下条件必须全部成立：

1. 一个框架 commit，真实数据路径和 owned diff 可指出；
2. 一个可证伪的原生失配，且有 oracle/headroom；
3. 同一 trace 下的原生、埋点、候选、ablation 与删除测试；
4. 主结果不是单一命中率，包含 tail 和系统 guardrail；
5. 至少一个输区、一个 break-even 或一个被证伪的假设；
6. 第三方能用文档和 artifact 重放代表结果；
7. roadmap、replay/simulation、shipped、experimentally validated 严格分开。

### No-go：只能作为学习记录，不能作为强简历项目

命中任意一项就不能按强项目包装：

- 没有改真实 runtime/cache 决策路径；
- generator 或 adapter 是最大代码量，但删除后研究结论不变；
- 只能在特别调出的合成 workload 上赢；
- 使用未来 trace 信息的“在线”策略；
- 没有原生 baseline、删除测试或负例；
- 双框架各做一半；
- 只展示命中率和平均值；
- FP8/offload 是调用现成功能却写成个人实现；
- 单卡结果外推生产、多机、RDMA 或通用最优。

**最终判断：这个题目值得做，但只有“单框架、单机制、强证据”的版本值得作为招聘主项目。题目名称不会替你回答 ownership；删除测试、失效边界和原始 artifact 才会。**
