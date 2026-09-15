# Diagnostic curve coverage

Use `scripts/curve_coverage.py` when a fitted mathematical response needs
diagnostic probes between frozen source anchors or when requested controls may
collapse to fewer effective runtime states. The helper is standard-library
only and is intended to be imported by a dataset-specific evaluator. This
relative path is resolved from the skill directory containing `SKILL.md`.

It is deliberately not a public-fit validator. It does not create target
magnitudes, add rows to `public-fit-domain.csv`, modify an inference target, or
turn a diagnostic result into a public-fit or product pass. A finite probe set
cannot mathematically guarantee every extremum of an arbitrary continuous
response. Its report therefore fixes `formal_gate_status=not_adjudicated`,
`diagnostic_only=true`, and `all_continuous_extrema_guaranteed=false`.

## Compact production control-shape gate

Mandatory before a new or changed EQ response/control law receives module or
product PASS. This is a separate engineering gate; it neither reduces frozen
row/rate coverage nor upgrades public-fit. Reuse matching existing results;
add only missing coverage. Historical receipts retain their original scope.
A credible new in-scope shape finding returns the current module/gate decision
to PENDING until adjudicated; an old PASS remains historical, not current
clearance. Preserve its receipt and the separate public-fit state.
The diagnostic helper above remains diagnostic-only: the owning production
verifier and reviewed receipt must explicitly adjudicate this gate.

### Small default matrix

The acceptance unit is native band/control identity × filter type × native
mode. Explicitly inventory Bell, Low Shelf, High Shelf, HPF and LPF wherever
supported. A band's Bell/Shelf switch creates separate units; HPF and LPF are
separate units too. Count and adjudicate each unit independently, including
Constant Q/Prop Q and every native discrete slope setting. A passing Bell or
shared kernel never covers another type. Deduplicate samples within a unit,
not identities across units.

| Filter type | Compact base axes | Shape region to judge |
|---|---|---|
| Bell | Gain × frequency × native Q; Constant/Prop Q separately | Peak and both skirts |
| Low Shelf / High Shelf, separately | Gain × frequency × native Q or shelf Slope when present | Both plateaus and transition, including supported resonance |
| HPF / LPF, separately | Three cutoff positions × every native dB/oct slope setting × three native Q/resonance positions when adjustable | Passband, cutoff transition and stopband |

Shelf Slope and HPF/LPF dB/oct slope are distinct native controls, never aliases.
For shelves, apply the gain matrix below with the native shape control replacing
Q. If Q and Slope are independently adjustable, sweep each with the other at
its middle value and add their four endpoint combinations at middle frequency
and the largest base gain; do not silently collapse either axis. Discrete slope
settings are all covered, continuous shape controls start at 0/0.5/1. HPF/LPF
have no invented gain axis: use their cutoff/shape axes for base states, corner
probes and nine-position tracks. Sweep each adjustable pass-filter axis at the
other axes' middle settings, retaining every discrete slope setting in the base.
Absent controls contribute one value and no traversal track.
Where Off/Bypass or a type switch exists, add one representative transition and
state readback per supported switch position, plus the Off detent and adjacent
active endpoint when present; reuse matching control/state receipts. Off is
not a substitute for an active HPF/LPF low/high cutoff limit. In that same
representative state, assert the production response matches the declared
Off/Bypass behavior, the adjacent active endpoint remains active, and a type or
slope switch selects its intended response unit/setting. Reuse curves/readback.

- For Bell and shelves, start with 27 states: +3/+6/+12 dB × narrow/middle/wide Q × low/middle/high
  frequency. Use native control positions 0/0.5/1 for Q and frequency and record
  actual values (log-frequency midpoint when the native law is logarithmic).
  Respect native ranges/detents and authorized gain support; substitute the
  nearest legal value and deduplicate, recording substitutions. Fixed or absent
  controls contribute one value, never an invented Q or mode. For cut-only
  identities mirror the base gain signs and use that supported family on tracks;
  do not add the separate nine-state cut check again.
