# First C0 one-shot runbook

One fail-fast stock C0 attempt only. This is not a runner, classifier, retry system, cloud launcher, or C1 harness. Target build/API/config/GPU/Store/request-render/terminal-Put failure before the A→C→B request chain is `BLOCKED_BEFORE_C0`; both predicates remain `NOT_EVALUATED`.

Before pasting any other block, run this independently as the first command on both the C host and worker host. Obtain `C0_EXPECTED_RUNBOOK_SHA256` from the owner-reviewed pre-rental record, not from this file. This avoids a self-hash cycle and binds the inline TCP, zero-segment, no-persistent-state and single-rank topology commands actually executed.

```bash
# BEGIN RUNBOOK TRUST PRECHECK
set -euo pipefail
: "${C0_STAGED_RUNBOOK:?absolute path to staged FIRST_C0_RUNBOOK.md}"
: "${C0_EXPECTED_RUNBOOK_SHA256:?owner-reviewed external runbook SHA-256}"
if command -v sha256sum >/dev/null 2>&1; then
  C0_ACTUAL_RUNBOOK_SHA256=$(sha256sum "$C0_STAGED_RUNBOOK" | awk '{print $1}')
else
  C0_ACTUAL_RUNBOOK_SHA256=$(shasum -a 256 "$C0_STAGED_RUNBOOK" | awk '{print $1}')
fi
printf 'expected=%s\nactual=%s\n' "$C0_EXPECTED_RUNBOOK_SHA256" "$C0_ACTUAL_RUNBOOK_SHA256"
test "$C0_ACTUAL_RUNBOOK_SHA256" = "$C0_EXPECTED_RUNBOOK_SHA256"
export C0_ACTUAL_RUNBOOK_SHA256
# END RUNBOOK TRUST PRECHECK
```

## 1. Safe local evidence seam

Paste this block first. `C0_RUN_DIR` and `C0_EXPORT_DIR` must not exist; the off-host directory must exist. `run_capture` preserves the command exit status while retaining separate stdout/stderr. Inventory is verified before an archive is created outside the run directory and never includes itself or archive output.

```bash
# BEGIN SAFE LOCAL HANDOFF SEAM
set -euo pipefail

c0_sha256_line() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1"; else shasum -a 256 "$1"; fi
}
c0_sha256_value() { c0_sha256_line "$1" | awk '{print $1}'; }
c0_sha256_check() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum -c "$1"; else shasum -a 256 -c "$1"; fi
}
init_c0_run_dir() {
  : "${C0_STAGED_RUNBOOK:?run the runbook trust precheck first}"
  : "${C0_EXPECTED_RUNBOOK_SHA256:?run the runbook trust precheck first}"
  : "${C0_ACTUAL_RUNBOOK_SHA256:?run the runbook trust precheck first}"
  test "$(c0_sha256_value "$C0_STAGED_RUNBOOK")" = "$C0_EXPECTED_RUNBOOK_SHA256"
  test "$C0_ACTUAL_RUNBOOK_SHA256" = "$C0_EXPECTED_RUNBOOK_SHA256"
  : "${C0_RUN_DIR:?set a new C0_RUN_DIR}"
  : "${C0_EXPORT_DIR:?set a new C0_EXPORT_DIR outside C0_RUN_DIR}"
  : "${C0_OFF_HOST_DIR:?set an existing off-host directory}"
  : "${C0_OFF_HOST_ID:?operator-reviewed durable destination identity}"
  : "${C0_OFF_HOST_DURABILITY_REVIEWED:?true only after review}"
  test "$C0_OFF_HOST_DURABILITY_REVIEWED" = true
  local run_path export_path work_path
  run_path=$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$C0_RUN_DIR")
  export_path=$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$C0_EXPORT_DIR")
  work_path=$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$C0_WORK_ROOT")
  case "$export_path/" in "$run_path/"*)
    echo "C0_RUN_DIR and C0_EXPORT_DIR must be separate, non-nested paths" >&2; return 1;;
  esac
  case "$run_path/" in "$export_path/"*)
    echo "C0_RUN_DIR and C0_EXPORT_DIR must be separate, non-nested paths" >&2; return 1;;
  esac
  case "$work_path/" in "$run_path/"*|"$export_path/"*)
    echo "C0_WORK_ROOT must be separate from run/export paths" >&2; return 1;;
  esac
  case "$run_path/" in "$work_path/"*) echo "C0_WORK_ROOT must be separate from run/export paths" >&2; return 1;; esac
  case "$export_path/" in "$work_path/"*) echo "C0_WORK_ROOT must be separate from run/export paths" >&2; return 1;; esac
  if [ -e "$C0_RUN_DIR" ]; then echo "C0_RUN_DIR already exists: $C0_RUN_DIR" >&2; return 1; fi
  if [ -e "$C0_EXPORT_DIR" ]; then echo "C0_EXPORT_DIR already exists: $C0_EXPORT_DIR" >&2; return 1; fi
  test -d "$C0_OFF_HOST_DIR"
  for name in c0-raw-evidence.tar c0-raw-evidence.tar.sha256; do
    if [ -e "$C0_OFF_HOST_DIR/$name" ]; then
      echo "off-host evidence target already exists: $C0_OFF_HOST_DIR/$name" >&2; return 1
    fi
  done
  mkdir "$C0_RUN_DIR" "$C0_EXPORT_DIR"
  mkdir "$C0_RUN_DIR/admission" "$C0_RUN_DIR/config" "$C0_RUN_DIR/store" \
    "$C0_RUN_DIR/a" "$C0_RUN_DIR/b-l3" "$C0_RUN_DIR/b-no-l3" "$C0_RUN_DIR/request"
  printf 'destination_id=%s\ndurability_reviewed=true\n' "$C0_OFF_HOST_ID" \
    >"$C0_RUN_DIR/admission/off-host-destination.txt"
  printf 'expected=%s\nactual=%s\n' "$C0_EXPECTED_RUNBOOK_SHA256" "$C0_ACTUAL_RUNBOOK_SHA256" \
    >"$C0_RUN_DIR/admission/runbook-root.txt"
  cp "$C0_STAGED_RUNBOOK" "$C0_RUN_DIR/admission/FIRST_C0_RUNBOOK.md"
}
run_capture() {
  local label="$1" status=0 display_status=0
  shift
  "$@" >"$C0_RUN_DIR/$label.stdout" 2>"$C0_RUN_DIR/$label.stderr" || status=$?
  tee /dev/null <"$C0_RUN_DIR/$label.stdout" || display_status=$?
  tee /dev/null <"$C0_RUN_DIR/$label.stderr" >&2 || display_status=$?
  if [ "$status" -ne 0 ]; then return "$status"; fi
  return "$display_status"
}
seal_and_copy_c0_evidence() {
  test ! -e "$C0_RUN_DIR/artifact-inventory.sha256"
  (
    cd "$C0_RUN_DIR"
    find . -type f -print | LC_ALL=C sort | while IFS= read -r file; do c0_sha256_line "$file"; done
  ) >"$C0_EXPORT_DIR/artifact-inventory.sha256.tmp"
  mv "$C0_EXPORT_DIR/artifact-inventory.sha256.tmp" "$C0_RUN_DIR/artifact-inventory.sha256"
  (cd "$C0_RUN_DIR" && c0_sha256_check artifact-inventory.sha256)
  tar -cf "$C0_EXPORT_DIR/c0-raw-evidence.tar" \
    -C "$(dirname "$C0_RUN_DIR")" "$(basename "$C0_RUN_DIR")"
  (cd "$C0_EXPORT_DIR" && c0_sha256_line c0-raw-evidence.tar >c0-raw-evidence.tar.sha256 \
    && c0_sha256_check c0-raw-evidence.tar.sha256)
  cp "$C0_EXPORT_DIR/c0-raw-evidence.tar" \
    "$C0_EXPORT_DIR/c0-raw-evidence.tar.sha256" "$C0_OFF_HOST_DIR/"
  (cd "$C0_OFF_HOST_DIR" && c0_sha256_check c0-raw-evidence.tar.sha256)
  printf 'destination_id=%s\narchive_sha256=%s\nverified=true\n' "$C0_OFF_HOST_ID" \
    "$(c0_sha256_value "$C0_OFF_HOST_DIR/c0-raw-evidence.tar")" \
    >"$C0_OFF_HOST_DIR/c0-raw-evidence.verified.txt"
}
# END SAFE LOCAL HANDOFF SEAM
```

## 2. C host terminal

Stage the trusted manifest, official Mooncake wheel and already prechecked runbook on the independent CPU/Store host. The first target probe also showed that the stock wheel loads `libcuda.so.1` and `libcudart.so.12` before Store setup even for TCP plus CPU memory. This block therefore accepts only the two observed host-runtime payloads, checks their target-recorded SHA-256 values, and retains their install metadata. They are post-rental realized dependencies, not additions to the pre-rental input-bundle claim. The C host still does not need the model, SGLang source, a GPU, a kernel driver, or a CUDA toolkit. Paste the block in the same C-host terminal and leave it open.

