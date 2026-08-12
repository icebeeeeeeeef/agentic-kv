# G0 D14 Survival Preregistration Contract

> 状态：**OWNER-DECIDED CONTRACT / 非运行时证据**（2026-08-11）
> 权威：本合同具体化 [D14](../project/DECISIONS.md#d14--shared-l3-publication-admission-收敛与替代攻击)、[PROJECT_PLAN 的 S1–S3](../project/PROJECT_PLAN.md#s1s3当前-survival-contract) 和 [G0 execution plan Active Task 2](G0_EXECUTION_PLAN.md#active-task-2-prepare-and-run-d14-s2s3-survival-gates)。如有冲突，以 PROJECT_PLAN 的 Gate/STOP 为准。
> 范围：C1 stock-only、treatment-blind preregistration；不是 D1、trace、hook、candidate、payload attribution 或 online oracle 的授权。

## 1. C1 的唯一时序

```text
fresh C1 cohort
  → redo C0 preflight
  → finite X* source audit and configuration probe
  → L2_ONLY baseline-only calibration
  → freeze/checksum manifest
  → S1
  → sticky-reuse S2/S3 plus declared X* arm
  → D14 PASS / STOP / INCONCLUSIVE ruling
```

C1 的 C0 preflight 是 runtime eligibility，不得用于挑选 target coordinate、SLO、`delta`、capacity 或统计方法。所有 S1–S3 treatment result 都必须在 manifest checksum 之后产生；同一 paired arm 不得跨重建 cohort 补跑。

## 2. 共同 endpoint、隔离和统计

主 endpoint 固定为：

```text
Goodput@TTFT-SLO
  = measurement window 中 completion 成功且 TTFT <= frozen SLO 的请求数 / window seconds
```

固定 decode、request completion/error accounting、warm-up/measurement/drain 边界和 arrival trace 必须进入 workload/config hash。`resumed_ttft`、token source、Store NIC/CPU 和 queue 指标只作机制诊断；没有 paired endpoint interval 不能通过任何 S gate。

每个 pair 使用相同 model/tokenizer、request stream、arrival timestamps、worker assignment、A/B physical-GPU mapping、L1/L2 configuration、transport、remote eviction implementation、warm-up/measurement/drain 和统计脚本。每个 L3 arm 使用 fresh Store 或有强于 restart 的容量/keyspace isolation proof；capacity 不得 in-place 改写。pair order 及 seed 在 treatment 前冻结。

对 effect `d`：单侧 interval lower bound `> delta` 才是 signal；所需 witness 全成立且 upper bound `< delta` 才是 valid false。区间跨阈值、分母非正、预算耗尽仍不清楚、任何 fairness/pressure witness 不可证，均为 `INCONCLUSIVE`。最少 3 paired repeats 是下限而非 null oracle；若 interval method 不支持 sequential classification，必须跑满冻结 maximum 后只分类一次。

## 3. S1 RESTORE_VALUE_REGION

每个 baseline-only 冻结的 target coordinate 使用 roomy C，避免容量竞争混入 restore/recompute：

- **L3 restore arm**：A 为 B request 使用的每个 unique page-aligned prefix 完成 Put；B local-cold 后从 C restore。
- **B-cold recompute control**：fresh B、L3 disabled、同一 raw request stream、同一 decode/arrival/assignment；B 重新 prefill。
- 一个 measurement run 内的 B request 不得重复同一 prefix 或其相互前缀，避免 B 自己变热；每个 request 仍需可关联的 coldness/get/output artifact。

主效应：

```text
d_restore = (Goodput_L3_restore - Goodput_B_cold_recompute)
            / Goodput_B_cold_recompute

m_restore = sum(storage_cached_tokens with matching remote Get/load evidence)
            / sum(prompt_tokens of eligible B-cold requests)
```

`m_restore` 是 remote-Get materiality quantity，不是 hit-count。它的 floor `gamma_restore`、target coordinates、SLO 和 interval 只能在 baseline-only calibration 后、第一次 target-workload L3 result 前冻结。

| S1 result | 规则 |
|---|---|
| surviving | 至少一个 covered coordinate 的 `d_restore` lower bound `> delta`，且 `m_restore` lower bound `> gamma_restore`；C0 的两个 predicate 也必须已通过。 |
| STOP | 全部 covered decisive coordinates 的 `d_restore` upper bound `<= 0`，或 target workload 的 `m_restore` upper bound `<= gamma_restore`。 |
| INCONCLUSIVE | B coldness、Get/load、token/endpoint comparability 或 interval exclusion 不足。 |

S1 通过不表示 publication policy 有机会；它只说明 shared-L3 restore 在该受限 region 有可裁决净价值。

## 4. X*：有限审计面，而不是“穷尽所有 upstream”

```text
X* = source-audited stock write_through_selective
   + baseline-only demonstrated sufficient L2
   + each control inside the frozen audit surface that is source/runtime verified,
     configurable, actually enabled, and fairness-compatible
```

审计面必须在 manifest 中逐项列出：pinned source paths/functions、selective/hit-count semantics、CLI/config propagation、adapter quota/eviction/prefetch/metric wiring、runtime config echo 和 effect evidence。每项状态只能为：`INCLUDED`、`EXCLUDED_NOT_SOURCE_VERIFIED`、`EXCLUDED_NOT_RUNTIME_EFFECTIVE` 或 `EXCLUDED_UNFAIR`。

“sufficient L2”要求目标 active set 落在冻结 L2 budget 内，且 L2_ONLY baseline-only 中提高一个可用 L2 configuration 后，endpoint 变化仍在冻结 calibration-noise band 内。否则 X* 仍是 `INCONCLUSIVE`，不能用“看起来够大”替代。

X* 是 external substitute，不混入 fixed-L2 的因果 ladder。它作为已冻结 additional arm 保留 config/effect/endpoint evidence；没有 source/runtime proof 的 quota 或 eviction 一律不得假设存在。

若已冻结的 X* arm 同时证明：(a) sticky publication mass 已低于阈值或相应 pressure witness 消失，且 (b) endpoint 不劣于预注册 best-stock reference 的 non-inferiority bound，则记录 `FRONTIER_ELIMINATES_OPPORTUNITY` 并按 D14 STOP。若 X* 本身或其 mass/effect 不可证，是 `INCONCLUSIVE`，不是该 STOP。

## 5. sticky-reuse、S2 和 S3

sticky-reuse 的每个 prefix 必须：已满足 source-audited stock local selective condition；在固定 horizon `H` 内 remote value 低；并保存 source-derived 或 stock-observable的 logical publication-mass lower bound。它不是 `new_physical_put_bytes`，也不能由 NIC 流量代替。exact admitted/new-Put physical bytes 保持 D1 后的 trace 问题。

| Gate | 固定 causal pair | signal 的额外 witness | 禁止推论 |
|---|---|---|---|
| S2 `PUBLICATION_COST_ENVELOPE` | `STOCK_L3` vs `L2_ONLY`，固定 L2 | local-selective proof、非零 logical publication-mass lower bound、baseline-selected knee、stock-visible Store/publication activity、predeclared Store/queue/resource witness、paired endpoint | NIC/CPU 单独证明 Put cost，或任何 new-Put payload attribution |
| S3 `CAPACITY_EXTERNALITY` | `STOCK_L3_roomy` vs `STOCK_L3_small`，各自 fresh C | actual segment responses；`reusable_set < small < reusable_set + sticky_background`；`roomy > full_distinct_set + margin`；同向的 query-time storage/useful Get 与 uncached/prefill token changes | victim、eviction reason、精确 occupancy 或 admission candidate value |

```text
d_publication = (Goodput_L2_ONLY - Goodput_STOCK_L3) / Goodput_L2_ONLY
d_capacity    = (Goodput_roomy - Goodput_small) / Goodput_roomy
```

S2/S3 任一 signal 只授权后续 trace-path investment，不授权 candidate。二者 valid false 才触发 D14 pre-implementation STOP；任一 `INCONCLUSIVE` 阻止该 null STOP。one-shot/unique-heavy 只可作为 X* negative control，不能构成 S2 signal 或替代 sticky-reuse。

## 6. manifest 冻结表

| manifest fields | 合法来源与冻结时点 |
|---|---|
| `identity` | C1 build/API probe 的 realized identity；不得复用旧 C0 identity。 |
| `common` | L2_ONLY calibration 冻结 SLO、window、delta、interval、confidence、repeat budget、arm order、fresh-store method。 |
| `workload_splits` | workload generation 后、首次 treatment 前冻结 hash；只有未来 O1 可读 `oracle_eval` future label，`target_held_out` 永不读 future label。 |
| `x_star` | finite source audit、runtime config/effect probe、L2_ONLY calibration；未证实项写 exclusion reason。 |
| `s1_restore_value_region` | C0 preflight 合格后，由 baseline-only 选择 target coordinates、B-cold controls、`gamma_restore` 和 interval。 |
| `sticky_reuse_definition` | source-audited selective semantics + frozen workload ledger；H、low-value rule 和 mass floor 必须在 treatment 前确定。 |
| `s2` / `s3` | baseline-only pressure and fairness calibration；S3 segment formula 先由 frozen KV-payload estimate 导出，再以 runtime Store response 验证。 |

完成的 preregistration 必须先 checksum；任一 workload、X* construction、load/knee、capacity、SLO、delta、interval、repeat budget、arm order 或 split 变化都创建新版本并保留旧 artifact，绝不覆盖或静默重跑。

## 7. 未决项

本合同冻结规则，不伪造数值。以下仍为 `UNRESOLVED`，只能在相应冻结点填入：actual selective semantics/controls、target workload and splits、SLO、`delta`、`gamma_restore`、pressure thresholds、capacity values、interval method、maximum repeats 和 runtime-visible witness fields。
