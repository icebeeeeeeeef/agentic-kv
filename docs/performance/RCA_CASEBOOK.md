# Agentic-KV Performance RCA Casebook

> 文档性质：真实性能异常与根因分析案例的索引、准入和封存规则；不修改项目 Gate、STOP、scope、claim state 或当前状态。

## 1. 文档分工与权威边界

本 Casebook 只治理真实性能 RCA（Root Cause Analysis，根因分析）案例。仓库中的权威分工如下：

```text
PROJECT_PLAN
决定：项目做什么、何时通过 Gate、何时 STOP、哪些 claim 合法。

PERFORMANCE_ENGINEERING_PLAYBOOK
决定：面对异常时，如何提出假设、选择工具、做区分实验和完成性能调查。

PERFORMANCE_PATH_AND_OPTIMIZATION_MAP
决定：系统有哪些路径、每个节点由谁拥有、哪里可观察、哪里可修改。

OBSERVABILITY_AND_MEASUREMENT_CONTRACT
决定：记录哪些事件、如何关联、指标怎样计算、缺失数据怎样处理。

RCA_CASEBOOK
决定：哪些真实异常值得形成独立案例、案例如何编号和维护、哪些证据满足后可以封存。

RCA_TEMPLATE
决定：单个 RCA 文件必须按什么结构记录。

STATUS
决定：当前实际完成状态。

DECISIONS
记录：RCA 最终触发的持久 owner 决策。

INTERVIEW_QA
只从已经封存且有证据的 RCA 中派生面试防守口径。
```

对应文件为：

- [项目评价 SOP](../project/PROJECT_EVALUATION_SOP.md)；
- [项目计划](../project/PROJECT_PLAN.md)；
- [当前状态](../../STATUS.md)；
- [持久决策](../project/DECISIONS.md)；
- [性能工程 Playbook](./PERFORMANCE_ENGINEERING_PLAYBOOK.md)；
- [性能路径与优化面地图](./PERFORMANCE_PATH_AND_OPTIMIZATION_MAP.md)；
- [观测、指标与关联合同](../implementation/OBSERVABILITY_AND_MEASUREMENT_CONTRACT.md)；
- [固定版本源码与运行时审计](../implementation/G0_SOURCE_RUNTIME_AUDIT.md)；
- [仓库工作规则](../../AGENTS.md)；
- [单案模板](./RCA_TEMPLATE.md)。

`OBSERVABILITY_AND_MEASUREMENT_CONTRACT.md` 是预实现的 implementation contract：它定义事件、ID 关联、指标、缺失/重复/乱序/晚到处理和证据完整性，但不表示 trace、schema、hook 或 candidate 已经实现。具体 RCA 必须服从该合同，并继续以 `STATUS.md` 判断实际可用能力。

权威顺序是：SOP 约束证据和主张方法；`PROJECT_PLAN.md` 约束 scope、Gate、STOP 和实验合同；`STATUS.md` 记录实际完成状态；`DECISIONS.md` 记录 owner 已确认的持久决策；implementation 文档记录 pinned source、运行合同和证据；performance 文档只提供诊断与案例治理。低层 RCA 不得反向升级任何上位事实。

### 1.1 当前事实纪律

- 当前正式机制是 **Shared-L3 Publication Admission**。
- 唯一 owned behavior-changing decision 是：`L2 backup completion/ack → prefix closure → ADMIT_TO_L3 | DROP → upstream Mooncake Put 或直接返回`。
- SGLang HiCache、L1/L2 生命周期、scheduler、backup queue、remote lookup、restore 和模型执行属于 upstream。
- Mooncake shared L3、Put/Get、传输、存储和远端容量管理属于 upstream。
- 首次 C0 已在受限拓扑中通过并封存；fresh C1、S1、S2、S3 尚未执行。
- trace instrumentation、D1 new-physical-Put attribution、`ALWAYS_ADMIT` / `ALWAYS_DROP` behavior hook 尚未实现。
- candidate 尚未获设计授权；当前没有 TTFT、Goodput 或 payload-efficiency 正结果。
- 实际状态始终以 `STATUS.md` 为准；上述内容只用于约束本文，不构成第二份状态账本。