```bash
# BEGIN C HOST TERMINAL
set -euo pipefail
set +m
: "${C0_STAGED_RUNBOOK:?run the runbook trust precheck first}"
: "${C0_EXPECTED_RUNBOOK_SHA256:?run the runbook trust precheck first}"
: "${C0_ACTUAL_RUNBOOK_SHA256:?run the runbook trust precheck first}"
test "$C0_ACTUAL_RUNBOOK_SHA256" = "$C0_EXPECTED_RUNBOOK_SHA256"
export C0_C_INPUT_DIR=/absolute/path/to/c-host-inputs
export C0_EXPECTED_MANIFEST_SHA256=207f866e2bbc83f96207d112a8d10730280fddd91422b59f02e7b858d9b7c477
export C0_C_RUN_DIR=/absolute/path/to/new-c-host-run
export C0_C_EXPORT_DIR=/absolute/path/to/new-c-host-export
export C0_C_WORK_ROOT=/absolute/path/to/new-c-host-work
export C0_C_LIBCUDA_DEB=/absolute/path/to/libnvidia-compute-580_580.173.02-0ubuntu0.22.04.1_amd64.deb
export C0_C_LIBCUDA_SHA256=01327514a8fde543dc092b79016f92a51dc7d72aa59db193c2405bde7d371503
export C0_C_CUDART_WHEEL=/absolute/path/to/nvidia_cuda_runtime_cu12-12.8.90-py3-none-manylinux2014_x86_64.manylinux_2_17_x86_64.whl
export C0_C_CUDART_SHA256=adade8dcbd0edf427b7204d480d6066d33902cab2a4707dcfc48a2d0fd44ab90
: "${C0_C_PRIVATE_HOST:?}" "${C0_METADATA_PORT:?}" "${C0_MASTER_PORT:?}" "${C0_STORE_PORT:?}"
: "${C0_STORE_SEGMENT_SIZE:?nonzero bounded bytes}" "${C0_C_READY_WAIT_SECONDS:?}"
: "${C0_SECURITY_GROUP_EXPORT:?}" "${C0_STORE_PRIVATE_EXPOSURE_REVIEWED:?true only after review}"
test "$C0_STORE_SEGMENT_SIZE" -gt 0
test "$C0_STORE_PRIVATE_EXPOSURE_REVIEWED" = true
# BEGIN C HOST PATH SEAM
C_RUN_CANON=$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$C0_C_RUN_DIR")
C_EXPORT_CANON=$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$C0_C_EXPORT_DIR")
C_WORK_CANON=$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$C0_C_WORK_ROOT")
case "$C_EXPORT_CANON/" in "$C_RUN_CANON/"*) echo "C run/export must be separate, non-nested paths" >&2; exit 1;; esac
case "$C_RUN_CANON/" in "$C_EXPORT_CANON/"*) echo "C run/export must be separate, non-nested paths" >&2; exit 1;; esac
case "$C_WORK_CANON/" in "$C_RUN_CANON/"*|"$C_EXPORT_CANON/"*) echo "C work/run/export must be separate" >&2; exit 1;; esac
case "$C_RUN_CANON/" in "$C_WORK_CANON/"*) echo "C work/run/export must be separate" >&2; exit 1;; esac
case "$C_EXPORT_CANON/" in "$C_WORK_CANON/"*) echo "C work/run/export must be separate" >&2; exit 1;; esac
# END C HOST PATH SEAM
test ! -e "$C0_C_RUN_DIR" && test ! -e "$C0_C_EXPORT_DIR" && test ! -e "$C0_C_WORK_ROOT"
mkdir "$C0_C_RUN_DIR" "$C0_C_EXPORT_DIR" "$C0_C_WORK_ROOT" "$C0_C_RUN_DIR/admission" "$C0_C_RUN_DIR/store"
test "$(sha256sum "$C0_STAGED_RUNBOOK" | awk '{print $1}')" = "$C0_EXPECTED_RUNBOOK_SHA256"
printf 'expected=%s\nactual=%s\n' "$C0_EXPECTED_RUNBOOK_SHA256" "$C0_ACTUAL_RUNBOOK_SHA256" \
  >"$C0_C_RUN_DIR/admission/runbook-root.txt"
cp "$C0_STAGED_RUNBOOK" "$C0_C_RUN_DIR/admission/FIRST_C0_RUNBOOK.md"

actual_manifest=$(sha256sum "$C0_C_INPUT_DIR/bundle-manifest.json" | awk '{print $1}')
printf 'expected=%s\nactual=%s\n' "$C0_EXPECTED_MANIFEST_SHA256" "$actual_manifest" \
  >"$C0_C_RUN_DIR/admission/manifest-root.txt"
test "$actual_manifest" = "$C0_EXPECTED_MANIFEST_SHA256"
export C0_WHEEL_NAME=mooncake_transfer_engine-0.3.12.post1-cp311-cp311-manylinux_2_28_x86_64.whl
expected_wheel=$(python3 -c 'import json,os,sys; print(json.load(open(sys.argv[1]))["entries"][os.environ["C0_WHEEL_NAME"]]["sha256"])' "$C0_C_INPUT_DIR/bundle-manifest.json")
actual_wheel=$(sha256sum "$C0_C_INPUT_DIR/$C0_WHEEL_NAME" | awk '{print $1}')
printf 'expected=%s\nactual=%s\n' "$expected_wheel" "$actual_wheel" \
  >"$C0_C_RUN_DIR/admission/wheel-hash.txt"
test "$actual_wheel" = "$expected_wheel"
cp "$C0_C_INPUT_DIR/bundle-manifest.json" "$C0_C_RUN_DIR/admission/"
test "$(sha256sum "$C0_C_LIBCUDA_DEB" | awk '{print $1}')" = "$C0_C_LIBCUDA_SHA256"
test "$(sha256sum "$C0_C_CUDART_WHEEL" | awk '{print $1}')" = "$C0_C_CUDART_SHA256"
sha256sum "$C0_C_LIBCUDA_DEB" >"$C0_C_RUN_DIR/admission/libcuda-deb.sha256"
sha256sum "$C0_C_CUDART_WHEEL" >"$C0_C_RUN_DIR/admission/cudart-wheel.sha256"
dpkg-deb --info "$C0_C_LIBCUDA_DEB" >"$C0_C_RUN_DIR/admission/libcuda-deb-info.stdout" \
  2>"$C0_C_RUN_DIR/admission/libcuda-deb-info.stderr"
dpkg-deb -x "$C0_C_LIBCUDA_DEB" "$C0_C_WORK_ROOT/libcuda"

python3.11 -m venv "$C0_C_WORK_ROOT/venv"
export C0_C_PYTHON="$C0_C_WORK_ROOT/venv/bin/python"
export C0_MASTER_BIN="$C0_C_WORK_ROOT/venv/bin/mooncake_master"
"$C0_C_PYTHON" -m pip --version >"$C0_C_RUN_DIR/admission/pip-bootstrap-before.txt"
"$C0_C_PYTHON" -m pip install --upgrade pip >"$C0_C_RUN_DIR/admission/pip-bootstrap.stdout" \
  2>"$C0_C_RUN_DIR/admission/pip-bootstrap.stderr"
"$C0_C_PYTHON" -m pip --version >"$C0_C_RUN_DIR/admission/pip-bootstrap-after.txt"
"$C0_C_PYTHON" -m pip install --report "$C0_C_RUN_DIR/admission/install-report.json" \
  "$C0_C_INPUT_DIR/$C0_WHEEL_NAME" >"$C0_C_RUN_DIR/admission/pip-install.stdout" \
  2>"$C0_C_RUN_DIR/admission/pip-install.stderr"
"$C0_C_PYTHON" -m pip install --no-index --no-deps \
  --report "$C0_C_RUN_DIR/admission/cudart-install-report.json" "$C0_C_CUDART_WHEEL" \
  >"$C0_C_RUN_DIR/admission/cudart-pip-install.stdout" \
  2>"$C0_C_RUN_DIR/admission/cudart-pip-install.stderr"
export C0_CUDART_LIB="$C0_C_WORK_ROOT/venv/lib/python3.11/site-packages/nvidia/cuda_runtime/lib"
export LD_LIBRARY_PATH="$C0_C_WORK_ROOT/libcuda/usr/lib/x86_64-linux-gnu:$C0_CUDART_LIB${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export C0_MASTER_ELF
C0_MASTER_ELF=$("$C0_C_PYTHON" -c 'import mooncake,pathlib; print(pathlib.Path(mooncake.__file__).parent / "mooncake_master")')
test -x "$C0_MASTER_ELF"
ldd "$C0_MASTER_ELF" >"$C0_C_RUN_DIR/admission/master-ldd.stdout" 2>"$C0_C_RUN_DIR/admission/master-ldd.stderr"
! grep -F -- "not found" "$C0_C_RUN_DIR/admission/master-ldd.stdout"
"$C0_C_PYTHON" -c 'from mooncake.store import MooncakeDistributedStore; print("MOONCAKE_STORE_IMPORT_OK")' \
  >"$C0_C_RUN_DIR/admission/store-import.stdout" 2>"$C0_C_RUN_DIR/admission/store-import.stderr"
"$C0_C_PYTHON" -m pip check >"$C0_C_RUN_DIR/admission/pip-check.stdout" 2>"$C0_C_RUN_DIR/admission/pip-check.stderr"
"$C0_C_PYTHON" -m pip freeze --all >"$C0_C_RUN_DIR/admission/pip-freeze.stdout" 2>"$C0_C_RUN_DIR/admission/pip-freeze.stderr"
export C0_MASTER_METRICS_PORT=9003

export C0_METADATA_URL="http://$C0_C_PRIVATE_HOST:$C0_METADATA_PORT/metadata"
export C0_MASTER_ADDRESS="$C0_C_PRIVATE_HOST:$C0_MASTER_PORT"
export C0_C_PRIVATE_HOST C0_STORE_SEGMENT_SIZE
"$C0_C_PYTHON" - "$C0_C_RUN_DIR/store/config.json" <<'PY'
import json,os,sys
json.dump({"local_hostname":os.environ["C0_C_PRIVATE_HOST"],
 "metadata_server":os.environ["C0_METADATA_URL"],
 "master_server_address":os.environ["C0_MASTER_ADDRESS"],"protocol":"tcp","device_name":"",
 "global_segment_size":int(os.environ["C0_STORE_SEGMENT_SIZE"]),"local_buffer_size":0},
 open(sys.argv[1],"w"),indent=2,sort_keys=True)
PY
"$C0_C_PYTHON" - "$C0_C_RUN_DIR/store/config.json" "$C0_STORE_SEGMENT_SIZE" <<'PY'
import json,sys
x=json.load(open(sys.argv[1])); assert x["global_segment_size"]==int(sys.argv[2])>0
assert x["protocol"]=="tcp" and x["device_name"]=="" and x["local_buffer_size"]==0
PY
sha256sum "$C0_C_RUN_DIR/store/config.json" >"$C0_C_RUN_DIR/store/config.sha256"
cp "$C0_SECURITY_GROUP_EXPORT" "$C0_C_RUN_DIR/admission/store-port-security-group-export.txt"
printf 'store_private_exposure_reviewed=true\n' >"$C0_C_RUN_DIR/admission/private-store-exposure.txt"
setsid "$C0_C_PYTHON" -m mooncake.http_metadata_server --port "$C0_METADATA_PORT" \
  >"$C0_C_RUN_DIR/store/metadata.stdout" 2>"$C0_C_RUN_DIR/store/metadata.stderr" &
setsid "$C0_MASTER_BIN" --port "$C0_MASTER_PORT" >"$C0_C_RUN_DIR/store/master.stdout" \
  2>"$C0_C_RUN_DIR/store/master.stderr" &
setsid "$C0_C_PYTHON" -m mooncake.mooncake_store_service --config="$C0_C_RUN_DIR/store/config.json" \
  --port="$C0_STORE_PORT" >"$C0_C_RUN_DIR/store/service.stdout" \
  2>"$C0_C_RUN_DIR/store/service.stderr" &
sleep "$C0_C_READY_WAIT_SECONDS"
discover_listener_pid() {
  local port=$1 pids count
  pids=$(ss -H -lntp "sport = :$port" | sed -n 's/.*pid=\([0-9][0-9]*\).*/\1/p' | sort -u)
  count=$(printf '%s\n' "$pids" | sed '/^$/d' | wc -l | tr -d ' ')
  test "$count" = 1
  printf '%s\n' "$pids"
}
C0_METADATA_PID=$(discover_listener_pid "$C0_METADATA_PORT")
C0_MASTER_PID=$(discover_listener_pid "$C0_MASTER_PORT")
C0_MASTER_METRICS_PID=$(discover_listener_pid "$C0_MASTER_METRICS_PORT")
C0_STORE_PID=$(discover_listener_pid "$C0_STORE_PORT")
test "$C0_MASTER_METRICS_PID" = "$C0_MASTER_PID"
ps -o args= -p "$C0_METADATA_PID" | grep -F -- "mooncake.http_metadata_server" >/dev/null
ps -o args= -p "$C0_MASTER_PID" | grep -F -- "mooncake_master" >/dev/null
ps -o args= -p "$C0_STORE_PID" | grep -F -- "mooncake.mooncake_store_service" >/dev/null
C0_METADATA_PGID=$(ps -o pgid= -p "$C0_METADATA_PID" | tr -d ' ')
C0_MASTER_PGID=$(ps -o pgid= -p "$C0_MASTER_PID" | tr -d ' ')
C0_STORE_PGID=$(ps -o pgid= -p "$C0_STORE_PID" | tr -d ' ')
printf 'metadata_pid=%s\nmetadata_pgid=%s\nmaster_pid=%s\nmaster_pgid=%s\nstore_pid=%s\nstore_pgid=%s\n' \
  "$C0_METADATA_PID" "$C0_METADATA_PGID" "$C0_MASTER_PID" "$C0_MASTER_PGID" "$C0_STORE_PID" "$C0_STORE_PGID" \
  >"$C0_C_RUN_DIR/store/pids.txt"
ps -o pid=,ppid=,lstart=,command= -p "$C0_METADATA_PID,$C0_MASTER_PID,$C0_STORE_PID" \
  >"$C0_C_RUN_DIR/store/processes.txt"
nc -vz "$C0_C_PRIVATE_HOST" "$C0_METADATA_PORT" >"$C0_C_RUN_DIR/admission/metadata-tcp.stdout" 2>"$C0_C_RUN_DIR/admission/metadata-tcp.stderr"
nc -vz "$C0_C_PRIVATE_HOST" "$C0_MASTER_PORT" >"$C0_C_RUN_DIR/admission/master-tcp.stdout" 2>"$C0_C_RUN_DIR/admission/master-tcp.stderr"
nc -vz "$C0_C_PRIVATE_HOST" "$C0_MASTER_METRICS_PORT" >"$C0_C_RUN_DIR/admission/master-metrics-tcp.stdout" 2>"$C0_C_RUN_DIR/admission/master-metrics-tcp.stderr"
nc -vz "$C0_C_PRIVATE_HOST" "$C0_STORE_PORT" >"$C0_C_RUN_DIR/admission/store-tcp.stdout" 2>"$C0_C_RUN_DIR/admission/store-tcp.stderr"
# Pinned wheel mooncake_store_service.py logs this only after store.setup(...) returns 0.
grep -F -- "Store service started successfully on $C0_C_PRIVATE_HOST" \
  "$C0_C_RUN_DIR/store/service.stdout" "$C0_C_RUN_DIR/store/service.stderr" \
  >"$C0_C_RUN_DIR/admission/store-setup-success.txt"
curl --fail-with-body --silent --show-error \
  "http://$C0_C_PRIVATE_HOST:$C0_MASTER_METRICS_PORT/get_all_segments" \
  >"$C0_C_RUN_DIR/admission/get-all-segments.txt" 2>"$C0_C_RUN_DIR/admission/get-all-segments.stderr"
# BEGIN SEGMENT RESPONSE ADMISSION
"$C0_C_PYTHON" - "$C0_C_RUN_DIR/admission/get-all-segments.txt" "$C0_C_RUN_DIR/store/config.json" \
  "$C0_C_RUN_DIR/store/service.stderr" "$C0_C_PRIVATE_HOST" "$C0_STORE_SEGMENT_SIZE" \
  "$C0_C_RUN_DIR/admission/segment-admission.json" <<'PY'
import json,re,sys
raw_path,config_path,log_path,host,size_text,output_path=sys.argv[1:]
size=int(size_text); config=json.load(open(config_path)); log=open(log_path).read()
ports=re.findall(rf"server_name: {re.escape(host)} port: ([0-9]+)",log)
if len(set(ports)) != 1: raise ValueError("missing or ambiguous stock segment port")
segment_id=f"{host}:{ports[0]}"
segments=[line.strip() for line in open(raw_path) if line.strip()]
if segments != [segment_id]: raise ValueError("unexpected get_all_segments response")
if config.get("local_hostname") != host or config.get("global_segment_size") != size or size <= 0:
  raise ValueError("configured segment identity/size mismatch")
if f"Mounting segment: {size} bytes" not in log:
  raise ValueError("store log does not confirm configured segment bytes")
json.dump({"endpoint_format":"stock_text","segment_id":segment_id,"host":host,
 "segment_size":size},open(output_path,"w"),sort_keys=True)
PY
# END SEGMENT RESPONSE ADMISSION
printf 'C_HOST_READY\n'
# END C HOST TERMINAL
```

