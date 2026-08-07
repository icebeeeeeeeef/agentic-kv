# R3 — object payload bytes 与 run isolation

**结论：STOP（new-payload branch）。** adapter 可以看到 physical key、pointer、`buffer_sizes`
和 raw result，却无法从 `put=0` 分辨 new Put 与 race-existing；因此不能报告
`completed_new_put_bytes`。这不是通过补 runtime trace 可以修复的缺口。

## 定义（待 runtime 对账）

该指标的原定义需要同一 decision/attempt 下 **new Put** 的每个 physical object
`buffer_size` 之和；但当前 terminal 不能确认 new Put，故该指标不可得。不得把
`put=0` 的 `buffer_size` 之和换名为 completed/new payload。若用户授权 pre-collapse
Mooncake observation，可重开该分支；否则 canonical plan 必须停止 payload-efficiency claim。

## 隔离结论

adapter `clear()` 调 `remove_all()`，但本次没有 fixed-version runtime before/after 证据，
所以不能把 `clear()` 当作 comparative isolation oracle。每 scenario 使用 fresh Store/epoch，
并记录 epoch、capacity 和 object-state evidence。
