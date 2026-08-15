# Agentic-KV Performance Engineering Playbook

> 文档性质：稳定的性能诊断与优化方法；不修改项目 Gate、STOP、scope 或当前状态。

本文件服从 [PROJECT_EVALUATION_SOP](../project/PROJECT_EVALUATION_SOP.md) 和
[PROJECT_PLAN](../project/PROJECT_PLAN.md)。它不修改 Gate、STOP、scope、claim state 或当前完成状态。
实际进度以 [STATUS.md](../../STATUS.md) 为准。

## 1. 文档权威、适用范围与非目标

本文件回答的是一个操作问题：当 Agentic-KV 出现不符合预期的性能现象时，如何从服务端症状逐层下钻，形成竞争假设，选择最小观测工具，定位源码接缝，判断根因是否受 **Shared-L3 Publication Admission** 控制，并把修改闭合为可复核的性能因果链。

它在仓库中的位置低于方法论宪法和项目合同：

- [PROJECT_EVALUATION_SOP](../project/PROJECT_EVALUATION_SOP.md) 决定什么证据足以支持什么强度的项目主张；
- [PROJECT_PLAN](../project/PROJECT_PLAN.md) 决定当前 Gate、STOP、scope、实验合同与 ownership；
- [STATUS.md](../../STATUS.md) 记录实际完成状态；
- [DECISIONS](../project/DECISIONS.md) 记录 owner 已决约束，但 `DECIDED` 不等于已实现或已验证；
- [AGENTS.md](../../AGENTS.md) 约束实现、测试、审查和 claim 纪律；
- 本文件只规定“怎么诊断、怎么证明、什么时候停止继续下钻”。

因此，这份 playbook 可以帮助形成 Gate 所需证据，却不能自行决定项目继续、绕过 STOP、提高 claim state，或凭一次 profiler 结果授权新的优化方向。具体完成状态始终只在 `STATUS.md` 维护，不在这里复制第二份动态账本。

当前正式机制只有 speculative/opportunistic **Shared-L3 Publication Admission**：

```text
L1 → L2 backup 完成
→ L2 ack
→ prefix-closure 检查
→ ADMIT_TO_L3 | DROP
→ upstream Mooncake Put 或直接返回
```

首次 C0 的窄结论只涉及固定环境中的 stock shared-L3 restore 路径和 prefill substitution。它不是 S1、S2、S3、G0 完成或性能收益。本文出现的项目 trace、D1 new-physical-Put observation、`ALWAYS_ADMIT` / `ALWAYS_DROP` 和 candidate 均是方法、验收要求或受 Gate 约束的未来对象；不得从本文推断它们已经实现。相关源码和运行时边界见 [G0 source/runtime audit](../implementation/G0_SOURCE_RUNTIME_AUDIT.md)、[D14 survival preregistration contract](../implementation/G0_D14_SURVIVAL_PREREGISTRATION_CONTRACT.md) 与 [first-C0 deployment retrospective](../implementation/G0_FIRST_C0_DEPLOYMENT_RETROSPECTIVE.md)。

本文件不是：

- 新版路线图或 S1–S3、G0–G4 合同的副本；
- Nsight、Torch Profiler、`perf` 或 `py-spy` 的入门教程；
- 常见推理优化技巧、candidate policy、自动调参或阈值清单；
- 修改 SGLang scheduler、Mooncake backend、远端 eviction、router、RDMA/GDR、kernel 或 PD disaggregation 的授权；
- 当前项目已获得 TTFT、Goodput、payload-efficiency 或通用兼容性收益的声明。

无论 RCA 下钻到哪里，都必须区分 upstream 能力、项目 owned modification 和实验观察。SGLang 的 serving、HiCache 的分层 KV 生命周期、Mooncake 的 Put/Get/Store 与恢复能力不能写成本项目个人实现。

## 2. 核心性能工程原则

### 2.1 从异常开始，而不是从工具开始

错误流程是：

```text
想展示性能分析
→ 先开 nsys
→ 找一个看起来耗时长的 kernel
→ 决定优化它
```

这条流程没有定义异常，也没有证明 kernel 位于请求关键路径，更没有排除 workload、路径或观测本身造成的混淆。正确流程是：

```text
定义异常
→ 固定可复现 workload
→ 验证真实路径
→ 分解阶段
→ 提出竞争假设
→ 选择能区分假设的最小工具
```

“异常”必须是可比较的差值，而不是模糊感受。至少写清观测对象、期望、实际结果、比较基线、发生范围和重复条件。例如，“相同 frozen workload 下，L3 arm 的 storage-cached tokens 增加，但 paired TTFT 分布没有按预期移动”比“L3 很慢”更可调查。

工具选择由待区分的问题决定。日志已经能否定一个假设时，不升级到 profiler；系统时间线已经证明 CPU launch starvation 时，不再对所有 kernel 做 Nsight Compute replay。

### 2.2 表面指标不是根因

单一指标通常同时受多种机制影响。下列等式均不成立：

- GPU utilization 高，不等于 SM、显存带宽或 Tensor Core 正在有效完成目标工作；utilization 只表示采样窗口中 GPU 有活动。
- collective duration 长，不等于 collective implementation 慢；某个 rank 更晚到达会让其他 rank 的等待表现为 collective 时间。
- GPU kernel 之间有空白，不等于 CUDA launch 本身昂贵；CPU scheduler、Python、序列化、同步或输入准备都可能延迟下一次 launch。
- cache hit 增加，不等于实际减少了 prefill；必须关联 Get/load terminal、storage-cached tokens 和 uncached/recomputed tokens。
- `submitted_bytes` 或 `admitted_bytes` 减少，不等于 `new_physical_put_bytes` 减少；exists skip、并发 race、failure 和 object expansion 必须分开。
- Put bytes 减少，不等于 TTFT 或 Goodput 改善；异步写入可能完全隐藏，也可能只改善容量或资源余量。
- query-time unavailable 不等于已经证明具体 eviction victim、eviction time 或 eviction reason；没有 source-verified telemetry 时只能报告“查询时不可用”。
- 单个函数耗时不能直接相加为请求 critical path；异步阶段、并行 worker、CPU/GPU overlap 和 queue wait 会使简单求和重复计算或漏算。
- TTFT 改善但 TPOT 恶化，不等于服务整体改善；这可能只是把资源压力转移到 decode 阶段。

