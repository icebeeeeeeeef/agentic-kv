# Phase 5：闭合因果链并裁决 candidate 必要性

Status: open
Assignee: unassigned
Labels: wayfinder:grilling
Parent: [Agentic-KV：从 fresh C1 到证据收口的 Phase 0–7 八阶段推进地图](../MAP.md)
Blocked by: [Phase 4：验证 fail-open hook 与 forced actions](05-phase-4-hook-and-forced-actions.md)

## Question

在 actuator 与生命周期正确性已经成立后，如何规划同一 fixed-L2 treatment 内的 `ADMIT_ALL / SECOND_HIT / STATIC_FREQ*` 在线对照、各 arm 自身的 runtime mediators 和 paired `Goodput@TTFT-SLO`，使链 A 或链 B 至少一条真正闭合，并检查 STATIC_FREQ* 的 admitted-but-not-read 与 dropped-then-demanded residual？

随后如何按冻结顺序执行 actual X* 替代攻击与真实在线 O1 cheating-oracle stop bound，并只在 residual、O1 与 owner review 都保留机会时决定是否建立 conditional ledger、定义一个最小 candidate；什么结果应直接收口为 shared-L3-no-value、payload-only、static-sufficient 或 X*-sufficient，而不是继续增加 signal？

## Comments

<!-- 认领后再开始；答案在 resolution comment 中记录。 -->