[首次 C0 部署复盘](../implementation/G0_FIRST_C0_DEPLOYMENT_RETROSPECTIVE.md) 保持其原有 implementation retrospective 权威和用途。它可以作为保留失败过程与运行证据的写作参考，但不会被自动迁移、复制或重新包装为性能 RCA。

### 1.2 Casebook 不产生项目事实

- 一个案例存在，不等于对应根因已经确认。
- 一份 profiler trace 存在，不等于已经形成 RCA。
- 一个 RCA 被 `SEALED`，不等于项目 Gate 通过或 claim state 升级。
- 一个局部修复有效，不等于获得 Goodput、TTFT 或外部有效性结论。
- RCA 中的源码事实必须绑定对应 repository 的 pinned commit；“最新版”不能解释固定 runtime。
- Gate outcome、案例 lifecycle 和 canonical claim state 是三个正交字段，不得互相替代。

## 2. 独立 RCA 的准入条件

RCA 围绕一个真实、可复现且可证伪的核心问题建案，而不是围绕一种工具、一次 run 或一张图命名。异常已拥有可引用的初始证据，并至少满足下列一项时，才值得创建独立案例：

- endpoint 明显偏离冻结预期，例如 TTFT、TPOT、Goodput 或 error rate 异常；
- mechanism 与 endpoint 不一致，例如 restored tokens 增加但 TTFT 不改善；
- profiler、service metrics 与 runtime trace 相互矛盾；
- forced action 没有产生预期 mediator；
- mediator 改变但 endpoint 没有响应；
- endpoint 改善但理论 mediator 没有变化；
- instrumentation 或 profiler 改变了被测系统；
- benchmark 出现稳定 regression；
- 多 rank、CPU/GPU 或 Store 路径出现不能由表面指标解释的 skew；
- queue、reference、host protection 或异步 terminal 无法闭合；
- 结果可能影响 Gate、STOP、scope、claim ceiling 或 candidate 设计；
- 异常揭示了稳定、可复用且有证据支持的工程规律。

以下情况通常不单独建案：

- 正常通过的 smoke test，或已知且符合预期的 losing workload；
- 单次偶发噪声且无法复现；
- 仅仅运行一次 profiler，或只发现某函数“看起来耗时较长”；
- 没有问题定义的 exploratory trace 或尚未验证的猜测；
- 普通部署命令错误；
- 已由现有 implementation retrospective 完整覆盖的问题；
- 只有结果数字，没有调查、排除与证据链；
- 为了丰富案例数量而拆分同一个根因；
- 每个实验步骤、失败命令或截图各建一个 RCA。

> 一个 RCA 应围绕一个可证伪的核心问题，而不是围绕一种工具或一次运行命名。

方法示例（不是当前项目事实，也不分配案例编号）：

```text
错误：Nsight 分析 / Torch Profiler 分析
正确：为什么 storage-cached tokens 增加后 TTFT 没有下降？
```

## 3. RCA 与其他证据载体的边界

| 内容 | 应存放位置 |
|---|---|
| 一次 run 的配置、seed、commit、环境 | run manifest |
| 原始日志、trace、profile | raw artifact |
| benchmark 汇总和统计结果 | analysis/result artifact |
| 稳定的项目 Gate 和 STOP | `PROJECT_PLAN.md` |
| 当前完成状态 | `STATUS.md` |
| 持久 owner 决策 | `DECISIONS.md` |
| 单个异常的假设、排除过程和根因 | RCA |
| 多个已验证案例共同形成的方法 | Performance Playbook |
| 多个 workload 的最终胜负边界 | future Regime Map |
| 可公开 headline claim 的证据索引 | future Results Index |

RCA 引用运行证据，不复制全部原始日志；它不是 raw artifact、最终结果索引、状态账本或 candidate 设计文档的替代。RCA 应保留错误路径、被证伪假设和停止理由；结果索引只保留最终可公开结论。

