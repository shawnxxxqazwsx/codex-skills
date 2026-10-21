# Detailed post-deployment matrix

## 1. Freeze the inventory and test path

One unit is device/revision + module/point identity + band + filter type + native
mode. Bell, Low Shelf, High Shelf, HPF and LPF are separate units, even when
switchable within one band. Constant Q and Prop Q are separate modes. Record
every native discrete slope/order setting; shelf Slope is not HPF/LPF dB/oct.
Preserve excluded identities and reasons. Do not manufacture unavailable gain,
Q, resonance, slope or negative-gain states.

For each control bind parameter ID, normalized-to-native mapping, legal range,
quantization, default, Off behavior, interpolation knots and native units.
Record requested values, host readback and effective DSP values independently.
A neutral curve does not establish identity equivalence. Deduplicate effective
states within a unit; shared samples may be referenced by separate identity
rows only when each adapter/control binding is independently verified.
Canonicalize numeric state keys before hashing: integer/float spellings such as
-15 and -15.0 must identify the same effective value. Include unit, rate, route
and effective controls for coverage counting. Separately bind acquisition reuse
to binary/host identity, rate/block/channels/quality, stimulus level/schedule,
method and measurement settings. Equal control states do not make different
acquisition conditions interchangeable. Layer labels alone do not create new
acquisitions. Reuse only matching acquisition keys and retain all coverage
reasons on that row rather than counting the same capture twice.

Record plug-in path/format, installed executable hash/signature, build/source
receipt, host/version/process and loaded-binary evidence. A version label or
hash of a file on disk alone is insufficient. Record rate, block size, channels,
quality/oversampling, latency, stimulus, input level, settle rule and analyzer
resolution. An isolated offline host must load the installed bundle itself.
If the available host cannot automate a matrix or export audio, use an authorized
isolated host/adapter or mark the missing installed coverage PENDING; do not
substitute a C++ model probe and call it deployed verification.

Partition execution into deterministic identity/type/mode/rate shards. Persist
completed state rows and curve artifacts atomically before advancing. Resume by
stable state ID and matching plan/guard/binary hashes; never count partial writes
as completed or rerun matching passing shards solely after interruption. Keep
failed shards and continue independent units in a comprehensive audit, while
holding dependent stages of the failing unit. Estimate unique-state count and
pilot acquisition cost before the full run; report time estimates without
silently shrinking promised coverage. An interrupted audit remains PENDING
with its exact remaining shards and a resumable checkpoint.

## 2. Detailed static control sets

Defaults below belong to the comprehensive profile. Freeze substitutions before
execution; honor narrower source/owner-authorized inference gain support.
This reduced profile versions the added engineering sampling plan, not frozen
source/target acceptance. Preserve previous plans/results and reuse compatible
completed acquisitions; do not interrupt running batches or silently rewrite
an active frozen plan. Adopt a separately versioned plan at the next safe
checkpoint and disclose reduced coverage. Preserve all native discrete detents,
independent modes, exact historical failures and frozen target rows/rates.

| Axis | Values |
|---|---|
| Gain | 0, ±3, ±6 dB and native legal extremes (normally seven unique values); omit unsupported signs |
| Continuous frequency | Native shaft 0, .25, .5, .75, 1; report actual Hz, using the native log law where applicable |
| Discrete frequency | Every legal native detent |
| Continuous Q/resonance/shelf Slope | Native shaft 0, .25, .5, .75, 1, with actual values and direction |
| Discrete Q/resonance/shelf Slope | Every legal detent |
| HPF/LPF slope/order | Every native setting, separately counted |
| Other native switches | Each position on one representative context; expand coupled modes as separate units |

Map requested gains to nearest legal detents without extrapolation, retain both
supported signs, and report duplicates/substitutions. Fixed controls contribute
one value, absent controls no invented dimension. `G*` is the largest absolute
legal base gain per sign; `Fmid` and `Qmid` mean native shaft middle, not an
assumed arithmetic mean. If the middle is between detents, freeze one nearest
choice and include the adjacent one on a track when it crosses a model knot.
Test nearest effective values on each supported side of zero only once per
independent gain-control path at Fmid/middle shape; do not multiply these tiny
values across frequency/shape planes. Native gain detents remain fully covered
by their track even when the base gain set is smaller.

### Bell: union of three planes, not the full Cartesian cube