Pinned SGLang calls the stock master `/get_all_segments` endpoint on metrics port 9003. The fixed port and live raw response are retained; execution pauses for owner-confirmed JSON pointers before checking the exact C endpoint and configured nonzero size. Any missing conjunct is `BLOCKED_BEFORE_C0`.

## 3. Worker/operator terminal

After the C terminal prints `C_HOST_READY`, paste the safe seam and then this block on the single-GPU worker/operator host. It verifies the full bundle, installs the pinned SGLang package from its actual `python/` packaging root, renders one request, and runs three non-overlapping worker lifecycles.

```bash
# BEGIN WORKER OPERATOR TERMINAL
set +m
export C0_BUNDLE=/absolute/path/to/first-c0-20260812-r7
export C0_EXPECTED_MANIFEST_SHA256=207f866e2bbc83f96207d112a8d10730280fddd91422b59f02e7b858d9b7c477
export C0_RUN_DIR=/absolute/path/to/new-worker-run
export C0_EXPORT_DIR=/absolute/path/to/new-worker-export-outside-run
export C0_OFF_HOST_DIR=/absolute/path/to/existing-per-attempt-off-host-destination
export C0_OFF_HOST_ID=operator-reviewed-remote-or-object-store-destination
export C0_OFF_HOST_DURABILITY_REVIEWED=true
export C0_WORK_ROOT=/absolute/path/to/new-worker-work
export C0_MASTER_METRICS_PORT=9003
init_c0_run_dir
test ! -e "$C0_WORK_ROOT" && mkdir "$C0_WORK_ROOT"

actual=$(c0_sha256_value "$C0_BUNDLE/bundle-manifest.json")
printf 'expected=%s\nactual=%s\n' "$C0_EXPECTED_MANIFEST_SHA256" "$actual" >"$C0_RUN_DIR/admission/manifest-root.txt"
test "$actual" = "$C0_EXPECTED_MANIFEST_SHA256"
expected_verifier=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["entries"]["verify-input-bundle.py"]["sha256"])' "$C0_BUNDLE/bundle-manifest.json")
actual_verifier=$(c0_sha256_value "$C0_BUNDLE/verify-input-bundle.py")
printf 'expected=%s\nactual=%s\n' "$expected_verifier" "$actual_verifier" >"$C0_RUN_DIR/admission/verifier-hash.txt"
test "$actual_verifier" = "$expected_verifier"
run_capture admission/bundle-verify python3 "$C0_BUNDLE/verify-input-bundle.py" \
  --bundle "$C0_BUNDLE" --expected-manifest-sha256 "$C0_EXPECTED_MANIFEST_SHA256"
cp "$C0_BUNDLE/bundle-manifest.json" "$C0_RUN_DIR/admission/"

mkdir "$C0_WORK_ROOT/sglang"
tar -xf "$C0_BUNDLE/sglang-source.tar" -C "$C0_WORK_ROOT/sglang"
test -f "$C0_WORK_ROOT/sglang/python/pyproject.toml" -o -f "$C0_WORK_ROOT/sglang/python/setup.py"
python3.11 -m venv "$C0_WORK_ROOT/venv"
export C0_PYTHON="$C0_WORK_ROOT/venv/bin/python"
export C0_WHEEL="$C0_BUNDLE/mooncake_transfer_engine-0.3.12.post1-cp311-cp311-manylinux_2_28_x86_64.whl"
export C0_MODEL="$C0_BUNDLE/model"
run_capture admission/pip-bootstrap-before "$C0_PYTHON" -m pip --version
run_capture admission/pip-bootstrap "$C0_PYTHON" -m pip install --upgrade pip
run_capture admission/pip-bootstrap-after "$C0_PYTHON" -m pip --version
run_capture admission/pip-install "$C0_PYTHON" -m pip install \
  --report "$C0_RUN_DIR/admission/install-report.json" "$C0_WORK_ROOT/sglang/python" "$C0_WHEEL"
run_capture admission/pip-check "$C0_PYTHON" -m pip check
run_capture admission/pip-freeze "$C0_PYTHON" -m pip freeze --all
run_capture admission/sglang-help "$C0_PYTHON" -m sglang.launch_server --help
"$C0_PYTHON" - "$C0_WORK_ROOT/sglang/python/sglang/srt/mem_cache/storage/mooncake_store/mooncake_store.py" \
  "$C0_RUN_DIR/admission/warmup-namespace-source-proof.json" <<'PY'
import hashlib,json,sys
raw=open(sys.argv[1],"rb").read(); source=raw.decode()
warmup='warmup_key = "sglang_mooncake_store_warmup_key" + uuid.uuid4().hex'
tagged='return [f"{self.config_prefix}_{key}" for key in keys]'
if warmup not in source or tagged not in source: raise SystemExit("pinned warmup namespace proof missing")
json.dump({"adapter_sha256":hashlib.sha256(raw).hexdigest(),
 "warmup_key_prefix":"sglang_mooncake_store_warmup_key","warmup_uses_config_prefix":False,
 "tested_page_keys_use_config_prefix":True},open(sys.argv[2],"w"),sort_keys=True)
PY
"$C0_PYTHON" - "$C0_RUN_DIR/admission/sglang-distribution-record.txt" <<'PY'
import importlib.metadata as m,sys
d=m.distribution("sglang"); candidates=[p for p in d.files or () if p.name=="RECORD" and p.parent.name.endswith(".dist-info")]
if len(candidates)!=1: raise SystemExit("BLOCKED_BEFORE_C0: installed sglang RECORD not unique")
record=d.locate_file(candidates[0])
if not record.is_file(): raise SystemExit("BLOCKED_BEFORE_C0: installed sglang RECORD missing")
open(sys.argv[1],"wb").write(record.read_bytes())
PY
c0_sha256_line "$C0_RUN_DIR/admission/sglang-distribution-record.txt" >"$C0_RUN_DIR/admission/distribution-record.sha256"
run_capture admission/import-api "$C0_PYTHON" - <<'PY'
import importlib.metadata as m,sglang
from mooncake.store import MooncakeDistributedStore
assert m.version("mooncake-transfer-engine") == "0.3.12.post1"
store=MooncakeDistributedStore()
for name in ("setup","register_buffer","batch_is_exist","batch_put_from","batch_get_into"):
    assert hasattr(store,name),name
print("SGLANG_IMPORT_OK",sglang.__file__); print("MOONCAKE_API_SURFACE_OK")
PY

: "${C0_C_PRIVATE_HOST:?}" "${C0_METADATA_PORT:?}" "${C0_MASTER_PORT:?}" "${C0_MASTER_METRICS_PORT:?}" "${C0_STORE_PORT:?}"
: "${C0_WORKER_PRIVATE_HOST:?reviewed private worker endpoint}" "${C0_WORKER_PORT:?}" "${C0_GPU_UUID:?}"
: "${C0_RUN_ID:?unique}" "${C0_PAGE_SIZE:?}" "${C0_MIN_PREFIX_TOKENS:?}" "${C0_MAX_FILLER_REPETITIONS:?}"
: "${C0_HICACHE_SIZE_GB:?}" "${C0_WORKER_READY_WAIT_SECONDS:?}" "${C0_METRIC_SETTLE_SECONDS:?short positive integer}"
: "${C0_IMAGE_ID:?operator-recorded immutable rental image ID}"
: "${C0_STORE_PRIVATE_EXPOSURE_REVIEWED:?}"
: "${C0_SECURITY_GROUP_EXPORT:?absolute reviewed export}"
test "$C0_STORE_PRIVATE_EXPOSURE_REVIEWED" = true
test "$C0_MASTER_METRICS_PORT" -eq 9003
export C0_WRITE_POLICY=write_through
export C0_WRITE_THRESHOLD=1
export C0_A_TRIGGER_REQUESTS=1
export C0_PREFETCH_THRESHOLD=256
test "$C0_PAGE_SIZE" -gt 0 && test "$C0_METRIC_SETTLE_SECONDS" -gt 0
test "$C0_MIN_PREFIX_TOKENS" -ge "$C0_PREFETCH_THRESHOLD"
export C0_C_PRIVATE_HOST C0_WORKER_PRIVATE_HOST C0_PAGE_SIZE C0_WRITE_POLICY C0_WRITE_THRESHOLD
export C0_MASTER_METRICS_PORT C0_A_TRIGGER_REQUESTS C0_PREFETCH_THRESHOLD C0_MIN_PREFIX_TOKENS C0_MAX_FILLER_REPETITIONS C0_RUN_ID
export C0_MODEL_NAME=c0-qwen2.5-1.5b-instruct
export C0_METADATA_URL="http://$C0_C_PRIVATE_HOST:$C0_METADATA_PORT/metadata"
export C0_MASTER_ADDRESS="$C0_C_PRIVATE_HOST:$C0_MASTER_PORT"
printf 'private_store_exposure_reviewed=true\n' \
  >"$C0_RUN_DIR/admission/c-host-review.txt"
cp "$C0_SECURITY_GROUP_EXPORT" "$C0_RUN_DIR/admission/store-port-security-group-export.txt"
run_capture admission/metadata-tcp nc -vz "$C0_C_PRIVATE_HOST" "$C0_METADATA_PORT"
run_capture admission/master-tcp nc -vz "$C0_C_PRIVATE_HOST" "$C0_MASTER_PORT"
run_capture admission/master-metrics-tcp nc -vz "$C0_C_PRIVATE_HOST" "$C0_MASTER_METRICS_PORT"
run_capture admission/get-all-segments curl --fail-with-body --silent --show-error \
  "http://$C0_C_PRIVATE_HOST:$C0_MASTER_METRICS_PORT/get_all_segments"
run_capture admission/store-tcp nc -vz "$C0_C_PRIVATE_HOST" "$C0_STORE_PORT"
run_capture admission/gpu nvidia-smi --query-gpu=uuid,name,driver_version --format=csv,noheader
grep -F "$C0_GPU_UUID" "$C0_RUN_DIR/admission/gpu.stdout"
printf '%s\n' "$C0_IMAGE_ID" >"$C0_RUN_DIR/admission/image-id.txt"
cp /etc/os-release "$C0_RUN_DIR/admission/os-release.txt"
run_capture admission/kernel uname -a
run_capture admission/python-version "$C0_PYTHON" --version
run_capture admission/cuda-identity nvidia-smi --query-gpu=uuid,name,driver_version --format=csv,noheader

umask 077
export C0_REQUEST_TMP=$(mktemp -d)
export C0_REQUEST_BODY="$C0_REQUEST_TMP/request.json"
"$C0_PYTHON" - "$C0_BUNDLE/request-template.json" "$C0_MODEL" "$C0_REQUEST_BODY" \
  "$C0_RUN_DIR/request/identity.json" "$C0_RUN_DIR/request/write-trigger.json" <<'PY'
import hashlib,json,os,sys
from transformers import AutoTokenizer
t=json.load(open(sys.argv[1])); tok=AutoTokenizer.from_pretrained(sys.argv[2],local_files_only=True)
p=int(os.environ["C0_PAGE_SIZE"]); minimum=int(os.environ["C0_MIN_PREFIX_TOKENS"]); selected=None
for repeat in range(int(os.environ["C0_MAX_FILLER_REPETITIONS"])+1):
    prompt=t["seed_text"]+t["filler_text"]*repeat+t["suffix_text"]; ids=tok.encode(prompt,add_special_tokens=False)
    if len(ids)>=minimum and len(ids)%p==0: selected=(repeat,prompt,ids); break
if selected is None: raise SystemExit("BLOCKED_BEFORE_C0: no aligned candidate")
repeat,prompt,ids=selected; body={"model":os.environ["C0_MODEL_NAME"],"prompt":prompt,**t["decode"]}
raw=json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode(); open(sys.argv[3],"wb").write(raw)
identity={"template_sha256":hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest(),
 "raw_prompt_sha256":hashlib.sha256(prompt.encode()).hexdigest(),"request_body_sha256":hashlib.sha256(raw).hexdigest(),
 "token_ids_sha256":hashlib.sha256(json.dumps(ids,separators=(",",":")).encode()).hexdigest(),
 "token_count":len(ids),"request_byte_count":len(raw),"decode":t["decode"]}
trigger={"page_size":p,"minimum_prefix_tokens":minimum,"filler_repetitions":repeat,"token_count":len(ids),
 "write_policy":os.environ["C0_WRITE_POLICY"],"write_threshold":int(os.environ["C0_WRITE_THRESHOLD"]),
 "a_trigger_requests":int(os.environ["C0_A_TRIGGER_REQUESTS"]),**{k:identity[k] for k in
 ("raw_prompt_sha256","request_body_sha256","token_ids_sha256")}}
json.dump(identity,open(sys.argv[4],"w"),indent=2,sort_keys=True); json.dump(trigger,open(sys.argv[5],"w"),indent=2,sort_keys=True)
PY
c0_sha256_line "$C0_REQUEST_BODY" >"$C0_RUN_DIR/request/request-body.sha256"

"$C0_PYTHON" - "$C0_RUN_DIR/config" <<'PY'
import json,os,sys
for role in ("worker-a","worker-b-l3"):
  json.dump({"local_hostname":os.environ["C0_WORKER_PRIVATE_HOST"],
   "metadata_server":os.environ["C0_METADATA_URL"],"master_server_address":os.environ["C0_MASTER_ADDRESS"],
   "protocol":"tcp","device_name":"","global_segment_size":0,"tenant_id":"default",
   "prefetch_threshold":int(os.environ["C0_PREFETCH_THRESHOLD"]),
   "master_metrics_port":int(os.environ["C0_MASTER_METRICS_PORT"]),"check_server":True,
   "extra_backend_tag":os.environ["C0_RUN_ID"]},open(f"{sys.argv[1]}/{role}.json","w"),indent=2,sort_keys=True)
PY
"$C0_PYTHON" - "$C0_RUN_DIR/config/worker-a.json" "$C0_RUN_DIR/config/worker-b-l3.json" <<'PY'
import json,os,sys
for path in sys.argv[1:]:
  x=json.load(open(path)); assert x["global_segment_size"]==0 and x["protocol"]=="tcp"
  assert x["prefetch_threshold"]==256 and x["master_metrics_port"]==int(os.environ["C0_MASTER_METRICS_PORT"])
  assert x["check_server"] is True and x["extra_backend_tag"]==os.environ["C0_RUN_ID"]
PY

export C0_A_STATE="$C0_WORK_ROOT/state-a"; test ! -e "$C0_A_STATE"
mkdir "$C0_A_STATE" "$C0_A_STATE/cache" "$C0_A_STATE/tmp"
setsid env CUDA_VISIBLE_DEVICES="$C0_GPU_UUID" SGLANG_ENABLE_UNIFIED_RADIX_TREE=0 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
 XDG_CACHE_HOME="$C0_A_STATE/cache" TMPDIR="$C0_A_STATE/tmp" \
 "$C0_PYTHON" -m sglang.launch_server --model-path "$C0_MODEL" --served-model-name "$C0_MODEL_NAME" \
 --dtype bfloat16 --host "$C0_WORKER_PRIVATE_HOST" --port "$C0_WORKER_PORT" --tp-size 1 --pp-size 1 --dp-size 1 \
 --dcp-size 1 --page-size "$C0_PAGE_SIZE" --enable-hierarchical-cache --hicache-size "$C0_HICACHE_SIZE_GB" \
 --hicache-write-policy "$C0_WRITE_POLICY" --hicache-storage-prefetch-policy wait_complete \
 --hicache-storage-backend mooncake --hicache-storage-backend-extra-config "@$C0_RUN_DIR/config/worker-a.json" \
 --enable-cache-report --enable-metrics --skip-server-warmup >"$C0_RUN_DIR/a/server.stdout" 2>"$C0_RUN_DIR/a/server.stderr" & C0_A_PID=$!
C0_A_PGID=$(ps -o pgid= -p "$C0_A_PID" | tr -d ' '); test "$C0_A_PGID" = "$C0_A_PID"
printf '[]\n' >"$C0_RUN_DIR/a/request-ledger-before.json"
printf 'pid=%s\npgid=%s\n' "$C0_A_PID" "$C0_A_PGID" >"$C0_RUN_DIR/a/pid.txt"
sleep "$C0_WORKER_READY_WAIT_SECONDS"; kill -0 "$C0_A_PID"
grep -F "Mooncake store warmup successfully." "$C0_RUN_DIR/a/server.stdout" "$C0_RUN_DIR/a/server.stderr" >"$C0_RUN_DIR/a/mooncake-warmup-success.txt"
grep -F "Using Mooncake config prefix: ${C0_RUN_ID}_${C0_MODEL_NAME}" "$C0_RUN_DIR/a/server.stdout" "$C0_RUN_DIR/a/server.stderr" >"$C0_RUN_DIR/a/config-prefix.txt"
ps -o pid=,ppid=,lstart=,command= -p "$C0_A_PID" >"$C0_RUN_DIR/a/process-before.txt"
tr '\0' '\n' <"/proc/$C0_A_PID/environ" | grep -E '^(CUDA_VISIBLE_DEVICES|SGLANG_ENABLE_UNIFIED_RADIX_TREE|XDG_CACHE_HOME|TMPDIR|HF_HUB_OFFLINE|TRANSFORMERS_OFFLINE)=' >"$C0_RUN_DIR/a/process-environ.txt"
grep -Fx "CUDA_VISIBLE_DEVICES=$C0_GPU_UUID" "$C0_RUN_DIR/a/process-environ.txt"
grep -Fx "SGLANG_ENABLE_UNIFIED_RADIX_TREE=0" "$C0_RUN_DIR/a/process-environ.txt"
grep -Fx "XDG_CACHE_HOME=$C0_A_STATE/cache" "$C0_RUN_DIR/a/process-environ.txt"
grep -Fx "TMPDIR=$C0_A_STATE/tmp" "$C0_RUN_DIR/a/process-environ.txt"
run_capture a/server-info curl --fail-with-body --silent --show-error "http://$C0_WORKER_PRIVATE_HOST:$C0_WORKER_PORT/server_info"
"$C0_PYTHON" - "$C0_RUN_DIR/a/server-info.stdout" "$C0_MODEL" "$C0_MODEL_NAME" "$C0_PAGE_SIZE" \
 "$C0_WRITE_POLICY" "@$C0_RUN_DIR/config/worker-a.json" "$C0_HICACHE_SIZE_GB" <<'PY'
import json,sys
x=json.load(open(sys.argv[1])); assert x["model_path"]==sys.argv[2] and x["served_model_name"]==sys.argv[3]
assert x["page_size"]==int(sys.argv[4]) and all(x[k]==1 for k in ("tp_size","pp_size","dp_size","dcp_size"))
assert x["dtype"]=="bfloat16" and x["enable_hierarchical_cache"] is True and x["hicache_size"]==int(sys.argv[7])
assert x["hicache_write_policy"]==sys.argv[5] and x["hicache_storage_prefetch_policy"]=="wait_complete"
assert x["hicache_storage_backend"]=="mooncake" and x["hicache_storage_backend_extra_config"]==sys.argv[6]
assert x["enable_cache_report"] is True and x["enable_metrics"] is True and x["skip_server_warmup"] is True
PY
c0_sha256_line "$C0_RUN_DIR/config/worker-a.json" >"$C0_RUN_DIR/a/config.sha256"
printf '%s\n' "$C0_A_STATE" >"$C0_RUN_DIR/a/state-path.txt"
run_capture a/metrics-before curl --fail-with-body --silent --show-error "http://$C0_WORKER_PRIVATE_HOST:$C0_WORKER_PORT/metrics"
A_REQUEST_STATUS=0
curl --fail-with-body --silent --show-error -H 'Content-Type: application/json' \
  --data-binary "@$C0_REQUEST_BODY" "http://$C0_WORKER_PRIVATE_HOST:$C0_WORKER_PORT/v1/completions" \
  >"$C0_REQUEST_TMP/a-response-1.json" 2>"$C0_RUN_DIR/a/request-1.stderr" || A_REQUEST_STATUS=$?
printf '%s\n' "$A_REQUEST_STATUS" >"$C0_RUN_DIR/a/request-1.status"
# BEGIN A RESPONSE REDUCER
A_REDUCER_STATUS=0
"$C0_PYTHON" - "$C0_REQUEST_TMP/a-response-1.json" "$C0_RUN_DIR/a/response-summary.json" <<'PY' || A_REDUCER_STATUS=$?
import hashlib,json,sys
raw=open(sys.argv[1],"rb").read(); output=sys.argv[2]
json.dump({"raw_response_sha256":hashlib.sha256(raw).hexdigest()},open(output,"w"),sort_keys=True)
x=json.loads(raw); choices=x["choices"]; usage=x["usage"]
if not isinstance(choices,list) or len(choices)!=1 or not isinstance(choices[0]["text"],str): raise ValueError("invalid A response choice")
prompt=usage["prompt_tokens"]; completion=usage["completion_tokens"]
details=usage.get("prompt_tokens_details")
if details is not None and (not isinstance(details,dict) or "cached_tokens" not in details): raise ValueError("invalid A cached-token details")
cached=0 if details is None else details["cached_tokens"]
if any(type(v) is not int or v < 0 for v in (prompt,completion,cached)) or completion < 1: raise ValueError("invalid A response counts")
json.dump({"raw_response_sha256":hashlib.sha256(raw).hexdigest(),"model":x["model"],"choice_count":1,
 "prompt_tokens":prompt,"completion_tokens":completion,"cached_tokens":cached,
 "output_utf8_sha256":hashlib.sha256(choices[0]["text"].encode()).hexdigest()},open(output,"w"),sort_keys=True)
PY
printf '%s\n' "$A_REDUCER_STATUS" >"$C0_RUN_DIR/a/response-reducer.status"
# END A RESPONSE REDUCER
C0_A_BLOCKED=0
if [ "$A_REQUEST_STATUS" -eq 0 ] && [ "$A_REDUCER_STATUS" -eq 0 ]; then
  sleep "$C0_METRIC_SETTLE_SECONDS"
  run_capture a/metrics-after curl --fail-with-body --silent --show-error "http://$C0_WORKER_PRIVATE_HOST:$C0_WORKER_PORT/metrics"
  A_COUNTER_STATUS=0
  "$C0_PYTHON" - "$C0_RUN_DIR/a/metrics-before.stdout" "$C0_RUN_DIR/a/metrics-after.stdout" \
    "$C0_RUN_DIR/a/backuped-counter-delta.json" <<'PY' || A_COUNTER_STATUS=$?
import json,sys
def value(path):
  return sum(float(line.rsplit(None,1)[1]) for line in open(path) if line.startswith("sglang:backuped_tokens_total{") or line.startswith("sglang:backuped_tokens_total "))
before=value(sys.argv[1]); after=value(sys.argv[2]); delta=after-before
json.dump({"before":before,"after":after,"delta":delta,"positive":delta>0},open(sys.argv[3],"w"),sort_keys=True)
if delta <= 0: raise SystemExit("no completed stock backup token delta")
PY
else
  A_COUNTER_STATUS=1
fi
if [ "$A_REQUEST_STATUS" -ne 0 ] || [ "$A_REDUCER_STATUS" -ne 0 ] || [ "$A_COUNTER_STATUS" -ne 0 ]; then
  printf 'BLOCKED_BEFORE_C0: A request/response or completed stock Put evidence missing\n' >"$C0_RUN_DIR/blocked-before-c0.txt"
  C0_A_BLOCKED=1
fi
kill -TERM -- "-$C0_A_PGID"; A_EXIT=0; wait "$C0_A_PID" || A_EXIT=$?
if ps -eo pgid= | awk -v p="$C0_A_PGID" '$1==p{found=1} END{exit found?0:1}'; then exit 1; fi
printf 'pid=%s\npgid=%s\nexit=%s\nno_process_group_members=true\n' "$C0_A_PID" "$C0_A_PGID" "$A_EXIT" >"$C0_RUN_DIR/a/exit.txt"

if [ "$C0_A_BLOCKED" -eq 0 ]; then
export C0_B_L3_STATE="$C0_WORK_ROOT/state-b-l3"; test ! -e "$C0_B_L3_STATE"
mkdir "$C0_B_L3_STATE" "$C0_B_L3_STATE/cache" "$C0_B_L3_STATE/tmp"
setsid env CUDA_VISIBLE_DEVICES="$C0_GPU_UUID" SGLANG_ENABLE_UNIFIED_RADIX_TREE=0 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
 XDG_CACHE_HOME="$C0_B_L3_STATE/cache" TMPDIR="$C0_B_L3_STATE/tmp" \
 "$C0_PYTHON" -m sglang.launch_server --model-path "$C0_MODEL" --served-model-name "$C0_MODEL_NAME" \
 --dtype bfloat16 --host "$C0_WORKER_PRIVATE_HOST" --port "$C0_WORKER_PORT" --tp-size 1 --pp-size 1 --dp-size 1 \
 --dcp-size 1 --page-size "$C0_PAGE_SIZE" --enable-hierarchical-cache --hicache-size "$C0_HICACHE_SIZE_GB" \
 --hicache-write-policy "$C0_WRITE_POLICY" --hicache-storage-prefetch-policy wait_complete \
 --hicache-storage-backend mooncake --hicache-storage-backend-extra-config "@$C0_RUN_DIR/config/worker-b-l3.json" \
 --enable-cache-report --enable-metrics --skip-server-warmup >"$C0_RUN_DIR/b-l3/server.stdout" 2>"$C0_RUN_DIR/b-l3/server.stderr" & C0_B_L3_PID=$!
C0_B_L3_PGID=$(ps -o pgid= -p "$C0_B_L3_PID" | tr -d ' '); test "$C0_B_L3_PGID" = "$C0_B_L3_PID"
printf '[]\n' >"$C0_RUN_DIR/b-l3/request-ledger-before.json"
printf 'pid=%s\npgid=%s\n' "$C0_B_L3_PID" "$C0_B_L3_PGID" >"$C0_RUN_DIR/b-l3/pid.txt"
sleep "$C0_WORKER_READY_WAIT_SECONDS"; kill -0 "$C0_B_L3_PID"
grep -F "Mooncake store warmup successfully." "$C0_RUN_DIR/b-l3/server.stdout" "$C0_RUN_DIR/b-l3/server.stderr" >"$C0_RUN_DIR/b-l3/mooncake-warmup-success.txt"
grep -F "Using Mooncake config prefix: ${C0_RUN_ID}_${C0_MODEL_NAME}" "$C0_RUN_DIR/b-l3/server.stdout" "$C0_RUN_DIR/b-l3/server.stderr" >"$C0_RUN_DIR/b-l3/config-prefix.txt"
ps -o pid=,ppid=,lstart=,command= -p "$C0_B_L3_PID" >"$C0_RUN_DIR/b-l3/process-before.txt"
tr '\0' '\n' <"/proc/$C0_B_L3_PID/environ" | grep -E '^(CUDA_VISIBLE_DEVICES|SGLANG_ENABLE_UNIFIED_RADIX_TREE|XDG_CACHE_HOME|TMPDIR|HF_HUB_OFFLINE|TRANSFORMERS_OFFLINE)=' >"$C0_RUN_DIR/b-l3/process-environ.txt"
grep -Fx "CUDA_VISIBLE_DEVICES=$C0_GPU_UUID" "$C0_RUN_DIR/b-l3/process-environ.txt"
grep -Fx "SGLANG_ENABLE_UNIFIED_RADIX_TREE=0" "$C0_RUN_DIR/b-l3/process-environ.txt"
grep -Fx "XDG_CACHE_HOME=$C0_B_L3_STATE/cache" "$C0_RUN_DIR/b-l3/process-environ.txt"
grep -Fx "TMPDIR=$C0_B_L3_STATE/tmp" "$C0_RUN_DIR/b-l3/process-environ.txt"
run_capture b-l3/server-info curl --fail-with-body --silent --show-error "http://$C0_WORKER_PRIVATE_HOST:$C0_WORKER_PORT/server_info"
"$C0_PYTHON" - "$C0_RUN_DIR/b-l3/server-info.stdout" "$C0_MODEL" "$C0_MODEL_NAME" "$C0_PAGE_SIZE" \
 "$C0_WRITE_POLICY" "@$C0_RUN_DIR/config/worker-b-l3.json" "$C0_HICACHE_SIZE_GB" <<'PY'
import json,sys
x=json.load(open(sys.argv[1])); assert x["model_path"]==sys.argv[2] and x["served_model_name"]==sys.argv[3]
assert x["page_size"]==int(sys.argv[4]) and all(x[k]==1 for k in ("tp_size","pp_size","dp_size","dcp_size"))
assert x["dtype"]=="bfloat16" and x["enable_hierarchical_cache"] is True and x["hicache_size"]==int(sys.argv[7])
assert x["hicache_write_policy"]==sys.argv[5] and x["hicache_storage_prefetch_policy"]=="wait_complete"
assert x["hicache_storage_backend"]=="mooncake" and x["hicache_storage_backend_extra_config"]==sys.argv[6]
assert x["enable_cache_report"] is True and x["enable_metrics"] is True and x["skip_server_warmup"] is True
PY
c0_sha256_line "$C0_RUN_DIR/config/worker-b-l3.json" >"$C0_RUN_DIR/b-l3/config.sha256"
printf '%s\n' "$C0_B_L3_STATE" >"$C0_RUN_DIR/b-l3/state-path.txt"
run_capture b-l3/metrics-before curl --fail-with-body --silent --show-error "http://$C0_WORKER_PRIVATE_HOST:$C0_WORKER_PORT/metrics"
B_L3_REQUEST_STATUS=0
curl --fail-with-body --silent --show-error -H 'Content-Type: application/json' \
  --data-binary "@$C0_REQUEST_BODY" "http://$C0_WORKER_PRIVATE_HOST:$C0_WORKER_PORT/v1/completions" \
  >"$C0_REQUEST_TMP/b-l3-response.json" 2>"$C0_RUN_DIR/b-l3/response.stderr" || B_L3_REQUEST_STATUS=$?
printf '%s\n' "$B_L3_REQUEST_STATUS" >"$C0_RUN_DIR/b-l3/response.status"; test "$B_L3_REQUEST_STATUS" -eq 0
sleep "$C0_METRIC_SETTLE_SECONDS"
run_capture b-l3/metrics-after curl --fail-with-body --silent --show-error "http://$C0_WORKER_PRIVATE_HOST:$C0_WORKER_PORT/metrics"
"$C0_PYTHON" - "$C0_RUN_DIR/b-l3/metrics-before.stdout" "$C0_RUN_DIR/b-l3/metrics-after.stdout" \
  "$C0_RUN_DIR/b-l3/prefetched-counter-delta.json" <<'PY'
import json,sys
def value(path):
  return sum(float(line.rsplit(None,1)[1]) for line in open(path) if line.startswith("sglang:prefetched_tokens_total{") or line.startswith("sglang:prefetched_tokens_total "))
before=value(sys.argv[1]); after=value(sys.argv[2]); delta=after-before
json.dump({"before":before,"after":after,"delta":delta,"positive":delta>0},open(sys.argv[3],"w"),sort_keys=True)
PY
kill -TERM -- "-$C0_B_L3_PGID"; B_L3_EXIT=0; wait "$C0_B_L3_PID" || B_L3_EXIT=$?
if ps -eo pgid= | awk -v p="$C0_B_L3_PGID" '$1==p{found=1} END{exit found?0:1}'; then exit 1; fi
printf 'pid=%s\npgid=%s\nexit=%s\nno_process_group_members=true\n' "$C0_B_L3_PID" "$C0_B_L3_PGID" "$B_L3_EXIT" >"$C0_RUN_DIR/b-l3/exit.txt"

export C0_B_NO_L3_STATE="$C0_WORK_ROOT/state-b-no-l3"; test ! -e "$C0_B_NO_L3_STATE"
mkdir "$C0_B_NO_L3_STATE" "$C0_B_NO_L3_STATE/cache" "$C0_B_NO_L3_STATE/tmp"
setsid env CUDA_VISIBLE_DEVICES="$C0_GPU_UUID" SGLANG_ENABLE_UNIFIED_RADIX_TREE=0 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
 XDG_CACHE_HOME="$C0_B_NO_L3_STATE/cache" TMPDIR="$C0_B_NO_L3_STATE/tmp" \
 "$C0_PYTHON" -m sglang.launch_server --model-path "$C0_MODEL" --served-model-name "$C0_MODEL_NAME" \
 --dtype bfloat16 --host "$C0_WORKER_PRIVATE_HOST" --port "$C0_WORKER_PORT" --tp-size 1 --pp-size 1 --dp-size 1 \
 --dcp-size 1 --page-size "$C0_PAGE_SIZE" --enable-hierarchical-cache --hicache-size "$C0_HICACHE_SIZE_GB" \
 --hicache-write-policy "$C0_WRITE_POLICY" --enable-cache-report --enable-metrics --skip-server-warmup \
 >"$C0_RUN_DIR/b-no-l3/server.stdout" 2>"$C0_RUN_DIR/b-no-l3/server.stderr" & C0_B_NO_L3_PID=$!
C0_B_NO_L3_PGID=$(ps -o pgid= -p "$C0_B_NO_L3_PID" | tr -d ' '); test "$C0_B_NO_L3_PGID" = "$C0_B_NO_L3_PID"
printf '[]\n' >"$C0_RUN_DIR/b-no-l3/request-ledger-before.json"
printf 'pid=%s\npgid=%s\n' "$C0_B_NO_L3_PID" "$C0_B_NO_L3_PGID" >"$C0_RUN_DIR/b-no-l3/pid.txt"
sleep "$C0_WORKER_READY_WAIT_SECONDS"; kill -0 "$C0_B_NO_L3_PID"
ps -o pid=,ppid=,lstart=,command= -p "$C0_B_NO_L3_PID" >"$C0_RUN_DIR/b-no-l3/process-before.txt"
tr '\0' '\n' <"/proc/$C0_B_NO_L3_PID/environ" | grep -E '^(CUDA_VISIBLE_DEVICES|SGLANG_ENABLE_UNIFIED_RADIX_TREE|XDG_CACHE_HOME|TMPDIR|HF_HUB_OFFLINE|TRANSFORMERS_OFFLINE)=' >"$C0_RUN_DIR/b-no-l3/process-environ.txt"
grep -Fx "CUDA_VISIBLE_DEVICES=$C0_GPU_UUID" "$C0_RUN_DIR/b-no-l3/process-environ.txt"
grep -Fx "SGLANG_ENABLE_UNIFIED_RADIX_TREE=0" "$C0_RUN_DIR/b-no-l3/process-environ.txt"
grep -Fx "XDG_CACHE_HOME=$C0_B_NO_L3_STATE/cache" "$C0_RUN_DIR/b-no-l3/process-environ.txt"
grep -Fx "TMPDIR=$C0_B_NO_L3_STATE/tmp" "$C0_RUN_DIR/b-no-l3/process-environ.txt"
run_capture b-no-l3/server-info curl --fail-with-body --silent --show-error "http://$C0_WORKER_PRIVATE_HOST:$C0_WORKER_PORT/server_info"
"$C0_PYTHON" - "$C0_RUN_DIR/b-no-l3/server-info.stdout" "$C0_MODEL" "$C0_MODEL_NAME" "$C0_PAGE_SIZE" \
 "$C0_WRITE_POLICY" "$C0_HICACHE_SIZE_GB" <<'PY'
import json,sys
x=json.load(open(sys.argv[1])); assert x["model_path"]==sys.argv[2] and x["served_model_name"]==sys.argv[3]
assert x["page_size"]==int(sys.argv[4]) and all(x[k]==1 for k in ("tp_size","pp_size","dp_size","dcp_size"))
assert x["dtype"]=="bfloat16" and x["enable_hierarchical_cache"] is True and x["hicache_size"]==int(sys.argv[6])
assert x["hicache_write_policy"]==sys.argv[5]
assert x["hicache_storage_backend"] is None and x["hicache_storage_backend_extra_config"] is None
assert x["enable_cache_report"] is True and x["enable_metrics"] is True and x["skip_server_warmup"] is True
PY
printf '%s\n' "$C0_B_NO_L3_STATE" >"$C0_RUN_DIR/b-no-l3/state-path.txt"
B_NO_L3_REQUEST_STATUS=0
curl --fail-with-body --silent --show-error -H 'Content-Type: application/json' \
  --data-binary "@$C0_REQUEST_BODY" "http://$C0_WORKER_PRIVATE_HOST:$C0_WORKER_PORT/v1/completions" \
  >"$C0_REQUEST_TMP/b-no-l3-response.json" 2>"$C0_RUN_DIR/b-no-l3/response.stderr" || B_NO_L3_REQUEST_STATUS=$?
printf '%s\n' "$B_NO_L3_REQUEST_STATUS" >"$C0_RUN_DIR/b-no-l3/response.status"; test "$B_NO_L3_REQUEST_STATUS" -eq 0
kill -TERM -- "-$C0_B_NO_L3_PGID"; B_NO_L3_EXIT=0; wait "$C0_B_NO_L3_PID" || B_NO_L3_EXIT=$?
if ps -eo pgid= | awk -v p="$C0_B_NO_L3_PGID" '$1==p{found=1} END{exit found?0:1}'; then exit 1; fi
printf 'pid=%s\npgid=%s\nexit=%s\nno_process_group_members=true\n' "$C0_B_NO_L3_PID" "$C0_B_NO_L3_PGID" "$B_NO_L3_EXIT" >"$C0_RUN_DIR/b-no-l3/exit.txt"
c0_sha256_line "$C0_REQUEST_BODY" >>"$C0_RUN_DIR/request/request-body.sha256"

# BEGIN RESPONSE EVIDENCE REDUCER
"$C0_PYTHON" - "$C0_RUN_DIR/request/identity.json" "$C0_REQUEST_TMP/b-l3-response.json" \
  "$C0_REQUEST_TMP/b-no-l3-response.json" "$C0_RUN_DIR/request/oracle-inputs.json" \
  "$C0_MODEL_NAME" "$C0_RUN_DIR/b-l3/prefetched-counter-delta.json" \
  "$C0_REQUEST_TMP"/a-response-*.json <<'PY'
import hashlib,json,sys

identity=json.load(open(sys.argv[1])); expected_prompt_hash=identity["token_ids_sha256"]
def h(value): return hashlib.sha256(value).hexdigest()
def ids_hash(value): return h(json.dumps(value,separators=(",",":")).encode())
def count(value,name):
    if type(value) is not int or value < 0: raise ValueError(f"invalid {name}")
    return value
def cached_count(usage,label):
    details=usage.get("prompt_tokens_details")
    if details is None: return 0
    if not isinstance(details,dict) or "cached_tokens" not in details: raise ValueError(f"invalid {label} cached-token details")
    return count(details["cached_tokens"],f"{label} cached_tokens")
def reduce_response(path,label,require_storage=False):
    raw=open(path,"rb").read(); response=json.loads(raw); choices=response["choices"]
    if response["model"] != sys.argv[5] or not isinstance(choices,list) or len(choices) != 1:
        raise ValueError(f"invalid {label} model/choice count")
    choice=choices[0]
    if choice["index"] != 0 or not isinstance(choice["text"],str): raise ValueError(f"invalid {label} choice")
    prompt_ids=choice["prompt_token_ids"]; completion_ids=choice["token_ids"]
    if (not isinstance(prompt_ids,list) or not prompt_ids or any(type(x) is not int for x in prompt_ids)
        or not isinstance(completion_ids,list) or not completion_ids or any(type(x) is not int for x in completion_ids)):
        raise ValueError(f"invalid {label} token IDs")
    usage=response["usage"]; prompt=count(usage["prompt_tokens"],f"{label} prompt_tokens")
    completion=count(usage["completion_tokens"],f"{label} completion_tokens")
    cached=cached_count(usage,label)
    if completion < 1 or completion != len(completion_ids) or prompt != len(prompt_ids) or cached > prompt:
        raise ValueError(f"invalid {label} token counts")
    storage=None
    if require_storage:
        storage=count(response["sglext"]["cached_tokens_details"]["storage"],f"{label} storage")
    summary={"raw_response_sha256":h(raw),"model":response["model"],"choice_count":1,"completion_tokens":completion,
      "prompt_tokens":prompt,"cached_tokens":cached,"uncached_prompt_tokens":prompt-cached,
      "output_utf8_sha256":h(choice["text"].encode()),"prompt_token_ids_sha256":ids_hash(prompt_ids),
      "completion_token_ids_sha256":ids_hash(completion_ids)}
    if storage is not None: summary["storage_cached_tokens"]=storage
    if summary["prompt_token_ids_sha256"] != expected_prompt_hash: raise ValueError(f"{label} prompt identity mismatch")
    return summary
b_l3=reduce_response(sys.argv[2],"b_l3",True); control=reduce_response(sys.argv[3],"b_no_l3")
prefetch=json.load(open(sys.argv[6]))
if (set(prefetch)!={"before","after","delta","positive"} or type(prefetch["positive"]) is not bool
    or prefetch["delta"] != prefetch["after"]-prefetch["before"] or prefetch["positive"] != (prefetch["delta"]>0)):
    raise ValueError("invalid prefetched counter delta evidence")
a=[reduce_response(path,f"a_{index}") for index,path in enumerate(sys.argv[7:],1)]
facts={"request_body_sha256":identity["request_body_sha256"],
 "prompt_token_ids_equal_and_match_request":b_l3["prompt_token_ids_sha256"]==control["prompt_token_ids_sha256"]==expected_prompt_hash,
 "completion_token_ids_equal":b_l3["completion_token_ids_sha256"]==control["completion_token_ids_sha256"],
 "output_utf8_equal":b_l3["output_utf8_sha256"]==control["output_utf8_sha256"],
 "prefetched_counter_positive":prefetch["positive"],
 "storage_positive":b_l3["storage_cached_tokens"]>0,
 "uncached_tokens_strictly_lower":b_l3["uncached_prompt_tokens"]<control["uncached_prompt_tokens"]}
json.dump({"a":a,"b_l3":b_l3,"b_no_l3":control,"facts":facts},open(sys.argv[4],"w"),indent=2,sort_keys=True)
PY
# END RESPONSE EVIDENCE REDUCER
else
  printf 'WORKER_BLOCKED_READY_FOR_C_STOP_TRANSFER_AND_SEAL\n'
fi
rm -f "$C0_REQUEST_TMP"/*
rmdir "$C0_REQUEST_TMP"
# END WORKER OPERATOR TERMINAL
```