## 4. 文件命名与稳定编号

真实案例统一放在：

```text
docs/performance/rca/RCA-0001-<kebab-case-short-title>.md
docs/performance/rca/RCA-0002-<kebab-case-short-title>.md
```

规则：

- ID 使用四位递增编号；只有满足建案准入并创建真实文件时才分配。
- ID 创建后不得复用或重编号；删除、废弃和 superseded 的编号继续保留。
- 文件短标题只描述症状或核心问题，不提前写根因、工具名或最终性能数字。
- 一个 RCA 只有一个稳定 `case_id`。
- 同一根因影响多个 endpoint 时，可在一个主 RCA 中记录多个症状；多个独立根因即使症状相似，也应分别建案。
- 新证据推翻旧结论时，不静默改写历史；使用 amendment 或新建 superseding RCA。

本文件不分配 `RCA-0001`，也不创建空目录或 `.gitkeep`。

## 5. 案例生命周期

案例只使用以下三个 lifecycle。它们不是 Gate outcome，也不是 claim state。

### `DRAFT`

- 调查仍在进行，假设和结论可以变化；
- 根因可能尚未确认；
- 不得进入面试 headline 或性能 claim。

### `SEALED`

- 调查已经停止，证据、结论、限制和 artifact 完整；
- 终局可以是确认根因、合法负结果、scope handoff、现象不可复现或诚实的不可裁决边界；
- `SEALED` 不等于正结果、Gate `PASS` 或 `EXPERIMENTALLY_VALIDATED`。

### `SUPERSEDED`

- 新证据证明旧 RCA 的关键结论不再成立；
- 原文件和原始证据保留，并明确链接 superseding RCA；
- 不删除、覆盖或重新编号历史。

不得用 `PASS` / `FAIL` 代替 lifecycle。只有证据合同满足，且 owner 或当前任务明确授权时，才能封存。Agent 不得因为“文档写完了”自动把 `DRAFT` 改为 `SEALED`。

## 6. 单案元数据合同

每个 RCA 开头至少记录：

| Field | Meaning |
|---|---|
| Case ID | 稳定编号 |
| Title | 症状或核心问题 |
| Case lifecycle | `DRAFT` / `SEALED` / `SUPERSEDED` |
| Opened at | 建案日期 |
| Sealed at | 封存日期或空 |
| Related phase/gate | 相关阶段，仅引用，不改写 Gate |
| Primary symptom | 主要异常 |
| Primary path | publication / restore / scheduler / resource / instrumentation / kernel 等 |
| Affected endpoint | TTFT、TPOT、Goodput、correctness 或 measurement integrity |
| Scope relation | owned / indirectly controllable / upstream observe-only / out-of-scope |
| Pinned code identity | project、SGLang、Mooncake commit |
| Baseline run IDs | 基线运行 |
| Comparison run IDs | 对照或 treatment 运行 |
| Manifest checksum | 冻结运行合同 |
| Raw evidence location | 原始证据 |
| Analysis commit | 分析代码版本 |
| Profiler state | off / nsys / torch-profiler / ncu / other |
| Claim state before | 调查前 canonical claim state |
| Claim state after | 调查后实际 claim state；无升级则保持不变 |
| Related decisions | 若有，链接 `DECISIONS.md` |
| Supersedes / superseded by | 历史关系 |

这些是人工记录字段，不是机器解析 schema，也不表示已有自动生成系统。不存在或不适用的值可写 `N/A`，但必须说明为什么不适用；不能用 `N/A` 掩盖 SEALED 所需证据缺失。

## 7. 案例索引

| Case ID | Title | Lifecycle | Symptom | Primary path | Final disposition | Scope result | Claim impact | File |
|---|---|---|---|---|---|---|---|---|

当前尚无经本 Casebook 合同建立并封存的性能 RCA。

首次真实案例只有在异常可复现、证据可引用且完成最小调查合同后创建。

首次 C0 的 r1–r6 blocker 不自动进入该索引。