- For Bell/shelves with cuts, add -6 dB at the same nine Q/frequency pairs. Expand cuts to
  their own 27-state matrix only when their topology/control law differs from
  boost or a probe exposes asymmetry unexplained by the declared model.
- For Bell/shelves at middle frequency/shape, add neutral, nearest effective values on both sides
  of zero on each supported side, and supported positive/negative gain limits. Do not multiply these
  extra gains across the whole matrix.
- For Bell/shelves, add three one-axis tracks per mode: gain across its supported range at middle
  frequency/Q; Q across its range at middle frequency and the largest legal
  base-matrix boost; frequency across its range at narrow Q and that gain.
  Start each track at nine equally spaced native control positions. Also probe
  every authored model/control-law interpolation knot (not every host detent)
  and its immediate effective neighbors along the
  relevant track. For a continuous control, freeze the small neighbor step;
  for a detented control, use adjacent real detents. Deduplicate overlapping
  states. Fixed/absent axes have no traversal track. Prop Q's Q track and
  gain track are both required when those axes are adjustable.
- Include exact user-reported failure states and immediate neighbors on the
  implicated axis, with their original rate/mode. Group bulk diagnostic flags
  by the same defect region: retain one frozen reproducer context, each
  implicated detent and boundary neighbors (or a local refined continuous
  track), and map the remaining flags to that group. Add other gain/frequency/
  rate contexts only for a distinct dependency; preserve all raw flags without
  replaying thousands of equivalent states. On a shared kernel defect, use one
  mapped reproducer per affected sibling identity first; do not launch a whole
  new matrix for unrelated passing bands.

Run this base plan at 48 kHz. At each other supported rate, reuse the existing
rate validation. For Bell/shelves, add only low/high-frequency × native
shape-endpoint probes at the largest supported base gain and representative cut
when available. For HPF/LPF, add low/high-cutoff × native shape-endpoint probes
at every discrete slope setting, without a gain axis. Record unsupported
sides/axes as not applicable and include rate-specific historical failures. Expand only the implicated axis, mode, band, or rate when a failure,
unresolved feature, or distinct rate-dependent implementation warrants it.
Existing broader frozen validation obligations still apply.

### Judge shape and motion from the same sampled curves

Freeze the finite frequency domain, sampling resolution, shape metrics and
model-specific limits before judging the candidate. Cover the type-specific
regions in the table and declared exterior, not just the requested center;
include
pole-aware/local refinement for narrow features and the declared near-Nyquist
region. Reuse one curve export for all metrics rather than adding separate runs.

Check finite/bounded output; extra extrema, shoulders/plateaus and unsupported
exterior offsets; slope/curvature versus log-frequency; and changes of the
whole response, peak location and bandwidth along each control track. Finite
and monotone curves can still have a visible slope fold. Use prominence and
resolution-aware limits, not raw derivative sign counts or a universal single-
peak/symmetry/nonnegative-boost rule. The public/inference 0.2 dB magnitude gate
is not a derivative threshold. Preserve source-supported asymmetry and tails;
Prop Q bandwidth is judged against its declared gain-dependent law. Do not
require shelves or pass filters to have a Bell peak or return to 0 dB at both
ends. Use plateau/cutoff/transition metrics where peak location or bandwidth is
not meaningful, and preserve source-supported resonant overshoot.

Reuse each consecutive three-state group on an existing control track to compare
its middle curve with both neighbors on the same frequency grid. Flag unexpected
local bulges/dips or peak-location jumps using the predeclared control law and
resolution-aware limits. This adds analysis, not new sampled states. Do not
require universal containment within the two neighboring curves or assume linear
dB interpolation: frequency motion and Prop Q may legitimately leave that
envelope. Treat unexplained departures under the same pending/refinement rule
below; the comparison is a shape diagnostic, not an external fidelity target.

