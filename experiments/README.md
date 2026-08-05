# Experiment contract

Experiment runs are not committed by default. Store raw runs under experiments/runs and summarize validated evidence in a reviewed document.

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

The example manifest is a schema example only. It is not a validated configuration.