## 8. 从症状到根因的证据层级

| 层级 | 定义 | 示例（仅方法示例） |
|---|---|---|
| Symptom | 外部观察到的不符合预期现象 | `TTFT p95 高于冻结 baseline` |
| Observation | 原始或直接派生事实，不包含原因解释 | `某个 rank 比其他 rank 晚进入 collective` |
| Hypothesis | 对事实的可证伪解释 | `该 rank 的 CPU launch path 更慢` |
| Mechanism | 已由区分实验支持的中间作用机制 | `CPU 工作阻塞了后续 kernel launch` |
| Root cause | 能解释症状、排除主要替代解释，并定位到具体阶段、配置或源码行为的原因 | 只有证据闭合后填写 |
| Fix | 针对根因的最小改变 | 不得预先假定 |
| Validation | 同 workload 下 mediator 与 endpoint 按预期变化，guardrail 保持 | 必须引用真实 runs |

表面耗时最长的阶段不一定是根因；一个截图、一个热点、一个高度相关指标或“可能是”不能确认根因。局部改善不自动证明原假设；修复碰巧有效也可能同时改变了多个机制。根因必须解释异常为何只在特定 workload 或 regime 出现。

## 9. 竞争假设合同

每个 RCA 至少保留：

1. 当前最可能解释；
2. 一个合理替代解释；
3. 一个 workload、运行顺序、环境漂移或 instrumentation 混淆解释。

若实际只有两个有意义的技术解释，不机械编造第三个，但必须显式审查测量混淆。每个假设至少记录：

| Hypothesis | Why plausible | Expected evidence | Discriminating experiment | Falsifier | Result |
|---|---|---|---|---|---|

`Result` 只能使用 `supported`、`weakened`、`falsified`、`unresolved`。它们是单个假设的调查结果，不是项目 claim state。

禁止在看完结果后改写最初假设，只保留最终正确解释，把“没有观察到”自动写成 `falsified`，或使用不能区分多个假设的实验。顺序、温度、负载、Store 状态和 profiler overhead 必须作为潜在混淆检查。

## 10. 区分实验的最低要求

有效区分实验必须先回答：

> 如果 H1 成立而 H2 不成立，预期观测应有什么不同？

每个关键实验记录：控制变量、唯一改变、workload、baseline、treatment、fresh state/coldness、profiler on/off、H1/H2 预期、实际结果、排除能力与失效条件。实验结果是 signal、valid false 或 `INCONCLUSIVE` 时，服从 canonical 定义；“未显著”不能自动证伪。

禁止：

- 同时改变多个关键配置；
- 用 profiler-on 与 profiler-off 的性能差直接解释系统差异；
- 比较不同 workload、arrival、worker assignment 或受污染 Store；
- 只比较平均值或事后挑选最有利坐标；
- 把同一 run 内请求当作独立重复；
- 只有相关性、没有反事实差异的实验。

## 11. Path truth 先于性能解释

每个 RCA 必须先证明请求真实走过的路径。根据案例类型至少检查：

- request 成功与 output correctness；
- L1/L2/L3 hit/miss 和 Worker 本地 coldness；
- Put/Get terminal 与 storage-cached、uncached/recomputed token accounting；
- operation、batch、attempt、physical object 的关联；
- trace loss、missing/duplicate terminal；
- queue、reference、host protection 的闭合；
- profiler 是否改变运行配置或执行模式。

没有足够 path truth 时，最大结论只能是：

```text
当前异常无法可靠归因。
```

不得用 profiler 截图补足路径缺口。

## 12. Critical path 与共享资源干扰

每个 RCA 必须把异常分类为：

```text
direct request critical path
```

或：

```text
shared-resource indirect interference
```

restore 可能直接进入 resumed request TTFT；异步 Put 通常不在当前请求的直接 TTFT 路径，却可能通过 queue、CPU、Host DRAM、NIC 或 Store 争用影响其他请求。scheduler re-admission 可能吞掉 restore 的计算节省；collective duration 可能包含其他 rank 的迟到；GPU 空白可能由 CPU 尚未 launch 造成；并行或重叠的局部 duration 不能无条件相加。