## 4. Stop C and join evidence

After the worker chain (or any blocked A attempt), paste this in the still-open C terminal. It stops only C-local PIDs and creates the C-host archive outside its run directory.

```bash
# BEGIN C HOST STOP
kill -TERM -- "-$C0_STORE_PGID"
kill -TERM -- "-$C0_MASTER_PGID"
kill -TERM -- "-$C0_METADATA_PGID"
STORE_EXIT=0; wait "$C0_STORE_PID" || STORE_EXIT=$?
MASTER_EXIT=0; wait "$C0_MASTER_PID" || MASTER_EXIT=$?
METADATA_EXIT=0; wait "$C0_METADATA_PID" || METADATA_EXIT=$?
for pgid in "$C0_STORE_PGID" "$C0_MASTER_PGID" "$C0_METADATA_PGID"; do
  if ps -eo pgid= | awk -v p="$pgid" '$1==p{found=1} END{exit found?0:1}'; then exit 1; fi
done
printf 'store=%s\nmaster=%s\nmetadata=%s\nall_process_groups_empty=true\n' \
  "$STORE_EXIT" "$MASTER_EXIT" "$METADATA_EXIT" >"$C0_C_RUN_DIR/store/exit.txt"
(cd "$C0_C_RUN_DIR" && find . -type f -print | LC_ALL=C sort | xargs sha256sum) \
  >"$C0_C_EXPORT_DIR/c-host-inventory.sha256.tmp"
mv "$C0_C_EXPORT_DIR/c-host-inventory.sha256.tmp" "$C0_C_RUN_DIR/c-host-inventory.sha256"
(cd "$C0_C_RUN_DIR" && sha256sum -c c-host-inventory.sha256)
tar -cf "$C0_C_EXPORT_DIR/c-host-evidence.tar" -C "$(dirname "$C0_C_RUN_DIR")" "$(basename "$C0_C_RUN_DIR")"
(cd "$C0_C_EXPORT_DIR" && sha256sum c-host-evidence.tar >c-host-evidence.tar.sha256 && sha256sum -c c-host-evidence.tar.sha256)
# END C HOST STOP
```

