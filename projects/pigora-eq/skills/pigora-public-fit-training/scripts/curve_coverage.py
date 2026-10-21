#!/usr/bin/env python3
"""Deterministic diagnostic coverage helpers for Pigora curve evaluation.

This module constructs additional *evaluation* probes around frozen frequency
anchors and declared pole locations.  It does not construct target magnitudes,
change a frozen target grid, or adjudicate a public-fit/engineering gate.
Dataset-specific adapters supply the scalar magnitude evaluator.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass, field
from typing import Any, Callable, Hashable, Iterable, Sequence


class CoverageInputError(ValueError):
    """Raised when a coverage request is ambiguous or numerically invalid."""


class _EvaluationBudgetExhausted(RuntimeError):
    pass


@dataclass(frozen=True)
class FrequencyInterval:
    low_hz: float
    high_hz: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "low_hz": self.low_hz,
            "high_hz": self.high_hz,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class PoleHint:
    """A declared pole neighborhood, in direct or digital-pole form.

    Supply exactly one form:

    * ``center_hz`` and ``bandwidth_hz``; or
    * ``radius``, ``angle_rad``, and ``sample_rate_hz``.

    For the digital form, the neighborhood center is ``angle * fs / (2*pi)``
    and the radial decay-width proxy is ``-fs * log(radius) / pi``.  The proxy
    is for probe placement only; it is not asserted to be a target 3 dB width.
    """

    center_hz: float | None = None
    bandwidth_hz: float | None = None
    radius: float | None = None
    angle_rad: float | None = None
    sample_rate_hz: float | None = None
    label: str = ""


@dataclass(frozen=True)
class ResolvedPoleHint:
    center_hz: float
    neighborhood_width_hz: float
    method: str
    label: str


@dataclass(frozen=True)
class FrequencyResolution:
    subdivisions_per_anchor_interval: int
    maximum_log_step_ratio: float
    pole_bandwidth_multipliers: tuple[float, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "subdivisions_per_anchor_interval": (
                self.subdivisions_per_anchor_interval
            ),
            "maximum_log_step_ratio": self.maximum_log_step_ratio,
            "pole_bandwidth_multipliers": list(
                self.pole_bandwidth_multipliers
            ),
        }


@dataclass(frozen=True)
class FrequencyProbePlan:
    frequencies_hz: tuple[float, ...]
    intervals_hz: tuple[tuple[float, float], ...]
    bounds_hz: tuple[float, float]
    sample_rate_hz: float
    anchor_count: int
    pole_hints_requested: int
    pole_hints_in_bounds: int
    method: str
    resolution: FrequencyResolution


@dataclass(frozen=True)
class FrequencySample:
    frequency_hz: float
    magnitude_db: float

    def to_dict(self) -> dict[str, float]:
        return {
            "frequency_hz": self.frequency_hz,
            "magnitude_db": self.magnitude_db,
        }


@dataclass(frozen=True)
class LocalExtremum:
    kind: str
    frequency_hz: float
    magnitude_db: float
    bracket_low_hz: float
    bracket_high_hz: float
    converged: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "frequency_hz": self.frequency_hz,
            "magnitude_db": self.magnitude_db,
            "bracket_low_hz": self.bracket_low_hz,
            "bracket_high_hz": self.bracket_high_hz,
            "converged": self.converged,
        }


@dataclass(frozen=True)
class RefinementResult:
    initial_frequencies_hz: tuple[float, ...]
    bounds_hz: tuple[float, float]
    samples: tuple[FrequencySample, ...]
    extrema: tuple[LocalExtremum, ...]
    unresolved_intervals: tuple[FrequencyInterval, ...]
    evaluation_count: int
    max_evaluations: int
    budget_exhausted: bool
    method: str
    resolution_hz: float


@dataclass(frozen=True)
class EffectiveStateGroup:
    effective_state_repr: str
    requested_indices: tuple[int, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "effective_state_repr": self.effective_state_repr,
            "requested_indices": list(self.requested_indices),
        }


@dataclass(frozen=True)
class StateCoverage:
    requested_state_count: int
    distinct_effective_state_count: int
    duplicate_effective_state_count: int
    groups: tuple[EffectiveStateGroup, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "requested_state_count": self.requested_state_count,
            "distinct_effective_state_count": self.distinct_effective_state_count,
            "duplicate_effective_state_count": self.duplicate_effective_state_count,
            "groups": [group.to_dict() for group in self.groups],
        }


@dataclass(frozen=True)
class CoverageReport:
    """Serializable diagnostic report; deliberately has no PASS field."""

    frequency_method: str
    frequency_resolution: FrequencyResolution
    anchor_count: int
    initial_probe_count: int
    evaluated_probe_count: int
    requested_state_count: int | None
    distinct_effective_state_count: int | None
    duplicate_effective_state_count: int | None
    unresolved_intervals: tuple[FrequencyInterval, ...]
    budget_exhausted: bool
    refinement_resolution_hz: float | None
    refinement_max_evaluations: int | None
    evaluation_status: str
    formal_gate_status: str = field(default="not_adjudicated", init=False)
    diagnostic_only: bool = field(default=True, init=False)
    all_continuous_extrema_guaranteed: bool = field(default=False, init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "frequency_method": self.frequency_method,
            "frequency_resolution": self.frequency_resolution.to_dict(),
            "anchor_count": self.anchor_count,
            "initial_probe_count": self.initial_probe_count,
            "evaluated_probe_count": self.evaluated_probe_count,
            "requested_state_count": self.requested_state_count,
            "distinct_effective_state_count": (
                self.distinct_effective_state_count
            ),
            "duplicate_effective_state_count": (
                self.duplicate_effective_state_count
            ),
            "unresolved_intervals": [
                interval.to_dict() for interval in self.unresolved_intervals
            ],
            "budget_exhausted": self.budget_exhausted,
            "refinement_resolution_hz": self.refinement_resolution_hz,
            "refinement_max_evaluations": self.refinement_max_evaluations,
            "evaluation_status": self.evaluation_status,
            "formal_gate_status": self.formal_gate_status,
            "diagnostic_only": self.diagnostic_only,
            "all_continuous_extrema_guaranteed": (
                self.all_continuous_extrema_guaranteed
            ),
        }


def _finite_float(value: Any, field: str) -> float:
    if isinstance(value, bool):
        raise CoverageInputError(f"{field} must be a finite number")
    try:
        parsed = float(value)
    except (TypeError, ValueError) as error:
        raise CoverageInputError(f"{field} must be a finite number") from error
    if not math.isfinite(parsed):
        raise CoverageInputError(f"{field} must be finite")
    return parsed


def resolve_pole_hint(
    hint: PoleHint,
    *,
    expected_sample_rate_hz: float,
) -> ResolvedPoleHint:
    """Validate and convert one declared pole hint into a probe neighborhood."""

    expected_rate = _finite_float(
        expected_sample_rate_hz, "expected_sample_rate_hz"
    )
    if expected_rate <= 0.0:
        raise CoverageInputError("expected_sample_rate_hz must be positive")

    has_direct = hint.center_hz is not None or hint.bandwidth_hz is not None
    has_digital = any(
        value is not None
        for value in (hint.radius, hint.angle_rad, hint.sample_rate_hz)
    )
    if has_direct == has_digital:
        raise CoverageInputError(
            "pole hint must use exactly one of center/bandwidth or "
            "radius/angle/sample-rate"
        )

    if has_direct:
        if hint.center_hz is None or hint.bandwidth_hz is None:
            raise CoverageInputError(
                "direct pole hint requires both center_hz and bandwidth_hz"
            )
        center = _finite_float(hint.center_hz, "pole center_hz")
        width = _finite_float(hint.bandwidth_hz, "pole bandwidth_hz")
        method = "declared-center-bandwidth"
    else:
        if (
            hint.radius is None
            or hint.angle_rad is None
            or hint.sample_rate_hz is None
        ):
            raise CoverageInputError(
                "digital pole hint requires radius, angle_rad, and "
                "sample_rate_hz"
            )
        radius = _finite_float(hint.radius, "pole radius")
        angle = _finite_float(hint.angle_rad, "pole angle_rad")
        rate = _finite_float(hint.sample_rate_hz, "pole sample_rate_hz")
        if not 0.0 < radius < 1.0:
            raise CoverageInputError("pole radius must be strictly between 0 and 1")
        if not 0.0 < angle < math.pi:
            raise CoverageInputError("pole angle_rad must be between 0 and pi")
        if rate <= 0.0:
            raise CoverageInputError("pole sample_rate_hz must be positive")
        if not math.isclose(
            rate, expected_rate, rel_tol=1.0e-12, abs_tol=1.0e-9
        ):
            raise CoverageInputError(
                "pole sample_rate_hz must match the probe-plan sample rate"
            )
        center = angle * rate / (2.0 * math.pi)
        width = -rate * math.log(radius) / math.pi
        method = "digital-radius-angle-decay-width"

    if center <= 0.0 or center >= 0.5 * expected_rate:
        raise CoverageInputError("resolved pole center must be below Nyquist")
    if width <= 0.0:
        raise CoverageInputError("resolved pole neighborhood width must be positive")
    return ResolvedPoleHint(center, width, method, hint.label)


def build_frequency_probes(
    anchors_hz: Sequence[float],
    *,
    sample_rate_hz: float,
    interval_hz: tuple[float, float] | None = None,
    subdivisions_per_interval: int = 1,
    pole_hints: Sequence[PoleHint] = (),
    pole_bandwidth_multipliers: Sequence[float] = (
        -2.0,
        -1.0,
        -0.5,
        0.0,
        0.5,
        1.0,
        2.0,
    ),
) -> FrequencyProbePlan:
    """Build deterministic log subdivisions plus declared-pole probes."""

    rate = _finite_float(sample_rate_hz, "sample_rate_hz")
    if rate <= 0.0:
        raise CoverageInputError("sample_rate_hz must be positive")
    if isinstance(subdivisions_per_interval, bool) or not isinstance(
        subdivisions_per_interval, int
    ):
        raise CoverageInputError("subdivisions_per_interval must be an integer")
    if subdivisions_per_interval < 0:
        raise CoverageInputError("subdivisions_per_interval cannot be negative")

    anchors = tuple(sorted(_finite_float(value, "anchor") for value in anchors_hz))
    if len(anchors) < 2:
        raise CoverageInputError("at least two frequency anchors are required")
    if any(value <= 0.0 for value in anchors):
        raise CoverageInputError("frequency anchors must be positive")
    if any(left == right for left, right in zip(anchors, anchors[1:])):
        raise CoverageInputError("frequency anchors must be distinct")

    if interval_hz is None:
        low, high = anchors[0], anchors[-1]
    else:
        if len(interval_hz) != 2:
            raise CoverageInputError("interval_hz must contain low and high")
        low = _finite_float(interval_hz[0], "interval low")
        high = _finite_float(interval_hz[1], "interval high")
    if not 0.0 < low < high:
        raise CoverageInputError("frequency interval must satisfy 0 < low < high")
    if high >= 0.5 * rate:
        raise CoverageInputError("frequency interval high must be below Nyquist")
    if anchors[0] < low or anchors[-1] > high:
        raise CoverageInputError("all anchors must lie inside interval_hz")

    multipliers = tuple(
        _finite_float(value, "pole bandwidth multiplier")
        for value in pole_bandwidth_multipliers
    )
    if not multipliers:
        raise CoverageInputError("pole_bandwidth_multipliers cannot be empty")
    multipliers = tuple(sorted(set(multipliers)))
    if 0.0 not in multipliers:
        raise CoverageInputError(
            "pole_bandwidth_multipliers must include 0 to probe the center"
        )

    division_knots = tuple(sorted(set((low, *anchors, high))))
    frequencies: set[float] = set(division_knots)
    log_segments = subdivisions_per_interval + 1
    maximum_log_step_ratio = 1.0
    for left, right in zip(division_knots, division_knots[1:]):
        step = (math.log(right) - math.log(left)) / log_segments
        maximum_log_step_ratio = max(maximum_log_step_ratio, math.exp(step))
        for index in range(1, log_segments):
            frequencies.add(math.exp(math.log(left) + index * step))

    resolved = [
        resolve_pole_hint(hint, expected_sample_rate_hz=rate)
        for hint in pole_hints
    ]
    in_bounds = 0
    for hint in resolved:
        if not low <= hint.center_hz <= high:
            continue
        in_bounds += 1
        for multiplier in multipliers:
            frequency = hint.center_hz + multiplier * hint.neighborhood_width_hz
            if low <= frequency <= high and frequency < 0.5 * rate:
                frequencies.add(frequency)

    ordered = tuple(sorted(frequencies))
    intervals = tuple(zip(ordered, ordered[1:]))
    method = "log-anchor-subdivision"
    if resolved:
        method += "+declared-pole-neighborhoods"
    return FrequencyProbePlan(
        frequencies_hz=ordered,
        intervals_hz=intervals,
        bounds_hz=(low, high),
        sample_rate_hz=rate,
        anchor_count=len(anchors),
        pole_hints_requested=len(resolved),
        pole_hints_in_bounds=in_bounds,
        method=method,
        resolution=FrequencyResolution(
            subdivisions_per_anchor_interval=subdivisions_per_interval,
            maximum_log_step_ratio=maximum_log_step_ratio,
            pole_bandwidth_multipliers=multipliers,
        ),
    )


def refine_local_extrema(
    evaluator: Callable[[float], float],
    initial_frequencies_hz: Sequence[float],
    *,
    interval_hz: tuple[float, float] | None = None,
    max_evaluations: int = 512,
    max_iterations_per_interval: int = 48,
    frequency_tolerance_hz: float = 1.0e-4,
) -> RefinementResult:
    """Refine sampled local extrema in log-frequency with a hard budget.

    Candidate brackets come only from the supplied probes.  Therefore, an
    unprobed extremum can still be missed even when this function converges.
    """

    if not callable(evaluator):
        raise CoverageInputError("evaluator must be callable")
    for value, field in (
        (max_evaluations, "max_evaluations"),
        (max_iterations_per_interval, "max_iterations_per_interval"),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise CoverageInputError(f"{field} must be a positive integer")
    tolerance = _finite_float(frequency_tolerance_hz, "frequency_tolerance_hz")
    if tolerance <= 0.0:
        raise CoverageInputError("frequency_tolerance_hz must be positive")

    frequencies = tuple(
        sorted(set(_finite_float(value, "initial frequency")
                   for value in initial_frequencies_hz))
    )
    if len(frequencies) < 2 or frequencies[0] <= 0.0:
        raise CoverageInputError(
            "at least two distinct positive initial frequencies are required"
        )
    if interval_hz is None:
        lower, upper = frequencies[0], frequencies[-1]
    else:
        if len(interval_hz) != 2:
            raise CoverageInputError("interval_hz must contain low and high")
        lower = _finite_float(interval_hz[0], "interval low")
        upper = _finite_float(interval_hz[1], "interval high")
        if not 0.0 < lower < upper:
            raise CoverageInputError("frequency interval must satisfy 0 < low < high")
        if frequencies[0] < lower or frequencies[-1] > upper:
            raise CoverageInputError("initial frequencies must lie inside interval_hz")

    cache: dict[float, float] = {}

    def evaluate(frequency_hz: float) -> float:
        if frequency_hz in cache:
            return cache[frequency_hz]
        if len(cache) >= max_evaluations:
            raise _EvaluationBudgetExhausted
        try:
            raw = evaluator(frequency_hz)
        except Exception as error:
            raise CoverageInputError(
                f"evaluator failed at {frequency_hz:.12g} Hz: {error}"
            ) from error
        value = _finite_float(raw, "evaluator magnitude")
        cache[frequency_hz] = value
        return value

    unresolved: list[FrequencyInterval] = []
    budget_exhausted = False
    try:
        for frequency in frequencies:
            evaluate(frequency)
    except _EvaluationBudgetExhausted:
        budget_exhausted = True
        unresolved.append(
            FrequencyInterval(lower, upper, "initial probe budget exhausted")
        )

    extrema: list[LocalExtremum] = []
    if not budget_exhausted:
        candidates: list[tuple[str, float, float]] = []
        for left, middle, right in zip(
            frequencies, frequencies[1:], frequencies[2:]
        ):
            left_value = cache[left]
            middle_value = cache[middle]
            right_value = cache[right]
            if (
                middle_value >= left_value
                and middle_value >= right_value
                and (middle_value > left_value or middle_value > right_value)
            ):
                candidates.append(("maximum", left, right))
            elif (
                middle_value <= left_value
                and middle_value <= right_value
                and (middle_value < left_value or middle_value < right_value)
            ):
                candidates.append(("minimum", left, right))

        golden_fraction = (math.sqrt(5.0) - 1.0) / 2.0
        for candidate_index, (kind, bracket_low, bracket_high) in enumerate(
            candidates
        ):
            log_low = math.log(bracket_low)
            log_high = math.log(bracket_high)
            converged = False
            try:
                for _ in range(max_iterations_per_interval):
                    if math.exp(log_high) - math.exp(log_low) <= tolerance:
                        converged = True
                        break
                    log_one = log_high - golden_fraction * (log_high - log_low)
                    log_two = log_low + golden_fraction * (log_high - log_low)
                    frequency_one = math.exp(log_one)
                    frequency_two = math.exp(log_two)
                    value_one = evaluate(frequency_one)
                    value_two = evaluate(frequency_two)
                    if kind == "maximum":
                        choose_right = value_one < value_two
                    else:
                        choose_right = value_one > value_two
                    if choose_right:
                        log_low = log_one
                    else:
                        log_high = log_two
                if not converged:
                    converged = (
                        math.exp(log_high) - math.exp(log_low) <= tolerance
                    )
            except _EvaluationBudgetExhausted:
                budget_exhausted = True
                unresolved.append(
                    FrequencyInterval(
                        math.exp(log_low),
                        math.exp(log_high),
                        "local refinement budget exhausted",
                    )
                )
                for remaining_kind, remaining_low, remaining_high in candidates[
                    candidate_index + 1:
                ]:
                    unresolved.append(
                        FrequencyInterval(
                            remaining_low,
                            remaining_high,
                            "not started after budget exhaustion "
                            f"({remaining_kind})",
                        )
                    )
                break

            bracket_samples = [
                (frequency, magnitude)
                for frequency, magnitude in cache.items()
                if bracket_low <= frequency <= bracket_high
            ]
            chooser = max if kind == "maximum" else min
            best_frequency, best_value = chooser(
                bracket_samples, key=lambda item: item[1]
            )
            extrema.append(
                LocalExtremum(
                    kind=kind,
                    frequency_hz=best_frequency,
                    magnitude_db=best_value,
                    bracket_low_hz=bracket_low,
                    bracket_high_hz=bracket_high,
                    converged=converged,
                )
            )
            if not converged:
                unresolved.append(
                    FrequencyInterval(
                        math.exp(log_low),
                        math.exp(log_high),
                        "local refinement iteration limit reached",
                    )
                )

    samples = tuple(
        FrequencySample(frequency, magnitude)
        for frequency, magnitude in sorted(cache.items())
    )
    return RefinementResult(
        initial_frequencies_hz=frequencies,
        bounds_hz=(lower, upper),
        samples=samples,
        extrema=tuple(extrema),
        unresolved_intervals=tuple(unresolved),
        evaluation_count=len(cache),
        max_evaluations=max_evaluations,
        budget_exhausted=budget_exhausted,
        method="bounded-golden-section-log-frequency",
        resolution_hz=tolerance,
    )


def summarize_effective_states(
    requested_states: Sequence[Any],
    effective_state: Callable[[Any], Hashable] | None = None,
) -> StateCoverage:
    """Report requested controls that collapse to the same effective state."""

    if not requested_states:
        raise CoverageInputError("requested_states cannot be empty")
    mapper = effective_state if effective_state is not None else lambda value: value
    groups: dict[Hashable, list[int]] = {}
    for index, requested in enumerate(requested_states):
        effective = mapper(requested)
        _validate_canonical_effective_key(effective, "effective state")
        try:
            hash(effective)
        except TypeError as error:
            raise CoverageInputError("effective states must be hashable") from error
        groups.setdefault(effective, []).append(index)

    rendered = tuple(
        EffectiveStateGroup(_canonical_key_repr(effective), tuple(indices))
        for effective, indices in groups.items()
    )
    requested_count = len(requested_states)
    distinct_count = len(rendered)
    return StateCoverage(
        requested_state_count=requested_count,
        distinct_effective_state_count=distinct_count,
        duplicate_effective_state_count=requested_count - distinct_count,
        groups=rendered,
    )


def _validate_canonical_effective_key(value: Any, path: str) -> None:
    """Reject non-canonical keys and non-finite numbers at any nesting depth."""

    if value is None or isinstance(value, (bool, int, str, bytes)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise CoverageInputError(f"{path} contains a non-finite float")
        return
    if isinstance(value, complex):
        if not math.isfinite(value.real) or not math.isfinite(value.imag):
            raise CoverageInputError(f"{path} contains a non-finite complex value")
        return
    if isinstance(value, tuple):
        for index, item in enumerate(value):
            _validate_canonical_effective_key(item, f"{path}[{index}]")
        return
    if isinstance(value, frozenset):
        for item in value:
            _validate_canonical_effective_key(item, f"{path} frozenset item")
        return
    raise CoverageInputError(
        f"{path} must use canonical finite primitives, tuples, or frozensets"
    )


def _canonical_key_repr(value: Any) -> str:
    if isinstance(value, tuple):
        body = ", ".join(_canonical_key_repr(item) for item in value)
        if len(value) == 1:
            body += ","
        return f"({body})"
    if isinstance(value, frozenset):
        rendered = sorted(_canonical_key_repr(item) for item in value)
        return "frozenset({" + ", ".join(rendered) + "})"
    return repr(value)


def pooled_median_from_validated_midpoint_groups(
    midpoint_groups: Iterable[Iterable[float]],
) -> float:
    """Pool finite, already-validated midpoint observations and take a median.

    This function is only an aggregation helper.  It does not validate strict
    boost/cut pairing keys, equal gain magnitudes, vertex alignment, provenance,
    or whether a group is eligible for the paired-midpoint contract.
    """

    pooled: list[float] = []
    group_count = 0
    for group_index, group in enumerate(midpoint_groups):
        values = [
            _finite_float(value, f"midpoint group {group_index} value")
            for value in group
        ]
        if not values:
            raise CoverageInputError(
                f"midpoint group {group_index} cannot be empty"
            )
        group_count += 1
        pooled.extend(values)
    if group_count == 0:
        raise CoverageInputError("at least one validated midpoint group is required")
    pooled.sort()
    middle = len(pooled) // 2
    if len(pooled) % 2:
        result = pooled[middle]
    else:
        # Halving before addition prevents a finite same-sign pair such as
        # [1e308, 1e308] from overflowing while calculating its midpoint.
        result = math.fsum((0.5 * pooled[middle - 1], 0.5 * pooled[middle]))
    if not math.isfinite(result):
        raise CoverageInputError("pooled midpoint median must be finite")
    return result


def make_coverage_report(
    plan: FrequencyProbePlan,
    *,
    refinement: RefinementResult | None = None,
    state_coverage: StateCoverage | None = None,
) -> CoverageReport:
    """Combine frequency and effective-state diagnostics without adjudication."""

    method = plan.method
    unresolved: tuple[FrequencyInterval, ...] = (
        FrequencyInterval(
            plan.bounds_hz[0],
            plan.bounds_hz[1],
            "frequency probes constructed but not evaluated",
        ),
    )
    budget_exhausted = False
    evaluated_count = 0
    refinement_resolution_hz: float | None = None
    refinement_max_evaluations: int | None = None
    evaluation_status = "not_evaluated"
    if refinement is not None:
        if refinement.initial_frequencies_hz != plan.frequencies_hz:
            raise CoverageInputError(
                "refinement initial frequencies do not match the probe plan"
            )
        if refinement.bounds_hz != plan.bounds_hz:
            raise CoverageInputError(
                "refinement bounds do not match the probe plan"
            )
        method += "+" + refinement.method
        unresolved = refinement.unresolved_intervals
        budget_exhausted = refinement.budget_exhausted
        evaluated_count = refinement.evaluation_count
        refinement_resolution_hz = refinement.resolution_hz
        refinement_max_evaluations = refinement.max_evaluations
        if refinement.budget_exhausted:
            evaluation_status = "incomplete_budget_exhausted"
        elif refinement.unresolved_intervals:
            evaluation_status = "incomplete_unresolved_intervals"
        else:
            evaluation_status = "evaluated_discovered_brackets"
    return CoverageReport(
        frequency_method=method,
        frequency_resolution=plan.resolution,
        anchor_count=plan.anchor_count,
        initial_probe_count=len(plan.frequencies_hz),
        evaluated_probe_count=evaluated_count,
        requested_state_count=(
            state_coverage.requested_state_count if state_coverage else None
        ),
        distinct_effective_state_count=(
            state_coverage.distinct_effective_state_count
            if state_coverage
            else None
        ),
        duplicate_effective_state_count=(
            state_coverage.duplicate_effective_state_count
            if state_coverage
            else None
        ),
        unresolved_intervals=unresolved,
        budget_exhausted=budget_exhausted,
        refinement_resolution_hz=refinement_resolution_hz,
        refinement_max_evaluations=refinement_max_evaluations,
        evaluation_status=evaluation_status,
    )


def _self_test() -> dict[str, Any]:
    true_center_hz = 1163.38
    width_hz = 0.38

    def narrow_resonance(frequency_hz: float) -> float:
        half_width = 0.5 * width_hz
        return 12.0 / (
            1.0 + ((frequency_hz - true_center_hz) / half_width) ** 2
        )

    coarse = build_frequency_probes(
        [1141.0, 1186.0],
        sample_rate_hz=48000.0,
        subdivisions_per_interval=0,
    )
    coarse_peak = max(narrow_resonance(f) for f in coarse.frequencies_hz)
    if coarse_peak >= 0.1:
        raise AssertionError("coarse anchor-only grid unexpectedly saw resonance")

    hinted = build_frequency_probes(
        [1141.0, 1186.0],
        sample_rate_hz=48000.0,
        subdivisions_per_interval=0,
        pole_hints=[PoleHint(center_hz=1163.30, bandwidth_hz=width_hz)],
    )
    refined = refine_local_extrema(
        narrow_resonance,
        hinted.frequencies_hz,
        interval_hz=hinted.bounds_hz,
        max_evaluations=160,
        frequency_tolerance_hz=1.0e-5,
    )
    maxima = [item for item in refined.extrema if item.kind == "maximum"]
    if not maxima:
        raise AssertionError("declared pole probes did not bracket the resonance")
    peak = max(maxima, key=lambda item: item.magnitude_db)
    if abs(peak.frequency_hz - true_center_hz) > 0.01:
        raise AssertionError("local refinement did not locate the narrow resonance")

    states = summarize_effective_states(
        [0.00, 0.04, 0.06, 0.14], lambda value: round(value, 1)
    )
    if states.requested_state_count != 4 or states.distinct_effective_state_count != 2:
        raise AssertionError("effective-state duplicate accounting failed")
    if pooled_median_from_validated_midpoint_groups(
        [[0.0, 0.0, 0.0], [0.4]]
    ) != 0.0:
        raise AssertionError("pooled midpoint median weighted groups incorrectly")

    budgeted = refine_local_extrema(
        narrow_resonance,
        hinted.frequencies_hz,
        interval_hz=hinted.bounds_hz,
        max_evaluations=len(hinted.frequencies_hz) + 1,
        frequency_tolerance_hz=1.0e-9,
    )
    if not budgeted.budget_exhausted or not budgeted.unresolved_intervals:
        raise AssertionError("refinement did not stop and report exhausted budget")

    report = make_coverage_report(
        hinted, refinement=refined, state_coverage=states
    )
    return {
        "selftest": "ok",
        "coarse_peak_db": coarse_peak,
        "refined_peak_hz": peak.frequency_hz,
        "refined_peak_db": peak.magnitude_db,
        "diagnostic_report": report.to_dict(),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run deterministic synthetic diagnostics (not a fit adjudication)",
    )
    arguments = parser.parse_args(argv)
    if not arguments.self_test:
        parser.error("use --self-test; import this module for dataset adapters")
    print(json.dumps(_self_test(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