单案必须绘制或文字描述：

```text
endpoint
← stage delay
← mediator
← action or upstream event
```

若无法建立这条依赖关系，不得把局部耗时称为 endpoint 根因。

方法示例（均不表示本项目已观察）：

- collective 假象：对齐全部 rank 的 arrival 与共同 completion，排除晚到 rank。
- GPU gap 假象：关联 Python/CPU timeline 与 CUDA launch，排除 CPU 工作阻塞。
- restore 未传导：依次检查 Get wait、runnable→re-admission 和 remaining prefill。
- payload-only：new physical Put bytes 下降而 Goodput 不变时，检查异步隐藏和资源余量。

## 13. 工具使用记录

RCA 必须说明工具回答了什么问题，而不只是列出用过哪些工具：

| Tool | Question it answers | Capture configuration | Overhead risk | Result | Why next tool was or was not needed |
|---|---|---|---|---|---|

默认升级顺序是：

```text
日志 / 服务 metrics
→ request/KV lifecycle trace
→ py-spy / perf / OS counters
→ Nsight Systems 或 Torch Profiler
→ Nsight Compute
```

规则：profiler run 与正式 benchmark run 分开；profile 下的数字不能作为 headline；截图必须追溯到 raw trace；Torch Profiler、nsys、ncu 配置必须记录；prefill/decode 按问题分开；多 rank 问题对齐全部相关 rank；ncu 只在已定位具体 hot kernel 和 shape 后使用。没有必要时允许不使用 profiler，不为丰富 Casebook 强行进入 kernel 层。

## 14. Source mapping 与源码接缝

每个 RCA 记录 repository、pinned commit、文件路径、类/函数/状态对象、调用路径、异常到接缝的映射、ownership，以及源码事实与 runtime 事实的区别。还要回答：删除或改变该接缝，理论上是否会消除异常？

禁止使用最新版源码解释 pinned runtime、用博客替代源码、只给函数名而不解释状态所有权、看到相关函数就称为根因，或把 upstream 修复写成本项目个人实现。

## 15. Controllability 与 scope 裁决

每个 RCA 必须回答：

```text
当前根因是否受 Shared-L3 Publication Admission 控制？
```

### Owned behavior：可直接控制

包括 publication `ADMIT/DROP`、decision overhead、prefix-group/closure、fail-open 和 instrumentation overhead。只有 canonical Gate 已授权时，才进入最小修复和 forced-action 验证。

### Admission 可间接影响

包括 `StorageOperation` 数量、backup queue pressure、actual Put、shared-L3 内容组成、useful availability 和 recomputed tokens。必须闭合 `action → mediator → endpoint`，不能凭相关性修改 policy。

### Upstream observe-only

包括 scheduler re-admission、Mooncake Store 内部、CPU launch、network transport、prefill/decode operator、collective 和 kernel。合法处理是记录根因、判断其是否阻断项目、形成 substrate limitation 或 upstream handoff，并按 canonical Gate STOP 或降级。

### 当前 out-of-scope

RCA 不能直接授权 scheduler rewrite、RDMA/GDR/NIXL、eviction、router、PD disaggregation、quantization、kernel rewrite 或 HA。值得独立研究时，只能建议新的 owner scope 决议，不能在单案中顺便实现。

## 16. 根因确认标准

只有以下条件大部分成立，才可写“根因已确认”：

1. 异常能够稳定复现；
2. path truth 足以支持归因；
3. 竞争假设已被有排除能力的实验区分；
4. 根因能解释 workload/regime 边界；
5. 根因对应明确 runtime stage 或源码接缝；
6. 操作根因后，关键 mediator 按预期变化；
7. endpoint 在同一 workload 下按预期变化，或明确证明 endpoint 对该 mediator 不敏感；
8. correctness、TPOT 和资源生命周期 guardrail 保持；
9. profiler/instrumentation 干扰已排除；
10. 主要替代解释已被证伪或显著削弱。