Then return to the worker/operator terminal. This is the only cross-host evidence transfer; it is a manual handoff, not an SSH orchestrator.

```bash
# BEGIN C EVIDENCE TRANSFER
: "${C0_C_EVIDENCE_SCP_BASE:?user@c-private-host:/absolute/c-export-dir}"
scp "$C0_C_EVIDENCE_SCP_BASE/c-host-evidence.tar" "$C0_C_EVIDENCE_SCP_BASE/c-host-evidence.tar.sha256" \
  "$C0_RUN_DIR/store/"
(cd "$C0_RUN_DIR/store" && c0_sha256_check c-host-evidence.tar.sha256)
# END C EVIDENCE TRANSFER
```

## 5. Manual oracle and handoff

`oracle-inputs.json` contains only counts, hashes, equality/reduction facts, and no prompt/output/token plaintext. The owner reviews it together with cold/Put/Get evidence, applies the frozen table, and writes exactly one five-line `classification.txt`; the runbook does not choose that record. Legal combinations are: blocked/all `NOT_EVALUATED`/`RETRY_BLOCKER`; executed `PASS`/both `PASS`/`REVIEW_C1`; executed `FAIL` with restore `FAIL` and remote `NOT_APPLICABLE`, or restore `PASS` and remote `FAIL`, both with `STOP`; executed/all `INCONCLUSIVE`/`REVIEW_EVIDENCE`.