根因不是“与异常同时变化的指标”，而是能解释异常、经区分实验排除合理替代解释、对应到明确源码或运行时接缝，并能被受控 action 操作的机制。

### 2.3 先正确性，再性能

任何性能调查开始前，先证明：

1. 请求成功完成，固定解码下输出 oracle 成立；
2. 请求实际走了预期的 L1/L2/L3 hit/miss、Put/Get 与 restore 路径；
3. coldness、fresh Store、keyspace 和 worker isolation 成立；
4. prompt、cached、storage-cached 与 uncached/recomputed token accounting 可解释；
5. queue、`ongoing_backup`、引用与 host protection 在 terminal/drain 后回到基线；
6. 没有把 error、hang、丢请求或错误输出当作吞吐改善。

任一项失败，当前问题先归类为正确性、路径真值或实验资格问题。此时得到的 latency/throughput 数字不能进入性能 claim。

### 2.4 先找 critical path，再优化局部耗时

关键路径（critical path）是决定 endpoint 完成时间的依赖链。只有两类工作可能产生端到端收益：

1. 它直接位于请求 endpoint 的关键路径；
2. 它虽异步，但争用 CPU、内存、NIC、Store、queue 或 GPU 等共享资源，间接延长关键路径。

例如，异步 Put 即使 wall-clock duration 很长，只要完全隐藏且没有造成共享资源争用，缩短它也不会改善 TTFT 或 Goodput。相反，一个短小但串行的 scheduler re-admission wait 可能直接控制 first token。

restore、network、CPU work、GPU copy 与 compute 可能重叠。诊断时应画依赖和 overlap，而不是把每段 duration 相加。microbenchmark 只证明局部能力边界；任何局部改善都必须回到同一真实 serving workload，以相同 endpoint 和 guardrail 重验。

### 2.5 控制变量与反事实

一次调查只改变一个因果决策面。对当前项目，这意味着 fixed-L2 treatment 中只改变 L3 publication action；不得同时改变路由、远端 eviction、传输 backend、KV 表示或 scheduler。

同时必须区分两类比较：

- fixed-L2 causal baseline 用于归因 publication action；
- X* external substitute 用于攻击“为什么不采用更简单的 upstream 组合”。

X* 不是相同 L2 treatment，不能混入 L3-only 因果归因。conditional ledger 也不能把某一 arm 的 eligibility stream 伪装成另一 arm 的闭环反事实；每个在线 arm 必须用自己演化出的 lifecycle trace 证明 Put、availability、Get、recompute 和 endpoint。

profiling run 与正式 benchmark run 必须分开。前者允许更高观测开销来定位机制，后者使用通过 non-interference 的最小观测面生成 headline 数据。同一个 run 内的请求共享温度、queue、Store 和环境状态，不能被当成独立统计重复。

## 3. 统一性能调查闭环

```text
服务症状
  → 复现与公平性
  → 路径真值
  → 阶段分解
  → 资源归因
  → 竞争假设
  → 区分实验
  → 源码接缝
  → 可控性判断
  → 最小修改
  → 同 workload 回归
  → 因果链与 claim 裁决
```

每一步都必须产生可审查输出，并有明确的停止或返回条件。

| 阶段 | 输入 | 必须输出 | 停止或返回条件 |
|---|---|---|---|
| 服务症状 | 用户可见 endpoint 或资源异常 | 精确的 expected vs observed、受影响范围、基线 | 现象无法被定义为可比较差值时，先补定义 |
| 复现与公平性 | workload、manifest、运行顺序 | 稳定复现、固定变量、独立 run 单元 | 只在一次 run 或漂移环境中出现时，不下结论 |
| 路径真值 | 请求、KV、worker 和 Store 事件 | 实际 L1/L2/L3、Put/Get、coldness、output 链 | 路径不符或 correlation 不足时，先修复观测/资格 |
| 阶段分解 | request lifecycle | queue、lookup、restore、re-admission、prefill、decode 等阶段边界 | endpoint 无法映射到阶段时，不直接跳到资源或 kernel |
| 资源归因 | 阶段时间线与系统计数器 | 哪个共享资源在何时造成 wait/pressure | 资源变化不与异常窗口或 critical path 对齐时，保留为旁证 |
| 竞争假设 | 已知事实与未知项 | 至少一个主要、一个替代、一个混淆解释（有必要时） | 假设不可证伪或不产生不同预测时，重写假设 |
| 区分实验 | 假设的不同预测 | 单变量实验、falsifier、预期观测 | 实验同时改变多个决策面时，重新设计 |
| 源码接缝 | 已定位生命周期阶段 | pinned commit 的对象、queue、callback、terminal | 只能定位到模块名而不能定位状态转移时，不开始 patch |
| 可控性判断 | 根因与 owned seam | admission 是否能改变根因，及作用方向 | 根因不受 admission 控制时，STOP、上游报告或另立项目 |
| 最小修改 | 可证伪的控制点 | 最小 patch、正确性 oracle、回滚方式 | 修改需扩展 scope 或引入第二权威时，先停止评审 |
| 同 workload 回归 | 原始复现合同 | before/after、mediator、endpoint、guardrail | workload、环境或观测改变导致不可比时，结果作废 |
| 因果链与 claim 裁决 | 全部 retained evidence | SIGNAL / VALID_FALSE / INCONCLUSIVE 与 claim ceiling | 缺 action、mediator、endpoint 任一层时，降低结论 |

根因定位不是“找到一个相关指标”，优化完成也不是“局部耗时下降”。完整闭环要求在同一 workload 下同时拥有：

```text
before/after
+ action separation
+ physical/runtime mediator
+ serving endpoint
+ correctness/resource guardrail
```

