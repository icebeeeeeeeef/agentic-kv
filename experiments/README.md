# Experiment contract

Experiment runs are not committed by default. Store raw runs under experiments/runs and summarize validated evidence in a reviewed document.

The active G0 survival contract has two different artifacts:

1. a treatment-blind preregistration copied from
   [`manifests/d14-survival-preregistration.example.json`](manifests/d14-survival-preregistration.example.json),
   completed from source audit and baseline-only calibration and checksummed before any treatment result is viewed; it records the S1 hard veto, sticky-reuse S2/S3 witnesses, actual X* construction, and workload-split boundaries; and
2. one run manifest per actual arm/repeat, linked back to that preregistration checksum.

The preceding C0 functional preflight is governed separately by the
[`G0 C0 Restore Qualification Contract`](../docs/implementation/G0_C0_RESTORE_QUALIFICATION_CONTRACT.md).
The local pre-rental input materializer, target-side checksum verifier, and one-shot manual procedure live in
[`c0/`](c0/); they prepare C0 delivery only and do not start upstream or classify runtime outcomes.
The current ignored materialization is `data/c0-input-bundles/first-c0-20260812-r7`; its owner trust-root
`bundle-manifest.json` SHA-256 is `207f866e2bbc83f96207d112a8d10730280fddd91422b59f02e7b858d9b7c477`.
The independent owner trust-root for [`c0/FIRST_C0_RUNBOOK.md`](c0/FIRST_C0_RUNBOOK.md) is SHA-256
`577588c07b7cb7d5a593f5dd2b0d69a8d733a6c6cc898767374dc7a3b241b4ec`; verify it before executing either host block and retain the verified file in run evidence.
This local root/checksum evidence is `IMPLEMENTED_UNVALIDATED`, not target-host or C0 evidence.
The completed D14 schema is interpreted by the
[`G0 D14 Survival Preregistration Contract`](../docs/implementation/G0_D14_SURVIVAL_PREREGISTRATION_CONTRACT.md).
Before any formal cohort, the staged inputs, role artifact paths, archive finalizer and release boundary are governed by
the [`G0 Pre-rental Execution and Evidence Contract`](../docs/implementation/G0_PRE_RENTAL_EXECUTION_CONTRACT.md).
Neither document is a runtime artifact or a license to run a cohort.

Do not combine these lifecycles. A run result cannot rewrite the frozen workload, knee, capacity coordinate, TTFT-SLO, materiality
threshold, interval/stopping method pair or repeat budget. A necessary change creates a new preregistration version while retaining the old artifact and
result. S1 is a hard veto. For S2/S3, a signal is a valid `false` only when every pressure/fairness prerequisite holds and the preregistered one-sided
effect interval upper bound is below the engineering materiality threshold. A non-significant result or exhausted repeat budget with an
interval that still crosses the threshold is `INCONCLUSIVE`, not a null. If the interval method is not valid under sequential looks, every
frozen repeat must run and classification occurs once at the end.

The older [`g0-stock-sentinels-preregistration.example.json`](manifests/g0-stock-sentinels-preregistration.example.json) is a retained **D12 historical schema**. It models one-shot write/capacity sentinels, is superseded by D14, and must not be copied for a new run.

Every run manifest must record:

- repository commit;
- SGLang and Mooncake commits/build hashes;
- model and tokenizer identity;
- workload seed and Prefix-DAG identity;
- request arrival and worker assignment;
- L1/L2/L3 capacities and page size;
- policy name, parameters and parameter provenance;
- reset/namespace method;
- warm-up, measurement and drain windows;
- TARGET_HELD_OUT or OOD_SHIFT classification;
- repeat index and run order.
- preregistration SHA-256 and S1/S2/S3 field when the run belongs to the active survival contract;
- `gate_outcome`, reason code and explicit `true` / `false` / `INCONCLUSIVE` signal field when applicable.

The example manifest is a schema example only. It is not a validated configuration.
