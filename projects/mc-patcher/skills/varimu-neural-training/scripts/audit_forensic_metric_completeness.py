#!/usr/bin/env python3
"""Enumerate and gate every comparable Target/Current forensic statistic."""

from __future__ import annotations

import argparse
import csv
import fnmatch
import json
import math
from pathlib import Path
import statistics
import sys
from typing import Any


STRUCTURAL_METADATA = {
    "metadata.path", "metadata.bytes", "metadata.sha256", "metadata.sample_rate",
    "metadata.channels", "metadata.frames", "metadata.duration_s", "metadata.subtype",
}
REPORT_ONLY_PREFIXES = (
    "alignment.output_delay_samples",
    "alignment.fractional_delay_samples",
    "alignment.fractional_remainder_samples",
)


class AuditError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AuditError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise AuditError(f"JSON root must be an object: {path}")
    return data


def flatten(value: Any, prefix: str = "") -> dict[str, float]:
    result: dict[str, float] = {}
    if isinstance(value, bool) or value is None:
        return result
    if isinstance(value, (int, float)):
        result[prefix] = float(value)
        return result
    if isinstance(value, dict):
        for key in sorted(value):
            child = f"{prefix}.{key}" if prefix else str(key)
            result.update(flatten(value[key], child))
        return result
    if isinstance(value, list):
        for index, item in enumerate(value):
            result.update(flatten(item, f"{prefix}[{index}]"))
    return result


def family(path: str) -> str:
    rules = (
        ("current_vs_target", "direct_target_current"),
        ("local_scalar_residuals", "global_and_multiscale_residual"),
        ("global_gain_fitted", "global_and_multiscale_residual"),
        ("gain_activity", "gain_reduction_and_dynamics"),
        ("modulation", "gain_modulation"),
        ("lobe_transitions", "zero_crossing_lobes"),
        ("distortion_conditioned_by_gr", "gr_conditioned_nonlinear_residue"),
        ("spectral_bands", "coherence_qualified_transfer"),
        ("stereo", "stereo_image_and_correlation"),
        ("crest", "level_and_peak"),
        ("metadata", "level_and_peak"),
        ("alignment", "alignment"),
    )
    for token, name in rules:
        if token in path:
            return name
    return "other_comparable"


def is_structural(path: str) -> bool:
    return any(path == item or path.startswith(item + ".") for item in STRUCTURAL_METADATA)


def matching_rule(metric_id: str, rules: list[dict[str, Any]]) -> dict[str, Any] | None:
    matches = [rule for rule in rules if fnmatch.fnmatchcase(metric_id, str(rule.get("metric_pattern", "")))]
    if not matches:
        return None
    matches.sort(key=lambda rule: len(str(rule.get("metric_pattern", ""))), reverse=True)
    return matches[0]


def huber(value: float, delta: float = 1.0) -> float:
    absolute = abs(value)
    if absolute <= delta:
        return 0.5 * absolute * absolute
    return delta * (absolute - 0.5 * delta)