如果验证暴露新的路径事实，应返回“路径真值”或“竞争假设”，而不是为了守住原方案继续加工具或代码。

## 4. 分层诊断模型

性能调查默认从 L0 向下，只有上一层证据把问题收窄到下一层时才升级。

| 层 | 核心问题 | 最小证据 | 常用工具 | 不允许直接推出 | 升级条件 |
|---|---|---|---|---|---|
| L0 正确性与路径真值 | 请求实际上走了什么路径？ | L1/L2/L3 hit/miss；A Put、B cold、Get terminal；storage-cached/uncached tokens；output；completion/error | 结构化日志、response metadata、Store/worker health、项目 trace（通过 non-interference 后） | hit 即有性能价值；Get 完成即减少 prefill；一次成功即通用兼容 | 路径和正确性成立，但 endpoint 仍异常 |
| L1 Serving endpoint | 用户看到的异常是什么？ | Goodput@TTFT-SLO、TTFT distribution、TPOT guardrail、queue wait、error/hang、offered load、service-curve knee | benchmark runner、服务 metrics、run-level statistics | 平均 latency 代表尾部；单个分位数代表整体；Goodput 变化说明具体机制 | endpoint 可复现且需要解释其生命周期来源 |
| L2 Framework/runtime 阶段 | 时间或状态压力出现在哪个生命周期阶段？ | scheduler waiting、prefix lookup、restore、runnable→re-admission、remaining prefill、decision、StorageOperation、backup queue、Put/Get completion、host protection release | 项目 request/KV lifecycle trace、定向日志、Torch Profiler（仅 representative operator 阶段） | 阶段 duration 可直接求和；Put duration 必然进入 TTFT | 异常已集中到某阶段，需识别共享资源或 operator |
| L3 系统资源 | 哪个共享资源产生等待或争用？ | CPU、Host DRAM、queue、Store CPU/RSS、NIC、outstanding operations/bytes、GPU copy/compute overlap、进程或 rank skew | `py-spy`、`perf`、OS/network counters、Nsight Systems | CPU/NIC 变化自动等于 endpoint 因果；GPU idle 自动等于 kernel 问题 | 资源证据将问题收窄为 GPU operator/kernel，或明确源码接缝 |
| L4 Operator/kernel | 哪个 operator 或 kernel 位于 representative critical path？ | operator→kernel mapping、真实 shape、时间占比、dependency/overlap、before/after 可回归 | Torch Profiler、Nsight Systems、Nsight Compute | kernel 局部加速等于 Goodput 提升；profile shape 可外推所有 workload | 只有上层证明 GPU compute/operator 是当前瓶颈时进入 |

### L0：正确性与路径真值

首先回答“请求实际上走了什么路径”。对 shared L3，至少把 A 的 Put terminal、B 的本地冷证据、B 的 remote Get/load、storage-cached tokens、uncached/recomputed tokens、固定解码输出和请求完成状态关联到同一 workload。路径不能确定时，性能现象没有可解释的分母。

### L1：Serving endpoint

把用户可见异常固定为 endpoint：Goodput@TTFT-SLO、TTFT 分布、TPOT、queue wait、error/hang 或 service-curve knee。主 endpoint 和 guardrail 必须在 treatment 前确定。平均 GPU utilization、cache hit 或 Put bytes 属于解释量，不属于这一层的成功定义。

### L2：Framework/runtime 阶段

把 endpoint 拆到请求生命周期：scheduler waiting、prefix lookup、remote restore、请求重新 runnable、scheduler re-admission、remaining prefill、first token、decode；写路径则包括 decision、StorageOperation、backup queue、Put terminal 与 host protection release。这里的目标是定位“哪个阶段控制了 endpoint”，不是收集所有函数耗时。

### L3：系统资源

阶段异常可能来自 CPU、Host DRAM、queue、Store CPU/RSS、NIC、outstanding operations/bytes 或 GPU copy/compute 争用。资源计数器必须与时间窗口和阶段对齐。只看到资源高，不足以证明它阻塞 critical path；需要区分实验改变该资源并观察 mediator 和 endpoint 是否按预测响应。

### L4：operator/kernel

仅当上层证据把主要问题定位到 representative GPU compute/operator，才进入 operator/kernel。此时要固定真实模型、shape、prefill/decode 阶段和 workload，先用系统/框架时间线找到 hot kernel family，再用 Nsight Compute 回答具体效率问题。否则 kernel 调优属于无目标下钻。

## 5. 症状分诊表

| 症状 | 优先检查 | 不应直接做什么 |
|---|---|---|
| TTFT 高、TPOT 正常 | queue、prefill、restore、runnable→re-admission、first token | 直接优化 decode kernel |
| TPOT 高或抖动 | decode、KV pressure、共享资源、preemption、请求间干扰 | 只看平均 GPU utilization |
| storage-cached tokens 增加但 TTFT 不降 | Get wait、scheduler re-admission、remaining prefill、restore/recompute critical-path cost | 直接宣称 restore 优化有效 |
| Put activity 高且 endpoint 下降 | backup queue、Store、CPU、Host DRAM、NIC、outstanding work 的争用 | 把 Put latency 直接加到 TTFT |
| Put bytes 下降但 endpoint 不变 | 异步隐藏、容量收益、测床是否形成资源压力 | 把 payload 节省写成性能提升 |
| query-time availability 下降 | useful Get、storage-cached/uncached tokens、capacity condition、paired endpoint | 无 telemetry 时断言具体 eviction |
| GPU timeline 有空白 | CPU launch、scheduler、同步、serialization、输入输出 | 直接说 Python 或 CUDA launch 慢 |
| collective 看起来很长 | 所有 rank 的到达、开始、结束与上游工作 | 只分析一个 rank |
| 只有首请求慢 | warm-up、JIT、native extension、graph capture、cold path | 混入稳定态 headline |
| trace-enabled 后性能变差 | serialization、锁、buffer、hot-path logging、drop/backpressure | 继续用该 trace 证明系统根因 |

