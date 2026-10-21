# Pigora fitting-to-product handoff

Read for Pigora response, parameter-adapter, or editor integration. This owns
product verification, not source research or a new fitting contract. Reuse
unchanged accepted targets and numerical receipts from `pigora-public-fit-training`.
Root `AGENTS.md` owns staged validation, lane isolation, and deployment authority.

## Accept one bound handoff

Record device/revision and module/point identity, authorized native controls and
mapping, target/grid hash, candidate/data/code hashes, supported rates, per-rate
gate results, inference/public status, excluded controls, and unresolved layers.
Use the actual implementation entry point and serialized coefficients; a helper
fit cannot establish production equivalence. Preserve unrelated concurrent
model data and verify the exact inputs of the integrated build.

## Check the path that users operate

Before a new fitting/module/product validation PASS, require
[measurement acceptance](../../pigora-public-fit-training/references/measurement-acceptance.md),
contract `pigora-eq-measurement-acceptance-20261001-v1`: complete actual
processed-audio measurements versus independently frozen targets, inclusive
per-row 0.2 dB primary or exact scoped reviewed 0.5 dB fallback, **and** objective
smoothness without unresolved discontinuities. Below representative path checks
cannot substitute for missing certificate measurements. Reuse complete,
hash-compatible audio receipts; fallback preserves historical failures, public/
inference provenance, unchanged targets and mandatory smoothness limits.
Also bind root addendum `pigora-eq-compact-extrema-smoothness-20261006-v2`:
the [compact matrix](../../pigora-public-fit-training/references/curve-coverage.md#small-default-matrix)
must include exact maximum boost/cut with native frequency and Q/shape extrema,
and every required unique matrix state needs actual processed-audio coverage.
Require separate `compact_matrix_status=PASS` and the frozen numeric
[smoothness profile](../../pigora-public-fit-training/references/smoothness-gate.md)
with complete endpoint coverage and no unresolved findings. Representative
handoff checks below cannot replace this certificate; original fitting gates
and magnitude tiers remain unchanged.
Bind the [execution plan](../../pigora-public-fit-training/references/smoothness-execution.md)
and preflight, authorized scope/exclusions, required rates, exact effective
tracks/contexts, metric applicability and permitted finding closure. Missing
construction/acquisition inputs are PENDING; confirmed mapping/DSP/hard failures
are FAIL. Aggregate FAIL before PENDING before PASS and retain missing counts.

Select rows affected by the change and one adjacent unaffected path. A static
hash or source-string match cannot replace the behavior in the middle column.

| Axis | Required observable check | Boundary |
|---|---|---|
| Visible control to parameter | Exercise the actual attachment; compare requested value and APVTS readback after native quantization | Keyboard/accessibility input does not by itself prove physical pointer dragging |
| Parameter to native model | Verify effective gain/frequency/Q, switches, channel/lane and any quarter-gain/Prop-Q mapping | Count distinct effective states, not repeated nominal inputs |
| Hidden or retired controls | Fresh defaults and restored Off/Link/preset states cannot silently defeat visible controls under the authorized semantics | Hiding does not authorize changing native DSP behavior; retain or migrate state only as explicitly scoped |
| Point/full and channel routes | Same native state gives the intended response in full module and point adapters; L/R, M/S and masks follow the declared mapping | Do not infer routing from one stereo case |
| Static response to audio | Compare the production response evaluator with settled `processBlock` output at the original failure and representative extremes | A plotted curve or a fitting helper is not actual processed audio |
| Dynamic operation | Probe parameter crossings, retargeting during ramps, bypass/reset and state round-trip at relevant block sizes | A static magnitude gate does not establish click-free or time-varying behavior |
| Panel geometry when changed | Smallest supported layout, control bounds/hit areas, visibility and real gestures | Layout must use visible rows, not a hidden legacy schema's row count |

Record untouched or inapplicable axes with reasons rather than rerunning all
tests. If a control does not work, trace visible control -> parameter readback
-> effective native state -> DSP -> graph before modifying the algorithm.

## Numerical and capacity limits are distinct

The fitting receipt must disclose frequency coverage separately from control
coverage, including narrow-pole/zero or cancellation-sensitive regions. A new
shape failure triggers a cheap diagnostic across other bands using that model
structure; only demonstrated failures expand the repair scope. Preserve frozen
source targets and separate engineering shape guards from public evidence.

Use root `AGENTS.md` runtime contract `pigora-eq-realtime-support-20261001-v2`
and [training-contract §1C](../../pigora-public-fit-training/references/training-contract.md#1c-realtime-deployment-support-matrix)
uniformly for every Pigora EQ curve-fitting identity, full module and point
adapter deployment handoff, without model or EQ-type restrictions:

| Sample rate | Required maximum supported channels | Minimum guaranteed buffer |
|---|---:|---:|
| 44.1 / 48 kHz | 64 | 128 samples |
| 88.2 / 96 kHz | 32 | 256 samples |

Support valid layouts from mono through these maxima and validate all four
rate/max-channel/minimum-buffer boundaries separately. The guaranteed workload
is one complete native EQ per Pigora instance, preserving the admitted native
topology, sections, paths and interactions. Activate all in-scope sections
available together in each tested mode; verify mutually exclusive modes
separately. Point-adapter or individual-section passes do not establish
complete-module capacity. Excluded sections remain excluded and cannot support
a complete-device claim. Include
steady processing and native control changes, applicable masks and L/R or M/S
paths. Declare instance/module/section counts; 12 rack slots do not establish a
12-complete-EQ guarantee. Check applicable lower-channel/layout and larger-buffer
paths. Missing or failed mandatory cases block a new deployment PASS.

Before committing to a new runtime, size and probe this required envelope.
Record both
steady and transition cost, allocation/lock instrumentation, sample counts,
wall-time maximum/percentiles, and execution environment. Thread CPU time may
help distinguish computation from scheduler delays, but does not replace the
exact callback wall deadline `block_samples / sample_rate_hz` (128/48 kHz and
256/96 kHz are each about 2.67 ms). Bind source/build/binary identity, host or
harness, scheduling conditions, layout/channel count, rate/block/workload,
callback count and deadline misses to the contract ID. Do not rerun until a lucky pass or relabel a frozen
failure after changing scheduling conditions. These standalone probes do not
prove full-host capacity.

Higher channel counts, smaller buffers, rates outside these four rows (including
176.4/192 kHz), multiple complete EQs in series, and concurrent instances are
separate stress/extension validation. Their performance failures alone do not
block deployment after the mandatory matrix and other applicable gates pass.
Keep safe handling of unsupported configurations as a hard gate. Preserve
historical results and frozen response targets/thresholds; report existing
receipts' missing runtime coverage explicitly rather than inferring compliance.
The carveout is limited to timing/capacity; frozen response tests, explicit
extension commitments, safety checks and authorization boundaries remain.
Contract notifications cannot resume a user-paused task or grant new writes
or deployments.

## Installed-path acceptance

After authorized deployment through the shared wrapper, bind installed binary
hash and signature to the accepted build. Confirm that the tested host actually
loaded that binary after restart/reload; a version label alone is insufficient.
Use a temporary instance or preserve/restore user state when live control is
authorized. Do not disturb another task's active host or manual verification.

Report numerical fit, production DSP, rack safety/capacity, installed binary,
and actual host gesture verification separately. An old gesture receipt can be
reused only with explicit unchanged editor/binding scope and compatible binary
provenance; otherwise mark that layer untested. No deployment upgrades the
public-fit or inference claim.