- Gain × Q at Fmid, separately for every native mode.
- Frequency × Q at G* for each supported sign.
- Gain × frequency at Qmid.
- Add low/high frequency × narrow/wide Q × gain extremes not already present.

This covers pairwise control interactions; it does not prove all three-way
combinations. A defect depending on three controls triggers a local full cube
around that region, not a whole-product expansion. Prop Q must cover both its
gain and Q dependencies even if its effective bandwidth is gain-dependent.

### Low and High Shelf: separate planes with native shape axes

Use the Bell plane construction for each shelf type, substituting its native
shape control for Q. With no shape control this reduces to gain × frequency.
If Q and Slope are independent, run the planes for each at the other's middle
and add Q × Slope at Fmid/G* per sign. Include their endpoint corners at the
frequency limits. Do not reinterpret a shelf plateau as a misplaced Bell peak.

### HPF and LPF: cutoff and shape, without an EQ gain matrix

At every native slope/order, evaluate frequency × Q/resonance using the sets
above. No Q/resonance means frequency only. A continuous native slope uses five
shaft positions plus its track; do not infer nominal dB/oct detents. If two
independent shape controls exist, cover their pairwise plane at Fmid and endpoint
corners at the cutoff limits. Respect separately documented resonant modes.

### Off, type changes and historical failures

For each unit include Off/Bypass and its adjacent active cutoff endpoint where
present. Read back state and measure the declared bypass/neutral response;
confirm the active endpoint is not already Off. Exercise each type/mode/slope
switch position at a representative context through the actual host parameter
path and measure its intended response. Do not multiply Off across all gains.

Include exact user-reported states and immediate neighbors at the original rate,
plus unresolved diagnostic regions. For a flagged detent interval, include each
implicated detent and one boundary neighbor on each side at a frozen reproducer
context. Preserve all original flags but group equivalent contexts; expand only
where gain/frequency/rate dependency differs. Existing failed rows never vanish
because a new sampling plan misses them.

## 3. Continuous tracks and interaction probes

For each adjustable axis, start with 17 equally spaced native shaft positions;
for a detented axis visit all unique detents in order instead. Add every authored
model interpolation knot and both immediate effective neighbors only when the
knot is verified in the actual production implementation. Bind its owning code
or table; regular nominal values are not automatically interpolation seams.
For continuous neighbors freeze a small normalized step; do not equate host
detents with knots. Retain historical failing seams regardless of base sampling.
Deduplicate against static rows. Fixed controls have no track.

- Gain track: Fmid and middle shape, plus one frequency-limit/narrow-shape
  context selected for the largest static shape residual across both signs.
  Sweep the full supported gain range in these two contexts, not both frequency
  limits by default. Add the other limit only for a distinct observed dependency.
- Frequency track: middle shape and narrowest shape at G* per sign.
- Q/shape track: Fmid and the more stressed frequency limit from static results,
  at representative 6 dB (nearest supported) and G* per sign.
- HPF/LPF: cutoff track at minimum/maximum resonance; shape track at middle and
  the more stressed cutoff limit, for every slope/order. Omit absent axes.

For continuous model cells also probe their interior, not only stored knots:
for each verified authored interval intersecting a track add its midpoint in
its actual interpolation coordinate. Add quarter/three-quarter positions only
when the midpoint, neighbors or history flag that interval. For a previously failed two-control
cell, include its center and edge midpoints with all other controls fixed.
These rows catch a smooth-node/rough-interior defect without a global 3D cube.

Selection of the stressed context uses the predeclared metric and deterministic
tie-break (lowest native shaft first), not visual preference. These adaptively
selected rows are engineering probes, never protected source holdouts.
Use consecutive three-state overlays to detect local bulges/dips, peak/cutoff
jumps and bandwidth discontinuities. No universal neighboring-envelope or
linear-dB constraint: frequency movement and Prop Q can legitimately violate it.
Refine flagged intervals with a finite declared evaluation budget and keep the
new reproducer. Unresolved intervals remain PENDING, not silently accepted.

## 4. What each measured curve must establish

At 48 kHz retain the full frozen evidence grid and its original gate separately.
For shape measurements start with at least 96 points/octave over the declared
finite audit domain; add source anchors, cutoff/peak neighborhoods and narrow
feature refinement. Choose the domain before judgment: include low-frequency
exterior, passband/stopband or both skirts/plateaus, and up to the declared
near-Nyquist limit (strictly below Nyquist). A 20 Hz–20 kHz host export does not
prove behavior outside that range. State inaccessible regions explicitly.

