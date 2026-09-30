#!/usr/bin/env python3
"""Validate a reviewed, hash-bound Pigora inference engineering evaluation.

This validator is deliberately read-only and standard-library-only.  It judges
only numeric magnitude agreement with a frozen inference target.  It does not
adjudicate public fit, product selection, deployment, safety, or hosted use.
"""

from __future__ import annotations

import argparse
import csv
from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from typing import Any, Iterable


SCHEMA_VERSION = "pigora-inference-validation-v1"
CLAIM_BOUNDARY = "inference-derived/source-informed approximation"
BASELINE_RATE = 48000
BASE_GATE = Decimal("0.2")
HIGH_GATE = Decimal("0.5")
BASE_GATE_KIND = "inference-engineering-0.2"
HIGH_GATE_KIND = "sample-rate-engineering-0.5"
COVERAGE = "complete-with-explicit-nyquist-ineligibility"
NOT_APPLICABLE = "not-applicable"

TARGET_HEADER = [
    "row_id",
    "identity_id",
    "control_state_id",
    "control_state_json",
    "point_id",
    "frequency_hz",
    "target_magnitude_db",
    "target_provenance",
]
EVALUATION_HEADER = TARGET_HEADER + [
    "sample_rate_hz",
    "predicted_magnitude_db",
    "eligibility",
    "ineligibility_reason",
]
EXCLUSION_HEADER = [
    "identity_id",
    "exclusion_scope",
    "exclusion_reason",
    "product_use_state",
    "public_fit_state",
    "evidence_policy_state",
    "engineering_decision_id",
]
PUBLIC_STATE_HEADER = [
    "identity_id",
    "public_fit_state",
    "evidence_policy_state",
]

MANIFEST_KEYS = {
    "schema_version",
    "contract_kind",
    "claim_boundary",
    "review",
    "scope",
    "candidate",
    "target",
    "exclusions",
    "public_state_snapshot",
    "public_state_current",
    "rates",
}
REVIEW_KEYS = {
    "author_id",
    "reviewer_id",
    "review_status",
    "review_decision_id",
}
SCOPE_KEYS = {"in_scope_identity_ids", "excluded_identity_ids"}
FILE_KEYS = {"path", "sha256"}
CANDIDATE_KEYS = {
    "candidate_id",
    "candidate_artifact",
    "response_path_id",
    "response_path_artifact",
}
TARGET_KEYS = {"path", "sha256", "target_grid_hash"}
RATE_KEYS = {
    "sample_rate_hz",
    "evaluation",
    "declared_nyquist_hz",
    "condition_id",
    "control_state_coverage",
    "engineering_gate_kind",
    "engineering_gate_db",
    "engineering_decision_id",
    "baseline_engineering_decision_id",
    "target_grid_hash",
    "candidate_id",
    "response_path_id",
}
PROVENANCE = {
    "measured",
    "image-digitized",
    "inference-donor",
    "human-supplemented-gain",
    "human-supplemented-frequency",
    "human-supplemented-curve",
}
PUBLIC_FIT_STATES = {
    "public-fit passed",
    "public-fit partial",
    "public-fit failed/withheld",
    "not publicly specified",
}
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")


class ValidationError(Exception):
    pass


def _duplicate_rejecting_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle, object_pairs_hook=_duplicate_rejecting_object)
    except ValidationError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read JSON {path}: {exc}") from exc


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as exc:
        raise ValidationError(f"cannot hash {path}: {exc}") from exc
    return digest.hexdigest()


def _require_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise ValidationError(f"{label} must be a lowercase 64-character SHA-256")
    return value


