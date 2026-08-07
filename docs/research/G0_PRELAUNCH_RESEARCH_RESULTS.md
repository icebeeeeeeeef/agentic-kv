# G0 启动前调查结果

> 调查完成日期：2026-08-06
> 总裁决：**G0-SOURCE BLOCKED**
> 范围：`G0_PRELAUNCH_RESEARCH_CONTRACT.md` 的 R0–R6。本文是源码/发布物调查，不是 runtime 验证。

## 结论

Mooncake 候选现在可以精确固定为 `v0.3.12.post1` / commit
`6041a609a8c3af35e778f70db344f145c2914980`；官方 Linux x86_64 CPython 3.11
wheel 的 SHA-256 也已确认。但当前工作区没有 Linux GPU、Mooncake 服务、已安装 wheel 或
SGLang adapter Put/Get artifact。因此版本身份的源码调查通过，不等于组合兼容。

| 包 | 总结论 | 已通过的调查事实 | 阻塞它成为 PASS 的证据 |
|---|---|---|---|
| R0 | INCONCLUSIVE | tag/full SHA、distribution version、官方 wheel digest | pinned adapter 初始化与真实 Put/Get 尚未运行 |
| R1 | INCONCLUSIVE | TCP、external non-zero segment、worker zero segment 是 pinned upstream 支持路径 | 没有 A/B/C 部署、health/segment response |
| R2 | STOP（state classification=FAIL） | adapter 的 exists-filter 与物理 object result 归约、Mooncake Put/Get 返回值语义 | Mooncake 将 `OBJECT_ALREADY_EXISTS` 归约为 Python `0`，race/existing 与真正新写在 adapter terminal 不可区分；同一 API 的 runtime 不能恢复该信息 |
| R3 | STOP | `buffer_sizes` 与 object key 在 adapter 可见；`clear()` 调用 `remove_all()` | R2 使 `completed_new_put_bytes` 不可归因；禁止 payload-efficiency claim，且不能仅凭 `clear()` 比较 |
| R4 | INCONCLUSIVE | first-miss lookup 与 storage-loaded-token 记账位置可审计 | 无 cold B、A Put、B Get、output join |
| R5 | INCONCLUSIVE | `StorageOperation.id`、batch 切分、adapter object 边界提供最小传播点 | 未实现 trace patch，未做 disabled/enabled 等价运行 |
| R6 | INCONCLUSIVE | L2 ack 后 seam、first-miss、ack/shutdown cleanup 是源码事实 | hook、hole、fail-open、DROP 与 drain artifact 均不存在 |

没有包达到运行时 `PASS`。R2 的 state-classification 检查是一个**源码已证实的 FAIL**，
因此该包的 payload/dedup/race 归因分支为 `STOP`：`precheck-miss + put=0` 不能区分新写和
另一 writer 已写；R3 因此对 new-payload bytes 为 `STOP`。此外 R0 仍缺
真实组合 probe。当前整体仍是 `G0-SOURCE BLOCKED`，不得实施 behavior hook 或声称
Mooncake 已兼容。

## 已固定的一手身份