Resolution must resolve the narrowest relevant feature: use at least eight
samples across its estimated bandwidth, refine local extrema and suspicious
slope changes, and confirm suspected features at finer resolution. FFT zero
padding/interpolated plot pixels do not improve acquisition resolution. For
very low/narrow responses extend acquisition and settling, not just plot density.

Freeze type-specific metrics, limits, stimulus level and numerical/noise-floor
handling before adjudication. Existing frozen gates remain unchanged. Do not
invent a universal new derivative tolerance or use 0.2 dB as a slope unit.

| Type | Required shape checks |
|---|---|
| Bell | Peak, both skirts, unsupported extra lobes/plateaus, exterior offset, gain/Q/frequency motion |
| Shelf | Low/high plateaus, transition location/width, native slope/resonant overshoot, unexpected ripple |
| HPF/LPF | Passband gain, cutoff transition, stopband attenuation/trend, native order/resonance, unintended lobes |
| All | Finite/bounded samples, log-frequency slope/curvature anomalies, control-track continuity and declared switch/Off behavior |

Preserve source-supported asymmetry and overshoot; do not require all boosts
nonnegative, all responses symmetric, or both endpoints at 0 dB. Do not enforce
an analog asymptotic dB/oct law at digital Nyquist. Treat values beneath the
measurement noise floor as bounded attenuation evidence, not accurate dB/phase.
Unknown shape-law evidence requires explicit engineering guards and nonclaims.

### Fast screening and adaptive installed-audio acquisition

Use this order without substituting model evidence for installed measurements.
Capture impulses/sines offline to files, or through a verified muted/disconnected
monitor output; freeze an appropriate stimulus level and resolve uncertain
hardware routing before emitting test signals.

1. Where a bound production evaluator is available, calculate the reduced
   static matrix cheaply, with pole neighborhoods and local extremum searches.
   Reuse matching predictions; no separate full rebuild/model matrix is required
   if adequate installed data already exists. This selects difficult acquisition
   states and frequencies, not passing deployed states. If unavailable, proceed
   through the installed path and record the model comparison as pending.
2. Acquire installed audio for every state in the declared reduced matrix using
   a validated adaptive-length impulse method on a linear, settled path. Avoid
   charging every short-tail state the longest low-frequency response duration.
3. Extend only unresolved/long-tail states; use local stepped sine to resolve
   flagged narrow peaks, dips or low-frequency regions and model/audio mismatch.
   Preserve raw short and extended results and their distinct acquisition status.

Freeze minimum/maximum acquisition length, growth rule (normally doubling),
settle criterion, tail window/energy limits, required frequency resolution and
short/long convergence tolerance before the run. A short result can stop only
when BOTH tail/truncation error and required frequency resolution are adequate.
Estimate bandwidth from the bound production model when available; verify it
against acquisition evidence. Low tail amplitude alone is not sufficient:
weak narrow resonances may persist. Zero padding is not extra resolution.
If dense FFT spacing would force a long global acquisition, a validated
frequency-selective measurement may fill the unresolved region, with explicit
coverage and uncertainty; interpolated bins cannot fill it as measured evidence.

Pilot the adaptive method on a short-tail/high-frequency state, a low-frequency
or narrowest state, and one retained known failure per relevant defect class.
Compare short/adaptive versus adequately long or local-sine results using the
same predeclared guards. Retain defect-detection sensitivity, worst differences,
actual wall times and selected lengths. If this pilot fails, keep the proven
longer method for the affected class; do not reduce resolution or thresholds.
Reuse the acquisition-method receipt while method, relevant implementation,
precision and measurement conditions remain compatible.

Reset/settle each state appropriately and record input level, latency, capture
length and achieved resolution. For nonlinear/time-varying paths use a validated
swept/stepped sine or other appropriate method with declared amplitude and
conditions; a single impulse does not prove their level-dependent behavior.
Multi-sine may cheaply check binding or selected frequencies, but its gaps do
not establish full curve shape. Maximum length/budget exhaustion leaves exact
regions PENDING. A convergence extension is one planned acquisition sequence,
not repeated attempts until a hard product failure disappears.

