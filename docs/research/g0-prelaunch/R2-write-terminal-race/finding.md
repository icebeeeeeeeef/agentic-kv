# R2 — 写入终态、dedup、race 与 failure

**结论：STOP（state classification=FAIL）。** 这不是“尚未测试”：fixed Mooncake source 把 `OBJECT_ALREADY_EXISTS` 归约
为 Python success `0`，而 adapter 同样以 `0` 表示 precheck 已存在。因此一个
`precheck-miss + put=0` terminal 不能区分本 writer 新写与 race 中别人先写。

## SOURCE_VERIFIED

- adapter 的 existing physical object 不送 Put，并预填 `0`；missing object 的 Put result
  返回后再归约为 logical page bool。
- Put object result 为 `0` 成功、负数错误；但 `OBJECT_ALREADY_EXISTS` 也会得到 `0`；Get 为正读取字节、负数错误。
- controller 在 failed batch 后 break，且源码明确 partial-success handling 未完成。

## 不能得出的结论

因此当前 adapter-only trace 不能满足 contract 的 state classification（该检查项为 `FAIL`），
R2 的 payload/dedup/race 归因分支为 `STOP`。
必须先获用户授权，在 Mooncake duplicate-to-success 归约**之前**添加独立、trace-only 的
原因字段；否则停止 new-write / payload 归因分支。运行 dedup/race/failure 仍可检查 cleanup，
但不得以其 `put=0` 计作新写。
