# First C0 deployment retrospective

> Evidence status: **RUNTIME_ARTIFACT**, scoped to the 2026-08-13 first-C0 attempts and the passing r6 topology.
> Purpose: carry forward only failures that actually occurred, so the next fresh deployment reaches the experiment faster. This note is not a new Gate, a complete dependency lock, or permission to reuse r6 Store/worker state in C1.

## 1. Known-working runtime profile

The following is a recorded working combination, not a general compatibility claim:

| Component | Passing r6 value |
|---|---|
| Worker OS | Ubuntu 22.04.5 LTS, x86_64 |
| GPU / driver | NVIDIA L20, driver `580.126.09`; `nvidia-smi` reported CUDA compatibility `13.0` |
| Python | stable CPython `3.11.13` with development headers |
| PyTorch | `2.11.0+cu130` |
| SGLang | pinned source `b058dc910619c9d4bce9e9e24117104ffc491fa6` |
| Mooncake | official CPython 3.11 wheel `0.3.12.post1` |
| Other recorded Python packages | `ninja==1.13.0`, `transformers==5.12.1`, `triton==3.6.0` |
| HiCache I/O | stock `--hicache-io-backend direct` on A, B-L3 and B-no-L3 |
| Store | independent CPU host, TCP, 1 GiB nonzero segment |

The CPU Store separately loaded `libcudart.so.12` from the recorded CUDA-runtime 12.8 wheel. That does **not** make the worker a CUDA 12.8 runtime: the passing worker used the driver/PyTorch CUDA 13.0 combination above.

## 2. Observed blockers and minimal fixes

| Attempt / symptom | Runtime evidence | Root cause | Minimal next-deployment action |
|---|---|---|---|
| r1: SGLang source install failed with `cargo is required` | `pip-install.stderr` | The pinned package tried to discover optional Rust extensions; C0 uses the Python HTTP server and did not require them. | Set `SGLANG_BUILD_RUST_EXTS=none` for the install. Do not install a Rust toolchain only for C0. |
| r2: `fatal error: Python.h: No such file or directory` | `sglang-help.stderr` | The selected CPython lacked usable development headers. | Use a stable CPython distribution that includes headers, or install the matching `python3.11-dev`; verify `Python.h` before installing SGLang. |
| r2: scheduler died with SIGSEGV while capturing the prefill CUDA graph | `Python 3.11.0rc1`, `a/server.stderr`; the stable 3.11.13 retry advanced past this stage | `INFERENCE`: the prerelease interpreter was not an admissible base; the retained evidence does not prove a universal Python-version root cause. | Reject prerelease Python. Reuse the known-working stable 3.11.13 build unless a new version is deliberately re-admitted. |
| r3: FlashInfer JIT could not spawn `ninja` although it existed in the venv | `FileNotFoundError: ninja` | The venv `bin` directory was not on the launcher's `PATH`. | Export `PATH="$VIRTUAL_ENV/bin:$PATH"`; verify both `command -v ninja` and `ninja --version` in the exact launch environment. |
| r4: first request failed while building `hicache_hash_cpp` | `fatal error: openssl/sha.h: No such file or directory` | HiCache native hash includes OpenSSL SHA headers and links `-lcrypto`. | Install `libssl-dev`; compile/load the native hash extension before the first experimental request. |
| r5: first request segfaulted in `cuMemcpyBatchAsync_v2` | `Fatal Python error: Segmentation fault` before a response or completed Put | The stock `kernel` HiCache D2H staged write-back path failed on the recorded L20/driver/PyTorch combination. | Use the pinned stock `--hicache-io-backend direct` path for all three worker lifecycles and retain `/server_info`/process evidence. Do not generalize this workaround to other hardware without admission. |
| C host: old pip did not support the required install report | pip `22.0.2` before bootstrap, `26.2.1` after | Base-image pip was too old for the evidence-preserving install flow. | Upgrade pip inside the fresh venv before `pip install --report`; save before/after versions. |
| C host: Mooncake binaries initially lacked runtime loaders | retained missing-library attempts; passing `ldd` resolved `libibverbs.so.1`, `libmlx5.so.1`, `libcuda.so.1`, and `libcudart.so.12` | The official wheel dynamically loads verbs and CUDA libraries even though C used TCP plus CPU memory. | On Ubuntu, provide the verbs runtime/provider and the same content-addressed `libcuda.so.1` loader plus CUDA-runtime wheel used by the passing run; require `ldd` to contain no `not found`. Do not install a full CUDA toolkit or GPU on C. |
| C process control: launcher PID was not always the serving PID; the original SSH terminal was later lost | listener-derived PIDs/PGIDs and `stop-control-deviation.txt` | Some launchers fork; shell `wait` works only while the original parent shell remains. | Discover the unique listener PID after startup, record its actual PGID and command, and terminate only recorded PGIDs. Keep the operator session alive when possible; after session loss, record that exit codes are unavailable instead of inventing them. |
| OSS handoff returned `403 AccessDenied` before the request chain | retained access attempts; r6 upload/Head/Get/readback later passed | Authorization/path admission was incomplete; the retained evidence does not isolate one unique 403 subcause across the cross-account policy, role and VPC path. | Before A, use the worker ECS RAM role and the intended internal endpoint to Put, Head and independently Get/hash a unique probe object. Treat failure as an evidence-handoff blocker, not a C0 failure. |

No other package is promoted to a mandatory prerequisite merely because it appeared in `pip freeze` or `ldd`. The next deployment still records its complete realized environment and fixes only a newly observed blocker.

## 3. Fast bootstrap checks for the next worker