- [Mooncake official release](https://github.com/kvcache-ai/Mooncake/releases/tag/v0.3.12.post1)
  把 `v0.3.12.post1` 指向
  [`6041a609a8c3af35e778f70db344f145c2914980`](https://github.com/kvcache-ai/Mooncake/commit/6041a609a8c3af35e778f70db344f145c2914980)。
- 该 tag 的 [wheel metadata](https://github.com/kvcache-ai/Mooncake/blob/6041a609a8c3af35e778f70db344f145c2914980/mooncake-wheel/pyproject.toml#L20-L29)
  为 distribution `mooncake-transfer-engine` version `0.3.12.post1`，且要求 Python >=3.10。
- 首轮唯一允许的 wheel 是
  `mooncake_transfer_engine-0.3.12.post1-cp311-cp311-manylinux_2_28_x86_64.whl`，
  SHA-256 `8b73bf8a4f1de741a73f04f32f1e73549c60bfbf7ee73710141ef1f8ea324439`。
  官方 setup 对 macOS 直接拒绝，故本 macOS 工作区不是这个 wheel probe 的替代环境。
  [setup.py](https://github.com/kvcache-ai/Mooncake/blob/6041a609a8c3af35e778f70db344f145c2914980/mooncake-wheel/setup.py#L5-L12)

## 关键源码结果

1. SGLang adapter 把 logical page 展开为 physical keys/pointers/`buffer_sizes`，先
   `batch_is_exist`，只对缺失 object 调用 Put，然后把每 object return 归约为每 logical
   page bool。已存在 object 被本 adapter 填为 `0`，所以 page-level `True` **不**表示新 Put。
   [adapter](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/storage/mooncake_store/mooncake_store.py#L999-L1115)
2. Mooncake 的公开 contract 是 Put 每 object `0` 成功、负数错误；Get 每 object 返回
   成功读取字节数、负数错误。更重要的是，Mooncake 把 `OBJECT_ALREADY_EXISTS` 也归约为
   成功。故 precheck miss 后的 `0` 既可能是本 writer 新写，也可能是 race winner 已写；
   adapter trace 无法恢复这一原因，不能将其计作 `completed_new_put_bytes`。
   [SGLang result adapter](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/storage/mooncake_store/mooncake_store.py#L999-L1028)
   [Mooncake duplicate handling](https://github.com/kvcache-ai/Mooncake/blob/6041a609a8c3af35e778f70db344f145c2914980/mooncake-store/src/client_service.cpp#L1531-L1565)
   [batch reduction](https://github.com/kvcache-ai/Mooncake/blob/6041a609a8c3af35e778f70db344f145c2914980/mooncake-store/src/client_service.cpp#L2427-L2459)
3. pinned SGLang 支持 `tcp`，external Store 设置非零 `global_segment_size`，而有 Store 时
   SGLang worker 可设为 `0`。同一共享 key-space 需要一致的 `tenant_id`、model name 和
   `extra_backend_tag`；`local_hostname` 是角色局部字段。部署是否实际符合这些条件仍未验证。
   [upstream README](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/storage/mooncake_store/README.md#L116-L183)
   [tenant/zero segment](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/storage/mooncake_store/README.md#L249-L261)
4. `MooncakeStore.clear()` 仅调用 `self.store.remove_all()`；没有 source + before/after
   service evidence 时，它不能作为 comparative-run isolation 的证明。优先每 scenario
   fresh Store/epoch。
   [clear](https://github.com/sgl-project/sglang/blob/b058dc910619c9d4bce9e9e24117104ffc491fa6/python/sglang/srt/mem_cache/storage/mooncake_store/mooncake_store.py#L1269-L1271)
5. R4–R6 已有的 SGLang source seam、first-miss 与 cleanup 事实保持
   `SOURCE_VERIFIED`，具体位置见 [G0 source audit](../implementation/G0_SOURCE_RUNTIME_AUDIT.md)。
   trace-only 与 hook 都仍是待实现的独立 patch，不存在可以运行的本地 artifact。

## 接续条件

下一位执行者必须从 R0 的 exact Linux GPU probe 开始，保存每个包要求的 `finding.md`、
`evidence.md`、manifest、原始 stdout/stderr、配置与 checksum。R2/R3 不能靠补 runtime
artifact 解除：必须先由用户裁决是否允许在 Mooncake 的 `OBJECT_ALREADY_EXISTS → success`
归约**之前**增加独立 trace-only observation；否则 canonical plan 必须删除“new payload bytes”
claim，而不是把模糊的 Put success 改名后继续使用。包目录中已写入本次 source-only 结果和
缺失 artifact。

各包详情：

- [R0](g0-prelaunch/R0-mooncake-compatibility/finding.md)
- [R1](g0-prelaunch/R1-external-store-topology/finding.md)
- [R2](g0-prelaunch/R2-write-terminal-race/finding.md)
- [R3](g0-prelaunch/R3-byte-isolation/finding.md)
- [R4](g0-prelaunch/R4-runtime-attribution/finding.md)
- [R5](g0-prelaunch/R5-trace-noninterference/finding.md)
- [R6](g0-prelaunch/R6-closure-failopen-cleanup/finding.md)
