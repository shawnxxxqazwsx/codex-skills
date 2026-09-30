#!/usr/bin/env python3
"""Validate an immutable Vari-Mu completed training folder."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA_RE = re.compile(r"^[0-9a-f]{40,64}$")
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")
ZERO_SHA256 = "0" * 64
REQUIRED_ROLES = {
    "annotation",
    "data_manifest",
    "model",
    "model_card",
    "training_config",
    "training_log",
    "training_ledger_receipt",
    "three_way_forensics",
    "metric_registry",
    "metric_completeness",
}
FORENSIC_REQUIRED_FILES = {
    "REPORT.md",
    "analysis_metrics.json",
    "window_metrics_20ms.csv",
    "worst_current_vs_target_windows.csv",
    "worst_current_windows.csv",
    "target_spectral_bands.csv",
    "current_spectral_bands.csv",
    "spectral_curves.csv",
    "target_distortion_by_gr.csv",
    "current_distortion_by_gr.csv",
    "target_largest_lobe_gain_jumps.csv",
    "current_largest_lobe_gain_jumps.csv",
    "excerpt_manifest.csv",
    "alignment_correlation.png",
    "envelope_and_gain_timeline.png",
    "local_residue_timeline.png",
    "coherence_and_residue_spectrum.png",
    "transfer_frequency_response.png",
    "gain_reduction_and_dynamics.png",
    "distortion_conditioned_by_gr.png",
}
IGNORED_NAMES = {".DS_Store", "completed-run-v1.json"}


class ValidationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read JSON {path}: {exc}") from exc
    require(isinstance(data, dict), f"JSON root must be an object: {path}")
    return data


def parse_utc(value: Any, label: str) -> datetime:
    require(isinstance(value, str) and value.endswith("Z"), f"{label} must end in Z")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationError(f"invalid {label}: {value!r}") from exc


def validate_sha(value: Any, label: str, *, git: bool = False) -> str:
    pattern = GIT_SHA_RE if git else SHA256_RE
    require(isinstance(value, str) and pattern.fullmatch(value) is not None,
            f"{label} has invalid digest")
    require(set(value) != {"0"}, f"{label} is still a placeholder")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_relative(value: Any, label: str) -> str:
    require(isinstance(value, str) and value, f"{label} is required")
    path = PurePosixPath(value)
    require(not path.is_absolute() and ".." not in path.parts, f"unsafe {label}: {value!r}")
    return path.as_posix()


def inventory_files(root: Path) -> set[str]:
    found: set[str] = set()
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValidationError(f"symlink is not permitted: {path}")
        if not path.is_file() or path.name in IGNORED_NAMES:
            continue
        found.add(path.relative_to(root).as_posix())
    return found


def validate_manifest(root: Path, data: dict[str, Any], *, check_files: bool) -> dict[str, Any]:
    require(data.get("schema_version") == 1, "schema_version must be 1")
    require(data.get("kind") == "varimu_completed_training_run", "invalid kind")
    require(data.get("status") == "COMPLETED", "status must be COMPLETED")
    for key in ("batch_id", "training_run_id", "training_objective_id"):
        require(isinstance(data.get(key), str) and SAFE_ID_RE.fullmatch(data[key]) is not None,
                f"unsafe or missing {key}")

    claim = data.get("claim")
    require(isinstance(claim, dict), "claim must be an object")
    require(isinstance(claim.get("machine_name"), str) and claim["machine_name"].strip(),
            "claim.machine_name is required")
    require(isinstance(claim.get("machine_id"), str)
            and SAFE_ID_RE.fullmatch(claim["machine_id"]) is not None,
            "claim.machine_id is invalid")
    claimed = parse_utc(claim.get("claimed_at_utc"), "claim.claimed_at_utc")
    validate_sha(claim.get("claim_sha256"), "claim.claim_sha256")
    started = parse_utc(data.get("started_at_utc"), "started_at_utc")
    completed = parse_utc(data.get("completed_at_utc"), "completed_at_utc")
    require(claimed <= started <= completed, "timestamps must satisfy claimed <= started <= completed")
    require(isinstance(data.get("operator"), str) and data["operator"].strip(), "operator is required")
    require(isinstance(data.get("claim_tier"), str) and data["claim_tier"].strip(), "claim_tier is required")

    dataset = data.get("dataset")
    require(isinstance(dataset, dict), "dataset must be an object")
    source_repo = dataset.get("source_release_repository")
    require(isinstance(source_repo, str) and "/" in source_repo,
            "dataset.source_release_repository is required")
    source_tag = dataset.get("source_release_tag")
    require(isinstance(source_tag, str) and SAFE_ID_RE.fullmatch(source_tag) is not None,
            "dataset.source_release_tag is invalid")
    require(
        dataset.get("source_release_url")
        == f"https://github.com/{source_repo}/releases/tag/{source_tag}",
        "dataset.source_release_url is not canonical",
    )
    validate_sha(dataset.get("metadata_code_commit"), "dataset.metadata_code_commit", git=True)
    for key in (
        "archive_manifest_sha256", "exact_allowlist_sha256",
        "split_manifest_sha256", "ready_ledger_sha256",
    ):
        validate_sha(dataset.get(key), f"dataset.{key}")

    implementation = data.get("implementation")
    require(isinstance(implementation, dict), "implementation must be an object")
    for key in ("repository", "model_family", "candidate_version"):
        require(isinstance(implementation.get(key), str) and implementation[key].strip(),
                f"implementation.{key} is required")
    validate_sha(implementation.get("git_commit"), "implementation.git_commit", git=True)
    validate_sha(implementation.get("environment_lock_sha256"),
                 "implementation.environment_lock_sha256")

    acceptance = data.get("acceptance")
    require(isinstance(acceptance, dict), "acceptance must be an object")
    require(acceptance.get("metric_registry_status") == "FROZEN",
            "metric_registry_status must be FROZEN")
    comparable = acceptance.get("comparable_metric_count")
    missing = acceptance.get("missing_comparable_metric_count")
    require(isinstance(comparable, int) and not isinstance(comparable, bool) and comparable > 0,
            "comparable_metric_count must be positive")
    require(missing == 0, "missing_comparable_metric_count must be zero")
    failures = acceptance.get("critical_gate_failures")
    require(isinstance(failures, list) and not failures, "critical_gate_failures must be empty")
    for key in (
        "three_way_forensics_status", "controlled_probes_status",
        "withheld_status", "listening_status",
    ):
        require(acceptance.get(key) == "PASS", f"acceptance.{key} must be PASS")
    require(acceptance.get("realtime_status") in {"PASS", "NOT_TESTED"},
            "realtime_status must be PASS or NOT_TESTED")

    limits = data.get("known_limits")
    require(isinstance(limits, list) and limits
            and all(isinstance(item, str) and item.strip() for item in limits),
            "known_limits must be a non-empty list")
    require(isinstance(data.get("reproduction_command"), str)
            and data["reproduction_command"].strip(), "reproduction_command is required")

    annotation_path = root / "ANNOTATION.md"
    require(annotation_path.is_file(), "ANNOTATION.md is required")
    annotation = annotation_path.read_text(encoding="utf-8")
    require(len(annotation.strip()) >= 500, "ANNOTATION.md is not detailed enough (minimum 500 characters)")
    for token in (claim["machine_name"], claim["machine_id"], data["training_run_id"]):
        require(token in annotation, f"ANNOTATION.md must contain {token!r}")

    for directory in ("data", "algorithm", "evaluation", "logs"):
        path = root / directory
        require(path.is_dir() and any(path.rglob("*")), f"required directory is empty: {directory}/")

    artifacts = data.get("artifacts")
    require(isinstance(artifacts, list) and artifacts, "artifacts must be non-empty")
    declared: set[str] = set()
    roles: set[str] = set()
    forensic_paths: set[str] = set()
    metric_completeness_paths: list[str] = []
    for index, record in enumerate(artifacts):
        require(isinstance(record, dict), f"artifacts[{index}] must be an object")
        relative = safe_relative(record.get("path"), f"artifacts[{index}].path")
        require(relative != "completed-run-v1.json", "root manifest must not inventory itself")
        require(relative not in declared, f"duplicate artifact path: {relative}")
        declared.add(relative)
        role = record.get("role")
        require(isinstance(role, str) and role.strip(), f"artifacts[{index}].role is required")
        roles.add(role)
        size = record.get("size")
        require(isinstance(size, int) and not isinstance(size, bool) and size >= 0,
                f"invalid artifact size: {relative}")
        validate_sha(record.get("sha256"), f"artifact SHA-256: {relative}")
        if role == "three_way_forensics":
            forensic_paths.add(relative)
        if role == "metric_completeness":
            metric_completeness_paths.append(relative)
        if check_files:
            path = root / relative
            require(path.is_file(), f"artifact is missing: {relative}")
            require(path.stat().st_size == size, f"artifact size mismatch: {relative}")
            require(sha256_file(path) == record["sha256"], f"artifact hash mismatch: {relative}")

    missing_roles = sorted(REQUIRED_ROLES - roles)
    require(not missing_roles, f"missing artifact roles: {', '.join(missing_roles)}")
    forensic_names = {PurePosixPath(path).name for path in forensic_paths}
    missing_forensics = sorted(FORENSIC_REQUIRED_FILES - forensic_names)
    require(not missing_forensics,
            f"incomplete three-way forensics: {', '.join(missing_forensics)}")
    require(len(metric_completeness_paths) == 1,
            "exactly one metric_completeness artifact is required")
    completeness = load_json(root / metric_completeness_paths[0])
    require(completeness.get("status") == "PASS", "metric completeness status must be PASS")
    summary = completeness.get("summary")
    require(isinstance(summary, dict), "metric completeness summary is missing")
    require(summary.get("comparable_metric_count") == comparable,
            "completed manifest comparable_metric_count disagrees with metric audit")
    require(summary.get("missing_comparable_metric_count") == 0,
            "metric audit has missing comparable metrics")
    require(summary.get("critical_gate_failure_count") == 0,
            "metric audit has critical gate failures")

    if check_files:
        actual = inventory_files(root)
        unlisted = sorted(actual - declared)
        missing = sorted(declared - actual)
        require(not unlisted, f"unlisted persistent files: {', '.join(unlisted[:20])}")
        require(not missing, f"declared files missing: {', '.join(missing[:20])}")

    return {
        "status": "VALID",
        "batch_id": data["batch_id"],
        "training_run_id": data["training_run_id"],
        "machine_name": claim["machine_name"],
        "machine_id": claim["machine_id"],
        "artifact_count": len(artifacts),
        "comparable_metric_count": comparable,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=Path)
    parser.add_argument("--check-files", action="store_true")
    args = parser.parse_args()
    try:
        root = args.run_directory.expanduser().resolve()
        require(root.is_dir(), f"run directory does not exist: {root}")
        manifest_path = root / "completed-run-v1.json"
        data = load_json(manifest_path)
        result = validate_manifest(root, data, check_files=args.check_files)
        result["manifest"] = str(manifest_path)
        result["manifest_sha256"] = sha256_file(manifest_path)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (ValidationError, OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
