#!/usr/bin/env python3
"""Tests for the diagnostic-only curve coverage helpers."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

import curve_coverage as coverage  # noqa: E402


class FrequencyCoverageTests(unittest.TestCase):
    @staticmethod
    def narrow_resonance(frequency_hz: float) -> float:
        center_hz = 1163.38
        full_width_hz = 0.38
        return 12.0 / (
            1.0
            + ((frequency_hz - center_hz) / (0.5 * full_width_hz)) ** 2
        )

    def test_pole_probes_and_refinement_find_peak_missed_by_coarse_grid(self) -> None:
        coarse = coverage.build_frequency_probes(
            [1141.0, 1186.0],
            sample_rate_hz=48000.0,
            subdivisions_per_interval=0,
        )
        coarse_peak = max(self.narrow_resonance(f) for f in coarse.frequencies_hz)
        self.assertLess(coarse_peak, 0.01)

        planned = coverage.build_frequency_probes(
            [1141.0, 1186.0],
            sample_rate_hz=48000.0,
            subdivisions_per_interval=0,
            pole_hints=[
                coverage.PoleHint(center_hz=1163.30, bandwidth_hz=0.38)
            ],
        )
        refined = coverage.refine_local_extrema(
            self.narrow_resonance,
            planned.frequencies_hz,
            interval_hz=planned.bounds_hz,
            max_evaluations=160,
            frequency_tolerance_hz=1.0e-5,
        )
        maxima = [item for item in refined.extrema if item.kind == "maximum"]
        self.assertTrue(maxima)
        peak = max(maxima, key=lambda item: item.magnitude_db)
        self.assertAlmostEqual(peak.frequency_hz, 1163.38, delta=0.01)
        self.assertGreater(peak.magnitude_db, 11.99)
        self.assertFalse(refined.budget_exhausted)
        self.assertEqual(refined.unresolved_intervals, ())

    def test_log_subdivision_uses_geometric_spacing(self) -> None:
        plan = coverage.build_frequency_probes(
            [100.0, 400.0],
            sample_rate_hz=48000.0,
            subdivisions_per_interval=1,
        )
        self.assertEqual(len(plan.frequencies_hz), 3)
        self.assertAlmostEqual(plan.frequencies_hz[1], 200.0)
        self.assertAlmostEqual(plan.resolution.maximum_log_step_ratio, 2.0)

    def test_declared_interval_boundaries_are_always_probed(self) -> None:
        plan = coverage.build_frequency_probes(
            [100.0, 1000.0],
            sample_rate_hz=48000.0,
            interval_hz=(20.0, 20000.0),
            subdivisions_per_interval=0,
        )
        self.assertEqual(plan.frequencies_hz, (20.0, 100.0, 1000.0, 20000.0))

    def test_digital_pole_is_resolved_from_radius_angle_and_rate(self) -> None:
        sample_rate_hz = 48000.0
        center_hz = 2000.0
        radius = 0.999
        hint = coverage.PoleHint(
            radius=radius,
            angle_rad=2.0 * math.pi * center_hz / sample_rate_hz,
            sample_rate_hz=sample_rate_hz,
        )
        resolved = coverage.resolve_pole_hint(
            hint, expected_sample_rate_hz=sample_rate_hz
        )
        self.assertAlmostEqual(resolved.center_hz, center_hz)
        self.assertAlmostEqual(
            resolved.neighborhood_width_hz,
            -sample_rate_hz * math.log(radius) / math.pi,
        )
        self.assertEqual(resolved.method, "digital-radius-angle-decay-width")

    def test_budget_exhaustion_stops_and_reports_unresolved_interval(self) -> None:
        plan = coverage.build_frequency_probes(
            [1141.0, 1186.0],
            sample_rate_hz=48000.0,
            subdivisions_per_interval=0,
            pole_hints=[
                coverage.PoleHint(center_hz=1163.30, bandwidth_hz=0.38)
            ],
        )
        result = coverage.refine_local_extrema(
            self.narrow_resonance,
            plan.frequencies_hz,
            max_evaluations=len(plan.frequencies_hz) + 1,
            frequency_tolerance_hz=1.0e-12,
        )
        self.assertTrue(result.budget_exhausted)
        self.assertLessEqual(result.evaluation_count, result.max_evaluations)
        self.assertTrue(result.unresolved_intervals)
        self.assertIn("budget exhausted", result.unresolved_intervals[0].reason)

    def test_report_is_diagnostic_and_never_claims_continuous_guarantee(self) -> None:
        plan = coverage.build_frequency_probes(
            [100.0, 1000.0], sample_rate_hz=48000.0
        )
        states = coverage.summarize_effective_states(
            [0.0, 0.1, 0.2], lambda _: 0
        )
        report = coverage.make_coverage_report(plan, state_coverage=states)
        serialized = report.to_dict()
        self.assertTrue(serialized["diagnostic_only"])
        self.assertEqual(serialized["formal_gate_status"], "not_adjudicated")
        self.assertFalse(serialized["all_continuous_extrema_guaranteed"])
        self.assertIsNone(serialized["refinement_resolution_hz"])
        self.assertEqual(serialized["evaluated_probe_count"], 0)
        self.assertEqual(serialized["evaluation_status"], "not_evaluated")
        self.assertEqual(len(serialized["unresolved_intervals"]), 1)
        self.assertIn(
            "not evaluated", serialized["unresolved_intervals"][0]["reason"]
        )
        self.assertNotIn("pass", serialized)
        with self.assertRaises(TypeError):
            coverage.CoverageReport(
                frequency_method="x",
                frequency_resolution=plan.resolution,
                anchor_count=2,
                initial_probe_count=2,
                evaluated_probe_count=2,
                requested_state_count=None,
                distinct_effective_state_count=None,
                duplicate_effective_state_count=None,
                unresolved_intervals=(),
                budget_exhausted=False,
                refinement_resolution_hz=None,
                refinement_max_evaluations=None,
                evaluation_status="not_evaluated",
                formal_gate_status="pass",  # type: ignore[call-arg]
            )

    def test_report_rejects_refinement_from_a_different_plan(self) -> None:
        plan_a = coverage.build_frequency_probes(
            [100.0, 1000.0], sample_rate_hz=48000.0
        )
        plan_b = coverage.build_frequency_probes(
            [100.0, 1100.0], sample_rate_hz=48000.0
        )
        refinement_b = coverage.refine_local_extrema(
            lambda frequency: math.log(frequency),
            plan_b.frequencies_hz,
            interval_hz=plan_b.bounds_hz,
        )
        with self.assertRaisesRegex(
            coverage.CoverageInputError, "do not match the probe plan"
        ):
            coverage.make_coverage_report(plan_a, refinement=refinement_b)

    def test_frequency_and_nyquist_inputs_fail_closed(self) -> None:
        bad_requests = (
            ([100.0], 48000.0, None),
            ([100.0, 100.0], 48000.0, None),
            ([100.0, math.nan], 48000.0, None),
            ([100.0, 24000.0], 48000.0, None),
            ([100.0, 1000.0], 48000.0, (100.0, math.inf)),
        )
        for anchors, rate, interval in bad_requests:
            with self.subTest(anchors=anchors, interval=interval):
                with self.assertRaises(coverage.CoverageInputError):
                    coverage.build_frequency_probes(
                        anchors,
                        sample_rate_hz=rate,
                        interval_hz=interval,
                    )

    def test_ambiguous_or_bad_pole_hints_fail_closed(self) -> None:
        bad_hints = (
            coverage.PoleHint(),
            coverage.PoleHint(center_hz=1000.0),
            coverage.PoleHint(center_hz=1000.0, bandwidth_hz=0.0),
            coverage.PoleHint(
                center_hz=1000.0,
                bandwidth_hz=10.0,
                radius=0.9,
                angle_rad=0.1,
                sample_rate_hz=48000.0,
            ),
            coverage.PoleHint(
                radius=1.0,
                angle_rad=0.1,
                sample_rate_hz=48000.0,
            ),
            coverage.PoleHint(
                radius=0.9,
                angle_rad=0.1,
                sample_rate_hz=44100.0,
            ),
        )
        for hint in bad_hints:
            with self.subTest(hint=hint):
                with self.assertRaises(coverage.CoverageInputError):
                    coverage.resolve_pole_hint(
                        hint, expected_sample_rate_hz=48000.0
                    )

    def test_nonfinite_evaluator_output_fails_closed(self) -> None:
        with self.assertRaisesRegex(
            coverage.CoverageInputError, "evaluator magnitude must be finite"
        ):
            coverage.refine_local_extrema(
                lambda _: math.nan,
                [100.0, 200.0],
                max_evaluations=2,
            )


class StateAndBaselineTests(unittest.TestCase):
    def test_quantized_duplicate_state_count_is_explicit(self) -> None:
        states = coverage.summarize_effective_states(
            [0.00, 0.04, 0.06, 0.14], lambda value: round(value, 1)
        )
        self.assertEqual(states.requested_state_count, 4)
        self.assertEqual(states.distinct_effective_state_count, 2)
        self.assertEqual(states.duplicate_effective_state_count, 2)
        self.assertEqual(
            [group.requested_indices for group in states.groups],
            [(0, 1), (2, 3)],
        )

    def test_pooled_median_uses_all_validated_midpoints(self) -> None:
        result = coverage.pooled_median_from_validated_midpoint_groups(
            [[0.0, 0.0, 0.0], [0.4]]
        )
        self.assertEqual(result, 0.0)
        self.assertNotEqual(result, 0.2)

    def test_pooled_median_avoids_finite_even_pair_overflow(self) -> None:
        result = coverage.pooled_median_from_validated_midpoint_groups(
            [[1.0e308, 1.0e308]]
        )
        self.assertTrue(math.isfinite(result))
        self.assertEqual(result, 1.0e308)

    def test_pooled_median_rejects_empty_and_nonfinite_groups(self) -> None:
        for groups in ([], [[0.0], []], [[0.0], [math.inf]]):
            with self.subTest(groups=groups):
                with self.assertRaises(coverage.CoverageInputError):
                    coverage.pooled_median_from_validated_midpoint_groups(groups)

    def test_state_mapper_must_return_hashable_finite_key(self) -> None:
        with self.assertRaises(coverage.CoverageInputError):
            coverage.summarize_effective_states([1], lambda _: [])
        with self.assertRaises(coverage.CoverageInputError):
            coverage.summarize_effective_states([1], lambda _: math.inf)
        with self.assertRaises(coverage.CoverageInputError):
            coverage.summarize_effective_states(
                [1], lambda _: ("band", (1000.0, math.nan))
            )
        with self.assertRaises(coverage.CoverageInputError):
            coverage.summarize_effective_states(
                [1], lambda _: frozenset({1000.0, math.inf})
            )

    def test_nested_canonical_state_key_has_deterministic_repr(self) -> None:
        states = coverage.summarize_effective_states(
            [1], lambda _: ("band", frozenset({2000.0, 1000.0}))
        )
        self.assertEqual(
            states.groups[0].effective_state_repr,
            "('band', frozenset({1000.0, 2000.0}))",
        )


if __name__ == "__main__":
    unittest.main()
