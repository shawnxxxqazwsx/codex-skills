#!/usr/bin/env python3
"""Validate structural invariants in a compressor capture session manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import re
import sys
from typing import Any


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SPLIT_ROLES = {"pilot", "train", "validation", "test", "repeatability"}


def nested_value(data: dict[str, Any], path: str) -> Any:
    value: Any = data
    for key in path.split("."):
        if not isinstance(value, dict) or key not in value:
            raise KeyError(path)
        value = value[key]
    return value


def is_finite_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def is_nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate(data: dict[str, Any], base_dir: pathlib.Path, check_files: bool) -> list[str]:
    errors: list[str] = []
    required = [
        "schema_version",
        "capture_id",
        "condition_id",
        "thermal_cycle_id",
        "claim_scope.behavior",
        "unit.manufacturer",
        "unit.model",
        "unit.serial",
        "session.started_at_utc",
        "session.operator",
        "session.warmup_minutes",
        "session.sample_rate_hz",
        "session.adc_encoding",
        "session.clock_topology",
        "routing.balanced",
        "routing.channel_map.input_reference",
        "routing.channel_map.wet",
        "calibration.reference_dbu_rms",
        "calibration.reference_dbfs_rms",
        "calibration.loopback_capture",
        "calibration.bypass_capture",
        "stimulus.stimulus_id",
        "stimulus.family",
        "stimulus.digital_path",
        "stimulus.sha256",
        "control_state.mode",
        "control_state.stereo_coupling",
        "control_state.physical_controls",
        "history.preroll_seconds",
        "history.reset_method",
        "history.settling_criterion",
        "files.digital_input",
        "files.input_reference",
        "files.wet_output",
        "files.raw_files_immutable",
        "alignment.method",
        "alignment.integer_delay_samples",
        "alignment.fractional_delay_samples",
        "alignment.drift_ppm",
        "alignment.raw_files_unchanged",
        "split.role",
        "split.leakage_group",
        "split.stimulus_group",
        "split.setting_group",
        "quality.clipping_detected",
        "quality.dropouts_detected",
        "quality.polarity_verified",
        "quality.channel_map_verified",
        "quality.operator_review",
    ]

    values: dict[str, Any] = {}
    for path in required:
        try:
            values[path] = nested_value(data, path)
        except KeyError:
            errors.append(f"missing required field: {path}")

    for path in (
        "capture_id",
        "condition_id",
        "thermal_cycle_id",
        "claim_scope.behavior",
        "unit.manufacturer",
        "unit.model",
        "unit.serial",
        "session.started_at_utc",
        "session.operator",
        "session.adc_encoding",
        "session.clock_topology",
        "calibration.loopback_capture",
        "calibration.bypass_capture",
        "stimulus.stimulus_id",
        "stimulus.family",
        "stimulus.digital_path",
        "control_state.mode",
        "control_state.stereo_coupling",
        "history.reset_method",
        "history.settling_criterion",
        "files.digital_input",
        "files.input_reference",
        "files.wet_output",
        "alignment.method",
        "split.leakage_group",
        "split.stimulus_group",
        "split.setting_group",
        "quality.operator_review",
    ):
        if path in values and not is_nonempty(values[path]):
            errors.append(f"field must be a non-empty string: {path}")

    for path in (
        "session.warmup_minutes",
        "session.sample_rate_hz",
        "calibration.reference_dbu_rms",
        "calibration.reference_dbfs_rms",
        "history.preroll_seconds",
        "alignment.integer_delay_samples",
        "alignment.fractional_delay_samples",
        "alignment.drift_ppm",
    ):
        if path in values and not is_finite_number(values[path]):
            errors.append(f"field must be a finite number: {path}")

    if is_finite_number(values.get("session.sample_rate_hz")) and values["session.sample_rate_hz"] <= 0:
        errors.append("session.sample_rate_hz must be positive")
    if is_finite_number(values.get("session.warmup_minutes")) and values["session.warmup_minutes"] < 0:
        errors.append("session.warmup_minutes cannot be negative")
    if is_finite_number(values.get("history.preroll_seconds")) and values["history.preroll_seconds"] < 0:
        errors.append("history.preroll_seconds cannot be negative")
    if is_finite_number(values.get("calibration.reference_dbfs_rms")) and values["calibration.reference_dbfs_rms"] > 0:
        errors.append("calibration.reference_dbfs_rms cannot exceed 0 dBFS")

    if values.get("schema_version") != 1:
        errors.append("schema_version must be 1")

    stimulus_hash = values.get("stimulus.sha256")
    if isinstance(stimulus_hash, str) and not SHA256_RE.fullmatch(stimulus_hash):
        errors.append("stimulus.sha256 must be 64 lowercase hexadecimal characters")

    split_role = values.get("split.role")
    if split_role not in SPLIT_ROLES:
        errors.append(f"split.role must be one of: {', '.join(sorted(SPLIT_ROLES))}")

    for path in ("routing.channel_map.input_reference", "routing.channel_map.wet"):
        value = values.get(path)
        if not isinstance(value, list) or not value or not all(is_nonempty(item) for item in value):
            errors.append(f"field must be a non-empty list of channel labels: {path}")

    ref_channels = values.get("routing.channel_map.input_reference")
    wet_channels = values.get("routing.channel_map.wet")
    if isinstance(ref_channels, list) and isinstance(wet_channels, list) and len(ref_channels) != len(wet_channels):
        errors.append("input-reference and wet channel counts must match")

    for path in (
        "routing.balanced",
        "files.raw_files_immutable",
        "alignment.raw_files_unchanged",
        "quality.clipping_detected",
        "quality.dropouts_detected",
        "quality.polarity_verified",
        "quality.channel_map_verified",
    ):
        if path in values and not isinstance(values[path], bool):
            errors.append(f"field must be boolean: {path}")

    if values.get("files.raw_files_immutable") is False:
        errors.append("files.raw_files_immutable must be true")
    if values.get("alignment.raw_files_unchanged") is False:
        errors.append("alignment.raw_files_unchanged must be true")
    if values.get("quality.clipping_detected") is True:
        errors.append("quality.clipping_detected must be false for acceptance")
    if values.get("quality.dropouts_detected") is True:
        errors.append("quality.dropouts_detected must be false for acceptance")

    controls = values.get("control_state.physical_controls")
    if not isinstance(controls, dict):
        errors.append("control_state.physical_controls must be an object")

    if check_files:
        for path in ("files.digital_input", "files.input_reference", "files.wet_output"):
            candidate = values.get(path)
            if is_nonempty(candidate):
                file_path = pathlib.Path(candidate)
                if not file_path.is_absolute():
                    file_path = base_dir / file_path
                if not file_path.is_file():
                    errors.append(f"referenced file does not exist: {path}={file_path}")

        stimulus_path = values.get("stimulus.digital_path")
        if is_nonempty(stimulus_path) and isinstance(stimulus_hash, str) and SHA256_RE.fullmatch(stimulus_hash):
            file_path = pathlib.Path(stimulus_path)
            if not file_path.is_absolute():
                file_path = base_dir / file_path
            if file_path.is_file():
                actual_hash = sha256_file(file_path)
                if actual_hash != stimulus_hash:
                    errors.append(
                        f"stimulus hash mismatch: expected {stimulus_hash}, got {actual_hash}"
                    )
            else:
                errors.append(f"stimulus.digital_path does not exist: {file_path}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=pathlib.Path)
    parser.add_argument(
        "--check-files",
        action="store_true",
        help="also require referenced audio files and verify the stimulus hash",
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

    errors = validate(data, args.manifest.resolve().parent, args.check_files)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
