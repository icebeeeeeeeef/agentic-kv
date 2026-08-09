# Experiment contract

Experiment runs are not committed by default. Store raw runs under experiments/runs and summarize validated evidence in a reviewed document.

G0 stock sentinels have two different artifacts:

1. a treatment-blind preregistration copied from
   [`manifests/g0-stock-sentinels-preregistration.example.json`](manifests/g0-stock-sentinels-preregistration.example.json),
   completed from baseline-only calibration and checksummed before any treatment result is viewed; and
2. one run manifest per actual arm/repeat, linked back to that preregistration checksum.

Do not combine these lifecycles. A run result cannot rewrite the frozen workload, knee, capacity coordinate, TTFT-SLO, materiality
threshold, interval/stopping method pair or repeat budget. A necessary change creates a new preregistration version while retaining the old artifact and
result. For D1 investment, a signal is a valid `false` only when every pressure/fairness prerequisite holds and the preregistered one-sided
effect interval upper bound is below the engineering materiality threshold. A non-significant result or exhausted repeat budget with an
interval that still crosses the threshold is `INCONCLUSIVE`, not a null. If the interval method is not valid under sequential looks, every
frozen repeat must run and classification occurs once at the end.

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
- preregistration SHA-256 when the run belongs to a stock sentinel;
- `gate_outcome`, reason code and explicit `true` / `false` / `INCONCLUSIVE` signal field when applicable.

The example manifest is a schema example only. It is not a validated configuration.
