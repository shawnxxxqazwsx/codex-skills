#!/usr/bin/env python3

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).with_name("validate_inference_fit.py")
SPEC = importlib.util.spec_from_file_location("validate_inference_fit", SCRIPT)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class InferenceValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.target_rows = [
            {
                "row_id": "row-100",
                "identity_id": "eq-main",
                "control_state_id": "gain-plus-1",
                "control_state_json": '{"gain_db":1}',
                "point_id": "100-hz",
                "frequency_hz": "100",
                "target_magnitude_db": "0",
                "target_provenance": "inference-donor",
            },
            {
                "row_id": "row-20k",
                "identity_id": "eq-main",
                "control_state_id": "gain-plus-1",
                "control_state_json": '{"gain_db":1}',
                "point_id": "20000-hz",
                "frequency_hz": "20000",
                "target_magnitude_db": "1",
                "target_provenance": "human-supplemented-gain",
            },
            {
                "row_id": "row-30k",
                "identity_id": "eq-main",
                "control_state_id": "gain-plus-1",
                "control_state_json": '{"gain_db":1}',
                "point_id": "30000-hz",
                "frequency_hz": "30000",
                "target_magnitude_db": "1",
                "target_provenance": "human-supplemented-frequency",
            },
        ]
        self.write_csv("target.csv", VALIDATOR.TARGET_HEADER, self.target_rows)
        self.write_csv(
            "exclusions.csv",
            VALIDATOR.EXCLUSION_HEADER,
            [
                {
                    "identity_id": "eq-excluded",
                    "exclusion_scope": "high-pass-stage",
                    "exclusion_reason": "no numeric donor",
                    "product_use_state": "not-product-selectable-inference",
                    "public_fit_state": "not publicly specified",
                    "evidence_policy_state": "source-constrained",
                    "engineering_decision_id": "inference-exclude-hpf-1",
                }
            ],
        )
        states = [
            {
                "identity_id": "eq-main",
                "public_fit_state": "public-fit partial",
                "evidence_policy_state": "source-constrained",
            },
            {
                "identity_id": "eq-excluded",
                "public_fit_state": "not publicly specified",
                "evidence_policy_state": "source-constrained",
            },
        ]
        self.write_csv("public-snapshot.csv", VALIDATOR.PUBLIC_STATE_HEADER, states)
        self.write_csv("public-current.csv", VALIDATOR.PUBLIC_STATE_HEADER, states)
        (self.root / "candidate.bin").write_bytes(b"candidate-v1")
        (self.root / "response-path.bin").write_bytes(b"production-response-path-v1")
        self.evaluations: dict[int, list[dict[str, str]]] = {}
        self.rates: list[dict[str, object]] = []
        self.add_rate(48000, ["0.2", "0.8", None])
        self.add_rate(96000, ["0.5", "1.5", "1"])
        _, grid_hash = VALIDATOR._load_target(self.root / "target.csv")
        self.grid_hash = grid_hash
        self.manifest: dict[str, object] = {
            "schema_version": VALIDATOR.SCHEMA_VERSION,
            "contract_kind": "donor-curve-inference-only",
            "claim_boundary": VALIDATOR.CLAIM_BOUNDARY,
            "review": {
                "author_id": "fit-author",
                "reviewer_id": "independent-reviewer",
                "review_status": "reviewed",
                "review_decision_id": "inference-review-1",
            },
            "scope": {
                "in_scope_identity_ids": ["eq-main"],
                "excluded_identity_ids": ["eq-excluded"],
            },
            "candidate": {
                "candidate_id": "candidate-v1",
                "candidate_artifact": {},
                "response_path_id": "production-response-v1",
                "response_path_artifact": {},
            },
            "target": {},
            "exclusions": {},
            "public_state_snapshot": {},
            "public_state_current": {},
            "rates": self.rates,
        }
        self.refresh_manifest()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_csv(
        self, name: str, header: list[str], rows: list[dict[str, object]]
    ) -> None:
        with (self.root / name).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=header, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    def add_rate(self, sample_rate: int, predictions: list[str | None]) -> None:
        rows: list[dict[str, str]] = []
        nyquist = sample_rate // 2
        for target, prediction in zip(self.target_rows, predictions):
            row = dict(target)
            row["sample_rate_hz"] = str(sample_rate)
            if int(target["frequency_hz"]) < nyquist:
                row["predicted_magnitude_db"] = "" if prediction is None else prediction
                row["eligibility"] = "eligible"
                row["ineligibility_reason"] = ""
            else:
                row["predicted_magnitude_db"] = ""
                row["eligibility"] = "ineligible"
                row["ineligibility_reason"] = "at-or-above-declared-nyquist"
            rows.append(row)
        self.evaluations[sample_rate] = rows
        self.write_csv(f"evaluation-{sample_rate}.csv", VALIDATOR.EVALUATION_HEADER, rows)
        high = sample_rate > 48000
        self.rates.append(
            {
                "sample_rate_hz": sample_rate,
                "evaluation": {},
                "declared_nyquist_hz": sample_rate / 2,
                "condition_id": f"condition-{sample_rate}",
                "control_state_coverage": VALIDATOR.COVERAGE,
                "engineering_gate_kind": (
                    VALIDATOR.HIGH_GATE_KIND if high else VALIDATOR.BASE_GATE_KIND
                ),
                "engineering_gate_db": 0.5 if high else 0.2,
                "engineering_decision_id": f"inference-rate-{sample_rate}",
                "baseline_engineering_decision_id": (
                    "inference-rate-48000" if high else VALIDATOR.NOT_APPLICABLE
                ),
                "target_grid_hash": "pending",
                "candidate_id": "candidate-v1",
                "response_path_id": "production-response-v1",
            }
        )

    def rewrite_evaluation(self, sample_rate: int) -> None:
        self.write_csv(
            f"evaluation-{sample_rate}.csv",
            VALIDATOR.EVALUATION_HEADER,
            self.evaluations[sample_rate],
        )

    def rewrite_target_and_sync_evaluations(self) -> None:
        self.write_csv("target.csv", VALIDATOR.TARGET_HEADER, self.target_rows)
        _, self.grid_hash = VALIDATOR._load_target(self.root / "target.csv")
        for sample_rate, rows in self.evaluations.items():
            for target, evaluation in zip(self.target_rows, rows):
                for field in VALIDATOR.TARGET_HEADER:
                    evaluation[field] = target[field]
            self.rewrite_evaluation(sample_rate)
        self.refresh_manifest()

    def refresh_manifest(self) -> None:
        def file_spec(name: str) -> dict[str, str]:
            path = self.root / name
            return {"path": name, "sha256": sha256(path)}

        candidate = self.manifest["candidate"]
        assert isinstance(candidate, dict)
        candidate["candidate_artifact"] = file_spec("candidate.bin")
        candidate["response_path_artifact"] = file_spec("response-path.bin")
        self.manifest["target"] = {
            **file_spec("target.csv"),
            "target_grid_hash": self.grid_hash,
        }
        self.manifest["exclusions"] = file_spec("exclusions.csv")
        self.manifest["public_state_snapshot"] = file_spec("public-snapshot.csv")
        self.manifest["public_state_current"] = file_spec("public-current.csv")
        for rate in self.rates:
            sample_rate = int(rate["sample_rate_hz"])
            rate["evaluation"] = file_spec(f"evaluation-{sample_rate}.csv")
            rate["target_grid_hash"] = self.grid_hash
        (self.root / "manifest.json").write_text(
            json.dumps(self.manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def run_validator(self, manifest_hash: str | None = None) -> subprocess.CompletedProcess[str]:
        manifest = self.root / "manifest.json"
        digest = sha256(manifest) if manifest_hash is None else manifest_hash
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--manifest-sha256",
                digest,
                str(manifest),
            ],
            text=True,
            capture_output=True,
            check=False,
        )

    def assert_failure(self, needle: str) -> None:
        result = self.run_validator()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(needle, result.stderr)

    def test_inclusive_point_two_and_point_five_pass(self) -> None:
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(
            report["status"], "inference-engineering-numeric-verification-passed"
        )
        self.assertEqual([rate["worst_error_db"] for rate in report["rates"]], ["0.2", "0.5"])
        self.assertEqual(report["deployment_status"], "not-evaluated")

    def test_external_manifest_hash_is_mandatory_and_exact(self) -> None:
        result = self.run_validator("0" * 64)
        self.assertEqual(result.returncode, 1)
        self.assertIn("reviewed manifest SHA-256 mismatch", result.stderr)
        missing = subprocess.run(
            [sys.executable, str(SCRIPT), str(self.root / "manifest.json")],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("--manifest-sha256", missing.stderr)

    def test_bound_artifact_hash_mismatch_fails(self) -> None:
        target = self.manifest["target"]
        assert isinstance(target, dict)
        target["sha256"] = "0" * 64
        (self.root / "manifest.json").write_text(
            json.dumps(self.manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        self.assert_failure("target SHA-256 mismatch")

    def test_missing_evaluation_row_fails(self) -> None:
        self.evaluations[96000].pop()
        self.rewrite_evaluation(96000)
        self.refresh_manifest()
        self.assert_failure("row count mismatch")

    def test_duplicate_evaluation_row_fails(self) -> None:
        self.evaluations[96000][2] = dict(self.evaluations[96000][1])
        self.rewrite_evaluation(96000)
        self.refresh_manifest()
        self.assert_failure("duplicate evaluation 96000 row_id")

    def test_extra_evaluation_row_fails(self) -> None:
        extra = dict(self.evaluations[96000][-1])
        extra["row_id"] = "extra-row"
        extra["point_id"] = "extra-point"
        self.evaluations[96000].append(extra)
        self.rewrite_evaluation(96000)
        self.refresh_manifest()
        self.assert_failure("row count mismatch")

    def test_missing_trailing_csv_field_fails_cleanly(self) -> None:
        path = self.root / "evaluation-48000.csv"
        lines = path.read_text(encoding="utf-8").splitlines()
        lines[-1] = lines[-1].rsplit(",", 1)[0]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.refresh_manifest()
        result = self.run_validator()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("missing CSV fields", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_changed_evaluation_target_fails(self) -> None:
        self.evaluations[96000][0]["target_magnitude_db"] = "0.01"
        self.rewrite_evaluation(96000)
        self.refresh_manifest()
        self.assert_failure("target_magnitude_db does not match frozen target")

    def test_nonfinite_prediction_fails(self) -> None:
        self.evaluations[96000][0]["predicted_magnitude_db"] = "NaN"
        self.rewrite_evaluation(96000)
        self.refresh_manifest()
        self.assert_failure("must be finite numeric data")

    def test_baseline_failure_is_not_rescued_by_high_rate_pass(self) -> None:
        self.evaluations[48000][0]["predicted_magnitude_db"] = "0.2000001"
        self.rewrite_evaluation(48000)
        self.refresh_manifest()
        self.assert_failure("rate 48000 numeric gate failed")

    def test_lower_rate_cannot_use_relaxed_gate(self) -> None:
        self.add_rate(44100, ["0", "1", None])
        rate = self.rates[-1]
        rate["engineering_gate_kind"] = VALIDATOR.HIGH_GATE_KIND
        rate["engineering_gate_db"] = 0.5
        self.refresh_manifest()
        self.assert_failure("rate <= 48000 must use")

    def test_48000_baseline_is_mandatory_even_for_lower_only_run(self) -> None:
        self.add_rate(44100, ["0", "1", None])
        self.rates[:] = [self.rates[-1]]
        self.refresh_manifest()
        self.assert_failure("every inference validation requires a 48000 baseline")

    def test_high_rate_may_keep_stricter_point_two_gate(self) -> None:
        rate = self.rates[1]
        rate["engineering_gate_kind"] = VALIDATOR.BASE_GATE_KIND
        rate["engineering_gate_db"] = 0.2
        self.evaluations[96000][0]["predicted_magnitude_db"] = "0.2"
        self.evaluations[96000][1]["predicted_magnitude_db"] = "1.2"
        self.evaluations[96000][2]["predicted_magnitude_db"] = "0.8"
        self.rewrite_evaluation(96000)
        self.refresh_manifest()
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        high = next(rate for rate in report["rates"] if rate["sample_rate_hz"] == 96000)
        self.assertEqual(high["gate_db"], "0.2")

    def test_donor_curve_contract_rejects_measured_anchor_provenance(self) -> None:
        self.target_rows[0]["target_provenance"] = "measured"
        self.rewrite_target_and_sync_evaluations()
        self.assert_failure("donor-curve-inference-only target has forbidden provenance")

    def test_sparse_grid_accepts_bound_measured_anchor_and_supplemented_rows(self) -> None:
        self.manifest["contract_kind"] = "sparse-grid-completion"
        self.target_rows[0]["target_provenance"] = "image-digitized"
        self.rewrite_target_and_sync_evaluations()
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_sparse_grid_rejects_inference_donor(self) -> None:
        self.manifest["contract_kind"] = "sparse-grid-completion"
        self.refresh_manifest()
        self.assert_failure("sparse-grid-completion target forbids inference-donor")

    def test_sparse_grid_requires_measured_or_image_anchor(self) -> None:
        self.manifest["contract_kind"] = "sparse-grid-completion"
        self.target_rows[0]["target_provenance"] = "human-supplemented-curve"
        self.rewrite_target_and_sync_evaluations()
        self.assert_failure("requires at least one measured or image-digitized accepted anchor")

    def test_one_failing_high_rate_fails_whole_validation(self) -> None:
        self.add_rate(192000, ["0.500001", "1", "1"])
        self.refresh_manifest()
        self.assert_failure("rate 192000 numeric gate failed")

    def test_explicit_nyquist_row_cannot_be_silently_removed(self) -> None:
        row = self.evaluations[48000][2]
        row["eligibility"] = "eligible"
        row["ineligibility_reason"] = ""
        row["predicted_magnitude_db"] = "1"
        self.rewrite_evaluation(48000)
        self.refresh_manifest()
        self.assert_failure("must be explicitly ineligible")

    def test_nested_nonfinite_or_overflowing_control_state_numbers_fail(self) -> None:
        for state in (
            '{"outer":{"value":NaN}}',
            '{"outer":[Infinity]}',
            '{"outer":[-Infinity]}',
            '{"outer":{"value":1e999}}',
        ):
            with self.subTest(state=state):
                with self.assertRaisesRegex(
                    VALIDATOR.ValidationError, "non-finite|overflowing"
                ):
                    VALIDATOR._canonical_state(state, "test state")

    def test_control_state_id_cannot_map_to_different_state_json(self) -> None:
        self.target_rows[1]["control_state_json"] = '{"gain_db":2}'
        self.write_csv("target.csv", VALIDATOR.TARGET_HEADER, self.target_rows)
        self.refresh_manifest()
        self.assert_failure("maps to conflicting control_state_json")

    def test_bound_artifact_change_during_validation_fails_before_receipt(self) -> None:
        original = VALIDATOR._validate_evaluation

        def mutate_after_evaluation(*args: object, **kwargs: object) -> dict[str, object]:
            result = original(*args, **kwargs)
            (self.root / "candidate.bin").write_bytes(b"candidate-changed-during-validation")
            return result

        manifest = self.root / "manifest.json"
        with mock.patch.object(
            VALIDATOR, "_validate_evaluation", side_effect=mutate_after_evaluation
        ):
            with self.assertRaisesRegex(VALIDATOR.ValidationError, "changed during validation"):
                VALIDATOR.validate(manifest, sha256(manifest))

    def test_excluded_identity_cannot_be_product_selectable(self) -> None:
        with (self.root / "exclusions.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        rows[0]["product_use_state"] = "product-selectable-inference-derived"
        self.write_csv("exclusions.csv", VALIDATOR.EXCLUSION_HEADER, rows)
        self.refresh_manifest()
        self.assert_failure("must use product_use_state not-product-selectable-inference")

    def test_review_decision_requires_inference_namespace(self) -> None:
        review = self.manifest["review"]
        assert isinstance(review, dict)
        review["review_decision_id"] = "review-1"
        self.refresh_manifest()
        self.assert_failure("must use the inference- prefix")

    def test_rate_decision_rejects_public_keyword(self) -> None:
        self.rates[0]["engineering_decision_id"] = "inference-public-primary-foo"
        self.refresh_manifest()
        self.assert_failure("contain no public/fallback keyword")

    def test_exclusion_decision_requires_inference_namespace(self) -> None:
        with (self.root / "exclusions.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        rows[0]["engineering_decision_id"] = "exclude-hpf-1"
        self.write_csv("exclusions.csv", VALIDATOR.EXCLUSION_HEADER, rows)
        self.refresh_manifest()
        self.assert_failure("must use the inference- prefix")

    def test_public_or_evidence_state_mutation_fails(self) -> None:
        with (self.root / "public-current.csv").open(
            encoding="utf-8", newline=""
        ) as handle:
            rows = list(csv.DictReader(handle))
        rows[0]["public_fit_state"] = "public-fit passed"
        self.write_csv("public-current.csv", VALIDATOR.PUBLIC_STATE_HEADER, rows)
        self.refresh_manifest()
        self.assert_failure("public/evidence states changed from frozen snapshot")

    def test_malformed_manifest_fails_closed(self) -> None:
        del self.manifest["review"]
        (self.root / "manifest.json").write_text(
            json.dumps(self.manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        self.assert_failure("manifest fields mismatch")


if __name__ == "__main__":
    unittest.main()
