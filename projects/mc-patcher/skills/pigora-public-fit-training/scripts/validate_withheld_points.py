#!/usr/bin/env python3
"""Validate exact point-level Pigora evidence-policy withheld decisions."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter
from pathlib import Path


LEDGER_COLUMNS = (
    "identity_key",
    "module_type",
    "model_name",
    "point_kind",
    "selector",
    "fixed_frequency_hz",
    "catalog_claim_status",
    "public_fit_state",
    "evidence_policy_reason",
    "reason_code",
    "source_claim_id",
    "missing_evidence",
    "decision_id",
)
EVIDENCE_REQUIRED = {
    "identity_key",
    "public_fit_state",
    "evidence_policy_decision",
    "evidence_policy_reason",
    "source_claim_id",
}
ALLOWED_POINT_KINDS = {
    "low_cut", "low_shelf", "bell", "high_shelf", "high_cut",
}
ALLOWED_PUBLIC_FIT_STATES = {
    "public-fit partial",
    "public-fit failed/withheld",
    "not publicly specified",
}
ALLOWED_REASON_CODES = {
    "missing_numeric_response",
    "source_uncertainty_over_fallback",
    "identity_revision_ambiguous",
    "source_conflict",
    "control_state_unbound",
    "fallback_gate_failed",
    "unsafe_or_unexpressible",
}
BROAD_MARKERS = {
    "*", "all", "all eq", "all points", "any", "entire module",
    "whole module", "model-wide", "n/a",
}


class ValidationError(RuntimeError):
    pass


def parse_integer(raw: str, field: str, row_number: int) -> int:
    try:
        value = int(raw)
    except ValueError as error:
        raise ValidationError(
            f"row {row_number}: {field} is not an integer: {raw!r}") from error
    if value < 0:
        raise ValidationError(f"row {row_number}: {field} must be non-negative")
    return value


def parse_positive_finite(raw: str, field: str, row_number: int) -> float:
    try:
        value = float(raw)
    except ValueError as error:
        raise ValidationError(
            f"row {row_number}: {field} is not numeric: {raw!r}") from error
    if not math.isfinite(value) or value <= 0.0:
        raise ValidationError(
            f"row {row_number}: {field} must be finite and positive")
    return value


def require_specific(raw: str, field: str, row_number: int) -> str:
    value = raw.strip()
    if not value or value.lower() in BROAD_MARKERS or "*" in value:
        raise ValidationError(
            f"row {row_number}: {field} must identify one exact point")
    return value


def load_catalog(path: Path) -> dict[str, dict]:
    catalog: dict[str, dict] = {}
    for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValidationError(
                f"catalog line {line_number}: invalid JSON") from error
        for field in ("module_type", "model_name", "point_kind", "selector",
                      "fixed_frequency_hz", "claim_status"):
            if field not in row:
                raise ValidationError(
                    f"catalog line {line_number}: missing {field}")
        key = f"{row['module_type']}:{row['point_kind']}:{row['selector']}"
        if key in catalog:
            raise ValidationError(f"catalog line {line_number}: duplicate {key}")
        catalog[key] = row
    if not catalog:
        raise ValidationError("catalog contains no point identities")
    return catalog


def load_expected_withheld(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fields = set(reader.fieldnames or ())
        missing = sorted(EVIDENCE_REQUIRED - fields)
        if missing:
            raise ValidationError(
                f"evidence policy CSV missing required columns: {missing}")
        expected: dict[str, dict[str, str]] = {}
        for row_number, row in enumerate(reader, start=2):
            if row["evidence_policy_decision"].strip() != "withheld":
                continue
            key = require_specific(row["identity_key"], "identity_key", row_number)
            if key in expected:
                raise ValidationError(
                    f"evidence policy row {row_number}: duplicate {key}")
            expected[key] = row
    return expected


def validate(catalog_path: Path, evidence_path: Path, ledger_path: Path) -> int:
    catalog = load_catalog(catalog_path)
    expected = load_expected_withheld(evidence_path)
    unknown_policy = sorted(set(expected) - set(catalog))
    if unknown_policy:
        raise ValidationError(
            f"evidence policy references {len(unknown_policy)} unknown catalog "
            f"identities: {unknown_policy[:5]}")

    with ledger_path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        columns = tuple(reader.fieldnames or ())
        missing = [field for field in LEDGER_COLUMNS if field not in columns]
        unexpected = [field for field in columns if field not in LEDGER_COLUMNS]
        if missing or unexpected or len(columns) != len(LEDGER_COLUMNS):
            raise ValidationError(
                "withheld ledger columns must exactly match the contract; "
                f"missing={missing}, unexpected={unexpected}")

        seen: set[str] = set()
        model_counts: Counter[str] = Counter()
        kind_counts: Counter[str] = Counter()
        reason_counts: Counter[str] = Counter()
        for row_number, row in enumerate(reader, start=2):
            if any(not row[field].strip() for field in LEDGER_COLUMNS):
                raise ValidationError(
                    f"row {row_number}: withheld ledger fields cannot be empty")
            key = require_specific(row["identity_key"], "identity_key", row_number)
            if key in seen:
                raise ValidationError(f"row {row_number}: duplicate identity {key}")
            if key not in expected:
                raise ValidationError(
                    f"row {row_number}: {key} is not evidence-policy withheld")
            seen.add(key)

            module_type = parse_integer(row["module_type"], "module_type", row_number)
            selector = parse_integer(row["selector"], "selector", row_number)
            model_name = require_specific(
                row["model_name"], "model_name", row_number)
            point_kind = require_specific(
                row["point_kind"], "point_kind", row_number)
            if point_kind not in ALLOWED_POINT_KINDS:
                raise ValidationError(
                    f"row {row_number}: unsupported point_kind {point_kind!r}")
            frequency = parse_positive_finite(
                row["fixed_frequency_hz"], "fixed_frequency_hz", row_number)
            exact_key = f"{module_type}:{point_kind}:{selector}"
            if key != exact_key:
                raise ValidationError(
                    f"row {row_number}: identity_key must equal {exact_key}")

            catalog_row = catalog[key]
            if model_name != str(catalog_row["model_name"]):
                raise ValidationError(
                    f"row {row_number}: model_name differs from catalog")
            if row["catalog_claim_status"] != str(catalog_row["claim_status"]):
                raise ValidationError(
                    f"row {row_number}: catalog_claim_status differs from catalog")
            catalog_frequency = float(catalog_row["fixed_frequency_hz"])
            if not math.isclose(
                    frequency, catalog_frequency, rel_tol=1.0e-12,
                    abs_tol=1.0e-6):
                raise ValidationError(
                    f"row {row_number}: fixed_frequency_hz differs from catalog")

            policy_row = expected[key]
            public_state = row["public_fit_state"].strip()
            if public_state not in ALLOWED_PUBLIC_FIT_STATES:
                raise ValidationError(
                    f"row {row_number}: invalid withheld public_fit_state")
            if public_state != policy_row["public_fit_state"].strip():
                raise ValidationError(
                    f"row {row_number}: public_fit_state differs from policy")
            if (row["evidence_policy_reason"].strip()
                    != policy_row["evidence_policy_reason"].strip()):
                raise ValidationError(
                    f"row {row_number}: evidence_policy_reason differs from policy")

            reason_code = row["reason_code"].strip()
            if reason_code not in ALLOWED_REASON_CODES:
                raise ValidationError(
                    f"row {row_number}: invalid reason_code {reason_code!r}")
            expected_source = policy_row["source_claim_id"].strip() or "none"
            if row["source_claim_id"].strip() != expected_source:
                raise ValidationError(
                    f"row {row_number}: source_claim_id differs from policy")
            missing_evidence = row["missing_evidence"].strip()
            if (len(missing_evidence) < 12
                    or missing_evidence.lower() in BROAD_MARKERS
                    or "*" in missing_evidence):
                raise ValidationError(
                    f"row {row_number}: missing_evidence must name a concrete artifact")
            if not row["decision_id"].strip().startswith("withheld-"):
                raise ValidationError(
                    f"row {row_number}: decision_id must start with 'withheld-'")

            model_counts[model_name] += 1
            kind_counts[point_kind] += 1
            reason_counts[reason_code] += 1

    omitted = sorted(set(expected) - seen)
    if omitted:
        raise ValidationError(
            f"withheld ledger omits {len(omitted)} policy-withheld points: "
            f"{omitted[:5]}")

    print(
        "Pigora withheld points PASS "
        f"points={len(seen)} modules={len(model_counts)} "
        f"filter_kinds={dict(sorted(kind_counts.items()))} "
        f"reasons={dict(sorted(reason_counts.items()))}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--evidence-policy", required=True, type=Path)
    parser.add_argument("withheld_csv", type=Path)
    args = parser.parse_args()
    try:
        return validate(args.catalog, args.evidence_policy, args.withheld_csv)
    except (OSError, ValidationError, ValueError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
