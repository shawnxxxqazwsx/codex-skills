#!/usr/bin/env python3
"""Validate file-level annotations required to close a capture round."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
QA_STATUSES = {"ACCEPTED", "PILOT", "REJECTED", "SUPERSEDED"}
UNRESOLVED = {"", "PENDING", "UNKNOWN", "UNREVIEWED", "NOT_RUN"}
PERSISTENT_EXTENSIONS = {
    ".aif", ".aiff", ".caf", ".csv", ".flac", ".json", ".jsonl",
    ".npy", ".npz", ".onnx", ".pt", ".tsv", ".wav", ".wave",
}


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: Any, *, allow_empty: bool) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(nonempty(item) for item in value)
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolved_file(path_text: str, base_dir: Path) -> Path:
    path = Path(path_text).expanduser()
    if not path.is_absolute():
        path = base_dir / path
    return path.resolve()


def validate(
    data: dict[str, Any],
    manifest_path: Path,
    check_files: bool,
    inventory_roots: list[Path],
) -> list[str]:
    errors: list[str] = []
    base_dir = manifest_path.resolve().parent

    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    for key in ("round_id", "session_id", "completed_at_utc"):
        if not nonempty(data.get(key)):
            errors.append(f"field must be a non-empty string: {key}")
    if data.get("annotation_status") != "COMPLETE":
        errors.append("annotation_status must be COMPLETE before handoff")

    handoff = data.get("handoff")
    if not isinstance(handoff, dict):
        errors.append("handoff must be an object")
        handoff = {}
    for key in ("purpose", "physical_state", "route", "next_action"):
        if not nonempty(handoff.get(key)):
            errors.append(f"handoff.{key} must be a non-empty string")
    for key, allow_empty in (
        ("capture_order", False),
        ("anomalies", True),
        ("known_exclusions", True),
        ("reading_order", False),
    ):
        if not string_list(handoff.get(key), allow_empty=allow_empty):
            qualifier = "a list of strings" if allow_empty else "a non-empty list of strings"
            errors.append(f"handoff.{key} must be {qualifier}")
    gates = handoff.get("gates")
    if not isinstance(gates, dict) or not gates:
        errors.append("handoff.gates must be a non-empty object")
    else:
        for name, status in gates.items():
            if not nonempty(name) or not nonempty(status):
                errors.append("handoff.gates names and statuses must be non-empty strings")
            elif status.strip().upper() in UNRESOLVED:
                errors.append(f"handoff gate remains unresolved: {name}={status}")

    files = data.get("files")
    if not isinstance(files, list) or not files:
        errors.append("files must be a non-empty list")
        files = []

    listed_paths: set[Path] = set()
    for index, record in enumerate(files):
        prefix = f"files[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for key in (
            "path", "role", "capture_id", "condition_id", "provenance",
            "control_state_ref", "processing", "note",
        ):
            if not nonempty(record.get(key)):
                errors.append(f"{prefix}.{key} must be a non-empty string")

        path_text = record.get("path")
        path = resolved_file(path_text, base_dir) if nonempty(path_text) else None
        if path is not None:
            if path in listed_paths:
                errors.append(f"duplicate annotated path: {path}")
            listed_paths.add(path)

        digest = record.get("sha256")
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            errors.append(f"{prefix}.sha256 must be 64 lowercase hexadecimal characters")

        if not string_list(record.get("channel_layout"), allow_empty=True):
            errors.append(f"{prefix}.channel_layout must be a list of channel labels")
        if not string_list(record.get("use_for"), allow_empty=False):
            errors.append(f"{prefix}.use_for must be a non-empty list of strings")
        if not string_list(record.get("exclude_from"), allow_empty=True):
            errors.append(f"{prefix}.exclude_from must be a list of strings")

        qa_status = record.get("qa_status")
        if qa_status not in QA_STATUSES:
            errors.append(f"{prefix}.qa_status must be one of: {', '.join(sorted(QA_STATUSES))}")
        training_eligible = record.get("training_eligible")
        if not isinstance(training_eligible, bool):
            errors.append(f"{prefix}.training_eligible must be boolean")
        if qa_status in {"REJECTED", "SUPERSEDED"} and training_eligible is True:
            errors.append(f"{prefix} cannot be training eligible when {qa_status}")
        if qa_status in {"REJECTED", "SUPERSEDED"} and not record.get("exclude_from"):
            errors.append(f"{prefix}.exclude_from must explain rejected/superseded use")

        if check_files and path is not None:
            if not path.is_file():
                errors.append(f"annotated file does not exist: {path}")
            elif isinstance(digest, str) and SHA256_RE.fullmatch(digest):
                actual = sha256_file(path)
                if actual != digest:
                    errors.append(f"hash mismatch for {path}: expected {digest}, got {actual}")

    manifest_resolved = manifest_path.resolve()
    for root in inventory_roots:
        resolved_root = root.expanduser().resolve()
        if not resolved_root.is_dir():
            errors.append(f"inventory root is not a directory: {resolved_root}")
            continue
        for candidate in resolved_root.rglob("*"):
            if not candidate.is_file() or candidate.suffix.lower() not in PERSISTENT_EXTENSIONS:
                continue
            candidate = candidate.resolve()
            if candidate == manifest_resolved:
                continue
            if candidate not in listed_paths:
                errors.append(f"persistent round file lacks annotation: {candidate}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--check-files", action="store_true")
    parser.add_argument(
        "--inventory-root",
        action="append",
        default=[],
        type=Path,
        help="repeatable directory whose persistent data files must all be annotated",
    )
    args = parser.parse_args()

    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read manifest: {exc}", file=sys.stderr)
        return 2
    if not isinstance(data, dict):
        print("ERROR: manifest root must be a JSON object", file=sys.stderr)
        return 2

    errors = validate(data, args.manifest, args.check_files, args.inventory_root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
