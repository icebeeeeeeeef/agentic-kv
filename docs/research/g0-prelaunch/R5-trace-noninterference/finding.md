# R5 — trace-only 传播与不干扰性

**结论：INCONCLUSIVE。** 最小 source map 已经明确，但 trace patch 没有实现，也没有 paired
stock/trace run，不能宣称 deterministic correlation 或 non-interference。

## 最小 map

在 prospective seam 生成 `run_id`/`observation_id`；在 `StorageOperation.id` 建立关联；controller
对每个 operation 的 batch ordinal 导出 `attempt_id`；adapter 在 preprocess、exists-filter、Put/Get
raw result 后记录 logical/physical mapping。opaque ID 不得进入 keys、queue ordering、retry、
dedup、Get 或 policy。

## PASS oracle

trace-disabled、trace-enabled、两个不同 opaque ID 的三次同一 isolated microcase，必须保持
keys/order/result/output/queue/ref terminal 恒等；trace 只改变已声明 JSONL。缺任一 terminal
为 `INCONCLUSIVE`，ID 影响行为为 `FAIL`。