Refine only a flagged interval and its immediate control neighbors, under a
recorded finite budget. Keep new failure states as regressions. Missing required
states, non-finite output, hard guard failures, budget-exhausted unresolved
intervals, or unexplained shape flags prevent module/product PASS. A diagnostic
flag may be closed by the existing independent candidate review with a specific
source/model-supported explanation and plotted evidence; do not silently waive
it, change a frozen limit to pass, or require another reviewer chain. Report
remaining flags as pending rather than a passing diagnostic footnote.

### Verify that a changed guard detects a known failure

When introducing or changing a shape guard, replay one retained representative
per affected defect class through the same guard: the known-bad response must
fail for the original defect and the corrected response must pass. Bind both
artifacts, control/rate context, sampling method and guard version; reuse saved
production curve exports when adequate instead of rebuilding old binaries.
A setup error or unrelated numerical failure is not successful defect detection.
If the bad response passes, the guard is not validated; if the corrected response
still fails, the repair is not cleared by it. Missing adequate historical data
leaves this sensitivity check pending until the representative is reproduced;
do not invent a historical failure or present a synthetic case as one. For a
new defect class with no recorded failure, disclose that limitation and use a
labelled synthetic negative control only as limited detector validation.

Run this check only when the relevant guard changes, and reuse its hash-bound
receipt on routine candidate runs. Do not replay the full historical matrix or
change frozen evidence targets/limits to obtain the expected fail/pass pair.

### Production binding and compact receipt

Execute the plan in a compiled background verifier using the production control
mapping and DSP response path, under the repository build-lane wrapper. A
Python fit, coefficient-only surrogate, or UI curve alone cannot pass it. Reuse
existing actual-audio/response agreement and parameter-transition checks when
their source/binary scope matches; otherwise verify only the worst/flagged state
and one representative control traversal through actual processing. Static
tracks do not establish click-free automation. Existing hosted checks remain
owned by the production handoff; do not add a full DAW matrix here.

Keep one receipt containing plan and guard versions, target/source/verifier
hashes, requested and unique effective states per identity/type/mode/rate, substitutions,
coverage omissions, worst metrics, exact failed states, flagged-interval
resolution and a compact overlay or sweep plot. Bind any reused audio/host
receipt and its binary identity. State PASS/FAIL/PENDING for this engineering
gate separately from public-fit. A finite passing plan is bounded sampled
coverage, never proof that every continuous position is defect-free.

## Frequency probes and local refinement

Start from the unchanged, frozen frequency anchors and the sample rate bound to
the evaluation. `build_frequency_probes` adds deterministic equal-log
subdivisions. It can also add neighborhoods from pole information already
declared by the candidate model:

- `PoleHint(center_hz=..., bandwidth_hz=...)` uses a declared center and width.
- `PoleHint(radius=..., angle_rad=..., sample_rate_hz=...)` uses center
  `angle * fs / (2*pi)` and the radial decay-width proxy
  `-fs * log(radius) / pi` for probe placement. The latter is not claimed as a
  target 3 dB bandwidth.

The helper rejects non-finite anchors, duplicate anchors, non-positive or empty
intervals, and any interval reaching Nyquist. A digital pole's sample rate must
match the probe plan. Explicit interval boundaries are always included as
diagnostic probes. Pole hints outside the declared finite interval are counted
as requested but do not add probes.

Pass `plan.frequencies_hz` to `refine_local_extrema` with a scalar callable that
evaluates the actual mathematical candidate at one frequency. The callable
comes from the owning dataset/model adapter; the generic helper never invents
a public target. Refinement uses bounded golden-section searches in
log-frequency only where the initial samples bracket a local maximum or
minimum. It has explicit evaluation and per-bracket iteration budgets. Budget
or iteration exhaustion leaves named `unresolved_intervals`; it is never
silently treated as coverage success.

Example:

```python
from curve_coverage import (
    PoleHint,
    build_frequency_probes,
    make_coverage_report,
    refine_local_extrema,
)

plan = build_frequency_probes(
    frozen_anchor_frequencies_hz,
    sample_rate_hz=48_000.0,
    subdivisions_per_interval=3,
    pole_hints=[PoleHint(center_hz=center, bandwidth_hz=bandwidth)],
)
refinement = refine_local_extrema(
    model_adapter.magnitude_db,
    plan.frequencies_hz,
    interval_hz=plan.bounds_hz,
    max_evaluations=512,
    frequency_tolerance_hz=1e-4,
)
report = make_coverage_report(plan, refinement=refinement)
```

