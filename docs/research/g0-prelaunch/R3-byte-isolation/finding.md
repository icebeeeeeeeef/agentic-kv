# R3 — object payload bytes 与 run isolation

**结论：STOP（new-payload branch）。** adapter 可以看到 physical key、pointer、`buffer_sizes`
和 raw result，却无法从 `put=0` 分辨 new Put 与 race-existing；因此不能报告
`new_physical_put_bytes`。在本次 adapter-only source audit 下，这不是通过 adapter runtime trace
可以修复的缺口；后续 [D1](../../../project/DECISIONS.md#d1--保留-new-put-payload-指标并授权最小观察-patch)
已固定若进入 payload 归因时允许的 Mooncake pre-collapse observation；是否施工还受 canonical pre-D1
ruling 与 D12 约束，未实现前本 finding 的 STOP 仍成立。

## 定义（待 runtime 对账）

该指标的原定义需要同一 decision/attempt 下 **new Put** 的每个 physical object
`buffer_size` 之和；但当前 terminal 不能确认 new Put，故该指标不可得。不得把
`put=0` 的 `buffer_size` 之和换名为 completed/new payload。D1 已固定 pre-collapse Mooncake observation
边界；只有 canonical pre-D1 ruling 允许施工且其 non-interference artifact 通过后才可重开该分支，否则
canonical plan 必须停止 payload-efficiency claim。

## 隔离结论

adapter `clear()` 调 `remove_all()`，但本次没有 fixed-version runtime before/after 证据，
所以不能把 `clear()` 当作 comparative isolation oracle。每 scenario 使用 fresh Store/epoch，
并记录 epoch、capacity 和 object-state evidence。
