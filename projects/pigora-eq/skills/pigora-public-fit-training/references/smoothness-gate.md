# Quantitative measured EQ smoothness gate

Use with [curve-coverage.md](curve-coverage.md#compact-production-control-shape-gate)
and [measurement-acceptance.md](measurement-acceptance.md) before a new Pigora
fitting/module/product PASS. Root owner addendum
`pigora-eq-compact-extrema-smoothness-20261006-v2` owns this requirement.
This is a separate engineering shape gate. It preserves frozen targets, native
controls, public/inference provenance and the existing magnitude tiers.
Use [smoothness-execution.md](smoothness-execution.md) to construct and preflight
the bound execution plan. V2 clarifies execution prospectively; retained v1
plans, measurements and verdicts are historical and are not edited into v2 PASS.

## Freeze a numerical profile and a measurable grid

Freeze the profile before judging the candidate, keyed by native identity,
filter type, mode, rate and response region. Each applicable metric needs a
finite numeric limit/range, unit, formula/guard version, scope, uncertainty
method, threshold role (`hard_limit` or `refinement_trigger`), and rationale
from independent source/native-control expectations and acquisition resolution.
Do not use a candidate's observed worst value to choose its passing limit.
Missing numeric limits are PENDING, not permission to use visual judgment.

Use type-specific profiles: Bell peak/skirts; Low/High Shelf plateaus and
transition separately; HPF/LPF passband, cutoff and stopband. Preserve supported
resonance, asymmetry, steep cutoff slopes, gain-dependent Prop Q and native
discrete modes. Limits may depend on native gain/Q/bandwidth and region under
a frozen rule. A universal raw-slope/curvature cap cannot describe all these
responses. The 0.2/0.5 dB magnitude tiers are not smoothness thresholds.

Bind a finite frequency grid to each rate, strictly below Nyquist, and include
all required fitting anchors plus the declared exterior/near-Nyquist domain.
Include peak/transition neighborhoods, tails, seams and authored interpolation
knots. Record maximum log-frequency spacing, minimum resolvable feature width,
capture length, extraction/window method, valid signal-to-reference range and
pointwise magnitude uncertainty. Plan local spacing no greater than one eighth
of the narrowest expected feature width in octaves, or freeze a separately
justified equivalent resolution. An FFT bin count or enlarged plot is not
resolution proof. Use longer acquisitions or local stepped-sine measurements
when a narrow/high-Q or low-frequency feature is unresolved. Do not remove a
required quiet/stopband region because it falls below the acquisition floor.

Freeze native-control coordinates, exact effective endpoint readback, nine-
position default tracks, interpolation knots and immediate effective neighbors.
For a reduced interior track, record its review and preserved mandatory states.
Use real detents for discrete controls; for continuous controls freeze the
neighbor step and local half-step refinement. Repeated requested values that
quantize to the same state do not establish neighboring-control coverage.
Bind explicit analysis triplets/stencils and the metric scale/spacing rule to
the grid and profile. Preflight whether propagated uncertainty can support the
limits. Adding closer points can increase derivative uncertainty; refinement
must follow the frozen scale and acquisition-precision strategy, not replace
the estimator with whichever sampling happens to pass.
All curves used for final judgment come from actual production processing;
compiled mathematical probes may locate regions to measure.

## Frequency-direction metrics

Let `x_i = log2(f_i / 1 Hz)`, `m_i` be the unsmoothed measured dB response,
and `u_i` its declared absolute uncertainty bound. Use strictly increasing
frequencies and `h_L = x_i - x_(i-1)`, `h_R = x_(i+1) - x_i`.

```text
s_L = (m_i - m_(i-1)) / h_L
s_R = (m_(i+1) - m_i) / h_R
c_i = 2 * (s_R - s_L) / (h_L + h_R)
w_L = h_R / (h_L + h_R)
w_R = h_L / (h_L + h_R)
d_i = m_i - (w_L * m_(i-1) + w_R * m_(i+1))
```

`s` is dB/octave, `c` is dB/octave², and `d` is a signed local chord departure
in dB. These definitions work on unequal grids; raw sample differences and
unscaled second differences do not. Record signed values and maxima separately
for each declared region, with the exact state/rate/frequency interval.

| Required check | Numeric limits to freeze | Decision purpose |
|---|---|---|
| Slope and slope folds | Allowed signed slope range/envelope, dB/octave | Detect unexpected reversals or a folded skirt/transition; preserve declared steepness |
| Curvature and chord departure | Allowed signed curvature envelope, dB/octave²; chord-departure bound, dB, at the declared spacing | Detect local shoulders, stair steps or bulges that magnitude anchors alone miss |
| Unsupported peaks, dips and shoulders | Prominence/height limit, dB; feature-width and separation resolution, octaves | Classify each extra feature against the declared native topology; derivative sign counts alone are insufficient |
| Exterior/plateau behavior | Allowed offset and ripple ranges, dB; slope range where a plateau/tail is expected | Check both shelves' plateaus, Bell skirts, and pass-filter passband/stopband without imposing Bell endpoint rules |
| Continuous frequency joins | One-sided intercept-jump bound, dB; slope-mismatch bound, dB/octave where the declared law is differentiable | Detect response seams at runtime joins without treating legitimate smooth curvature as a jump |

Define prominence against adjacent enclosing extrema or a frozen local baseline;
freeze search neighborhood, boundary handling and minimum resolvable width.
Also inspect shoulders with chord/slope metrics: a monotone fold need not create
an extra extremum. A feature censored at the finite domain edge has unknown
location/width unless a one-sided method is justified; it cannot silently count
as a resolved peak or a missing required feature.

At a continuous join `x_0`, freeze the estimator/order, minimum samples per
side, initial `h`, refinement budget and a justified one-sided remainder bound.
Use two explicitly nested stencils: distances `(h, h/2)` and `(h/2, h/4)` on
each applicable side. Another estimator needs its exact stencil, weights,
uncertainty and remainder rule frozen before judgment. A two-point zero fit
residual or agreement between refinements is not itself a truncation bound.
Missing a justified bound is PENDING, not zero uncertainty.

For the default linear intercept estimator, with side sign `sigma = -1/+1`:

```text
b_sigma(h) = 2 * m(x_0 + sigma*h/2) - m(x_0 + sigma*h)
u_b_sigma(h) = 2*u(x_0 + sigma*h/2) + u(x_0 + sigma*h)
                + B_sigma*h^2/4
```

`B_sigma` is an independently justified frozen bound on `abs(m''(x))` over
the entire closed one-sided extrapolation interval from the join-side limit
through the farthest sample: `[x_0-h, x_0]` for the left side and
`[x_0, x_0+h]` for the right side. It includes the unsampled gap between the
join and nearest point, not merely the hull of measured stencil points.
Use the declared coordinate units and one-sided regularity assumptions; an
alternate estimator also needs a remainder bound over its complete extrapolation
domain. The bound is not the candidate's sampled curvature maximum. Missing
support for that full domain is PENDING. Form the signed right-minus-left
intercept estimate and add both side uncertainties. Record both stencils;
check their jump intervals are compatible, then judge the declared finer
stencil. Incompatible intervals leave an acquisition/estimator-assumption
finding PENDING. Do not choose the more favorable stencil after seeing results.
For an absolute jump ceiling, clearance requires the entire signed uncertainty
interval inside `[-L, +L]`; an interval wholly outside is FAIL, otherwise PENDING.
Further halvings follow the frozen budget and precision strategy.

Where the declared law is differentiable, compare one-sided slopes too. The
default secant is `(m(x_0+sigma*h)-m(x_0+sigma*h/2))/(sigma*h/2)`, with uncertainty
`2*(u(h)+u(h/2))/h + B_sigma*h`; this includes a conservative derivative
extrapolation remainder. Apply the same finer-stencil/compatibility rule.
A previously evidenced native kink can make only the derivative-matching
metric not applicable; magnitude continuity remains required. These rules also
apply to control joins with `x` replaced by the frozen native coordinate `t`.

Refine a flagged frequency interval and its immediate neighbors with actual
measurements. Recompute metrics at the declared finer spacing and bind both
grids. Chord limits must be spacing-aware; derivatives cannot be made to PASS
by smoothing data, widening grid spacing or discarding a failing region.

## Continuous-control metrics

For every required gain, Q/shape and frequency track, compare whole curves on
the same valid frequency grid. Let `t_i` be the frozen effective native-control
coordinate and `k_L = t_i - t_(i-1)`, `k_R = t_(i+1) - t_i`. Compute at every
frequency the same first derivative, second derivative and middle-chord formulas
above with `h` replaced by `k`. Name units explicitly: dB per gain-dB, per
log2(Q), per octave of frequency, or per normalized native-control unit according
to the declared mapping. Do not mix physical and normalized coordinates.

| Required check | Numeric limits to freeze | Required contexts |
|---|---|---|
| Whole-response neighboring motion | Signed first/second derivative envelopes in declared control units; middle-chord departure, dB | Each consecutive three-state group, including near-neutral and maximum-gain tracks |
| Feature position and width | First derivative, octaves/control-unit; second derivative, octaves/control-unit²; middle-chord departure, octaves; extraction resolution | Bell peak/skirts; shelf transition/plateaus; HPF/LPF cutoff; Prop Q gain-dependent bandwidth |
| Control-knot continuity | Extrapolated one-sided jump, dB, and applicable derivative mismatch per control unit | Every continuous authored interpolation knot with effective neighbors and half-step refinement |
| New features during motion | Unsupported feature prominence/shoulder limits as above | Middle states as well as endpoints, at maximum gain and Q/shape extremes |

For feature location `p_i = log2(feature_hz / 1 Hz)` or declared bandwidth in
octaves, use the same unequal-spacing formulas with `m_i` replaced by `p_i`
and `h` by `k`. Propagate feature-coordinate uncertainty by the same absolute-
weight rules. Raw second differences are not normalized second derivatives.
For example, `p(t)=t^2` at `t=[0,1,3]` has normalized second derivative `2`,
not the raw second difference `7`. A coordinate rescaling must rescale first-
and second-derivative limits by the corresponding first and second powers.

Freeze each feature definition (for example a shelf transition level or cutoff
crossing), uncertainty, expected direction/law and boundary censoring, plus a
state/context applicability predicate justified by independent native evidence
or an authorized frozen law. A legitimately absent feature, such as a neutral
Bell peak under a declared neutral-band law, is `NOT_APPLICABLE` with that rule
ID; do not invent a peak or bandwidth from the requested knob value. Whole-
response, continuity and unsupported-feature checks remain required, so an
unexpected neutral bump can still fail. Acquisition-limited contrast is not
permission to disable a required feature: if the frozen predicate requires it
and extraction is unresolved, the metric is PENDING. Do not change the predicate
or definition after observing a candidate to obtain a pass.

Middle-chord departures are diagnostics unless the source/native law justifies
a hard bound. Frequency motion and Prop Q need not obey linear dB interpolation
or lie between neighboring curves. Compare them to the frozen nonlinear law
and region-specific envelopes. Source-supported exceptions must be identified
before judgment, not invented to waive an observed hard failure. Discrete type,
slope and bypass switches receive their own state/behavior checks; do not impose
continuous derivatives across them. Static curve motion does not certify
click-free automation or physical gestures.

## Propagate uncertainty and apply the gate

For conservative bounded point uncertainties, use:

```text
u_s_L = (u_i + u_(i-1)) / h_L
u_s_R = (u_(i+1) + u_i) / h_R
u_c_i = 2 * (u_s_L + u_s_R) / (h_L + h_R)
u_d_i = u_i + w_L * u_(i-1) + w_R * u_(i+1)
```

Use the same propagation for control differences with `k`. A justified
covariance-aware method is allowed only when its assumptions and method are
frozen; calibration cancellation must not be assumed. Include feature-location,
finite-resolution and one-sided-fit uncertainty, not just PCM quantization.
For a nonnegative upper-bound metric `v <= L`, clearance requires
`v + u_v <= L`; for an allowed signed interval, the whole metric uncertainty
interval must lie inside it. If the interval is wholly outside a hard limit,
report FAIL; if it overlaps the limit, refine or report PENDING. Exact equality
inside the inclusive limit is PASS. These uncertainty rules concern
smoothness; the separate magnitude gate keeps its existing formula and tier.

| Cause | Required status |
|---|---|
| Confirmed nonfinite production output or uncertainty-clear hard-limit violation | FAIL |
| Missing/invalid capture, invalid reference, unresolved acquisition floor, undefined metric caused by acquisition, missing plan/profile input, or uncertainty overlap | PENDING |
| Applicable metric's complete uncertainty interval clears its inclusive hard limit and no trigger is open | PASS |
| A predeclared metric-applicability predicate excludes a legitimately absent native feature | NOT_APPLICABLE with rule ID; retain every other required check |

An undefined extracted dB ratio does not by itself prove nonfinite DSP. Retain
the cause and original evidence; acquisition retries cannot erase a confirmed
production failure. An empty required-metric set cannot establish unit PASS.

A `refinement_trigger` crossing opens a named finding and is PENDING until
refined measurements clear it or independent source evidence / an already
authorized frozen modeling or native-control law permits that exact feature
under the frozen profile. Bind the feature/rule, independent evidence artifact
and existing non-author review. Candidate code, a spline overshoot or a plot
that merely explains how the defect arises may diagnose it but cannot close it.
A trigger is not a
hard acceptance ceiling. A hard-limit violation cannot be waived as a review
footnote. No average, percentile or another passing rate hides the worst failing
row/interval. Report uncertainty-limited regions explicitly.

Freeze refinement limits (intervals, extra states/points, capture length and
neighbor step). Budget exhaustion with an unresolved finding is PENDING.
Preserve failed/pending raw data and flagged controls as regressions. When a
guard changes, perform the existing known-bad/corrected sensitivity check in
curve-coverage; a detector that misses the retained defect is not validated.

## Certificate fields and completion

Record profile/plan/guard IDs and hashes, formulas/coordinates, finite numeric
limits and roles, source/native-law rationale, expected/native features, raw
capture/export/binary/target hashes, exact control/rate/path membership, grid
and resolution, uncertainty bounds, and every required/measured/missing extrema
combination. Each metric row records state, region/interval, signed value,
uncertainty, limit, verdict and any refinement/finding ID. Include per-unit,
per-rate and global worst rows, raw overlays and control tracks, independent
review, reused acquisition keys, hard failures and explained/unresolved flags.

Aggregate required rows/units/rates and certificate constituents deterministically:
any FAIL gives FAIL; otherwise any PENDING/missing required constituent gives
PENDING; otherwise all required applicable constituents PASS gives PASS. Only
predeclared `NOT_APPLICABLE` rows are excluded from this aggregation; retain
their reasons. Missing coverage is reported even when another row already FAILs.
The measured certificate requires all three named results:

```text
magnitude_status == PASS
compact_matrix_status == PASS  # complete required effective states and extrema
smoothness_status == PASS      # all hard metrics clear; no pending findings
```

Retain original public/inference fitting verdicts separately. A finite PASS
proves only the frozen sampled plan; it does not prove every continuous control
position, physical-hardware equivalence, realtime capacity or deployment.