def _require_exact_keys(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{label} must be an object")
    actual = set(value)
    if actual != keys:
        missing = sorted(keys - actual)
        extra = sorted(actual - keys)
        raise ValidationError(f"{label} fields mismatch: missing={missing} extra={extra}")
    return value


def _require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValidationError(f"{label} must be a non-empty trimmed string")
    return value


def _decimal(value: Any, label: str) -> Decimal:
    if isinstance(value, bool):
        raise ValidationError(f"{label} must be finite numeric data")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValidationError(f"{label} must be finite numeric data") from exc
    if not number.is_finite():
        raise ValidationError(f"{label} must be finite numeric data")
    return number


def _integer(value: Any, label: str) -> int:
    number = _decimal(value, label)
    if number != number.to_integral_value():
        raise ValidationError(f"{label} must be an integer")
    result = int(number)
    if result <= 0:
        raise ValidationError(f"{label} must be positive")
    return result


def _canonical_decimal(number: Decimal) -> str:
    if number == 0:
        return "0"
    rendered = format(number, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered


def _canonical_state(value: str, label: str) -> str:
    def reject_constant(constant: str) -> None:
        raise ValidationError(f"{label} contains non-finite JSON number {constant}")

    def reject_nonfinite(item: Any) -> None:
        if isinstance(item, float) and not math.isfinite(item):
            raise ValidationError(f"{label} contains a non-finite or overflowing JSON number")
        if isinstance(item, dict):
            for nested in item.values():
                reject_nonfinite(nested)
        elif isinstance(item, list):
            for nested in item:
                reject_nonfinite(nested)

    try:
        parsed = json.loads(
            value,
            object_pairs_hook=_duplicate_rejecting_object,
            parse_constant=reject_constant,
        )
    except ValidationError:
        raise
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{label} must be canonical JSON") from exc
    if not isinstance(parsed, dict):
        raise ValidationError(f"{label} must encode a JSON object")
    reject_nonfinite(parsed)
    canonical = json.dumps(
        parsed,
        allow_nan=False,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    if value != canonical:
        raise ValidationError(f"{label} is not canonical JSON; expected {canonical}")
    return canonical


def _resolve_file(
    manifest_dir: Path,
    spec: Any,
    label: str,
    bound_files: list[tuple[Path, str, str]] | None = None,
) -> Path:
    spec = _require_exact_keys(spec, FILE_KEYS, label)
    raw_path = _require_text(spec["path"], f"{label}.path")
    expected = _require_sha256(spec["sha256"], f"{label}.sha256")
    path = Path(raw_path)
    if not path.is_absolute():
        path = manifest_dir / path
    path = path.resolve()
    if not path.is_file():
        raise ValidationError(f"{label}.path is not a file: {path}")
    actual = _sha256(path)
    if actual != expected:
        raise ValidationError(f"{label} SHA-256 mismatch: expected {expected}, got {actual}")
    if bound_files is not None:
        bound_files.append((path, expected, label))
    return path


def _verify_bound_files_unchanged(bound_files: list[tuple[Path, str, str]]) -> None:
    for path, expected, label in bound_files:
        actual = _sha256(path)
        if actual != expected:
            raise ValidationError(
                f"{label} changed during validation: expected {expected}, got {actual}"
            )


def _read_csv(path: Path, header: list[str], label: str) -> list[dict[str, str]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != header:
                raise ValidationError(
                    f"{label} header mismatch: expected {header}, got {reader.fieldnames}"
                )
            rows = list(reader)
    except ValidationError:
        raise
    except (OSError, UnicodeError, csv.Error) as exc:
        raise ValidationError(f"cannot read {label} CSV {path}: {exc}") from exc
    for index, row in enumerate(rows, start=2):
        if None in row:
            raise ValidationError(f"{label} row {index} has extra CSV fields")
        missing = [field for field, value in row.items() if value is None]
        if missing:
            raise ValidationError(f"{label} row {index} has missing CSV fields: {missing}")
    return rows


def _nonempty_row_fields(row: dict[str, str], fields: Iterable[str], label: str) -> None:
    for field in fields:
        value = row[field]
        if not value or value != value.strip():
            raise ValidationError(f"{label}.{field} must be a non-empty trimmed string")


def _target_record(row: dict[str, str], index: int) -> dict[str, Any]:
    label = f"target row {index}"
    _nonempty_row_fields(
        row,
        [
            "row_id",
            "identity_id",
            "control_state_id",
            "control_state_json",
            "point_id",
            "frequency_hz",
            "target_magnitude_db",
            "target_provenance",
        ],
        label,
    )
    frequency = _decimal(row["frequency_hz"], f"{label}.frequency_hz")
    if frequency <= 0:
        raise ValidationError(f"{label}.frequency_hz must be positive")
    target = _decimal(row["target_magnitude_db"], f"{label}.target_magnitude_db")
    provenance = row["target_provenance"]
    if provenance not in PROVENANCE:
        raise ValidationError(f"{label}.target_provenance is invalid: {provenance}")
    state = _canonical_state(row["control_state_json"], f"{label}.control_state_json")
    return {
        "row_id": row["row_id"],
        "identity_id": row["identity_id"],
        "control_state_id": row["control_state_id"],
        "control_state_json": state,
        "point_id": row["point_id"],
        "frequency_hz": frequency,
        "target_magnitude_db": target,
        "target_provenance": provenance,
    }


def _canonical_target_row(row: dict[str, Any]) -> str:
    values = {
        "control_state_id": row["control_state_id"],
        "control_state_json": row["control_state_json"],
        "frequency_hz": _canonical_decimal(row["frequency_hz"]),
        "identity_id": row["identity_id"],
        "point_id": row["point_id"],
        "row_id": row["row_id"],
        "target_magnitude_db": _canonical_decimal(row["target_magnitude_db"]),
        "target_provenance": row["target_provenance"],
    }
    return json.dumps(values, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _load_target(path: Path) -> tuple[list[dict[str, Any]], str]:
    raw_rows = _read_csv(path, TARGET_HEADER, "target")
    if not raw_rows:
        raise ValidationError("target must contain at least one row")
    rows = [_target_record(row, index) for index, row in enumerate(raw_rows, start=2)]
    row_ids: set[str] = set()
    state_points: set[tuple[str, str, str]] = set()
    states: dict[tuple[str, str], str] = {}
    for row in rows:
        if row["row_id"] in row_ids:
            raise ValidationError(f"duplicate target row_id: {row['row_id']}")
        row_ids.add(row["row_id"])
        key = (row["identity_id"], row["control_state_id"], row["point_id"])
        if key in state_points:
            raise ValidationError(f"duplicate target identity/state/point: {key}")
        state_points.add(key)
        state_key = (row["identity_id"], row["control_state_id"])
        prior_state = states.get(state_key)
        if prior_state is not None and prior_state != row["control_state_json"]:
            raise ValidationError(
                "target identity/control_state_id maps to conflicting control_state_json: "
                f"{state_key}"
            )
        states[state_key] = row["control_state_json"]
    canonical = "\n".join(_canonical_target_row(row) for row in rows) + "\n"
    grid_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return rows, grid_hash


def _load_public_states(path: Path, label: str) -> dict[str, tuple[str, str]]:
    result: dict[str, tuple[str, str]] = {}
    for index, row in enumerate(_read_csv(path, PUBLIC_STATE_HEADER, label), start=2):
        _nonempty_row_fields(row, PUBLIC_STATE_HEADER, f"{label} row {index}")
        identity = row["identity_id"]
        if identity in result:
            raise ValidationError(f"duplicate {label} identity_id: {identity}")
        if row["public_fit_state"] not in PUBLIC_FIT_STATES:
            raise ValidationError(
                f"{label} row {index}.public_fit_state is invalid: {row['public_fit_state']}"
            )
        result[identity] = (row["public_fit_state"], row["evidence_policy_state"])
    return result


def _load_exclusions(
    path: Path, snapshot: dict[str, tuple[str, str]]
) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    decision_ids: set[str] = set()
    for index, row in enumerate(_read_csv(path, EXCLUSION_HEADER, "exclusions"), start=2):
        _nonempty_row_fields(row, EXCLUSION_HEADER, f"exclusions row {index}")
        identity = row["identity_id"]
        if identity in result:
            raise ValidationError(f"duplicate excluded identity_id: {identity}")
        if row["product_use_state"] != "not-product-selectable-inference":
            raise ValidationError(
                f"excluded identity {identity} must use product_use_state "
                "not-product-selectable-inference"
            )
        if identity not in snapshot:
            raise ValidationError(f"excluded identity absent from public snapshot: {identity}")
        frozen_public, frozen_policy = snapshot[identity]
        if (row["public_fit_state"], row["evidence_policy_state"]) != (
            frozen_public,
            frozen_policy,
        ):
            raise ValidationError(f"excluded identity public/evidence state changed: {identity}")
        decision = _require_inference_decision_id(
            row["engineering_decision_id"], f"exclusion {identity}"
        )
        if decision in decision_ids:
            raise ValidationError(f"duplicate exclusion engineering decision ID: {decision}")
        decision_ids.add(decision)
        result[identity] = row
    return result


def _require_inference_decision_id(value: Any, label: str) -> str:
    value = _require_text(value, f"{label} decision ID")
    lowered = value.casefold()
    if (
        not lowered.startswith("inference-")
        or "public" in lowered
        or "fallback" in lowered
    ):
        raise ValidationError(
            f"{label} decision ID must use the inference- prefix and contain no "
            f"public/fallback keyword: {value}"
        )
    return value


def _identity_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise ValidationError(f"{label} must be an array")
    result = [_require_text(item, f"{label} item") for item in value]
    if len(result) != len(set(result)):
        raise ValidationError(f"{label} contains duplicates")
    if result != sorted(result):
        raise ValidationError(f"{label} must be sorted")
    return result


def _verify_target_match(target: dict[str, Any], evaluation: dict[str, str], label: str) -> None:
    for field in (
        "row_id",
        "identity_id",
        "control_state_id",
        "point_id",
        "target_provenance",
    ):
        if evaluation[field] != target[field]:
            raise ValidationError(f"{label}.{field} does not match frozen target")
    state = _canonical_state(evaluation["control_state_json"], f"{label}.control_state_json")
    if state != target["control_state_json"]:
        raise ValidationError(f"{label}.control_state_json does not match frozen target")
    frequency = _decimal(evaluation["frequency_hz"], f"{label}.frequency_hz")
    magnitude = _decimal(evaluation["target_magnitude_db"], f"{label}.target_magnitude_db")
    if frequency != target["frequency_hz"]:
        raise ValidationError(f"{label}.frequency_hz does not match frozen target")
    if magnitude != target["target_magnitude_db"]:
        raise ValidationError(f"{label}.target_magnitude_db does not match frozen target")


def _validate_evaluation(
    path: Path,
    targets: list[dict[str, Any]],
    sample_rate: int,
    nyquist: Decimal,
    gate: Decimal,
) -> dict[str, Any]:
    raw_rows = _read_csv(path, EVALUATION_HEADER, f"evaluation {sample_rate}")
    if len(raw_rows) != len(targets):
        raise ValidationError(
            f"evaluation {sample_rate} row count mismatch: expected {len(targets)}, got {len(raw_rows)}"
        )
    seen: set[str] = set()
    worst_error = Decimal("-1")
    worst_row = ""
    eligible_count = 0
    ineligible_count = 0
    for offset, (target, row) in enumerate(zip(targets, raw_rows), start=2):
        label = f"evaluation {sample_rate} row {offset}"
        if row["row_id"] in seen:
            raise ValidationError(f"duplicate evaluation {sample_rate} row_id: {row['row_id']}")
        seen.add(row["row_id"])
        _verify_target_match(target, row, label)
        row_rate = _integer(row["sample_rate_hz"], f"{label}.sample_rate_hz")
        if row_rate != sample_rate:
            raise ValidationError(f"{label}.sample_rate_hz does not match manifest rate")
        should_be_eligible = target["frequency_hz"] < nyquist
        if should_be_eligible:
            if row["eligibility"] != "eligible":
                raise ValidationError(
                    f"{label} silently excludes a below-Nyquist target; expected eligible"
                )
            if row["ineligibility_reason"]:
                raise ValidationError(f"{label} eligible row has an ineligibility reason")
            predicted = _decimal(row["predicted_magnitude_db"], f"{label}.predicted_magnitude_db")
            error = abs(predicted - target["target_magnitude_db"])
            eligible_count += 1
            if error > worst_error:
                worst_error = error
                worst_row = target["row_id"]
            if error > gate:
                raise ValidationError(
                    f"rate {sample_rate} numeric gate failed at {target['row_id']}: "
                    f"error={_canonical_decimal(error)} gate={_canonical_decimal(gate)}"
                )
        else:
            if row["eligibility"] != "ineligible":
                raise ValidationError(
                    f"{label} is at/above declared Nyquist and must be explicitly ineligible"
                )
            if not row["ineligibility_reason"].strip():
                raise ValidationError(f"{label} ineligible row requires an explicit reason")
            if row["predicted_magnitude_db"]:
                raise ValidationError(f"{label} ineligible row must not contain a prediction")
            ineligible_count += 1
    if eligible_count == 0:
        raise ValidationError(f"evaluation {sample_rate} contains no eligible rows")
    return {
        "sample_rate_hz": sample_rate,
        "eligible_row_count": eligible_count,
        "nyquist_ineligible_row_count": ineligible_count,
        "worst_error_db": _canonical_decimal(worst_error),
        "worst_row_id": worst_row,
        "gate_db": _canonical_decimal(gate),
    }


def validate(manifest_path: Path, external_manifest_sha256: str) -> dict[str, Any]:
    expected_manifest_hash = _require_sha256(
        external_manifest_sha256, "--manifest-sha256"
    )
    manifest_path = manifest_path.resolve()
    actual_manifest_hash = _sha256(manifest_path)
    if actual_manifest_hash != expected_manifest_hash:
        raise ValidationError(
            "reviewed manifest SHA-256 mismatch: "
            f"expected {expected_manifest_hash}, got {actual_manifest_hash}"
        )
    bound_files = [(manifest_path, expected_manifest_hash, "reviewed manifest")]
    manifest = _require_exact_keys(_load_json(manifest_path), MANIFEST_KEYS, "manifest")
    if manifest["schema_version"] != SCHEMA_VERSION:
        raise ValidationError(f"manifest.schema_version must be {SCHEMA_VERSION}")
    contract_kind = manifest["contract_kind"]
    if contract_kind not in {
        "sparse-grid-completion",
        "donor-curve-inference-only",
    }:
        raise ValidationError("manifest.contract_kind is invalid")
    if manifest["claim_boundary"] != CLAIM_BOUNDARY:
        raise ValidationError(f"manifest.claim_boundary must be {CLAIM_BOUNDARY}")

    review = _require_exact_keys(manifest["review"], REVIEW_KEYS, "manifest.review")
    author = _require_text(review["author_id"], "manifest.review.author_id")
    reviewer = _require_text(review["reviewer_id"], "manifest.review.reviewer_id")
    if author == reviewer:
        raise ValidationError("manifest review must be non-author")
    if review["review_status"] != "reviewed":
        raise ValidationError("manifest.review.review_status must be reviewed")
    _require_inference_decision_id(
        review["review_decision_id"], "manifest.review"
    )

    scope = _require_exact_keys(manifest["scope"], SCOPE_KEYS, "manifest.scope")
    in_scope = _identity_list(scope["in_scope_identity_ids"], "in-scope identities")
    excluded = _identity_list(scope["excluded_identity_ids"], "excluded identities")
    if not in_scope:
        raise ValidationError("manifest scope must contain at least one in-scope identity")
    overlap = set(in_scope) & set(excluded)
    if overlap:
        raise ValidationError(f"in-scope and excluded identities overlap: {sorted(overlap)}")

    manifest_dir = manifest_path.parent
    candidate = _require_exact_keys(manifest["candidate"], CANDIDATE_KEYS, "manifest.candidate")
    candidate_id = _require_text(candidate["candidate_id"], "manifest.candidate.candidate_id")
    response_path_id = _require_text(
        candidate["response_path_id"], "manifest.candidate.response_path_id"
    )
    _resolve_file(
        manifest_dir,
        candidate["candidate_artifact"],
        "candidate artifact",
        bound_files,
    )
    _resolve_file(
        manifest_dir,
        candidate["response_path_artifact"],
        "response-path artifact",
        bound_files,
    )

    target_spec = _require_exact_keys(manifest["target"], TARGET_KEYS, "manifest.target")
    target_path = _resolve_file(
        manifest_dir,
        {"path": target_spec["path"], "sha256": target_spec["sha256"]},
        "target",
        bound_files,
    )
    expected_grid_hash = _require_sha256(
        target_spec["target_grid_hash"], "manifest.target.target_grid_hash"
    )
    targets, actual_grid_hash = _load_target(target_path)
    if actual_grid_hash != expected_grid_hash:
        raise ValidationError(
            f"target grid hash mismatch: expected {expected_grid_hash}, got {actual_grid_hash}"
        )
    target_provenances = {row["target_provenance"] for row in targets}
    generated_provenances = {
        "human-supplemented-gain",
        "human-supplemented-frequency",
        "human-supplemented-curve",
    }
    if contract_kind == "donor-curve-inference-only":
        invalid = target_provenances - ({"inference-donor"} | generated_provenances)
        if invalid:
            raise ValidationError(
                "donor-curve-inference-only target has forbidden provenance: "
                f"{sorted(invalid)}"
            )
    else:
        if "inference-donor" in target_provenances:
            raise ValidationError("sparse-grid-completion target forbids inference-donor rows")
        if not target_provenances & {"measured", "image-digitized"}:
            raise ValidationError(
                "sparse-grid-completion target requires at least one measured or "
                "image-digitized accepted anchor"
            )
    target_identities = {row["identity_id"] for row in targets}
    if target_identities != set(in_scope):
        raise ValidationError(
            "target identities do not exactly cover in-scope identities: "
            f"target={sorted(target_identities)} scope={in_scope}"
        )
    if target_identities & set(excluded):
        raise ValidationError("excluded identity has inference target rows")

    snapshot_path = _resolve_file(
        manifest_dir,
        manifest["public_state_snapshot"],
        "public-state snapshot",
        bound_files,
    )
    current_path = _resolve_file(
        manifest_dir,
        manifest["public_state_current"],
        "current public state",
        bound_files,
    )
    snapshot = _load_public_states(snapshot_path, "public-state snapshot")
    current = _load_public_states(current_path, "current public state")
    expected_public_identities = set(in_scope) | set(excluded)
    if set(snapshot) != expected_public_identities:
        raise ValidationError("public-state snapshot does not exactly cover declared scope")
    if current != snapshot:
        raise ValidationError("public/evidence states changed from frozen snapshot")

    exclusion_path = _resolve_file(
        manifest_dir, manifest["exclusions"], "exclusions", bound_files
    )
    exclusion_rows = _load_exclusions(exclusion_path, snapshot)
    if set(exclusion_rows) != set(excluded):
        raise ValidationError("exclusion ledger does not exactly cover excluded identities")

    rates_value = manifest["rates"]
    if not isinstance(rates_value, list) or not rates_value:
        raise ValidationError("manifest.rates must be a non-empty array")
    parsed_rates: list[tuple[int, dict[str, Any], Path, Decimal, Decimal]] = []
    rate_numbers: set[int] = set()
    decision_ids: set[str] = set()
    baseline_decision: str | None = None
    for index, raw_rate in enumerate(rates_value):
        label = f"manifest.rates[{index}]"
        rate = _require_exact_keys(raw_rate, RATE_KEYS, label)
        sample_rate = _integer(rate["sample_rate_hz"], f"{label}.sample_rate_hz")
        if sample_rate in rate_numbers:
            raise ValidationError(f"duplicate sample rate: {sample_rate}")
        rate_numbers.add(sample_rate)
        nyquist = _decimal(rate["declared_nyquist_hz"], f"{label}.declared_nyquist_hz")
        if nyquist != Decimal(sample_rate) / 2:
            raise ValidationError(f"{label}.declared_nyquist_hz must equal sample_rate_hz / 2")
        _require_text(rate["condition_id"], f"{label}.condition_id")
        if rate["control_state_coverage"] != COVERAGE:
            raise ValidationError(f"{label}.control_state_coverage must be {COVERAGE}")
        if rate["target_grid_hash"] != expected_grid_hash:
            raise ValidationError(f"{label}.target_grid_hash does not match frozen target")
        if rate["candidate_id"] != candidate_id:
            raise ValidationError(f"{label}.candidate_id does not match candidate")
        if rate["response_path_id"] != response_path_id:
            raise ValidationError(f"{label}.response_path_id does not match response path")
        decision = _require_inference_decision_id(
            rate["engineering_decision_id"], label
        )
        if decision in decision_ids:
            raise ValidationError(f"duplicate engineering decision ID: {decision}")
        decision_ids.add(decision)
        gate = _decimal(rate["engineering_gate_db"], f"{label}.engineering_gate_db")
        if sample_rate > BASELINE_RATE:
            gate_pair = (rate["engineering_gate_kind"], gate)
            if gate_pair not in {
                (BASE_GATE_KIND, BASE_GATE),
                (HIGH_GATE_KIND, HIGH_GATE),
            }:
                raise ValidationError(
                    f"{label} high rate must use {BASE_GATE_KIND} with 0.2 dB "
                    f"or {HIGH_GATE_KIND} with 0.5 dB"
                )
        else:
            if rate["engineering_gate_kind"] != BASE_GATE_KIND or gate != BASE_GATE:
                raise ValidationError(
                    f"{label} rate <= 48000 must use {BASE_GATE_KIND} with 0.2 dB"
                )
            if rate["baseline_engineering_decision_id"] != NOT_APPLICABLE:
                raise ValidationError(
                    f"{label}.baseline_engineering_decision_id must be {NOT_APPLICABLE}"
                )
        evaluation_path = _resolve_file(
            manifest_dir, rate["evaluation"], f"{label}.evaluation", bound_files
        )
        parsed_rates.append((sample_rate, rate, evaluation_path, nyquist, gate))
        if sample_rate == BASELINE_RATE:
            baseline_decision = decision

    if baseline_decision is None:
        raise ValidationError("every inference validation requires a 48000 baseline evaluation")
    for sample_rate, rate, _, _, _ in parsed_rates:
        if sample_rate > BASELINE_RATE:
            baseline_id = _require_text(
                rate["baseline_engineering_decision_id"],
                f"rate {sample_rate}.baseline_engineering_decision_id",
            )
            if baseline_id != baseline_decision:
                raise ValidationError(
                    f"rate {sample_rate} does not bind the 48000 baseline decision"
                )

    # Evaluate the baseline first so no high-rate pass can mask or rescue it.
    parsed_rates.sort(key=lambda item: (item[0] != BASELINE_RATE, item[0]))
    summaries = [
        _validate_evaluation(path, targets, sample_rate, nyquist, gate)
        for sample_rate, _, path, nyquist, gate in parsed_rates
    ]
    _verify_bound_files_unchanged(bound_files)
    return {
        "status": "inference-engineering-numeric-verification-passed",
        "schema_version": SCHEMA_VERSION,
        "manifest_sha256": actual_manifest_hash,
        "target_grid_hash": actual_grid_hash,
        "claim_boundary": CLAIM_BOUNDARY,
        "public_fit_status": "unchanged-from-frozen-snapshot-not-adjudicated",
        "deployment_status": "not-evaluated",
        "product_selectability_status": "not-evaluated",
        "rates": summaries,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest-sha256",
        required=True,
        help="externally recorded SHA-256 of the reviewed manifest",
    )
    parser.add_argument("manifest", type=Path, help="reviewed inference validation manifest")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = validate(args.manifest, args.manifest_sha256)
    except ValidationError as exc:
        print(f"INFERENCE_ENGINEERING_NUMERIC_VERIFICATION FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
