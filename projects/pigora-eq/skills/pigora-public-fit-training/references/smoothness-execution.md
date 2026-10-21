# Reproducible compact EQ smoothness execution

Contract `pigora-eq-compact-extrema-smoothness-20261006-v2` owns this procedure.
Use with [curve-coverage.md](curve-coverage.md#small-default-matrix) and
[smoothness-gate.md](smoothness-gate.md). This specifies the operational plan;
the owning production verifier still executes audio measurement and adjudicates
the certificate. The diagnostic helper `curve_coverage.py` is not that verifier.

## One explicit plan, before candidate judgment

Write a machine-readable JSON manifest with
`schema_id=pigora-compact-shape-plan-v2`. Freeze its reviewed content/hash
before judging a candidate. Reuse a matching plan; do not regenerate selections
from the passing captures available. Required fields are:

| Field | Required content |
|---|---|
| `bindings` | Contract IDs, inventory/control-map/authorization/scope/exclusion hashes, original source/target/grid hashes, guard/profile and production-path IDs |
| `units`, `excluded_units` | Admitted native identity/band/filter-type/mode IDs; each excluded ID, reason and existing authorization receipt |
| `required_shape_rates`, `rate_basis` | Finite rate list including 48 kHz and all applicable previously required response/product rates, with the contract/receipt basis for each; stress rates separately |
| `axes` | Stable axis IDs, continuous/detented/fixed/absent kind, native range and modes, sampling map/coordinate, analysis coordinate/unit, exact effective endpoints/middle, detents and neutral where present |
| `gain_families` | Actual boost/cut control bindings, supported sides, native polarity/direction, exact maxima, and `cut_relation=same_declared_law/distinct/unresolved` with evidence |
| `state_selection` | Continuous near-neutral step/direction/coordinate, knot-neighbor steps, exact middle/narrowest-shape contexts and legal-substitution/tie rule |
| `tracks` | Stable track ID, unit/rate/family, swept axis, scheduled positions, every other axis's exact fixed effective value, knot IDs and neighbors |
| `profile` | Exhaustive required metric ledger per state/context/region/rate, applicability predicates, numeric limits/roles/units, formulas/stencils/feature definitions, uncertainty and permitted-feature evidence; profile hash |
| `grid_and_acquisition` | Finite frequency grid/hash, analysis stencils/scales, resolution and uncertainty budget, stimulus/reference/window/settling method and capture requirements |
| `refinement` | Deterministic interval priority, neighbor/half-step rule, extra-state/point/capture budgets, join estimator/remainder bounds and stop conditions |
| `generated_coverage` | Sorted requested and expected effective states, request-to-effective mapping, canonical keys, required extrema/knots/track membership, expected counts and retained failure IDs |

Every native unit in the declared inventory must be admitted or accounted for
in an existing authorized exclusion ledger. Missing targets, failed fits,
runtime clamps or measurement cost cannot create an exclusion. Excluded units
receive no new target/capture obligations and cannot support a complete-device
claim. An admitted targetless state still needs engineering shape coverage;
it never creates a public/inference target or new inference authorization.

Rate membership comes from existing contracts and frozen scope, not an AI's
preferred subset. Record out-of-scope stress results separately; preserve any
already committed broader rate/response obligation. Missing or conflicting
rate/scope bases leave the affected plan PENDING.

`plan_status=READY` means all construction inputs and expected coverage have
passed the owning verifier's preflight. Missing inputs give `plan_status=PENDING`
with named reasons. READY is not matrix, smoothness or product PASS. The plan
may precede a build; actual binary/capture hashes belong in a separate immutable
candidate/acquisition binding. No measurement verdict may pass before that
binding is complete and matches the plan's path/control/guard identities.

## Deterministic state selection

1. Map requested positions through the frozen native control mapping. Preserve
   requested values, expected effective values and later actual readback. For
   a continuous axis, scheduling and analysis coordinates may differ (for
   example native normalized position versus log2(Q)); name both transforms.
   Never silently interpret a native percentage as gain dB.
2. Use exact native endpoints. For an interior "nearest legal" substitution,
   use the bound production mapping first. Where that mapping leaves a legal
   substitution choice, minimize distance in the frozen sampling coordinate;
   break an exact tie toward the lower coordinate, then the frozen detent order.
   Record it. Endpoints cannot be substituted.
3. Freeze the exact middle state of each present axis. The default continuous
   position is the sampling-coordinate midpoint mapped through the native law.
   A detented middle is an explicit effective detent ID using the rule above;
   an even-sized set does not have an implicit middle. A documented narrowest
   Q/resonance context is explicitly bound, never assumed to be position 0/1.
4. For detented/quantized Gain, near-neutral states are adjacent distinct legal
   effective detents on every supported side. For continuous Gain, use
   `neutral + direction * frozen_near_neutral_step` in the named sampling
   coordinate. Freeze a finite nonzero step, supported direction and acquisition
   resolvability per native family; no arbitrary machine epsilon or guessed
   0.01 dB. A separate positive-valued CUT knob uses its native direction, not
   an invented negative input. If mapping collapses a neighbor to neutral,
   report missing coverage/PENDING; do not silently enlarge the step.
5. Continuous interpolation knots use the frozen immediate-neighbor step and
   refinement half-step. Detented knots use adjacent actual detents. Boundary
   knots have explicit legal one-sided contexts; no out-of-range states. Knots
   and their required effective neighbors remain mandatory on reduced tracks.
6. Canonical state keys are `(unit_id, rate_hz, sorted effective controls)`.
   Detented values use stable IDs. Encode finite continuous effective numbers
   as their IEEE-754 binary64 big-endian 16-hex-digit representation after
   conversion from the declared native readback type; normalize negative zero
   to positive zero. Thus numeric 1 and 1.0 share a key. Reject nonfinite values;
   do not round nearly equal controls together. Preserve units separately.
   Serialize the tuple as compact JSON arrays with ASCII escapes and the
   positive integral rate in Hz; the control pairs are ordered by frozen axis
   IDs. Sort the resulting key strings by their ASCII bytes. Hash that compact
   ASCII-escaped JSON array of strings as `coverage_sha256`. Keep display values
   outside the keys. Hash the exact reviewed UTF-8 manifest file bytes separately
   as `plan_sha256` in an external receipt; do not embed its own hash or mutable
   run timestamps in the hashed file. This avoids cross-language numeric JSON
   spelling and self-referential hash ambiguities.

Coverage identity differs from acquisition reuse. Reuse requires a separate
key binding actual binary/verifier, path/mode/layout/channels/block/rate,
stimulus/reference/settling/extraction method and frequency grid. Equal-looking
curves or equal state keys alone do not establish reusable measurements.

## Name every control track and its fixed context

The existing compact base, extrema and failure states remain required. At
48 kHz the default track has nine equally spaced sampling positions; a smaller
interior set needs the existing frozen review, with all required boundaries,
knots/neighbors and historical defect states retained. Fixed/absent axes get
no fictitious traversal. Each applicable independent continuous shape axis
gets its own track, including independent shelf Q and Slope.

| Swept axis | Default fixed context for Bell/shelves |
|---|---|
| Gain | Middle frequency; middle of every independent shape axis |
| Q | Exact maximum boost, or maximum cut for cut-only units; middle frequency and independent Slope |
| Slope/other independent shape | Same gain extreme; middle frequency and every other shape axis |
| Frequency | Same gain extreme; documented narrowest native Q where present; middle independent Slope/other shape axes |

If Q is absent, bind a native-law-supported frequency-track shape context
explicitly. Every track lists every unswept control, including modes, compound
boost/cut controls and route settings. For HPF/LPF, use the existing cutoff and
adjustable shape tracks without Gain; name the exact discrete slope ID in every
context and preserve coverage of all required discrete settings. No implicit
"middle slope" choice is permitted.

For independent Q/Slope, the base uses the union of Q(min/mid/max) at Slope-mid
and Slope(min/mid/max) at Q-mid, plus the already required four endpoint pairs
at each extreme-gain/frequency context. Do not multiply all interior positions.
Separate Q and Slope tracks hold the other at its frozen middle state.

When cut topology/control law is distinct, or a retained finding establishes
unexplained boost/cut asymmetry, retain the existing separate cut base matrix
and add the implicated Q/shape/frequency track at exact maximum cut, including
its own knots/neighbors. An explicit same-law binding retains the compact
default. `cut_relation=unresolved` is PENDING for that plan branch; an AI must
establish the law from permitted evidence or freeze conservatively separate
coverage, not assume sameness to save measurements. Preserve earlier failures.

## Execute and report in this order

1. **Preflight.** The owning verifier checks admitted/excluded scope, rate
   bases, canonical states, exact contexts, all extrema/switches/knots/tracks,
   profile applicability/units/limits/roles, stencils, uncertainty/resolution
   and finite refinement inputs. Empty expected coverage or omitted required
   metrics is PENDING. Missing inputs are reported before expensive capture;
   AI may prepare them from permitted evidence but cannot invent a passing cap.
2. **Acquire.** Bind actual production binary/path and matching processed-audio
   captures or fully compatible reuse for every unique required state. Assert
   settled native readback reaches the declared state/endpoints. Missing/invalid
   acquisition is PENDING; a confirmed wrong native mapping/type/range is FAIL.
   Keep all missing states even after another state fails; stop unsafe captures.
3. **Compute.** The production verifier computes unsmoothed measured magnitude
   and the profile's applicable spacing-normalized metrics with uncertainty.
   Use [smoothness-gate.md](smoothness-gate.md) for exact formulas and verdicts;
   no candidate-generated external targets, raw second differences or changing
   stencils/limits to obtain a pass.
4. **Resolve.** Process flags in the frozen interval/state priority order with
   its finite refinement budget. Only independent source evidence or an already
   authorized frozen modeling/native law can explain a permitted feature under
   its frozen rule. Candidate code explaining a defect is not closure evidence.
   Hard failures cannot be waived; unresolved/budget-exhausted findings remain
   PENDING. Bind closure to the existing independent review without adding an
   extra approval chain.
5. **Aggregate.** For required applicable constituents: any FAIL => FAIL;
   otherwise any missing/PENDING => PENDING; otherwise all PASS => PASS.
   Keep predeclared NOT_APPLICABLE reasons and missing counts separately; an
   empty applicable set is PENDING. Report magnitude, compact matrix, smoothness
   and certificate independently, preserving public/inference/runtime/hosted
   states and historical verdicts.

## Repeatability and detector checks

On the same frozen manifest, two implementations must produce identical ordered
state keys, memberships, expected counts and `coverage_sha256`; they must bind
the same exact frozen file's `plan_sha256`. A normalized
unit/control rescaling must preserve metric verdicts with correctly rescaled
limits. Boundary fixtures must cover a neutral absent peak, an unresolved required
peak, unequal-spacing feature movement, curved-but-continuous joins, a real step,
uncertainty overlap, invalid reference versus nonfinite DSP, and mixed FAIL/PENDING.
Label synthetic fixtures; they test specification/estimator behavior, not EQ
acceptance. Existing known-bad/corrected production evidence remains required
for changed real shape guards. Reuse unchanged checks rather than rerunning a
full matrix. A finite passing plan does not guarantee every continuous position
or every future AI's behavior; missing inputs and unsupported conclusions remain
explicitly blocked.