一个热点函数、长 kernel、GPU 空白、NCCL duration、cache miss、相关指标、一次偶然改善、一次不可重复实验、模型估算或单 rank 截图都不足以单独确认根因。

## 17. 合法终局

### A. 根因确认，修复有效

```text
root cause → minimal fix → mediator change → endpoint improvement → guardrails pass
```

### B. 根因确认，但不属于当前 scope

形成 upstream limitation、handoff evidence、当前 Gate STOP/substrate qualification 或另立项目建议；不得为产生个人代码强行扩 scope。

### C. 机制改变，但 endpoint 不响应

例如 new physical Put 下降但 Goodput/TTFT 不变。合法结论可能是 payload/capacity efficiency、异步工作被隐藏或当前测床资源宽松；不得形成性能提升 claim。

### D. 表面异常被证明是假象

例如 collective 表观变慢实际来自 rank 晚到，或 GPU gap 实际来自 CPU 工作。证明误判如何被排除本身就是有效结论。

### E. 冻结预算内无法裁决

记录缺失证据、不能补足的原因、仍存假设、最大允许结论、是否触发实验系统 `INCONCLUSIVE`，以及重开所需的新能力。不可裁决不得写成“证明无性能机会”。

### F. 现象无法复现

记录原始异常、复现尝试、环境差异、最大重复预算、噪声判断和停止理由；不得不断改变 workload 强行复现。

## 18. 修复、验证与删除测试

若 RCA 包含代码或配置修复，至少要求：

**修复前：**异常复现、baseline manifest、raw artifacts、竞争假设和根因 mediator。

**修复实现：**最小 patch、pinned source、TDD 或明确替代验证；保持 workload 和不相关配置不变；一次只修改一个决策面；instrumentation patch 与 behavior patch 分离。

**修复后：**在相同 workload 下验证异常、mediator、TTFT、TPOT guardrail、Goodput、output correctness、request success、queue/ref/protection、CPU/RSS、trace loss、losing workload 和 regression。

同时记录删除或回滚测试：删除修复后，异常或收益是否重新出现？无法执行时说明原因，不能静默省略。

## 19. Action—mediator—endpoint manipulation check

每个性能优化 RCA 分开报告：

1. **Action**：`ADMIT/DROP` 或其他受控 action 是否真正分离；
2. **Mediator**：new physical Put、queue/resource pressure，或 availability/useful Get/avoided prefill 是否按理论变化；
3. **Endpoint**：Goodput@TTFT-SLO、TTFT、TPOT、request success 是否响应且 guardrail 保持。

裁决：

- action 未变化：实验没有操控成功；
- action 变化、mediator 不变：理论链断裂；
- mediator 变化、endpoint 不变：最多形成机制或效率结论；
- endpoint 变化、mediator 不变：优先怀疑混淆因素；
- 三层共同变化且 correctness 成立：才可能形成固定边界内的性能因果结论。

## 20. Evidence 与 artifact 合同

每个 `SEALED` RCA 必须能追溯到：run IDs、pair IDs、manifest checksum、project/SGLang/Mooncake commit、model/tokenizer identity、workload hash、policy/config、profiler on/off、raw logs、trace、profile、analysis script/commit、derived tables/charts、environment、command、output correctness artifact、统计方法、异常 run、failed hypotheses、losing workload 和剩余不确定性。

规则：

- RCA 不粘贴大段日志，只引用最小关键片段；
- 截图指向 raw trace，图表指向生成脚本和输入；
- raw artifact 不得被聚合结果替代，失败 run 不得静默删除；
- private prompt、token 文本和工具结果原文不得进入 RCA；
- 无法访问原始证据的结论不得封存为可复核 RCA。

## 21. Claim Ceiling

每个 RCA 必须包含 `## Claim Ceiling`，明确证据最多支持哪一层：