诊断示例：collective 的一个 rank 显示很长 duration，但多 rank 时间线显示它较早到达，另一个 rank 因 CPU 工作晚到；根因是 arrival skew，而非 collective 算法。另一个常见例子是 GPU kernel gap 与 CPU-side serialization 同时对齐，下一次 launch 直到 CPU 工作结束才出现；此时“CUDA launch overhead”只是表面解释。

表中不设置“健康 utilization”“可接受 queue depth”或固定百分比。所有 materiality、SLO、pressure witness 和 interval 必须来自当前环境、版本、workload 的 calibration 与 canonical preregistration。

## 6. 假设驱动的 RCA 协议

每次调查必须写清：

```text
Symptom
Expected vs observed
Reproduction contract
Path truth
Competing hypotheses
Discriminating experiment
Falsifier
Source seam
Controllability
Fix or STOP
Regression result
Claim ceiling
Retained artifacts
```

### 6.1 竞争假设

竞争假设不是数量游戏。存在真实不确定性时，至少保留：

1. 当前最可能的机制解释；
2. 一个同样能解释已有现象的合理替代解释；
3. 一个由 workload、运行顺序、环境漂移或 instrumentation 造成的混淆解释。

如果第三类在本次现象中不合理，应写明排除依据，不要机械编造。每个假设使用同一记录格式：

| 字段 | 要求 |
|---|---|
| Prediction | 若假设成立，新增观测或 manipulation 后应该看到什么 |
| Discriminator | 哪个最小实验能让它与其他假设产生不同结果 |
| Falsifier | 什么结果会推翻它，而不是只让它“看起来弱一些” |
| Source seam | 对应 pinned source 的对象、queue、callback、state transition 或 terminal |
| Controllability | Shared-L3 Publication Admission 能否控制它；控制的是 action、payload、资源还是都不能 |

例如“storage-cached tokens 增加但 TTFT 不降”至少可以有三种解释：Get/restore 本身位于 critical path；restore 后 scheduler re-admission 或 remaining prefill 吃掉收益；profiling/运行顺序使 L3 arm 处于更差环境。分别比较 Get terminal→runnable、runnable→re-admission、remaining prefill→first token，并交换 arm order，才能区分它们。

### 6.2 证据强度不可跳级

调查过程中明确区分：

```text
相关性
  指标与症状一起变化

机制一致性
  时间顺序、路径和源码与某假设一致

受控 action
  单变量 manipulation 确实改变目标 mediator

端到端因果结果
  mediator 与 endpoint 在公平 before/after 中按理论方向响应
```

相关性可以生成假设，机制一致性可以缩小范围，受控 action 可以证明操纵有效；只有端到端因果结果才能支持对应范围内的性能结论。profiler timeline 本身不能“证明 causality”。

### 6.3 区分实验的最小设计

优先设计能使两种解释给出相反或显著不同预测的实验，而不是增加更多 dashboards。例如：

- 若 Put 是共享资源瓶颈，forced DROP 应分离 actual Put work 和相应 queue/resource pressure；若 Put 完全隐藏，bytes 可能下降而 endpoint 不动。
- 若 capacity externality 是原因，roomy/small fresh Store 应改变 query-time availability、useful Get 和 recompute；若只是随机冷启动，交换顺序和 fresh Store 后效应不稳定。
- 若 CPU work 阻塞 GPU launch，降低或移除该 CPU work 后 launch gap 应缩短；若 kernel dependency 才是原因，CPU 改动不会使时间线按预测变化。

区分实验先写 falsifier，再运行。看完结果后补写无法推翻的解释，不属于 RCA。

## 7. 工具升级与选择规则

默认升级顺序是：

```text
日志 / 基础 metrics
→ 项目 request/KV lifecycle trace
→ CPU / OS / network 工具
→ Nsight Systems 或 Torch Profiler
→ Nsight Compute
```

升级不是按工具“高级程度”，而是按当前假设缺少的证据层级。

### 7.1 日志与服务 metrics

能回答：请求是否成功、endpoint 是否稳定复现、queue/cache/request 状态、配置是否生效、Store/worker 是否健康、错误发生在哪一阶段。

不能单独证明：new physical Put、跨异步层 critical path、kernel 根因或 treatment causality。日志时间戳也不能替代跨进程的因果关联；跨节点优先使用 ID、worker-local sequence 和 terminal，而不是假定 wall clock 全序。

### 7.2 项目自定义 request/KV lifecycle trace

能回答：request、prefix group、operation、batch、attempt、physical object terminal 如何关联；decision 如何传导到 Put/Get/recompute；queue dwell、completion 与 resource release 是否可见。

最小关联应覆盖：

```text
run / worker / request / observation or decision
→ StorageOperation
→ batch / attempt
→ logical and physical object terminal
→ later availability / Get / recompute
→ request endpoint
```

它不能在未通过 non-interference 时成为根因证据。它也不能自动看到 Mooncake 内部 occupancy、wire bytes 或 eviction reason；可见边界必须按 pinned source 记录。

### 7.3 `py-spy`、`perf` 与 OS/network counters

`py-spy` 适合回答 Python 进程在哪些栈上消耗 CPU，以及 scheduler、serialization 或 hot-path logging 是否占用前台。`perf` 适合更广的 CPU、系统调用、锁竞争、context switch、内存行为和原生栈。OS/network counters 适合判断 Host DRAM、RSS、NIC、socket 或 Store 资源压力是否与异常窗口对齐。

这些工具不能仅凭 hotspot 或 counter 变化证明 request critical path，更不能证明 policy 提高 Goodput。需要把采样窗口关联回 lifecycle 阶段，并通过 manipulation check 观察 endpoint。

### 7.4 Nsight Systems

能回答：CPU、CUDA kernel、copy、collective 和同步在系统时间线上的关系；GPU idle gap；多 rank arrival skew；restore/copy/compute overlap；哪段工作位于 critical path。

不能直接回答：单个 kernel 为什么低效，或 policy 是否提高 Goodput。它首先是时间线和依赖工具，不是 kernel 诊断或策略裁决工具。

