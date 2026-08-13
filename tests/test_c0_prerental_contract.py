from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
C0_ROOT = REPOSITORY_ROOT / "experiments" / "c0"
INPUT_SPEC_PATH = C0_ROOT / "input_bundle_spec.json"
MATERIALIZER_PATH = C0_ROOT / "materialize_input_bundle.py"
VERIFIER_PATH = C0_ROOT / "verify_input_bundle.py"
REQUEST_TEMPLATE_PATH = C0_ROOT / "request-template.json"
RUNBOOK_PATH = C0_ROOT / "FIRST_C0_RUNBOOK.md"
OFFICIAL_WHEEL_FILENAME = (
    "mooncake_transfer_engine-0.3.12.post1-cp311-cp311-manylinux_2_28_x86_64.whl"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def marked_body(text: str, begin: str, end: str) -> str:
    if begin not in text or end not in text:
        raise AssertionError(f"missing runbook seam: {begin} / {end}")
    return text.split(begin, 1)[1].split(end, 1)[0]


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class Fixture:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.source = root / "sglang-source"
        self.source.mkdir()
        (self.source / "README.md").write_text("pinned source\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(self.source)], check=True)
        subprocess.run(["git", "-C", str(self.source), "add", "README.md"], check=True)
        subprocess.run(
            [
                "git", "-C", str(self.source),
                "-c", "user.email=c0@example.invalid", "-c", "user.name=C0 Test",
                "commit", "-q", "-m", "fixture",
            ],
            check=True,
        )
        self.commit = subprocess.run(
            ["git", "-C", str(self.source), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        self.wheel = root / OFFICIAL_WHEEL_FILENAME
        self.wheel.write_bytes(b"fixture wheel bytes")
        self.model = root / "model"
        self.model.mkdir()
        (self.model / "config.json").write_text('{"model_type":"fixture"}\n', encoding="utf-8")
        (self.model / "tokenizer.json").write_text('{"version":"1.0"}\n', encoding="utf-8")
        self.template = root / "request-template.json"
        self.template.write_bytes(REQUEST_TEMPLATE_PATH.read_bytes())
        self.spec = root / "input-bundle-spec.json"
        self.refresh_spec()
        self.output = root / "bundle"

    def model_files(self) -> list[dict[str, str]]:
        return [
            {"path": path.relative_to(self.model).as_posix(), "sha256": sha256_file(path)}
            for path in sorted(self.model.rglob("*"))
            if path.is_file()
        ]

    def refresh_spec(self) -> None:
        write_json(
            self.spec,
            {
                "schema_version": 1,
                "purpose": "test fixture",
                "sglang": {"repository": "fixture", "commit": self.commit},
                "mooncake": {
                    "package": "mooncake-transfer-engine",
                    "repository": "https://github.com/kvcache-ai/Mooncake.git",
                    "tag": "v0.3.12.post1",
                    "commit": "6041a609a8c3af35e778f70db344f145c2914980",
                    "version": "0.3.12.post1",
                    "wheel_filename": OFFICIAL_WHEEL_FILENAME,
                    "wheel_sha256": sha256_file(self.wheel),
                },
                "model": {
                    "repository": "fixture/model",
                    "revision": "fixture-revision",
                    "dtype": "bfloat16",
                    "tokenizer_layout": "same_snapshot_as_model",
                    "files": self.model_files(),
                },
                "required_bundle_entries": [
                    "sglang-source.tar",
                    OFFICIAL_WHEEL_FILENAME,
                    "model",
                    "request-template.json",
                    "input-bundle-spec.json",
                    "verify-input-bundle.py",
                    "bundle-manifest.json",
                ],
            },
        )

    def materialize(self, *, check: bool = False) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(MATERIALIZER_PATH),
                "--output",
                str(self.output),
                "--sglang-source",
                str(self.source),
                "--mooncake-wheel",
                str(self.wheel),
                "--model-dir",
                str(self.model),
                "--request-template",
                str(self.template),
                "--spec",
                str(self.spec),
            ],
            check=check,
            capture_output=True,
            text=True,
        )

    def manifest_root(self) -> str:
        return sha256_file(self.output / "bundle-manifest.json")

    def verify(self, expected_root: str | None = None) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, str(VERIFIER_PATH), "--bundle", str(self.output)]
        if expected_root is not None:
            command.extend(["--expected-manifest-sha256", expected_root])
        return subprocess.run(command, capture_output=True, text=True)


class C0PrerentalContractTest(unittest.TestCase):
    def make_fixture(self, temporary_directory: str) -> Fixture:
        return Fixture(Path(temporary_directory))

    def test_production_spec_pins_official_wheel_and_complete_model_inventory(self) -> None:
        spec = json.loads(INPUT_SPEC_PATH.read_text(encoding="utf-8"))
        self.assertEqual(spec["schema_version"], 1)
        self.assertEqual(
            spec["sglang"]["commit"],
            "b058dc910619c9d4bce9e9e24117104ffc491fa6",
        )
        self.assertEqual(spec["mooncake"]["wheel_filename"], OFFICIAL_WHEEL_FILENAME)
        self.assertEqual(
            spec["mooncake"],
            {
                "package": "mooncake-transfer-engine",
                "repository": "https://github.com/kvcache-ai/Mooncake.git",
                "tag": "v0.3.12.post1",
                "commit": "6041a609a8c3af35e778f70db344f145c2914980",
                "version": "0.3.12.post1",
                "wheel_filename": OFFICIAL_WHEEL_FILENAME,
                "wheel_sha256": "8b73bf8a4f1de741a73f04f32f1e73549c60bfbf7ee73710141ef1f8ea324439",
            },
        )
        self.assertEqual(
            spec["mooncake"]["wheel_sha256"],
            "8b73bf8a4f1de741a73f04f32f1e73549c60bfbf7ee73710141ef1f8ea324439",
        )
        self.assertEqual(spec["model"]["revision"], "989aa7980e4cf806f80c7fef2b1adb7bc71aa306")
        expected_model_paths = [
            ".gitattributes",
            "LICENSE",
            "README.md",
            "config.json",
            "generation_config.json",
            "merges.txt",
            "model.safetensors",
            "tokenizer.json",
            "tokenizer_config.json",
            "vocab.json",
        ]
        model_files = spec["model"]["files"]
        self.assertEqual([item["path"] for item in model_files], expected_model_paths)
        self.assertTrue(all(len(item["sha256"]) == 64 for item in model_files))
        self.assertIn(OFFICIAL_WHEEL_FILENAME, spec["required_bundle_entries"])
        self.assertNotIn("mooncake-wheel.whl", spec["required_bundle_entries"])

    def test_request_template_is_a_complete_deterministic_raw_completion_contract(self) -> None:
        template = json.loads(REQUEST_TEMPLATE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(template["endpoint"], "/v1/completions")
        self.assertTrue(template["seed_text"])
        self.assertTrue(template["filler_text"])
        self.assertEqual(
            template["construction"],
            {
                "candidate": "seed_text + (filler_text * filler_repetitions) + suffix_text",
                "search_order": "ascending_nonnegative_filler_repetitions",
                "selection": "first token_count >= minimum_prefix_tokens and token_count % page_size == 0",
                "tokenization": {"add_special_tokens": False},
                "on_no_candidate": "BLOCKED_BEFORE_C0",
            },
        )
        self.assertEqual(
            template["serialization"],
            {
                "format": "utf8-json",
                "sort_keys": True,
                "separators": [",", ":"],
                "ensure_ascii": False,
                "trailing_newline": False,
            },
        )
        decode = template["decode"]
        self.assertEqual(decode["max_tokens"], 1)
        self.assertEqual(decode["min_tokens"], 1)
        self.assertEqual(decode["temperature"], 0.0)
        self.assertEqual(decode["n"], 1)
        self.assertTrue(decode["ignore_eos"])
        self.assertTrue(decode["return_cached_tokens_details"])
        self.assertTrue(decode["return_token_ids"])

    def test_materializer_accepts_only_a_self_consistent_pinned_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture = self.make_fixture(temporary_directory)
            completed = fixture.materialize(check=True)
            manifest = json.loads((fixture.output / "bundle-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["schema_version"], 1)
            self.assertEqual(set(manifest), {"schema_version", "entries"})
            self.assertIn(OFFICIAL_WHEEL_FILENAME, manifest["entries"])
            self.assertTrue((fixture.output / OFFICIAL_WHEEL_FILENAME).is_file())
            self.assertNotIn("mooncake-wheel.whl", manifest["entries"])
            self.assertIn("BUNDLE_MANIFEST=", completed.stdout)
            verified = fixture.verify(fixture.manifest_root())
            self.assertEqual(verified.returncode, 0, verified.stderr)

    def test_bundle_root_omits_dead_static_config_and_spec_derived_manifest_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture = self.make_fixture(temporary_directory)
            fixture.materialize(check=True)
            spec = json.loads(fixture.output.joinpath("input-bundle-spec.json").read_text())
            manifest = json.loads(fixture.output.joinpath("bundle-manifest.json").read_text())

            self.assertNotIn("static-config.json", spec["required_bundle_entries"])
            self.assertFalse(fixture.output.joinpath("static-config.json").exists())
            self.assertEqual(set(manifest), {"schema_version", "entries"})
            self.assertEqual(set(manifest["entries"]["model"]), {"sha256"})

    def test_verifier_requires_an_external_expected_manifest_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture = self.make_fixture(temporary_directory)
            fixture.materialize(check=True)
            missing = fixture.verify()
            self.assertNotEqual(missing.returncode, 0)
            fixture.output.joinpath("bundle-manifest.json").write_text("{not-json", encoding="utf-8")
            wrong = fixture.verify("0" * 64)
            self.assertNotEqual(wrong.returncode, 0)
            self.assertIn("manifest SHA-256 mismatch", wrong.stderr)
            self.assertNotIn("JSON", wrong.stderr)

    def test_manifest_and_payload_rewrite_cannot_replace_the_external_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture = self.make_fixture(temporary_directory)
            fixture.materialize(check=True)
            owner_root = fixture.manifest_root()
            copied_wheel = fixture.output / OFFICIAL_WHEEL_FILENAME
            copied_wheel.write_bytes(b"attacker replacement")
            manifest_path = fixture.output / "bundle-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["entries"][OFFICIAL_WHEEL_FILENAME]["sha256"] = sha256_file(copied_wheel)
            write_json(manifest_path, manifest)
            rewritten = fixture.verify(owner_root)
            self.assertNotEqual(rewritten.returncode, 0)
            self.assertIn("manifest SHA-256 mismatch", rewritten.stderr)

    def test_verifier_rejects_empty_missing_and_extra_manifest_entries(self) -> None:
        mutations = {
            "empty": lambda manifest: manifest.update(entries={}),
            "missing": lambda manifest: manifest["entries"].pop("request-template.json"),
            "extra": lambda manifest: manifest["entries"].update(
                {"rogue.txt": {"sha256": hashlib.sha256(b"rogue").hexdigest()}}
            ),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary_directory:
                fixture = self.make_fixture(temporary_directory)
                fixture.materialize(check=True)
                manifest_path = fixture.output / "bundle-manifest.json"
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                mutate(manifest)
                if name == "extra":
                    fixture.output.joinpath("rogue.txt").write_bytes(b"rogue")
                write_json(manifest_path, manifest)
                rejected = fixture.verify(sha256_file(manifest_path))
                self.assertNotEqual(rejected.returncode, 0)
                self.assertIn("manifest entries", rejected.stderr)

    def test_verifier_rejects_a_file_outside_the_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture = self.make_fixture(temporary_directory)
            fixture.materialize(check=True)
            root = fixture.manifest_root()
            fixture.output.joinpath("unmanifested.txt").write_text("extra", encoding="utf-8")
            rejected = fixture.verify(root)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("unexpected top-level bundle entry", rejected.stderr)

    def test_materializer_rejects_wrong_extra_and_missing_model_inventory(self) -> None:
        for mutation in ("wrong", "extra", "missing"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary_directory:
                fixture = self.make_fixture(temporary_directory)
                if mutation == "wrong":
                    fixture.model.joinpath("config.json").write_text("changed", encoding="utf-8")
                elif mutation == "extra":
                    fixture.model.joinpath("unexpected.bin").write_bytes(b"extra")
                else:
                    fixture.model.joinpath("tokenizer.json").unlink()
                rejected = fixture.materialize()
                self.assertNotEqual(rejected.returncode, 0)
                self.assertIn("model inventory mismatch", rejected.stderr)
                self.assertFalse(fixture.output.exists())

    def test_runbook_local_handoff_seam_fails_closed_and_inventory_is_not_recursive(self) -> None:
        runbook = RUNBOOK_PATH.read_text(encoding="utf-8")
        begin = "# BEGIN SAFE LOCAL HANDOFF SEAM"
        end = "# END SAFE LOCAL HANDOFF SEAM"
        self.assertIn(begin, runbook)
        self.assertIn(end, runbook)
        seam = runbook.split(begin, 1)[1].split(end, 1)[0]

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            trust_environment = {
                "C0_STAGED_RUNBOOK": str(RUNBOOK_PATH),
                "C0_EXPECTED_RUNBOOK_SHA256": sha256_file(RUNBOOK_PATH),
                "C0_ACTUAL_RUNBOOK_SHA256": sha256_file(RUNBOOK_PATH),
            }
            run_dir = root / "run"
            export_dir = root / "export"
            off_host = root / "off-host"
            off_host.mkdir()
            environment = {
                **trust_environment,
                "C0_RUN_DIR": str(run_dir),
                "C0_EXPORT_DIR": str(export_dir),
                "C0_OFF_HOST_DIR": str(off_host),
                "C0_OFF_HOST_ID": "test-durable-destination",
                "C0_OFF_HOST_DURABILITY_REVIEWED": "true",
                "C0_WORK_ROOT": str(root / "work"),
            }
            bootstrap = seam + "\ninit_c0_run_dir\n"
            created = subprocess.run(
                ["bash", "-c", bootstrap], env=environment, capture_output=True, text=True
            )
            self.assertEqual(created.returncode, 0, created.stderr)
            repeated = subprocess.run(
                ["bash", "-c", bootstrap], env=environment, capture_output=True, text=True
            )
            self.assertNotEqual(repeated.returncode, 0)
            self.assertIn("already exists", repeated.stderr)

            occupied_off_host = root / "occupied-off-host"
            occupied_off_host.mkdir()
            occupied_off_host.joinpath("c0-raw-evidence.tar").write_bytes(b"preserve me")
            occupied = subprocess.run(
                ["bash", "-c", bootstrap],
                env={
                    **trust_environment,
                    "C0_RUN_DIR": str(root / "occupied-run"),
                    "C0_EXPORT_DIR": str(root / "occupied-export"),
                    "C0_OFF_HOST_DIR": str(occupied_off_host),
                    "C0_OFF_HOST_ID": "occupied-destination",
                    "C0_OFF_HOST_DURABILITY_REVIEWED": "true",
                    "C0_WORK_ROOT": str(root / "occupied-work"),
                },
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(occupied.returncode, 0)
            self.assertIn("off-host evidence target already exists", occupied.stderr)
            self.assertEqual(
                occupied_off_host.joinpath("c0-raw-evidence.tar").read_bytes(), b"preserve me"
            )

            for name, invalid_export in {
                "equal": root / "invalid-equal",
                "nested": root / "invalid-nested" / "export",
            }.items():
                invalid_run = (
                    root / "invalid-equal" if name == "equal" else root / "invalid-nested"
                )
                invalid_environment = {
                    **trust_environment,
                    "C0_RUN_DIR": str(invalid_run),
                    "C0_EXPORT_DIR": str(invalid_export),
                    "C0_OFF_HOST_DIR": str(off_host),
                    "C0_OFF_HOST_ID": f"{name}-destination",
                    "C0_OFF_HOST_DURABILITY_REVIEWED": "true",
                    "C0_WORK_ROOT": str(root / f"{name}-work"),
                }
                rejected = subprocess.run(
                    ["bash", "-c", bootstrap],
                    env=invalid_environment,
                    capture_output=True,
                    text=True,
                )
                self.assertNotEqual(rejected.returncode, 0, name)
                self.assertIn("must be separate", rejected.stderr)
                self.assertFalse(invalid_run.exists(), name)

            run_dir.joinpath("raw.txt").write_text("raw evidence", encoding="utf-8")
            failed_capture = subprocess.run(
                [
                    "bash",
                    "-c",
                    seam + "\nrun_capture failing bash -c 'echo out; echo err >&2; exit 23'\n",
                ],
                env=environment,
                capture_output=True,
                text=True,
            )
            self.assertEqual(failed_capture.returncode, 23)
            self.assertEqual(run_dir.joinpath("failing.stdout").read_text().strip(), "out")
            self.assertEqual(run_dir.joinpath("failing.stderr").read_text().strip(), "err")

            sealed = subprocess.run(
                ["bash", "-c", seam + "\nseal_and_copy_c0_evidence\n"],
                env=environment,
                capture_output=True,
                text=True,
            )
            self.assertEqual(sealed.returncode, 0, sealed.stderr)
            inventory = run_dir.joinpath("artifact-inventory.sha256").read_text(encoding="utf-8")
            self.assertIn("raw.txt", inventory)
            self.assertNotIn("artifact-inventory.sha256", inventory)
            self.assertNotIn("c0-raw-evidence.tar", inventory)
            self.assertTrue(export_dir.joinpath("c0-raw-evidence.tar").is_file())
            self.assertTrue(off_host.joinpath("c0-raw-evidence.tar").is_file())
            confirmation = off_host.joinpath("c0-raw-evidence.verified.txt").read_text()
            self.assertIn("destination_id=test-durable-destination", confirmation)
            self.assertIn("verified=true", confirmation)

            c_path_seam = marked_body(
                runbook, "# BEGIN C HOST PATH SEAM", "# END C HOST PATH SEAM"
            )
            for name, c_run, c_export in (
                ("equal", root / "c-equal", root / "c-equal"),
                ("nested", root / "c-nested", root / "c-nested" / "export"),
            ):
                rejected = subprocess.run(
                    ["bash", "-c", "set -euo pipefail\n" + c_path_seam],
                    env={
                        "C0_C_RUN_DIR": str(c_run),
                        "C0_C_EXPORT_DIR": str(c_export),
                        "C0_C_WORK_ROOT": str(root / f"c-{name}-work"),
                    },
                    capture_output=True,
                    text=True,
                )
                self.assertNotEqual(rejected.returncode, 0, name)
                self.assertIn("must be separate", rejected.stderr)

            worker_nested = subprocess.run(
                ["bash", "-c", bootstrap],
                env={
                    **trust_environment,
                    "C0_RUN_DIR": str(root / "worker-nested"),
                    "C0_EXPORT_DIR": str(root / "worker-export"),
                    "C0_OFF_HOST_DIR": str(off_host),
                    "C0_OFF_HOST_ID": "nested-destination",
                    "C0_OFF_HOST_DURABILITY_REVIEWED": "true",
                    "C0_WORK_ROOT": str(root / "worker-nested" / "work"),
                },
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(worker_nested.returncode, 0)
            self.assertIn("C0_WORK_ROOT must be separate", worker_nested.stderr)

            c_nested = subprocess.run(
                ["bash", "-c", "set -euo pipefail\n" + c_path_seam],
                env={
                    "C0_C_RUN_DIR": str(root / "c-work-nested"),
                    "C0_C_EXPORT_DIR": str(root / "c-work-export"),
                    "C0_C_WORK_ROOT": str(root / "c-work-nested" / "work"),
                },
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(c_nested.returncode, 0)
            self.assertIn("must be separate", c_nested.stderr)

    def test_runbook_external_root_rejects_tampering_and_is_retained(self) -> None:
        runbook = RUNBOOK_PATH.read_text(encoding="utf-8")
        precheck = marked_body(
            runbook, "# BEGIN RUNBOOK TRUST PRECHECK", "# END RUNBOOK TRUST PRECHECK"
        )
        worker_seam = marked_body(
            runbook, "# BEGIN SAFE LOCAL HANDOFF SEAM", "# END SAFE LOCAL HANDOFF SEAM"
        )
        c_start = marked_body(
            runbook, "# BEGIN C HOST TERMINAL", "# END C HOST TERMINAL"
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            staged = Path(temporary_directory) / "FIRST_C0_RUNBOOK.md"
            staged.write_text(runbook, encoding="utf-8")
            expected = sha256_file(staged)
            environment = {
                "PATH": "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin",
                "C0_STAGED_RUNBOOK": str(staged),
                "C0_EXPECTED_RUNBOOK_SHA256": expected,
            }
            accepted = subprocess.run(
                ["bash", "-c", precheck], env=environment, capture_output=True, text=True
            )
            self.assertEqual(accepted.returncode, 0, accepted.stderr)

            environment["C0_EXPECTED_RUNBOOK_SHA256"] = "0" * 64
            wrong_root = subprocess.run(
                ["bash", "-c", precheck], env=environment, capture_output=True, text=True
            )
            self.assertNotEqual(wrong_root.returncode, 0)

            environment["C0_EXPECTED_RUNBOOK_SHA256"] = expected
            staged.write_text(runbook + "\nattacker rewrite\n", encoding="utf-8")
            rewritten = subprocess.run(
                ["bash", "-c", precheck], env=environment, capture_output=True, text=True
            )
            self.assertNotEqual(rewritten.returncode, 0)

        self.assertIn('cp "$C0_STAGED_RUNBOOK" "$C0_RUN_DIR/admission/FIRST_C0_RUNBOOK.md"', worker_seam)
        self.assertIn('cp "$C0_STAGED_RUNBOOK" "$C0_C_RUN_DIR/admission/FIRST_C0_RUNBOOK.md"', c_start)
        expected_root = sha256_file(RUNBOOK_PATH)
        for path in (
            REPOSITORY_ROOT / "STATUS.md",
            REPOSITORY_ROOT / "experiments/README.md",
            REPOSITORY_ROOT / "docs/implementation/G0_PRE_RENTAL_EXECUTION_CONTRACT.md",
        ):
            self.assertIn(expected_root, path.read_text(encoding="utf-8"), path)

    def test_runbook_separates_c_and_worker_hosts_and_joins_c_evidence_before_seal(self) -> None:
        runbook = RUNBOOK_PATH.read_text(encoding="utf-8")
        c_start = marked_body(
            runbook, "# BEGIN C HOST TERMINAL", "# END C HOST TERMINAL"
        )
        worker = marked_body(
            runbook,
            "# BEGIN WORKER OPERATOR TERMINAL",
            "# END WORKER OPERATOR TERMINAL",
        )
        c_stop = marked_body(runbook, "# BEGIN C HOST STOP", "# END C HOST STOP")
        transfer = marked_body(
            runbook, "# BEGIN C EVIDENCE TRANSFER", "# END C EVIDENCE TRANSFER"
        )

        self.assertIn("bundle-manifest.json", c_start)
        self.assertIn("expected_wheel", c_start)
        self.assertNotIn("verify-input-bundle.py", c_start)
        self.assertIn("verify-input-bundle.py", worker)
        self.assertIn("mooncake_store_service", c_start)
        self.assertNotIn("master-help", c_start)
        self.assertNotIn("sglang.launch_server", c_start)
        self.assertIn("must be separate", c_start)
        self.assertIn("sglang.launch_server", worker)
        self.assertNotIn("C0_STORE_PID", worker)
        self.assertIn("kill -TERM", c_stop)
        self.assertIn("scp", transfer)
        self.assertLess(runbook.index("# BEGIN C HOST STOP"), runbook.index("# BEGIN C EVIDENCE TRANSFER"))
        self.assertLess(runbook.index("# END C EVIDENCE TRANSFER"), runbook.rindex("seal_and_copy_c0_evidence"))
        self.assertIn('$C0_WORK_ROOT/sglang/python', worker)
        self.assertIn('"local_hostname":os.environ["C0_WORKER_PRIVATE_HOST"]', worker)
        self.assertNotIn('"local_hostname":"worker-a"', worker)
        self.assertNotIn('"local_hostname":"worker-b-l3"', worker)
        self.assertGreaterEqual(worker.count('mkdir "$C0_'), 3)
        self.assertGreaterEqual(worker.count('/cache" "$C0_'), 3)
        self.assertGreaterEqual(worker.count('CUDA_VISIBLE_DEVICES="$C0_GPU_UUID"'), 3)
        self.assertGreaterEqual(worker.count('/server_info'), 3)
        self.assertGreaterEqual(worker.count('/proc/$C0_'), 3)
        self.assertGreaterEqual(worker.count('x["dtype"]=="bfloat16"'), 3)
        self.assertGreaterEqual(worker.count('x["hicache_size"]==int('), 3)
        self.assertGreaterEqual(worker.count('x["hicache_storage_prefetch_policy"]=="wait_complete"'), 2)
        self.assertGreaterEqual(worker.count("--skip-server-warmup"), 3)
        self.assertGreaterEqual(worker.count('x["skip_server_warmup"] is True'), 3)
        self.assertGreaterEqual(worker.count("setsid env"), 3)
        self.assertIn("set +m", worker)
        self.assertGreaterEqual(worker.count('ps -o pgid= -p "$C0_'), 3)
        self.assertGreaterEqual(worker.count('test "$C0_'), 3)
        self.assertGreaterEqual(worker.count("kill -TERM -- \"-$C0_"), 3)
        self.assertGreaterEqual(worker.count("no_process_group_members=true"), 3)
        self.assertNotIn("log-offsets.txt", worker)
        self.assertNotIn("post-request.stdout", worker)
        self.assertNotIn("post-request.stderr", worker)
        self.assertNotIn("C0_A_PUT_PATTERN", worker)
        self.assertNotIn("C0_B_GET_PATTERN", worker)
        self.assertGreaterEqual(worker.count("--enable-metrics"), 3)
        self.assertGreaterEqual(worker.count('x["enable_metrics"] is True'), 3)
        self.assertIn("sglang:backuped_tokens_total", worker)
        self.assertIn("sglang:prefetched_tokens_total", worker)
        self.assertIn("a/metrics-before", worker)
        self.assertIn("a/metrics-after", worker)
        self.assertIn("b-l3/metrics-before", worker)
        self.assertIn("b-l3/metrics-after", worker)
        self.assertIn("export C0_WRITE_POLICY=write_through", worker)
        self.assertIn("export C0_WRITE_THRESHOLD=1", worker)
        self.assertIn("export C0_A_TRIGGER_REQUESTS=1", worker)
        self.assertIn("export C0_PREFETCH_THRESHOLD=256", worker)
        self.assertIn('test "$C0_MIN_PREFIX_TOKENS" -ge "$C0_PREFETCH_THRESHOLD"', worker)
        self.assertGreaterEqual(worker.count('"prefetch_threshold":int(os.environ["C0_PREFETCH_THRESHOLD"])'), 1)
        self.assertIn("distribution-record.sha256", worker)
        self.assertIn("export C0_MASTER_METRICS_PORT=9003", worker)
        self.assertIn("C0_IMAGE_ID", worker)
        self.assertIn("/etc/os-release", worker)
        self.assertIn("uname", worker)
        self.assertIn("CUDA_VISIBLE_DEVICES", worker)
        self.assertGreaterEqual(c_start.count("setsid"), 3)
        self.assertGreaterEqual(c_start.count('ps -o pgid= -p "$C0_'), 3)
        self.assertGreaterEqual(c_stop.count('kill -TERM -- "-$C0_'), 3)
        self.assertIn("all_process_groups_empty=true", c_stop)
        self.assertNotIn("no_process_group_members=true", c_stop)

    def test_runbook_bootstraps_pip_before_requiring_install_report(self) -> None:
        """Fresh target venvs may ship pip too old for ``install --report``."""
        runbook = RUNBOOK_PATH.read_text(encoding="utf-8")
        c_start = marked_body(
            runbook, "# BEGIN C HOST TERMINAL", "# END C HOST TERMINAL"
        )
        worker = marked_body(
            runbook,
            "# BEGIN WORKER OPERATOR TERMINAL",
            "# END WORKER OPERATOR TERMINAL",
        )
        for body in (c_start, worker):
            self.assertIn("pip install --upgrade pip", body)
            self.assertIn("pip-bootstrap-before", body)
            self.assertIn("pip-bootstrap-after", body)
            self.assertLess(
                body.index("pip install --upgrade pip"),
                body.index("--report"),
            )

    def test_stock_warmup_exception_is_namespace_separated_and_retained(self) -> None:
        runbook = RUNBOOK_PATH.read_text(encoding="utf-8")
        worker = marked_body(
            runbook, "# BEGIN WORKER OPERATOR TERMINAL", "# END WORKER OPERATOR TERMINAL"
        )
        self.assertIn(
            'warmup_key = "sglang_mooncake_store_warmup_key" + uuid.uuid4().hex',
            worker,
        )
        self.assertIn('return [f"{self.config_prefix}_{key}" for key in keys]', worker)
        self.assertIn("warmup_uses_config_prefix", worker)
        self.assertIn("tested_page_keys_use_config_prefix", worker)
        self.assertGreaterEqual(worker.count("Mooncake store warmup successfully."), 2)
        self.assertGreaterEqual(worker.count("Using Mooncake config prefix:"), 2)
        self.assertIn("warmup-namespace-source-proof.json", worker)

    def test_segment_response_admission_matches_real_stock_text_and_fails_closed(self) -> None:
        runbook = RUNBOOK_PATH.read_text(encoding="utf-8")
        c_start = marked_body(runbook, "# BEGIN C HOST TERMINAL", "# END C HOST TERMINAL")
        self.assertIn("/get_all_segments", c_start)
        self.assertIn("C0_MASTER_METRICS_PORT", c_start)
        self.assertNotIn("PAUSE_FOR_OWNER_SEGMENT_SCHEMA_REVIEW", c_start)
        self.assertIn("discover_listener_pid", c_start)
        self.assertNotIn('kill -0 "$C0_METADATA_PID" "$C0_MASTER_PID" "$C0_STORE_PID"', c_start)
        admission = marked_body(
            runbook,
            "# BEGIN SEGMENT RESPONSE ADMISSION",
            "# END SEGMENT RESPONSE ADMISSION",
        )
        program = admission.split("<<'PY'", 1)[1].rsplit("\nPY", 1)[0]
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            raw = root / "segments.txt"
            config = root / "config.json"
            service_log = root / "service.stderr"
            output = root / "admission.json"
            raw.write_text("10.0.0.7:13122\n", encoding="utf-8")
            write_json(config, {"local_hostname": "10.0.0.7", "global_segment_size": 4096})
            service_log.write_text(
                "Transfer Engine parseHostNameWithPort. server_name: 10.0.0.7 port: 13122\n"
                "Mounting segment: 4096 bytes, 4096 of 4096\n",
                encoding="utf-8",
            )
            command = [
                sys.executable, "-c", program, str(raw), str(config), str(service_log),
                "10.0.0.7", "4096", str(output),
            ]
            accepted = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            self.assertEqual(json.loads(output.read_text())["segment_size"], 4096)
            output.unlink()
            rejected = subprocess.run(command[:-2] + ["8192", str(output)], capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertFalse(output.exists())

    def test_c_host_records_only_observed_cuda_loader_dependencies(self) -> None:
        runbook = RUNBOOK_PATH.read_text(encoding="utf-8")
        c_start = marked_body(runbook, "# BEGIN C HOST TERMINAL", "# END C HOST TERMINAL")
        self.assertIn("C0_C_LIBCUDA_DEB", c_start)
        self.assertIn("01327514a8fde543dc092b79016f92a51dc7d72aa59db193c2405bde7d371503", c_start)
        self.assertIn("C0_C_CUDART_WHEEL", c_start)
        self.assertIn("adade8dcbd0edf427b7204d480d6066d33902cab2a4707dcfc48a2d0fd44ab90", c_start)
        self.assertIn("cudart-install-report.json", c_start)
        self.assertIn("LD_LIBRARY_PATH", c_start)
        self.assertIn("C0_MASTER_ELF", c_start)
        self.assertIn("mooncake.__file__", c_start)

    def test_response_reducer_rejects_missing_accounting_and_emits_hashes_and_deltas(self) -> None:
        runbook = RUNBOOK_PATH.read_text(encoding="utf-8")
        self.assertIn('$C0_REQUEST_TMP/b-l3-response.json', runbook)
        self.assertIn('$C0_REQUEST_TMP/b-no-l3-response.json', runbook)
        self.assertIn('$C0_REQUEST_TMP/a-response-', runbook)
        self.assertIn("# BEGIN A RESPONSE REDUCER", runbook)
        self.assertIn("a/response-summary.json", runbook)
        a_reducer = marked_body(
            runbook, "# BEGIN A RESPONSE REDUCER", "# END A RESPONSE REDUCER"
        ).split("<<'PY'", 1)[1].split("\n", 1)[1].rsplit("\nPY", 1)[0]
        self.assertNotIn("run_capture b-l3/response", runbook)
        self.assertNotIn("run_capture b-no-l3/response", runbook)
        self.assertIn('rm -f "$C0_REQUEST_TMP"/*', runbook)
        reducer = marked_body(
            runbook,
            "# BEGIN RESPONSE EVIDENCE REDUCER",
            "# END RESPONSE EVIDENCE REDUCER",
        )
        reducer = reducer.split("<<'PY'", 1)[1].rsplit("\nPY", 1)[0]

        prompt_ids = [11, 12, 13, 14]
        output_ids = [42]
        prompt_hash = hashlib.sha256(
            json.dumps(prompt_ids, separators=(",", ":")).encode()
        ).hexdigest()
        output_ids_hash = hashlib.sha256(
            json.dumps(output_ids, separators=(",", ":")).encode()
        ).hexdigest()
        output_hash = hashlib.sha256("Z".encode()).hexdigest()

        def response(*, cached: int, storage: int | None) -> dict[str, object]:
            value: dict[str, object] = {
                "model": "c0-model",
                "choices": [
                    {
                        "index": 0,
                        "text": "Z",
                        "token_ids": output_ids,
                        "prompt_token_ids": prompt_ids,
                    }
                ],
                "usage": {
                    "prompt_tokens": 4,
                    "completion_tokens": 1,
                    "total_tokens": 5,
                    "prompt_tokens_details": {"cached_tokens": cached},
                },
            }
            if storage is not None:
                value["sglext"] = {"cached_tokens_details": {"storage": storage}}
            return value

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            identity = root / "identity.json"
            b_l3 = root / "b-l3.json"
            control = root / "control.json"
            output = root / "oracle-inputs.json"
            a_response = root / "a.json"
            prefetch_delta = root / "prefetch-delta.json"
            write_json(
                identity,
                {"token_ids_sha256": prompt_hash, "request_body_sha256": "a" * 64},
            )
            write_json(b_l3, response(cached=3, storage=2))
            write_json(control, response(cached=0, storage=None))
            write_json(a_response, response(cached=0, storage=0))
            a_value = json.loads(a_response.read_text())
            a_value["usage"]["prompt_tokens_details"] = None
            write_json(a_response, a_value)
            write_json(prefetch_delta, {"before": 0, "after": 3, "delta": 3, "positive": True})

            a_summary = root / "a-summary.json"
            accepted_a = subprocess.run(
                [sys.executable, "-c", a_reducer, str(a_response), str(a_summary)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(accepted_a.returncode, 0, accepted_a.stderr)
            self.assertEqual(json.loads(a_summary.read_text())["cached_tokens"], 0)

            malformed_a = root / "malformed-a.json"
            malformed_summary = root / "malformed-a-summary.json"
            malformed_a.write_bytes(b"not-json-sensitive-raw")
            malformed = subprocess.run(
                [sys.executable, "-c", a_reducer, str(malformed_a), str(malformed_summary)],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(malformed.returncode, 0)
            self.assertEqual(
                json.loads(malformed_summary.read_text())["raw_response_sha256"],
                sha256_file(malformed_a),
            )
            self.assertNotIn("not-json-sensitive-raw", malformed_summary.read_text())

            completed = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    reducer,
                    str(identity),
                    str(b_l3),
                    str(control),
                    str(output),
                    "c0-model",
                    str(prefetch_delta),
                    str(a_response),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            oracle = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(oracle["b_l3"]["uncached_prompt_tokens"], 1)
            self.assertEqual(oracle["b_no_l3"]["uncached_prompt_tokens"], 4)
            self.assertEqual(oracle["b_l3"]["output_utf8_sha256"], output_hash)
            self.assertEqual(oracle["b_l3"]["prompt_token_ids_sha256"], prompt_hash)
            self.assertEqual(oracle["b_l3"]["completion_token_ids_sha256"], output_ids_hash)
            self.assertEqual(oracle["b_l3"]["raw_response_sha256"], sha256_file(b_l3))
            self.assertTrue(oracle["facts"]["storage_positive"])
            self.assertTrue(oracle["facts"]["prefetched_counter_positive"])
            self.assertTrue(oracle["facts"]["uncached_tokens_strictly_lower"])
            self.assertTrue(oracle["facts"]["output_utf8_equal"])
            self.assertNotIn("a_outputs_match_b", oracle["facts"])
            self.assertNotIn("Z", output.read_text(encoding="utf-8"))
            self.assertNotIn(str(prompt_ids), output.read_text(encoding="utf-8"))

            invalid = response(cached=3, storage=2)
            invalid["usage"].pop("prompt_tokens")
            write_json(b_l3, invalid)
            output.unlink()
            rejected = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    reducer,
                    str(identity),
                    str(b_l3),
                    str(control),
                    str(output),
                    "c0-model",
                    str(prefetch_delta),
                    str(a_response),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(rejected.returncode, 0)
            self.assertFalse(output.exists())

            missing_control_accounting = response(cached=0, storage=None)
            missing_control_accounting["usage"].pop("prompt_tokens_details")
            write_json(control, missing_control_accounting)
            write_json(b_l3, response(cached=3, storage=2))
            accepted_missing_zero = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    reducer,
                    str(identity),
                    str(b_l3),
                    str(control),
                    str(output),
                    "c0-model",
                    str(prefetch_delta),
                    str(a_response),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(accepted_missing_zero.returncode, 0, accepted_missing_zero.stderr)
            self.assertEqual(json.loads(output.read_text())["b_no_l3"]["cached_tokens"], 0)

            output.unlink()
            missing_control_accounting["usage"]["prompt_tokens_details"] = {}
            write_json(control, missing_control_accounting)
            rejected_bad_details = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    reducer,
                    str(identity),
                    str(b_l3),
                    str(control),
                    str(output),
                    "c0-model",
                    str(prefetch_delta),
                    str(a_response),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(rejected_bad_details.returncode, 0)
            self.assertFalse(output.exists())

    def test_manual_classification_validator_rejects_duplicate_and_illegal_records(self) -> None:
        runbook = RUNBOOK_PATH.read_text(encoding="utf-8")
        validator = marked_body(
            runbook,
            "# BEGIN MANUAL CLASSIFICATION VALIDATOR",
            "# END MANUAL CLASSIFICATION VALIDATOR",
        )
        validator = validator.split("<<'PY'", 1)[1].rsplit("\nPY", 1)[0]
        valid = (
            "execution_status=EXECUTED\n"
            "gate_outcome=PASS\n"
            "RESTORE_PATH_PASS=PASS\n"
            "REMOTE_VALUE_SURVIVES=PASS\n"
            "next_action=REVIEW_C1\n"
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            record = Path(temporary_directory) / "classification.txt"
            for name, body, expected in (
                ("valid", valid, 0),
                ("duplicate", valid + "gate_outcome=FAIL\n", 1),
                (
                    "illegal",
                    valid.replace("REMOTE_VALUE_SURVIVES=PASS", "REMOTE_VALUE_SURVIVES=FAIL"),
                    1,
                ),
            ):
                with self.subTest(name=name):
                    record.write_text(body, encoding="utf-8")
                    completed = subprocess.run(
                        [sys.executable, "-c", validator, str(record)],
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(completed.returncode == 0, expected == 0, completed.stderr)


if __name__ == "__main__":
    unittest.main()