Compare every acquired static curve against the bound production evaluator
when available, using the actual effective parameters and measurement domain.
This adds numerical analysis, not capture states, and detects smooth but wrong
control mappings. Keep this correspondence metric separate from frozen target
errors; an unavailable evaluator leaves correspondence PENDING. All source-row gates,
installed-static coverage, dynamic checks and visualization requirements remain
separate. Report measured speedup only from pilot timing, never promise a fixed
reduction from state count alone.

## 5. Rates, dynamics and state: bounded additional layers

**Rates.** Run sections 2–4 completely at 48 kHz. At every other supported rate,
measure frequency/shape endpoint corners at each gain sign/extreme and native
mode/slope; exact historical rate failures; and seams in rate-specific code or
coefficient banks. For HPF/LPF omit gain. If a rate has a distinct control-law
implementation or fails this screen, expand the implicated units/axes there.
This does not reduce existing full frozen target/rate obligations. Higher-rate
0.5 dB engineering exceptions follow training only; never relax a 48 kHz gate,
a lower-rate gate or a public-source claim.

**Dynamic audio.** Static tracks do not establish automation quality. At 48 kHz
use one documented representative signal/level and replay each independent
control axis in both directions: slow traversal (default 2 s), fast traversal
(default 100 ms), one retarget during a ramp, and an applicable zero/knot crossing.
One middle context per unit/axis suffices initially; include exact dynamic
failures and the worst static context when it exposes a different dependency.
Use a small and a normal supported block size (prefer 64 and 512 if supported),
not their cross product with every static state/rate. Record exact automation
schedule, host granularity, smoothing/settling and actual readback. Judge dropped
updates, stale final state, non-finite output, unexplained spikes/discontinuities
using predeclared signal-appropriate guards; legitimate fast modulation is not
a click merely because it differs from a static curve. Add one representative
other-rate traversal only for distinct smoothing/rate behavior or a prior defect.

**Neutral insertion and mode effectiveness.** Once per distinct processing
route and quality/oversampling setting, compare empty rack, inserted active
neutral EQ and declared bypass using installed audio. Check near-Nyquist
magnitude and latency-aligned complex response where reliable; do not align
away unexplained frequency-dependent phase. This is route transparency, not a
hardware phase claim. For HPF/LPF use declared Off for the neutral case and
separately verify the adjacent active limit. Reuse matching route receipts.
For each type/Prop-Q switch, choose a source/model-declared distinguishing
non-neutral setting; equal responses at zero gain cannot prove the switch works.
Record quarter-gain or other native range mapping where available.

**State and routing.** Use one non-neutral distinguishing state per unit to test
save/restore and bypass/type/mode changes, including applicable hidden/retired
parameters. Verify effective values AND measured response after reload. For
point/full routes compare the same state; for supported L/R, M/S or masks use
an identifiable channel stimulus and verify affected/unaffected outputs. Keep
these as small adapter checks, not another copy of the curve matrix. Add one
pair of simultaneously active adjacent bands per distinct routing topology to
expose slot/ownership cross-talk, using declared composition behavior. Full rack
capacity/performance remains owned by existing handoff checks.

Parameter automation/readback does not prove mouse-drag behavior. Reuse a valid
unchanged binding/gesture receipt or mark that layer separately; only perform
one representative real gesture per distinct control binding when required.
Restore the prior host/session state and verify restoration at the end.

## 6. Adjudication and reproducible output

A new/changed detector must catch one retained known-bad response and accept its
corrected response per defect class, using the same guard. Reuse bound stored
production/audio exports; setup errors do not count as catching the defect.
Run this sensitivity check only on detector changes. Missing historical evidence
is disclosed; a labelled synthetic negative control is limited validation, not
a fabricated real-world regression.

Reuse one plan/receipt package rather than per-cell reports:

- Plan: scope, inventory, legal mappings, matrix/guard version, deterministic
  state-generation rules, rate/domain/measurement settings and exclusions.
- State table: stable state ID; identity/type/mode; requested/readback/effective
  controls; rate/block/channels; execution path; curve artifact; each metric,
  worst frequency, status and reason; dedup/reuse source when applicable.
- Receipt: installed/loaded binary and source/target/host bindings; requested
  and unique state counts per unit/rate/layer; missing cells; failures and
  unresolved flags; reused receipt identities; acquisition limits; separate
  target-fit, installed-static, installed-dynamic, state/routing verdicts.
- Visual summary: overlays for worst/failed states, control-track waterfall or
  heatmap, and slope/curvature detail for flagged regions. Link full raw data.