```bash
# BEGIN MANUAL CLASSIFICATION VALIDATOR
"$C0_PYTHON" - "$C0_RUN_DIR/classification.txt" <<'PY'
import sys
lines=open(sys.argv[1]).read().splitlines(); keys=("execution_status","gate_outcome","RESTORE_PATH_PASS","REMOTE_VALUE_SURVIVES","next_action")
if len(lines)!=len(keys) or any("=" not in line for line in lines): raise ValueError("classification must contain five key=value lines")
pairs=[line.split("=",1) for line in lines]
if [key for key,_ in pairs] != list(keys) or len({key for key,_ in pairs}) != len(keys): raise ValueError("unknown, duplicate, or out-of-order classification key")
record=dict(pairs)
legal=(
 {"execution_status":"BLOCKED_BEFORE_C0","gate_outcome":"NOT_EVALUATED","RESTORE_PATH_PASS":"NOT_EVALUATED","REMOTE_VALUE_SURVIVES":"NOT_EVALUATED","next_action":"RETRY_BLOCKER"},
 {"execution_status":"EXECUTED","gate_outcome":"PASS","RESTORE_PATH_PASS":"PASS","REMOTE_VALUE_SURVIVES":"PASS","next_action":"REVIEW_C1"},
 {"execution_status":"EXECUTED","gate_outcome":"FAIL","RESTORE_PATH_PASS":"FAIL","REMOTE_VALUE_SURVIVES":"NOT_APPLICABLE","next_action":"STOP"},
 {"execution_status":"EXECUTED","gate_outcome":"FAIL","RESTORE_PATH_PASS":"PASS","REMOTE_VALUE_SURVIVES":"FAIL","next_action":"STOP"},
 {"execution_status":"EXECUTED","gate_outcome":"INCONCLUSIVE","RESTORE_PATH_PASS":"INCONCLUSIVE","REMOTE_VALUE_SURVIVES":"INCONCLUSIVE","next_action":"REVIEW_EVIDENCE"},
)
if record not in legal: raise ValueError("illegal classification combination")
print("CLASSIFICATION_RECORD_VALID")
PY
# END MANUAL CLASSIFICATION VALIDATOR
test -s "$C0_RUN_DIR/store/c-host-evidence.tar"
seal_and_copy_c0_evidence
```

Do not release either host until the off-host checksum succeeds. Missing build/API/config, private exposure/connectivity, nonzero segment, process environment, terminal Put, or C evidence is fail-closed; target facts remain runtime-only. OCI/OSS, a classifier/finalizer, retry framework, runner, and SSH orchestration remain out of scope.