These checks belong in the next **newly hashed** C1 runbook. The r6 copy of `FIRST_C0_RUNBOOK.md` is historical evidence and must not be edited in place.

```bash
# Use the reviewed stable CPython 3.11.13 executable.
PYTHON=/absolute/path/to/python3.11
"$PYTHON" - <<'PY'
import pathlib, sys, sysconfig
assert sys.version_info[:3] == (3, 11, 13)
assert sys.version_info.releaselevel == "final"
header = pathlib.Path(sysconfig.get_paths()["include"]) / "Python.h"
assert header.is_file(), header
print(sys.version)
print(header)
PY

"$PYTHON" -m venv /absolute/path/to/new-venv
export VIRTUAL_ENV=/absolute/path/to/new-venv
export PATH="$VIRTUAL_ENV/bin:$PATH"
export SGLANG_BUILD_RUST_EXTS=none
python -m pip install --upgrade pip
python -m pip install --report /absolute/path/to/install-report.json \
  /absolute/path/to/pinned-sglang/python /absolute/path/to/pinned-mooncake.whl
python -m pip check
command -v ninja
ninja --version
test -f /usr/include/openssl/sha.h
command -v c++
```

Before starting A, force the native-hash compile once with a fresh per-run build directory:

```bash
export TORCH_EXTENSIONS_DIR=/absolute/path/to/new-run/native-extensions
python - <<'PY'
from sglang.srt.mem_cache.cpp_utils.native_hash import _load_native_hash_module
print(_load_native_hash_module())
PY
```

Start A, B-L3 and B-no-L3 with the same reviewed static configuration and include:

```text
--hicache-io-backend direct
```

The flag is part of the realized configuration and must be present in `/server_info` or the retained process command. C1 remains fresh: use a new Store lifecycle/keyspace, new worker state directories, new request ledger and new evidence destination. Reusing the dependency recipe does not authorize reuse of r6 runtime state.

## 4. Fast C-host and evidence admission

Before workers start:

1. Upgrade pip in C's fresh venv and install the pinned Mooncake wheel with an install report.
2. Run `ldd` on `mooncake_master`; stop if any library is `not found`.
3. Import `MooncakeDistributedStore` and verify the required API surface.
4. Start metadata, master and Store; discover actual listener PIDs/PGIDs rather than trusting `$!`.
5. Retain the raw text returned by `/get_all_segments`; for the passing pin it was one `host:port` line, not JSON. Join it with the Store mount log and exact configured nonzero bytes.
6. From the worker, probe every realized private listener/segment endpoint. Do not expose the Store data path publicly.
7. Prove OSS Put/Head/Get/readback hash with the ECS RAM role before the first A request.

For the passing evidence handoff, the working client mode was:

```text
ossutil --mode EcsRamRole -e oss-cn-beijing-internal.aliyuncs.com --region cn-beijing ...
```

The bucket need not share the region of every future experiment for C0 correctness or steady-state performance, because OSS is only the low-frequency input/evidence handoff. If regions differ, use the correct reachable endpoint, record the route and accept transfer cost; never put OSS on the measured KV data path.

## 5. Evidence pointers and boundary

- Passing artifact: `oss://agentic-kv-c0-evidence-20260812/c0/runs/first-c0-20260813-r6/c0-raw-evidence.tar`
- Archive SHA-256: `a155afe674d7a0fa76ad4e14a3b02a5cbeabf3ba22b437fd67ce79310b43f35c`
- r1–r5 are deployment/admission attempts. r2–r5 are `BLOCKED_BEFORE_C0`; their predicates are `NOT_EVALUATED`.
- Only r6 is classified `EXECUTED/PASS` for first C0.
- This note accelerates deployment only. It is not C1 C0 evidence, S1, G0 completion, a performance result, or a reason to build OCI/orchestration before another real need appears.

Before instance release, the small raw blocker bundles were copied to the same off-host OSS evidence store. Each row below was independently downloaded and rehashed on 2026-08-13; the readback matched both the source archive and its retained `.sha256` object. r1 stopped before a formal classification record, so its archive preserves a pre-classification install attempt rather than inventing `BLOCKED_BEFORE_C0` retroactively.

| Attempt | Off-host artifact | SHA-256 |
|---|---|---|
| r1 | `oss://agentic-kv-c0-evidence-20260812/c0/runs/first-c0-20260813-r1/preflight-blocker-evidence.tar` | `460d64e5b2d3a97b0c1b88622bebfa95ed22aac7a01007ca9fb5e31a16eed955` |
| r2 | `oss://agentic-kv-c0-evidence-20260812/c0/runs/first-c0-20260813-r2/preflight-blocker-evidence.tar` | `3aa100909584371a4825d39c943d34b983be30173dac391097b178d420aec5f8` |
| r3 | `oss://agentic-kv-c0-evidence-20260812/c0/runs/first-c0-20260813-r3/preflight-blocker-evidence.tar` | `a3bbce6a5d642c8bf5961b5ad1bbe1da9483c46fb83a9e82b5833ea83b4833b8` |
| r4 | `oss://agentic-kv-c0-evidence-20260812/c0/runs/first-c0-20260813-r4/preflight-blocker-evidence.tar` | `075adaacb1caaf1e97b91ad94d293501d1fa662773f041fe14ce01f6264717fa` |
| r5 | `oss://agentic-kv-c0-evidence-20260812/c0/runs/first-c0-20260813-r5/preflight-blocker-evidence.tar` | `15a9f081f22d967acbec9bc6d33ecde52305e9c520dfc773ca44a155258b326a` |
