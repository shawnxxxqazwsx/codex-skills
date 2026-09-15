#!/usr/bin/env python3
"""Cross-check round file annotations against an exact dataset allowlist."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve(path_text: str, base: Path) -> Path:
    path = Path(path_text).expanduser()
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def is_below(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def load_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root is not an object: {path}")
    return data


def validate(
    annotation_path: Path,
    allowlist_path: Path,
    check_files: bool,
) -> list[str]:
    errors: list[str] = []
    annotation = load_object(annotation_path)
    allowlist = load_object(allowlist_path)
    annotation_base = annotation_path.resolve().parent
    allowlist_base = allowlist_path.resolve().parent

    if annotation.get("annotation_status") != "COMPLETE":
        errors.append("round annotation_status must be COMPLETE")
    if allowlist.get("status") != "EXACT_DATASET_ALLOWLIST":
        errors.append("allowlist status must be EXACT_DATASET_ALLOWLIST")
    if annotation.get("round_id") != allowlist.get("round_id"):
        errors.append("round_id differs between annotation and allowlist")

    annotation_rows: dict[Path, dict[str, Any]] = {}
    for index, row in enumerate(annotation.get("files", [])):
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            errors.append(f"annotation files[{index}] lacks a valid path")
            continue
        path = resolve(row["path"], annotation_base)
        if path in annotation_rows:
            errors.append(f"duplicate annotation path: {path}")
        annotation_rows[path] = row

    allowlist_rows: dict[Path, dict[str, Any]] = {}
    for index, row in enumerate(allowlist.get("accepted_files", [])):
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            errors.append(f"allowlist accepted_files[{index}] lacks a valid path")
            continue
        path = resolve(row["path"], allowlist_base)
        if path in allowlist_rows:
            errors.append(f"duplicate allowlist path: {path}")
        allowlist_rows[path] = row
        annotation_row = annotation_rows.get(path)
        if annotation_row is None:
            errors.append(f"allowlisted file lacks round annotation: {path}")
            continue

        expected_eligible = row.get("eligible_for_training")
        if not isinstance(expected_eligible, bool):
            errors.append(f"allowlist eligibility is not boolean: {path}")
            continue
        actual_eligible = annotation_row.get("training_eligible")
        if actual_eligible is not expected_eligible:
            errors.append(
                f"training eligibility mismatch for {path}: "
                f"allowlist={expected_eligible}, annotation={actual_eligible}"
            )

        expected_sha = row.get("sha256")
        annotation_sha = annotation_row.get("sha256")
        if expected_sha != annotation_sha:
            errors.append(f"SHA-256 differs between allowlist and annotation: {path}")
        if check_files:
            if not path.is_file():
                errors.append(f"allowlisted file does not exist: {path}")
            elif not isinstance(expected_sha, str) or sha256_file(path) != expected_sha:
                errors.append(f"allowlisted file hash mismatch: {path}")

        split = row.get("split")
        if split in {"validation", "withheld"} and expected_eligible:
            errors.append(f"{split} file cannot be training eligible: {path}")
        if expected_eligible:
            if annotation_row.get("qa_status") != "ACCEPTED":
                errors.append(f"training-eligible annotation is not ACCEPTED: {path}")
            uses = annotation_row.get("use_for")
            excludes = annotation_row.get("exclude_from")
            if not isinstance(uses, list) or not any("training" in str(item) for item in uses):
                errors.append(f"training-eligible annotation lacks an explicit training use: {path}")
            forbidden = {"model_training", "direct_model_training"}
            if not isinstance(excludes, list):
                errors.append(f"training-eligible annotation lacks exclude_from list: {path}")
            elif any(item in forbidden or str(item).startswith("direct_model_training") for item in excludes):
                errors.append(f"training-eligible annotation still excludes direct/model training: {path}")

    for path, row in annotation_rows.items():
        if row.get("training_eligible") is True:
            allowlist_row = allowlist_rows.get(path)
            if allowlist_row is None or allowlist_row.get("eligible_for_training") is not True:
                errors.append(f"annotation grants training eligibility outside exact allowlist: {path}")
        if row.get("qa_status") in {"REJECTED", "SUPERSEDED"} and row.get("training_eligible") is True:
            errors.append(f"rejected/superseded file is training eligible: {path}")

    policy = allowlist.get("training_policy")
    if not isinstance(policy, dict):
        errors.append("allowlist training_policy must be an object")
        policy = {}
    if policy.get("validation_and_withheld_are_never_training_eligible") is not True:
        errors.append("allowlist must forbid training on validation and withheld splits")

    primary_variant = policy.get("primary_target_variant")
    eligible_variants = {
        str(row.get("variant"))
        for row in allowlist_rows.values()
        if row.get("eligible_for_training") is True
    }
    if len(eligible_variants) > 1:
        if policy.get("comparison_variant_must_not_be_silently_mixed_with_primary") is not True:
            errors.append("multiple eligible variants require an explicit no-silent-mixing policy")
        for path, row in allowlist_rows.items():
            if row.get("eligible_for_training") is not True:
                continue
            annotation_row = annotation_rows.get(path, {})
            uses = [str(item) for item in annotation_row.get("use_for", [])]
            excludes = [str(item) for item in annotation_row.get("exclude_from", [])]
            variant = row.get("variant")
            if variant == primary_variant:
                if not any("primary" in item and "training" in item for item in uses):
                    errors.append(f"primary variant lacks primary-only training use: {path}")
                if not any("comparison" in item or "mixed" in item for item in excludes):
                    errors.append(f"primary variant lacks comparison/mixed-variant exclusion: {path}")
            else:
                if not any("comparison" in item and "training" in item for item in uses):
                    errors.append(f"comparison variant lacks comparison-only training use: {path}")
                if not any("primary" in item or "mixed" in item for item in excludes):
                    errors.append(f"comparison variant lacks primary/mixed-variant exclusion: {path}")

    for prefix in allowlist.get("excluded_prefixes", []):
        if not isinstance(prefix, str):
            errors.append("allowlist excluded_prefixes entries must be strings")
            continue
        excluded_root = resolve(prefix, allowlist_base)
        for path, row in annotation_rows.items():
            if is_below(path, excluded_root) and row.get("training_eligible") is True:
                errors.append(f"file below excluded prefix is training eligible: {path}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("annotation", type=Path)
    parser.add_argument("allowlist", type=Path)
    parser.add_argument("--check-files", action="store_true")
    args = parser.parse_args()
    try:
        errors = validate(args.annotation, args.allowlist, args.check_files)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: {args.annotation} <-> {args.allowlist}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