def audit(metrics: dict[str, Any], registry: dict[str, Any] | None) -> dict[str, Any]:
    try:
        target_root = metrics["comparisons_to_original"]["Target"]
        current_root = metrics["comparisons_to_original"]["Current"]
        direct_root = metrics["current_vs_target"]
    except KeyError as exc:
        raise AuditError(f"not an audio_render_forensics_v1 metrics file: missing {exc}") from exc
    target = flatten(target_root)
    current = flatten(current_root)
    target_keys = {key for key in target if not is_structural(key)}
    current_keys = {key for key in current if not is_structural(key)}
    common = sorted(target_keys & current_keys)
    missing_target = sorted(current_keys - target_keys)
    missing_current = sorted(target_keys - current_keys)

    rules: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []
    frozen = False
    if registry is not None:
        if registry.get("schema_version") != 1:
            raise AuditError("registry schema_version must be 1")
        frozen = registry.get("status") == "FROZEN"
        rules = registry.get("metric_floors") or []
        exclusions = registry.get("explicit_exclusions") or []
        if not isinstance(rules, list) or not isinstance(exclusions, list):
            raise AuditError("registry metric_floors and explicit_exclusions must be lists")

    records: list[dict[str, Any]] = []
    uncovered: list[str] = []
    critical_failures: list[str] = []
    normalized: list[float] = []
    for path in common:
        metric_id = f"comparisons_to_original.{path}"
        target_value = target[path]
        current_value = current[path]
        finite = math.isfinite(target_value) and math.isfinite(current_value)
        report_only = any(path.startswith(prefix) for prefix in REPORT_ONLY_PREFIXES)
        exclusion = matching_rule(metric_id, exclusions)
        status = "EXCLUDED" if exclusion else ("REPORT_ONLY" if report_only else "ACTIVE")
        record: dict[str, Any] = {
            "metric_id": metric_id,
            "family": family(path),
            "comparison": "current_statistic_to_target_statistic",
            "target_value": target_value,
            "current_value": current_value,
            "absolute_distance": abs(current_value - target_value) if finite else None,
            "status": status,
            "finite": finite,
        }
        rule = matching_rule(metric_id, rules)
        if status == "ACTIVE":
            if not finite:
                missing_current.append(metric_id + ":non_finite")
            elif frozen and rule is None:
                uncovered.append(metric_id)
            elif rule is not None:
                floor = rule.get("floor")
                if not isinstance(floor, (int, float)) or isinstance(floor, bool) or floor <= 0:
                    raise AuditError(f"invalid positive floor for {metric_id}")
                distance = abs(current_value - target_value) / float(floor)
                record["normalization_floor"] = float(floor)
                record["normalized_distance"] = distance
                record["weight"] = float(rule.get("weight", 1.0))
                record["critical"] = bool(rule.get("critical", False))
                cap = rule.get("max_normalized_distance")
                if cap is not None:
                    if not isinstance(cap, (int, float)) or isinstance(cap, bool) or cap < 0:
                        raise AuditError(f"invalid max_normalized_distance for {metric_id}")
                    record["max_normalized_distance"] = float(cap)
                    record["gate_pass"] = distance <= float(cap)
                    if record["critical"] and not record["gate_pass"]:
                        critical_failures.append(metric_id)
                normalized.append(distance * record["weight"])
        if exclusion:
            reason = exclusion.get("reason")
            if not isinstance(reason, str) or not reason.strip():
                raise AuditError(f"exclusion for {metric_id} has no reason")
            record["exclusion_reason"] = reason
        records.append(record)

    direct = flatten(direct_root)
    for path in sorted(direct):
        value = direct[path]
        metric_id = f"current_vs_target.{path}"
        desired = 1.0 if path.endswith("correlation") else 0.0
        finite = math.isfinite(value)
        record = {
            "metric_id": metric_id,
            "family": "direct_target_current",
            "comparison": "direct_current_to_target",
            "desired_value": desired,
            "current_value": value,
            "absolute_distance": abs(value - desired) if finite else None,
            "status": "ACTIVE",
            "finite": finite,
        }
        rule = matching_rule(metric_id, rules)
        exclusion = matching_rule(metric_id, exclusions)
        if exclusion:
            reason = exclusion.get("reason")
            if not isinstance(reason, str) or not reason.strip():
                raise AuditError(f"exclusion for {metric_id} has no reason")
            record["status"] = "EXCLUDED"
            record["exclusion_reason"] = reason
        elif not finite:
            missing_current.append(metric_id + ":non_finite")
        elif frozen and rule is None:
            uncovered.append(metric_id)
        elif rule is not None:
            floor = rule.get("floor")
            if not isinstance(floor, (int, float)) or isinstance(floor, bool) or floor <= 0:
                raise AuditError(f"invalid positive floor for {metric_id}")
            distance = abs(value - desired) / float(floor)
            record["normalization_floor"] = float(floor)
            record["normalized_distance"] = distance
            record["weight"] = float(rule.get("weight", 1.0))
            record["critical"] = bool(rule.get("critical", False))
            cap = rule.get("max_normalized_distance")
            if cap is not None:
                record["max_normalized_distance"] = float(cap)
                record["gate_pass"] = distance <= float(cap)
                if record["critical"] and not record["gate_pass"]:
                    critical_failures.append(metric_id)
            normalized.append(distance * record["weight"])
        records.append(record)

    missing = sorted(set(missing_target + missing_current))
    active_count = sum(record["status"] == "ACTIVE" for record in records)
    status = "CHARACTERIZED"
    if frozen:
        status = "PASS" if not missing and not uncovered and not critical_failures else "FAIL"
    sorted_norm = sorted(normalized, reverse=True)
    tail_count = max(1, math.ceil(0.05 * len(sorted_norm))) if sorted_norm else 0
    summary = {
        "registry_status": registry.get("status") if registry else "NOT_PROVIDED",
        "comparable_metric_count": len(records),
        "active_metric_count": active_count,
        "excluded_metric_count": sum(record["status"] == "EXCLUDED" for record in records),
        "report_only_metric_count": sum(record["status"] == "REPORT_ONLY" for record in records),
        "missing_comparable_metric_count": len(missing),
        "uncovered_active_metric_count": len(uncovered),
        "critical_gate_failure_count": len(critical_failures),
        "weighted_huber_mean": (
            statistics.fmean(huber(value) for value in normalized) if normalized else None
        ),
        "worst_5_percent_cvar": (
            statistics.fmean(sorted_norm[:tail_count]) if tail_count else None
        ),
    }
    return {
        "schema_version": 1,
        "kind": "varimu_forensic_metric_completeness_audit",
        "status": status,
        "summary": summary,
        "missing_metrics": missing,
        "uncovered_active_metrics": uncovered,
        "critical_gate_failures": critical_failures,
        "metrics": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("analysis_metrics", type=Path)
    parser.add_argument("--registry", type=Path)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path)
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()
    try:
        metrics = load_json(args.analysis_metrics.expanduser().resolve())
        registry = load_json(args.registry.expanduser().resolve()) if args.registry else None
        result = audit(metrics, registry)
        output = args.output_json.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        if args.output_csv:
            csv_path = args.output_csv.expanduser().resolve()
            csv_path.parent.mkdir(parents=True, exist_ok=True)
            fields = sorted({key for row in result["metrics"] for key in row})
            with csv_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows(result["metrics"])
        print(json.dumps({"status": result["status"], **result["summary"]}, ensure_ascii=False))
        if args.require_pass and result["status"] != "PASS":
            return 2
        return 0
    except (AuditError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
