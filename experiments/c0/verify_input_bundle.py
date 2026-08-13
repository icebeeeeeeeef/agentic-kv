#!/usr/bin/env python3
"""Verify first-C0 inputs against an external owner-reviewed manifest root."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


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


def reject(message: str) -> int:
    print(message, file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--expected-manifest-sha256", required=True)
    args = parser.parse_args()
    expected_root = args.expected_manifest_sha256
    if not re.fullmatch(r"[0-9a-f]{64}", expected_root):
        return reject("expected manifest SHA-256 must be exactly 64 lowercase hex characters")

    bundle = args.bundle.resolve()
    manifest_path = bundle / "bundle-manifest.json"
    if not manifest_path.is_file():
        return reject(f"missing bundle manifest: {manifest_path}")
    actual_root = sha256_file(manifest_path)
    if actual_root != expected_root:
        return reject(f"manifest SHA-256 mismatch: expected {expected_root}, got {actual_root}")

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        return reject(f"invalid manifest JSON after root verification: {error}")
    required_manifest_keys = {
        "schema_version",
        "entries",
    }
    if (
        not isinstance(manifest, dict)
        or set(manifest) != required_manifest_keys
        or manifest.get("schema_version") != 1
        or not isinstance(manifest.get("entries"), dict)
        or not manifest["entries"]
    ):
        return reject("invalid manifest schema or empty manifest entries")

    entries = manifest["entries"]
    if any(
        not isinstance(name, str)
        or Path(name).name != name
        or not isinstance(value, dict)
        or not re.fullmatch(r"[0-9a-f]{64}", str(value.get("sha256", "")))
        for name, value in entries.items()
    ):
        return reject("invalid manifest entries: names and checksums must be exact")
    spec_path = bundle / "input-bundle-spec.json"
    if "input-bundle-spec.json" not in entries or not spec_path.is_file():
        return reject("invalid manifest entries: input-bundle-spec.json is required")
    if (
        sha256_file(spec_path) != entries["input-bundle-spec.json"].get("sha256")
    ):
        return reject("checksum mismatch: input-bundle-spec.json")
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        return reject(f"invalid input bundle spec: {error}")

    required_entries = spec.get("required_bundle_entries", [])
    expected_entries = set(required_entries) - {"bundle-manifest.json"}
    if (
        spec.get("schema_version") != 1
        or not required_entries
        or len(required_entries) != len(set(required_entries))
        or set(entries) != expected_entries
    ):
        return reject(
            f"invalid manifest entries: expected {sorted(expected_entries)}, got {sorted(entries)}"
        )
    actual_top = {item.name for item in bundle.iterdir()}
    expected_top = expected_entries | {"bundle-manifest.json"}
    if actual_top - expected_top:
        return reject(f"unexpected top-level bundle entry: {sorted(actual_top - expected_top)}")
    if expected_top - actual_top:
        return reject(f"missing top-level bundle entry: {sorted(expected_top - actual_top)}")

    errors = []
    for name in sorted(entries):
        path = bundle / name
        expected = entries[name]
        if path.is_dir():
            actual = inventory(path)
            if (
                name != "model"
                or set(expected) != {"sha256"}
                or actual["sha256"] != expected["sha256"]
                or actual["files"] != spec["model"]["files"]
            ):
                errors.append(f"checksum or file inventory mismatch: {name}")
        elif not path.is_file() or set(expected) != {"sha256"} or sha256_file(path) != expected["sha256"]:
            errors.append(f"checksum mismatch: {name}")
    if errors:
        return reject("\n".join(errors))
    print(f"BUNDLE_VERIFIED={actual_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