| 层级 | 最大允许表述 |
|---|---|
| Path truth | 某条请求路径真实存在 |
| Mechanism truth | 某个 action 改变了 Put/Get、queue 或 prefill |
| Resource truth | 某个共享资源压力发生变化 |
| Payload/capacity efficiency | endpoint 非劣时减少 new physical Put 或无效 publication |
| Endpoint performance | 冻结 workload 和 paired experiment 中改善 Goodput/TTFT |
| External validity | held-out 或额外 workload 中仍成立 |

禁止 path truth 直接升级为性能提升，submitted bytes 升级为 new physical Put，adapter payload 升级为 wire traffic，completed Get 升级为 useful restore，query unavailable 升级为 eviction proof，resource counter 升级为因果性，profiler 截图升级为根因，局部 kernel speedup 升级为 serving Goodput，单一 workload 升级为普适结论，或 upstream 能力升级为个人实现。

## 22. 必须拒绝的反模式

1. **工具驱动调查**：想展示 nsys，先抓 trace，再找异常解释。
2. **最大耗时等于根因**：看到 NCCL、kernel、Put、GPU gap 或 CPU 函数长就下结论。
3. **只看一个 rank 或进程**：忽略 collective、scheduler 和多进程 pipeline 的 arrival skew。
4. **profile 数字作为正式 benchmark**：忽略 profiler overhead 和执行模式变化。
5. **删除错误假设**：只保留事后看来正确的推理。
6. **修复有效等于根因正确**：忽略 patch 同时改变多个机制。
7. **bytes 下降等于性能提升**：忽略异步隐藏和资源宽松。
8. **cache hit 等于 useful restore**：忽略 Get/load 与 token substitution。
9. **query unavailable 等于 eviction proof**：越过 telemetry 边界。
10. **顺便实现 scope 外根因**：把项目扩成 scheduler、network、kernel 或 eviction 项目。
11. **每个实验都建 RCA**：产生低价值流水账。
12. **没有 raw artifacts**：只保留截图、结论或手工表格。
13. **事后挑 workload**：移动压力坐标直到修复有效。
14. **不报告 losing workload**：制造普适提升假象。
15. **把 `INCONCLUSIVE` 写成无机会**：实验没有排除能力却触发 STOP。

## 23. 维护与封存规则

- 一个 RCA 对应一个核心异常或根因问题；只有真实 evidence 存在后创建。
- `DRAFT` 可随调查更新；`SEALED` 后不得静默重写关键结论。
- 新证据推翻结论时，添加明确 amendment 或创建 superseding RCA；原始文件和 raw artifact 保留。
- raw artifact 保持不可变；索引随 lifecycle 更新。
- RCA 触发持久项目决策时，另行更新 `DECISIONS.md`；本任务不执行。
- RCA 改变实际状态时，另行更新 `STATUS.md`；本任务不执行。
- 只有封存且证据充分的 RCA 才可后续派生到 `INTERVIEW_QA.md`。
- 方法经验只有跨多个案例稳定复现后，才考虑升级到 Performance Playbook。
- 单案的 run-specific 结论不得写进 Path Map。
- 最终 headline claim 进入 future Results Index，不能只存在于 RCA。

## 24. 未来可能触发建案的问题类型

> 以下仅是触发条件示例，不代表项目已经观察到这些现象，也不得据此创建案例文件或预分配编号。

- restore token 增加但 TTFT 不下降；
- remote Get 成功但 storage-cached tokens 为零；
- Put activity 高但无法解释 endpoint；
- new physical Put bytes 下降但 Goodput 不变；
- capacity 变化导致 useful Get 和 prefill 变化；
- policy CPU overhead 抵消收益；
- trace-enabled 运行改变 queue 或 TTFT；
- profiler 与 service metrics 结论不一致；
- 一个 rank 的 collective 表观时间异常；
- GPU timeline 空白但 kernel duration 正常；
- 只有首请求慢；
- shutdown 或 Put failure 后资源未释放；
- endpoint 改善但预期 mediator 不变；
- static baseline 已经吃掉 candidate residual；
- 根因最终定位到当前 scope 外的 upstream 问题。