### 7.5 Torch Profiler

能回答：Python/operator 与 CUDA kernel 的关联、CPU launch、representative prefill/decode operator 分解，以及适用时由 SGLang HTTP profiling 入口捕获的 representative stage。

使用规则：

- prefill 与 decode 分开分析，避免把不同 shape 和目标混成一个 hotspot；
- profiler-enabled run 不生成正式 throughput/latency headline；
- 为调试关闭 CUDA Graph 或改变执行模式时，必须标为 profiling-only，不能静默替换正式 baseline；
- 只捕获能代表异常的短窗口，保留 workload、shape 和 profiler 配置。

### 7.6 Nsight Compute

只有以下条件全部成立才使用：

1. 上层时间线已定位到具体 kernel family；
2. 该 kernel 在 representative critical path 中占有物质时间；
3. model、shape、dtype 和 workload 与真实 serving 路径一致；
4. 任何修改都能回到同一真实 serving workload 复验。

Nsight Compute 用来回答具体 kernel 的执行效率问题，不对所有 kernel 做 full replay，也不为展示工具而使用。若 RCA 根因位于 queue、CPU launch、Store 或 scheduler re-admission，NCU 没有增加裁决信息。

## 8. 当前项目中的诊断入口

本节说明什么时候分析 SGLang 或 Mooncake 的哪条路径。定位到 upstream 对象不等于项目拥有或应该修改它。

### 情况 A：restore 成功、prefill tokens 减少，但 endpoint 不改善

依次检查：

```text
remote lookup
→ Get queue/wait
→ restore terminal
→ request runnable
→ scheduler re-admission
→ remaining prefill
→ first token
```

优先使用通过 non-interference 的项目 lifecycle trace。先证明 Get 对应到实际 storage-cached tokens 和较少 uncached/recomputed prefill，再检查收益消失在哪个阶段。只有需要判断 CPU/GPU/copy overlap 时，才升级到 Nsight Systems 或 Torch Profiler。

诊断示例：storage-cached tokens 增加且 remaining prefill 减少，但 request runnable 后长期等待 scheduler re-admission，最终 TTFT 不变。正确结论是“restore 机制有效，但 endpoint 收益被 re-admission wait 抵消”，不是“cache hit 提高了性能”，也不是自动授权修改 scheduler。

### 情况 B：S2 出现 publication cost 信号

优先检查：

```text
StorageOperation 数量
→ backup queue depth / dwell
→ outstanding operations / bytes
→ host protection duration
→ Mooncake adapter / Store CPU、RSS
→ NIC activity
→ 与后续 Get 或请求 endpoint 的争用
```

目标是判断 actual Put work 是否形成共享资源压力并传导到 endpoint。submitted/admitted bytes 不是 D1 new physical Put；Store/NIC counters 也只是 mediator 旁证。此类问题通常位于异步生命周期和系统资源层，不应优先使用 Nsight Compute。

### 情况 C：S3 出现 capacity externality 信号

检查：

```text
query-time availability
→ completed / useful Get
→ storage-cached tokens
→ uncached / recomputed prefill tokens
→ paired endpoint
```

roomy/small capacity 必须使用 fresh Store 或更强隔离，并保留实际 segment response。没有 source-verified telemetry 时，只能声称 query-time availability 变化，不能归因具体 victim、eviction time、eviction reason 或精确 runtime occupancy。

### 情况 D：policy 或 instrumentation 引入 CPU overhead

使用 decision-duration trace、`py-spy`、`perf`、queue/buffer 指标。重点检查 metadata 扫描、同步序列化、锁、无界队列、hot-path logging 与 buffer drop/backpressure。

先比较 stock upstream、patched+trace disabled、patched+trace enabled。若 disabled 已退化，问题在 patch 即使关闭仍改变路径；若只有 enabled 退化，问题在观测实现。两者都不能通过时，不得用该 trace 形成性能根因。

### 情况 E：remaining prefill 成为主要 critical path

先用 Torch Profiler 分析 representative prefill，分离 CPU launch、operator 和 CUDA kernel。只有识别到具体 hot kernel family 后才使用 Nsight Compute。

这可能定位到 upstream compute 路径。除非 [PROJECT_PLAN](../project/PROJECT_PLAN.md) 另有 scope 决议，否则应记录根因和阻断影响，而不是把 kernel 优化纳入当前项目。

### 情况 F：多 rank collective 看起来异常

这是通用性能方法，不是当前 TP=1 主线实验或授权。必须同时查看所有 rank，比较 collective 到达时间和共同结束时间，先排除上游 compute、CPU launch 或输入 skew，再判断 collective implementation 或 topology。

诊断示例：rank 0 较早进入 collective 并等待，rank 1 因前一 operator 晚到；单看 rank 0 会误判 NCCL 慢。该例只说明方法，不表示本项目已运行多 rank 实验。

## 9. KV 数据路径的性能分解

数据移动必须按语义和物理层级拆开：

```text
逻辑 payload
→ eligible
→ admitted
→ submitted
→ new physical Put / exists skip / race / failure
→ later availability
→ Get
→ actual prefill substitution
```

这些阶段不能合并：

- logical KV bytes 来自 tensor shape/dtype，不等于 adapter 展开后的 physical-object payload；
- adapter payload bytes 不等于 NIC/wire bytes，不含完整协议、metadata、复制和重试开销；
- eligible/admitted 只是资格和 action，不等于已进入 backend；
- submitted 不等于 new physical Put；precheck、race-existing 和 failure 会改变归属；
- completed Get 不等于 useful restore；只有它实际形成 storage-cached tokens 并减少 uncached/recomputed prefill，才有 useful work 证据；
- modeled occupancy 不等于 runtime occupancy；
- query-time unavailable 不自动证明 eviction。

