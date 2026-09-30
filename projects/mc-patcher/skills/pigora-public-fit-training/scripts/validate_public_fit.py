#!/usr/bin/env python3
"""Fail closed unless a complete Pigora domain passes its 0.2/0.5 dB tier."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import math
import re
import sys
from pathlib import Path
from typing import TextIO


PRIMARY_GATE_DB = 0.2
FALLBACK_GATE_DB = 0.5
ALLOWED_GATES = {PRIMARY_GATE_DB, FALLBACK_GATE_DB}
EPSILON = 1.0e-12
DOMAIN_COLUMNS = (
    "identity_id",
    "source_claim_id",
    "curve_id",
    "split",
    "sample_rate_hz",
    "control_state",
    "frequency_hz",
    "target_magnitude_db",
    "source_uncertainty_db",
    "gate_db",
    "gate_decision_id",
)
EVALUATION_COLUMNS = (
    DOMAIN_COLUMNS[:8] + ("predicted_magnitude_db",) + DOMAIN_COLUMNS[8:]
)
ALLOWED_SPLITS = {"training", "withheld", "full"}
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class ValidationError(RuntimeError):
    pass


def parse_finite(raw: str, field: str, row_number: int) -> float:
    try:
        value = float(raw)
    except ValueError as error:
        raise ValidationError(
            f"row {row_number}: {field} is not numeric: {raw!r}") from error
    if not math.isfinite(value):
        raise ValidationError(f"row {row_number}: {field} must be finite")
    return value


def open_input(path: str) -> tuple[TextIO, bool]:
    if path == "-":
        return sys.stdin, False
    return Path(path).open(newline="", encoding="utf-8"), True


def check_columns(reader: csv.DictReader, expected: tuple[str, ...],
                  label: str) -> None:
    columns = tuple(reader.fieldnames or ())
    missing = [column for column in expected if column not in columns]
    unexpected = [column for column in columns if column not in expected]
    if missing or unexpected or len(columns) != len(expected):
        raise ValidationError(
            f"{label} CSV columns must exactly match the contract; "
            f"missing={missing}, unexpected={unexpected}")


def row_key(row: dict[str, str], row_number: int) -> tuple[str, ...]:
    split = row["split"].strip().lower()
    if split not in ALLOWED_SPLITS:
        raise ValidationError(
            f"row {row_number}: split must be training, withheld, or full")
    sample_rate = parse_finite(
        row["sample_rate_hz"], "sample_rate_hz", row_number)
    frequency = parse_finite(row["frequency_hz"], "frequency_hz", row_number)
    if sample_rate <= 0.0 or frequency <= 0.0:
        raise ValidationError(
            f"row {row_number}: sample_rate_hz and frequency_hz must be positive")
    if frequency >= 0.5 * sample_rate:
        raise ValidationError(
            f"row {row_number}: domain frequency must be below Nyquist")
    identity = row["identity_id"].strip()
    source = row["source_claim_id"].strip()
    curve = row["curve_id"].strip()
    state = row["control_state"].strip()
    if not identity or not source or not curve or not state:
        raise ValidationError(
            f"row {row_number}: identity, source, curve, and control state "
            "cannot be empty")
    return (
        identity,
        source,
        curve,
        split,
        f"{sample_rate:.12g}",
        state,
        f"{frequency:.12g}",
    )


def read_domain(
        payload: bytes) -> dict[tuple[str, ...], tuple[float, float, float, str]]:
    try:
        text = payload.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValidationError("domain CSV must be valid UTF-8") from error
    reader = csv.DictReader(io.StringIO(text, newline=""))
    check_columns(reader, DOMAIN_COLUMNS, "domain")
    domain: dict[tuple[str, ...], tuple[float, float, float, str]] = {}
    partitions: dict[tuple[str, ...], str] = {}
    for row_number, row in enumerate(reader, start=2):
        if any(row[column].strip() == "" for column in DOMAIN_COLUMNS):
            raise ValidationError(
                f"domain row {row_number}: required fields cannot be empty")
        key = row_key(row, row_number)
        if key in domain:
            raise ValidationError(
                f"domain row {row_number}: duplicate response key {key}")
        partition = (key[0], key[1], key[2], key[5])
        prior_split = partitions.get(partition)
        if prior_split is not None and prior_split != key[3]:
            raise ValidationError(
                f"domain row {row_number}: curve/control partition "
                f"{partition} appears in both {prior_split} and {key[3]}")
        partitions[partition] = key[3]
        target = parse_finite(
            row["target_magnitude_db"], "target_magnitude_db", row_number)
        uncertainty = parse_finite(
            row["source_uncertainty_db"],
            "source_uncertainty_db",
            row_number,
        )
        gate = parse_finite(row["gate_db"], "gate_db", row_number)
        if gate not in ALLOWED_GATES:
            raise ValidationError(
                f"domain row {row_number}: gate_db must be exactly 0.2 or 0.5")
        decision_id = row["gate_decision_id"].strip()
        expected_prefix = "primary-" if gate == PRIMARY_GATE_DB else "fallback-"
        if not decision_id.startswith(expected_prefix):
            raise ValidationError(
                f"domain row {row_number}: gate_decision_id for {gate:.1f} dB "
                f"must start with {expected_prefix!r}")
        if uncertainty < 0.0 or uncertainty > gate + EPSILON:
            raise ValidationError(
                f"domain row {row_number}: source_uncertainty_db="
                f"{uncertainty:.9g} cannot support the fixed "
                f"{gate:.1f} dB gate")
        domain[key] = (target, uncertainty, gate, decision_id)
    if not domain:
        raise ValidationError("domain CSV contains no eligible response rows")
    return domain


def validate(domain_path: str, evaluation_path: str,
             expected_domain_sha256: str) -> int:
    if domain_path == "-" and evaluation_path == "-":
        raise ValidationError("domain and evaluation cannot both use stdin")
    if domain_path == "-":
        raise ValidationError("frozen domain must be a hashable file, not stdin")
    expected_hash = expected_domain_sha256.strip().lower()
    if HEX64.fullmatch(expected_hash) is None:
        raise ValidationError("domain SHA-256 must be 64 lowercase hex digits")
    domain_payload = Path(domain_path).read_bytes()
    actual_hash = hashlib.sha256(domain_payload).hexdigest()
    if actual_hash != expected_hash:
        raise ValidationError(
            f"domain SHA-256 mismatch: expected={expected_hash} actual={actual_hash}")
    domain = read_domain(domain_payload)
    stream, should_close = open_input(evaluation_path)
    try:
        reader = csv.DictReader(stream)
        check_columns(reader, EVALUATION_COLUMNS, "evaluation")
        seen: set[tuple[str, ...]] = set()
        failures: list[tuple[float, int, dict[str, str]]] = []
        worst: tuple[float, int, dict[str, str]] | None = None

        for row_number, row in enumerate(reader, start=2):
            if any(row[column].strip() == "" for column in EVALUATION_COLUMNS):
                raise ValidationError(
                    f"evaluation row {row_number}: required fields cannot be empty")
            key = row_key(row, row_number)
            if key in seen:
                raise ValidationError(
                    f"evaluation row {row_number}: duplicate response key {key}")
            if key not in domain:
                raise ValidationError(
                    f"evaluation row {row_number}: row is outside frozen domain {key}")
            seen.add(key)

            (frozen_target, frozen_uncertainty, frozen_gate,
             frozen_decision_id) = domain[key]
            target = parse_finite(
                row["target_magnitude_db"], "target_magnitude_db", row_number)
            predicted = parse_finite(
                row["predicted_magnitude_db"],
                "predicted_magnitude_db",
                row_number,
            )
            uncertainty = parse_finite(
                row["source_uncertainty_db"],
                "source_uncertainty_db",
                row_number,
            )
            gate = parse_finite(row["gate_db"], "gate_db", row_number)
            decision_id = row["gate_decision_id"].strip()
            if abs(target - frozen_target) > EPSILON:
                raise ValidationError(
                    f"evaluation row {row_number}: target differs from frozen domain")
            if abs(uncertainty - frozen_uncertainty) > EPSILON:
                raise ValidationError(
                    f"evaluation row {row_number}: uncertainty differs from frozen domain")
            if abs(gate - frozen_gate) > EPSILON:
                raise ValidationError(
                    f"evaluation row {row_number}: gate differs from frozen domain")
            if decision_id != frozen_decision_id:
                raise ValidationError(
                    f"evaluation row {row_number}: gate decision differs from frozen domain")

            error_db = abs(predicted - frozen_target)
            result = (error_db, row_number, row)
            if worst is None or error_db > worst[0]:
                worst = result
            if error_db > frozen_gate + EPSILON:
                failures.append(result)

        missing = sorted(set(domain) - seen)
        if missing:
            preview = "; ".join(str(key) for key in missing[:5])
            raise ValidationError(
                f"evaluation omits {len(missing)} frozen-domain rows: {preview}")
        if worst is None:
            raise ValidationError("evaluation CSV contains no response rows")

        split_counts = {
            split: sum(1 for key in domain if key[3] == split)
            for split in sorted(ALLOWED_SPLITS)
        }
        gate_counts = {
            gate: sum(1 for values in domain.values()
                      if abs(values[2] - gate) <= EPSILON)
            for gate in sorted(ALLOWED_GATES)
        }
        groups = {
            (key[0], key[1], key[2], key[3], key[4], key[5])
            for key in domain
        }
        identities = {key[0] for key in domain}
        print(
            "Pigora public-fit evaluation "
            f"domain_sha256={actual_hash} identities={len(identities)} "
            f"rows={len(domain)} groups={len(groups)} "
            f"training={split_counts['training']} "
            f"withheld={split_counts['withheld']} full={split_counts['full']} "
            f"primary_0p2={gate_counts[PRIMARY_GATE_DB]} "
            f"fallback_0p5={gate_counts[FALLBACK_GATE_DB]}"
        )
        worst_error, worst_row_number, worst_row = worst
        print(
            "worst "
            f"error_db={worst_error:.9g} row={worst_row_number} "
            f"identity={worst_row['identity_id']} "
            f"source={worst_row['source_claim_id']} curve={worst_row['curve_id']} "
            f"state={worst_row['control_state']} "
            f"sample_rate_hz={worst_row['sample_rate_hz']} "
            f"frequency_hz={worst_row['frequency_hz']} "
            f"gate_db={worst_row['gate_db']} "
            f"gate_decision_id={worst_row['gate_decision_id']}"
        )

        if failures:
            print(
                f"FAIL {len(failures)} frozen-domain rows exceed their "
                "fixed per-row gate",
                file=sys.stderr,
            )
            for error_db, row_number, row in sorted(
                    failures, key=lambda item: item[0], reverse=True)[:10]:
                print(
                    f"  row={row_number} error_db={error_db:.9g} "
                    f"identity={row['identity_id']} "
                    f"source={row['source_claim_id']} curve={row['curve_id']} "
                    f"state={row['control_state']} "
                    f"sample_rate_hz={row['sample_rate_hz']} "
                    f"frequency_hz={row['frequency_hz']} "
                    f"gate_db={row['gate_db']} "
                    f"gate_decision_id={row['gate_decision_id']}",
                    file=sys.stderr,
                )
            return 1

        print("PASS all frozen-domain rows are within their 0.2/0.5 dB tier")
        return 0
    finally:
        if should_close:
            stream.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--domain-sha256",
        required=True,
        help="SHA-256 recorded by the pre-training coverage review",
    )
    parser.add_argument("domain_csv", help="frozen domain CSV path")
    parser.add_argument("evaluation_csv", help="evaluation CSV path, or - for stdin")
    args = parser.parse_args()
    try:
        return validate(args.domain_csv, args.evaluation_csv, args.domain_sha256)
    except (OSError, ValidationError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