- Repair packet: exact host/binary, initial state, parameter sequence, rate,
  block/quality/channels, expected declared behavior, observed metric/curve,
  nearest passing neighbors, and a replay command or saved host state.

FAIL means an executed hard gate failed. PENDING means missing required evidence
or unexplained findings. Not-applicable requires a native-scope reason, never
an unimplemented test. No overall PASS while any required unit/layer is FAIL or
PENDING. Independent review can explain a diagnostic flag with specific bound
evidence, but cannot waive a hard failure or relabel an unexplained shoulder.
A later credible in-scope failure makes current clearance PENDING while retaining
historical receipts. Finite coverage is never an all-continuous or hardware-
equivalence guarantee. Stop at the audit result unless repair is authorized.


## 7. Required visualization pack

Generate evidence plots from retained measured/exported data with standard
plotting tools, never image generation or hand-drawn approximations. Reuse the
same data for metrics and plots. Images are mandatory on PASS, FAIL and PENDING;
if acquisition is blocked, show coverage/status only, never fabricated curves.
This requirement adds rendering, not more measurement states.

Deliver PNG images (at least 1600 pixels wide for multi-panel sheets, readable
labels at normal viewing size) and a Markdown index linking images, state IDs
and raw data. Optional SVG/PDF or an interactive explorer may supplement PNGs,
not replace immediately viewable images.

| Image | Required content |
|---|---|
| `overview.png` | Separate rows for identity/type/mode and columns for rate/layer; PASS/FAIL/PENDING/not-applicable text plus unique-state counts and missing coverage. Split into numbered sheets if crowded. |
| Per-unit curve sheets | One sheet per identity/type/mode at 48 kHz with representative gain, frequency and shape-control slices, including both supported signs. Add other-rate worst cases without mixing curves into an unreadable bundle. Bell, shelves and pass filters remain separately labelled. |
| Per-unit control-track maps | Frequency on logarithmic x-axis, actual control position/value on y-axis, measured dB as color; separate gain/frequency/Q or native shape tracks. Include a small overlay of selected neighboring curves. Static settled tracks must not be labelled dynamic audio. |
| Per-defect detail | Full-domain context plus magnified region, exact offending state and nearest passing neighbors, anomaly marker and applicable slope/curvature or residual panel. Group duplicate flags by mechanism, but link every grouped state. |
| Dynamic/neutral detail when applicable | Worst dynamic traversal: time waveform or suitable residual with parameter schedule and marked anomaly. Neutral insertion: empty/neutral/bypass magnitude and reliable latency-aligned phase difference. |

For a wholly passing unit, still show its representative curves and worst
metric state; do not output only a green status grid. For a partial audit show
measured subsets and visibly mark missing ones. Dense detent maps must preserve
narrow flagged regions; do not average them away for display.

### Comparable and truthful presentation

- Label frequency in Hz/kHz, magnitude in dB, log-frequency derivatives in
  dB/oct or dB/oct², time in seconds, and actual native control values/units.
  A shelf Slope shaft value must not be relabelled as HPF/LPF dB/oct.
- Use common x/y limits and color scales within each comparison group; show
  a 0 dB reference where meaningful. Add a zoom panel for small shoulders
  instead of silently changing scales. Mark clipping/noise-floor regions.
- Show installed measurement as the primary trace. Overlay the bound production
  prediction and frozen target only when available, with clearly different
  legends. Distinguish public, inference and engineering-only references;
  unsupported regions stay unshaded or explicitly marked unjudged.
- Annotate identity, filter type, mode, actual Gain/Frequency/Q/Slope, rate,
  state ID, acquisition path, abbreviated binary hash and guard version.
  Put long provenance in the index rather than hiding the curve with labels.
- Use labels/line styles as well as color. Plot exact sampled values without
  cosmetic smoothing; split invalid/missing segments instead of bridging them.
  Limit an overlay to about seven traces and use small multiples for the rest.
- Bind a plot manifest to input curve hashes, state IDs, plotting script/version,
  axis limits and generated image paths. Reuse unchanged plots only when these
  inputs match; a screenshot of an old binary is not a current audit figure.

Render and open the actual output files for visual QA: readable text, complete
legends, truthful axes, visible worst-case feature, no cropped curves or missing
panels. Correct plotting defects without altering measured data or acceptance
limits. Final response embeds `overview.png` and the most informative curve or
failure image using absolute filesystem paths, then links the full image index.
If an audit could not run, explicitly label the status-only image as PENDING.