D1 要求在 Mooncake 把 `OBJECT_ALREADY_EXISTS` 归约为 success 之前观察原始原因，并通过 opaque attempt ID 与 SGLang adapter 关联。在该 observation patch 和 non-interference 证据完成前，不得报告 `new_physical_put_bytes` 或 payload-efficiency claim。具体边界见 [D1](../project/DECISIONS.md#d1--保留-new-put-payload-指标并授权最小观察-patch)。

### 9.1 粗略成本模型

诊断时可使用下界估算：

```text
T_transfer_lower_bound ≈ payload_bytes / effective_bandwidth
```

它用来发现数量级异常：若观测时间远高于下界，应进一步检查 packing、fragmentation、queue、conversion、copy、protocol、release timing 和 overlap；若观测时间接近但完全异步隐藏，也不意味着 endpoint 会改善。

restore 的价值取决于：

```text
restore critical-path cost
vs
被避免的 recompute / prefill critical-path cost
```

该模型只帮助提出竞争假设和选择实验，不能代替 runtime measurement。`effective_bandwidth` 不是硬件峰值，且随 shape、并发、packing 和路径变化。各阶段可能并发或重叠，不能简单相加为 TTFT。

### 9.2 从 Put 到 endpoint 的两个反例

诊断示例一：forced DROP 使 new Put bytes 明显下降，但异步写入完全隐藏、queue 和共享资源都不受压，Goodput 不变。允许结论是 payload 变化或“当前坐标无前台收益”，不是性能提升。

诊断示例二：TTFT 改善，但 TPOT 因资源转移而恶化，导致 Goodput@TTFT-SLO 或整体 guardrail 不通过。不能只挑 TTFT 宣告优化成功。

## 10. 实验、公平性与 profiling 隔离

任何可用于 claim 的性能实验至少遵守：

1. 先做 baseline-only calibration；只用 baseline 冻结可区分 load、SLO、capacity、noise/interval 方法与物质性阈值。
2. treatment 前冻结 manifest checksum；不得看结果后移动 workload、knee、分位数或阈值。
3. 固定 request/token/arrival/worker assignment、模型、tokenizer、解码、L1/L2 配置、transport 和远端实现。
4. 使用 fresh Store 或有更强证明的容量隔离；namespace/tag 只防 key collision，不自动消除容量和 eviction 历史。
5. 每个 arm 保留 coldness proof、实际 Store/worker identity 和路径真值。
6. warm-up、measurement、drain 一致；首请求/JIT/graph capture 不混入稳态 headline，除非首请求本身是预注册目标。
7. 使用 ABBA 或 treatment 前冻结的随机顺序抵消温度、运行顺序和环境漂移。
8. profiling run 与 benchmark run 分开；profile 配置、开关和 overhead 单独记录。
9. 以独立 run 或预注册 paired run 为统计单元；同一 run 内请求不是独立重复。
10. 固定解码与 output correctness；error、hang、queue/ref/protection leak 不能通过性能结果抵消。
11. 主 endpoint、TPOT/正确性/资源生命周期 guardrail 在 treatment 前确定。
12. 原始日志、异常 run、失败 run 和 losing workload 全部保留，不只报告最有利 workload、分位数或 profiler 截图。

### 10.1 三类冻结点

1. **环境与资格冻结**：固定 source/build/model/tokenizer/runtime、路径资格、coldness、fresh Store 方法和 evidence destination。
2. **baseline-only calibration 后冻结**：固定 workload coordinate、offered load、SLO、capacity、pressure witness、materiality、interval、重复预算和 arm order。
3. **candidate 与 TARGET_HELD_OUT 前冻结**：仅在 canonical Gate 授权 candidate 后，固定其定义、参数、合法在线输入、calibration/ORACLE_EVAL/TARGET_HELD_OUT/OOD split 与 strongest baselines。

具体 D14 数值和字段由 [D14 survival preregistration contract](../implementation/G0_D14_SURVIVAL_PREREGISTRATION_CONTRACT.md) 维护。本文件不复制或修改该合同。

### 10.2 避免 workload 和 profiler 污染

- workload 必须因能区分机制而选择，不能因“最容易跑出正结果”而选择；one-shot/unique-heavy 只能保持其 canonical negative-control 地位。
- profile 后若改变 workload、执行模式或 CUDA Graph 配置，必须重新建立 before/after 可比性。
- profiler 截图只作为诊断 artifact；正式结论需要原始 trace、解析方法和 non-profiled benchmark。
- 异常 run 不能静默删除；若按预注册规则排除，保留 run ID、排除原因和原始 artifact。

## 11. Instrumentation non-interference

观测能力必须先证明不改变被观测系统。至少比较：

```text
stock upstream
patched + trace disabled
patched + trace enabled
ALWAYS_ADMIT（behavior hook 实现后）
```

其中前三项验收 observation patch；`ALWAYS_ADMIT` 在 behavior hook 实现后证明 patched behavior seam 退化为 stock write-through path。当前 trace 和 hook 的实际完成状态仍以 [STATUS.md](../../STATUS.md) 为准，本文只规定未来验收。

### 11.1 行为等价检查

逐项检查：

- logical/physical key、operation 和 batch 顺序；
- Put/Get terminal、dedup/race/failure 可见性；
- request output、completion/error；
- queue、`ongoing_backup`、ref/buffer、host protection 和 shutdown/detach 生命周期；
- correlation coverage 与 missing/duplicate terminal；
- trace loss、drop counter 和解析完整性；
- CPU、RSS/Host memory、TTFT、Goodput 和 queue overhead。

trace-disabled 若与 stock 不等价，说明 patch 即使关闭仍干扰行为；trace-enabled 若明显越过冻结的 non-interference bound，说明观测实现不可用于 headline 或根因。两种情况都应修正、缩小观测面或停止，而不是用更多日志解释干扰。

### 11.2 实现纪律

- hot path 不同步写大量 JSON，不做无界 metadata 扫描；
- 使用 bounded buffer；满时记录明确的 drop counter，优先保证 serving；
- correlation ID 不参与 key、queue、retry、dedup、Get 或 admission 语义；
- observation patch 与 behavior-changing admission patch 分 commit、分测试、分 claim；
- trace loss 或 missing terminal 使相关分析降级为 `INCONCLUSIVE`，不能用估算补齐。

trace 通过 non-interference 前，不能用它形成性能根因、性能 headline 或 new-Put attribution。

## 12. 因果链闭合与 manipulation check

性能闭环统一为：

```text
action
→ physical/runtime mediator
→ resource or useful-work change
→ serving endpoint
```

当前允许检验的正向链只有两类。

### 链 A：写成本 / 资源争用

```text
DROP
→ new_physical_put_bytes / actual Put work 下降
→ backup queue、CPU、内存、NIC 或 Store pressure 下降
→ TTFT / Goodput 改善
```

这条链要求 D1 attribution 可用，并在同一 arm 中关联 decision、Put terminal、资源压力和 endpoint。若 actual Put work 下降但 endpoint 不变，只能得到机制、payload 或当前坐标无前台收益的结论。

### 链 B：容量 / 查询时可用性

```text
publication decision
→ query-time availability 改变
→ useful Get / avoided prefill 改变
→ TTFT / Goodput 改变
```

这条链要求 fresh capacity isolation、各 arm 自己的 lifecycle、storage-cached/uncached token oracle 和 paired endpoint。没有 eviction telemetry 时，链条停在 query-time availability，不升级为具体 eviction claim。

### 12.1 三层 manipulation check

每次 forced-action 实验检查：

1. **Action separation**：`ADMIT` / `DROP` 是否按预期真正分离，错误或 fail-open 是否被正确记账；
2. **Mediator separation**：new physical Put、queue/resource pressure，或 availability/useful Get/recompute 是否按理论方向分离；
3. **Endpoint response**：TTFT/Goodput 是否在公平 paired result 中按理论方向响应，TPOT、正确性和生命周期 guardrail 是否保持。

裁决规则：

- bytes 单独变化不能通过性能因果链；
- CPU/NIC 计数器单独变化不能通过；
- modeled occupancy 单独变化不能通过；
- endpoint 改善但 mediator 不变，优先怀疑 workload、顺序、环境或 instrumentation 混淆；
- mediator 改变但 endpoint 不变，只能得到机制或 payload/capacity-efficiency 上限内的结论；
- `ALWAYS_ADMIT` / `ALWAYS_DROP` 是因果探针和 correctness oracle，不是最终 headline policy。

## 13. 优化选择与项目 scope

### 13.1 当前 owned 优先方向

只有 canonical Gate 允许进入相应实现时，优化优先级为：

1. 对 speculative Shared-L3 publication 做最小 `ADMIT_TO_L3` / `DROP` 控制；
2. 减少没有远端价值的实际 Put 工作；
3. 在 bounded capacity 下保护 useful remote availability；
4. 降低 admission decision 自身开销；
5. 降低 instrumentation 的 CPU、内存和时序干扰；
6. 保持 prefix closure、fail-open 和异步生命周期正确。

这些是受现有 scope 约束的调查/优化顺序，不是 trace、hook 或 candidate 已获实现授权。candidate 仍由 [PROJECT_PLAN](../project/PROJECT_PLAN.md) 的 Gate 与新的 owner decision 决定。

### 13.2 只有证据触发时才分析

- SGLang scheduler / re-admission；
- Mooncake Store 或 adapter；
- CPU serialization；
- copy/communication overlap；
- prefill/decode operator；
- kernel；
- multi-rank collective。

“分析”用于判断它是否解释当前机制价值或阻断实验，不自动转化为 owned optimization。

### 13.3 默认不纳入当前 owned optimization

- 修改 SGLang scheduler；
- 修改 Mooncake transfer/storage backend；
- RDMA/GDR/NIXL；
- L1/L2/L3 eviction；
- PD disaggregation；
- KV 量化/稀疏化；
- CUDA/Triton kernel；
- router；
- HA。

如果 RCA 定位到这些方向：

```text
记录根因
→ 判断是否阻断当前机制价值
→ STOP、形成 upstream issue 证据，或另立项目
```

不得通过修改本 playbook、增加 profiler 或顺手 patch 静默扩大 scope。

### 13.4 值得优化的最低条件

优化方案必须同时满足：

- 根因可在冻结 workload 中稳定复现；
- 根因影响 serving endpoint 或预注册资源目标；
- owned action 能控制该根因；
- 存在可比较 baseline 和明确 falsifier；
- 可以用最小、可回滚 patch 验证；
- 有 regression、correctness/resource guardrail 和 losing workload；
- 复杂方案能击败简单规则或 X* 的替代攻击。

任一条件缺失，优先补证据或 STOP，不以平台化、通用策略框架或更多 feature 弥补。

## 14. 三态裁决与 STOP

性能调查统一使用：

```text
SIGNAL
VALID_FALSE
INCONCLUSIVE
```

### SIGNAL

所需路径、fairness 和 pressure witness 均成立，且预注册效应区间越过物质性阈值。SIGNAL 表示该通道值得按 canonical contract 继续，不表示 candidate 已有效或性能 claim 已成立。

### VALID_FALSE

实验具有充分排除能力：所有资格和 witness 成立，效应区间上界已经低于预注册物质性阈值。VALID_FALSE 是有证据的负结论，不是“p-value 不显著”或点估计接近零。

### INCONCLUSIVE

包括但不限于：

- 区间仍跨阈值；
- workload 没有形成所需压力；
- coldness、fairness、path truth 或 instrumentation 不可信；
- mediator 分母无效或 correlation 不完整；
- 最大重复预算耗尽仍无法裁决。

```text
没有统计显著差异 ≠ 没有性能机会
```

合法 STOP 至少包括：

- restore 没有净价值区域；
- target remote Get 近似为零；
- S2、S3 都是有效 false；
- 根因不受 publication admission 控制；
- instrumentation 无法做到低干扰和完整关联；
- static rule 或 X* 已吃掉 residual；
- online oracle 无法物质性击败 X*；
- candidate 只在 calibration 赢，在 TARGET_HELD_OUT 失败；
- candidate endpoint 收益被 policy overhead、TPOT 退化或生命周期错误抵消。

STOP 可以导向根因记录、payload-only 窄终局、upstream issue 或另立项目，具体选择仍由 canonical 合同决定。不得把 `INCONCLUSIVE` 改写为 STOP，也不得用更多工程量补救一个有效 null。

## 15. Claim ladder

### 层 1：路径正确性

示例：

```text
shared-L3 restore 真实发生，并替代部分 prefill。
```

需要 Put/coldness/Get/token/output 证据，但不能称为性能提升。首次 C0 的结论上限属于这类窄路径/机制资格，不应向后续 Gate 外推。

### 层 2：机制变化

示例：

```text
forced DROP 确实绕开了 StorageOperation 和 Put。
```

需要 `ALWAYS_ADMIT` / `ALWAYS_DROP` path truth、prefix closure 和 lifecycle oracle。它不能称为 Goodput 提升。

### 层 3：payload / capacity efficiency

示例：

```text
在 Goodput 非劣下，new physical Put payload 下降 X%。
```

只有 D1 new-Put attribution、trace non-interference、在线 treatment、公平性、non-inferiority 与 raw artifacts 全部成立后才允许。若只测到 adapter payload，不得写“网络流量下降”；若只测到 query-time unavailable，不得写“eviction 改善”。

### 层 4：端到端性能

示例：

```text
在冻结 workload、SLO 和 paired repeats 下，
相对 strongest fixed-L2 baseline，
Goodput@TTFT-SLO 提升 X%。
```

必须同时有 action、mediator、endpoint、TPOT/正确性/资源生命周期 guardrail、interval 方法和 raw artifacts。与 X* 的比较还要明确它是 external substitute，而非 fixed-L2 causal attribution。

### 层 5：外部有效性

只有不同 workload、环境或真实 trace 的独立验证后，才能讨论可迁移性。单一固定拓扑、单次 profiler 或一个 held-out workload 不能支持“production-ready”“普适提升”或大集群经济外推。

任何层级都禁止：

- 把 upstream SGLang HiCache 或 Mooncake 写成个人实现；
- 用 profiler 截图声称 causality；
- 把 adapter payload 叫作 NIC/wire traffic；
- 在无 telemetry 时声称具体 eviction；
- 把 ROADMAP、SOURCE_VERIFIED、IMPLEMENTED_UNVALIDATED 与 EXPERIMENTALLY_VALIDATED 混用。

## 16. RCA 最小记录模板

以下模板可复制到具体 RCA artifact。RCA 文件是否进入仓库、放置位置和命名由当次任务决定；本模板不自动创建任务或新 Gate。

```markdown
# RCA-XXX：标题

## 1. Symptom

- 用户可见 endpoint / 资源异常：
- 发生范围：
- 首次发现时间：
- Run IDs：

## 2. Expected vs observed

- Expected：
- Observed：
- 比较基线与效应定义：
- 当前 claim ceiling：

## 3. Reproduction contract

- Code commit：
- Upstream commits / build identity：
- Manifest path and checksum：
- Workload / request / token / arrival / worker assignment：
- Model / tokenizer / decode：
- Store lifecycle / capacity / keyspace isolation：
- Warm-up / measurement / drain：
- Arm order and repeat IDs：
- Profiler on/off and exact configuration：

## 4. Path truth

- L1/L2/L3 hit/miss：
- Put/Get terminals：
- Worker coldness proof：
- storage-cached / uncached / recomputed tokens：
- Output / completion / error oracle：
- Queue / ref / protection terminal：

## 5. Competing hypotheses

### H1 — 当前主要解释

- Prediction：
- Discriminating experiment：
- Falsifier：
- Source seam：
- Controllability by publication admission：

### H2 — 合理替代解释

- Prediction：
- Discriminating experiment：
- Falsifier：
- Source seam：
- Controllability by publication admission：

### H3 — workload / order / drift / instrumentation confound

- Prediction：
- Discriminating experiment：
- Falsifier：
- 若不适用，排除依据：

## 6. Discriminating experiments

| Experiment | Changed variable | Frozen variables | Expected separation | Stop condition | Run IDs |
|---|---|---|---|---|---|
| | | | | | |

## 7. Evidence

- Raw artifact location：
- Analysis script path / commit：
- Logs / metrics / trace：
- Profiler artifacts：
- Interval / statistical method：
- Excluded runs and preregistered reason：

## 8. Source seam

- Pinned file / object / queue / callback / terminal：
- State before and after seam：
- Facts vs inference：
- Upstream vs owned boundary：

## 9. Root cause

- Root cause statement：
- Evidence that distinguishes it from alternatives：
- Falsified hypotheses：
- Causal chain：

## 10. Controllability and scope

- Is the root cause controlled by Shared-L3 Publication Admission?：
- Exact owned action and mediator：
- In-scope / upstream / separate-project ruling：

## 11. Fix or STOP

- Smallest fix, rollback, or STOP：
- Why a simpler option is insufficient：
- Gate / owner decision required：

## 12. Before/after validation

- Same-workload before run IDs：
- Same-workload after run IDs：
- Action separation：
- Mediator separation：
- Endpoint response：
- Regression result：

## 13. Correctness and guardrails

- Output / request success：
- TPOT / error / hang：
- Queue / ref / protection / shutdown：
- Trace non-interference：
- Resource overhead：

## 14. Claim ceiling

- SIGNAL / VALID_FALSE / INCONCLUSIVE：
- Path / mechanism / payload-capacity / endpoint / external-validity layer：
- Explicitly unsupported claims：

## 15. Retained artifacts

- Run IDs：
- Manifest checksum：
- Code and analysis commits：
- Raw artifact locations and hashes：
- Profiler on/off：
- Analysis environment：
- Losing workloads：

## 16. Remaining uncertainty

- Unresolved uncertainty：
- Missing evidence：
- What result would change the ruling：
```

一份 RCA 只有在他人能够从 manifest、commit、run IDs、raw logs/trace、analysis 方法和 falsified hypotheses 重建其结论时，才算可复核。保留 losing workloads 和未解决不确定性，不把失败实验从证据链中删除。