The method and resolution belong in the diagnostic receipt: anchor count,
subdivisions, maximum log-step ratio, pole-neighborhood multipliers, refinement
tolerance, evaluation count and maximum-evaluation budget, and all unresolved
intervals. If an
unexpected peak exposes a failure, keep the old frozen target and the failed
diagnostic artifact. Change the model/control law or add a separately reviewed
shape guard; do not retrofit generated probe values into the old evidence
target.

## Effective control-state coverage

Use `summarize_effective_states(requested_states, effective_state)` after the
owning adapter applies the same quantization or coefficient-selection rule as
the candidate. The report distinguishes:

- the number of requested states;
- the number of distinct effective states; and
- the duplicate count caused by several requests mapping to one state.

This detects apparent sweep coverage that is actually repeated coefficients.
Test gain and frequency independently, even if production exposes them in one
combined state. Include neutral, extremes, interiors, anchor crossings, and the
declared near-Nyquist domain where applicable. Duplicate reporting does not
decide whether quantization is allowed; that remains part of the frozen control
contract. Effective-state keys must be canonical hashable values made from
finite primitive values, tuples, or frozensets; nested `NaN` and infinity are
rejected, and frozenset reporting is sorted deterministically.

## How to use diagnostics without changing evidence

Downstream verification should:

1. Bind the original frozen anchor artifact and grid hash before running the
   diagnostic.
2. Keep source-row magnitude gates separate from any predeclared engineering
   shape, continuity, monotonicity, or turning-point guards. Never invent a new
   numeric guard after seeing a candidate and call it a formal judgment.
3. Sweep gain and frequency independently through their declared interiors and
   boundaries, then evaluate their intended combinations if the contract owns
   an interaction.
4. Scan retained failed diagnostic artifacts for the whole shared model family.
   A repaired route is not enough when sibling identities reuse the same pole,
   interpolation, quantization, or sample-rate transform.
5. Run the formal row-for-row evaluator separately against the unchanged
   target. Diagnostic probes supplement failure discovery; they do not replace
   eligible public rows, protected holdouts, inference rows, or hosted-path
   validation.

`make_coverage_report` records the probe method/resolution, requested versus
distinct effective states, budget exhaustion, and unresolved intervals. The
report records zero evaluated probes and marks the full interval unresolved as
`not_evaluated` when no `RefinementResult` is supplied; constructing a plan is
never reported as executing its evaluator. A refinement also records its exact
initial frequency tuple and bounds, and the report rejects a refinement created
for a different plan. The
absence of an unresolved interval means only that every *discovered* candidate
bracket finished within the configured budget. It is not an all-continuous
mathematical guarantee.

## Pooled midpoint aggregation

`pooled_median_from_validated_midpoint_groups` flattens all supplied midpoint
observations and computes one median. Unequal group cardinalities remain
meaningful: groups `[0, 0, 0]` and `[0.4]` pool to `[0, 0, 0, 0.4]`, whose
median is `0`, not the median-of-group-medians value `0.2`.
For an even pooled count, the helper halves the two center values before adding
them, so finite large values such as `[1e308, 1e308]` remain finite rather than
overflowing during median calculation. A non-finite result still fails closed.

The helper is aggregation only. Before calling it, the owning evidence adapter
must enforce the strict pairing key, equal nonzero gain magnitudes, exactly one
finite boost and cut value at each aligned vertex, tolerance, identity,
revision, section, topology/routing, conditions, native frequency, provenance,
and measured-baseline precedence required by `paired-midpoint-median-v1`.

Run the synthetic regression and unit suite with:

```bash
python3 .agents/skills/pigora-public-fit-training/scripts/curve_coverage.py --self-test
python3 .agents/skills/pigora-public-fit-training/scripts/test_curve_coverage.py
```
