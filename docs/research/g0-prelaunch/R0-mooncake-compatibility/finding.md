# R0 — Mooncake 精确版本与 adapter 兼容性

> Historical prelaunch finding. It records only evidence available before first-C0. The later r6 artifact scoped-validates the recorded stock target-Linux combination; current state is [STATUS.md](../../../../STATUS.md).

**结论：INCONCLUSIVE。** 已通过 source identity；未运行 binary identity、adapter
initialization 或 Put/Get terminal，因而不能称 compatible。

## 已通过

- `v0.3.12.post1` 的完整 commit 是 `6041a609a8c3af35e778f70db344f145c2914980`。
- distribution/version、CPython 3.11 Linux x86_64 wheel 名称与 SHA-256 已固定。

## 阻塞与下一步

在本 finding 的采集工作区中是 macOS，官方 wheel setup 明确不支持该平台；这不是候选 `FAIL`，但不能用它
代替目标 Linux GPU probe。进入下一步前，在目标机执行 contract 中的 wheel 安装、metadata、
five-API、adapter initialization、最小 Put/Get，并保存所有 raw artifacts。若任何 API/ABI/CUDA
错误出现，结论改为 `FAIL`；若 service 未就绪，保留 `INCONCLUSIVE`。
