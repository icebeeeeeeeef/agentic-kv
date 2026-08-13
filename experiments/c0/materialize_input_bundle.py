#!/usr/bin/env python3
"""Materialize the exact, locally reviewed first-C0 inputs without networking."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parent


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inventory(path: Path) -> dict[str, object]:
    files = [
        {"path": item.relative_to(path).as_posix(), "sha256": sha256_file(item)}
        for item in sorted(path.rglob("*"))
        if item.is_file()
    ]
    encoded = json.dumps(files, separators=(",", ":"), sort_keys=True).encode()
    return {"sha256": hashlib.sha256(encoded).hexdigest(), "files": files}


def require_request_contract(template: dict[str, object]) -> None:
    decode = template.get("decode", {})
    required_decode = {
        "max_tokens": 1,
        "min_tokens": 1,
        "temperature": 0.0,
        "top_p": 1.0,
        "top_k": -1,
        "min_p": 0.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "repetition_penalty": 1.0,
        "n": 1,
        "stream": False,
        "echo": False,
        "ignore_eos": True,
        "return_cached_tokens_details": True,
        "return_token_ids": True,
    }
    valid = (
        template.get("schema_version") == 1
        and template.get("endpoint") == "/v1/completions"
        and all(template.get(key) for key in ("template_id", "seed_text", "filler_text", "suffix_text"))
        and template.get("construction", {}).get("on_no_candidate") == "BLOCKED_BEFORE_C0"
        and template.get("construction", {}).get("search_order")
        == "ascending_nonnegative_filler_repetitions"
        and template.get("serialization")
        == {
            "format": "utf8-json",
            "sort_keys": True,
            "separators": [",", ":"],
            "ensure_ascii": False,
            "trailing_newline": False,
        }
        and isinstance(decode, dict)
        and all(decode.get(key) == value for key, value in required_decode.items())
        and type(decode.get("seed")) is int
    )
    if not valid:
        raise ValueError("invalid first-C0 request template")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sglang-source", type=Path, required=True)
    parser.add_argument("--mooncake-wheel", type=Path, required=True)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--request-template", type=Path, default=ROOT / "request-template.json")
    parser.add_argument("--spec", type=Path, default=ROOT / "input_bundle_spec.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = args.output.resolve()
    source = args.sglang_source.resolve()
    wheel = args.mooncake_wheel.resolve()
    model = args.model_dir.resolve()
    if output.exists():
        raise ValueError(f"output must not already exist: {output}")
    if not source.is_dir() or not model.is_dir() or not wheel.is_file():
        raise ValueError("required source, wheel, or model input does not exist")

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    template = json.loads(args.request_template.read_text(encoding="utf-8"))
    require_request_contract(template)

    expected_model = spec.get("model", {}).get("files")
    actual_model = inventory(model)
    if not expected_model or actual_model["files"] != expected_model:
        expected = {item["path"]: item["sha256"] for item in expected_model or []}
        actual = {item["path"]: item["sha256"] for item in actual_model["files"]}
        raise ValueError(
            "model inventory mismatch: "
            f"missing={sorted(expected.keys() - actual.keys())}, "
            f"extra={sorted(actual.keys() - expected.keys())}, "
            f"changed={sorted(path for path in expected.keys() & actual.keys() if expected[path] != actual[path])}"
        )

    commit = subprocess.run(
        ["git", "-C", str(source), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if commit != spec["sglang"]["commit"]:
        raise ValueError(f"SGLang commit mismatch: expected {spec['sglang']['commit']}, got {commit}")
    if sha256_file(wheel) != spec["mooncake"]["wheel_sha256"]:
        raise ValueError("Mooncake wheel mismatch")

    wheel_name = spec["mooncake"]["wheel_filename"]
    expected_entries = {
        "sglang-source.tar",
        wheel_name,
        "model",
        "request-template.json",
        "input-bundle-spec.json",
        "verify-input-bundle.py",
        "bundle-manifest.json",
    }
    if set(spec.get("required_bundle_entries", [])) != expected_entries:
        raise ValueError("invalid first-C0 input bundle spec: required_bundle_entries mismatch")

    output.mkdir(parents=True)
    source_tar = output / "sglang-source.tar"
    with source_tar.open("wb") as handle:
        subprocess.run(
            ["git", "-C", str(source), "archive", "--format=tar", "HEAD"],
            check=True,
            stdout=handle,
        )
    shutil.copy2(wheel, output / wheel_name)
    shutil.copytree(model, output / "model")
    copies = {
        "request-template.json": args.request_template,
        "input-bundle-spec.json": args.spec,
        "verify-input-bundle.py": ROOT / "verify_input_bundle.py",
    }
    for name, source_file in copies.items():
        shutil.copy2(source_file, output / name)

    entries: dict[str, dict[str, object]] = {
        "sglang-source.tar": {"sha256": sha256_file(source_tar)},
        wheel_name: {"sha256": sha256_file(output / wheel_name)},
        "model": {"sha256": actual_model["sha256"]},
    }
    entries.update(
        {name: {"sha256": sha256_file(output / name)} for name in copies}
    )
    manifest = {
        "schema_version": 1,
        "entries": entries,
    }
    manifest_path = output / "bundle-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"BUNDLE_MANIFEST={sha256_file(manifest_path)}")
    print(f"BUNDLE_PATH={output}")


if __name__ == "__main__":
    main()
