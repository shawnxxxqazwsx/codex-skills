# Compressor capture protocol

Use this reference to turn a proposed hardware-emulation campaign into a
calibrated, falsifiable measurement plan. Adapt the numbers to the unit and
capture chain; do not import a universal level grid or duration target.

## 1. Freeze the observation contract

Record before routing audio:

- exact unit, serial, revision, options, service/tube state, and channel health;
- target claim and excluded behaviors;
- source and load impedance, balanced wiring, cable and patch path;
- converter models, firmware, analogue reference authority, current output/input
  trims, clock topology, sample format, and bandwidth;
- requested sample rates, production latency, controls, modes, stereo states,
  temperature/warm-up protocol, and maximum history horizon;
- who may operate the hardware and the verified maximum playback/output level.

If the user declares the converter state immutable, record that authority in
the session contract before capture. From that point onward, all converter
inspection is read-only. Do not alter routing/patching, gain/trim, clock,
sample rate, buffer size, or stored state as part of qualification or fault
isolation.

Record channel-number semantics at both boundaries: the user-facing/CLI values
and the converter driver's internal indices. Pass the user's declared CLI
numbers literally when the capture tool already converts from one-based to
zero-based indices. For this user's MOTU route, the only authorized invocation
is output `33/34` and return `37/38`; reject any other values before opening the
audio device. A recording made with rebased or different values is retained as
incident evidence, annotated `REJECTED`, and excluded from every dataset
allowlist.

Photograph recall settings. For continuous pots, record the position, the
direction from which it was approached, and any channel tracking limitation.
For stepped controls, record the physical label or detent rather than a guessed
normalized value.

## 2. Route a measurable chain

Route qualification does not authorize a converter write. When the converter
control plane is frozen, diagnose only from the declared physical route,
read-only state, capture logs, and received audio. Stop and report a route
failure instead of repatching or changing converter settings.

If the user stops converter discovery, stop all CoreAudio, CueMix, AVB, USB,
network, or vendor-control enumeration and probing as well. Do not reopen the
audio device merely to confirm identity or channel availability. Interrupt an
active capture, retain and label any partial/unpaired artifact as rejected,
and require a new explicit user instruction before any later device access.
Hashing, annotation, validation, packaging, and release upload of files that
already exist remain offline operations and must not perform device discovery.

Preferred topology for stereo capture:

```text
digital stimulus -> clocked DAC -> DUT L/R -> ADC wet L/R
                              \-> high-Z differential tap -> ADC reference L/R
```

Use one converter clock domain when possible. A stereo run with simultaneous
input reference and wet output normally needs four ADC channels. If a splitter,
distribution amplifier, pad, transformer, or reference tap is inserted,
measure its response, headroom, polarity, delay, source impedance, and loading
with the exact downstream connections present.

The input-reference tap is not automatically the model input. Preserve:

1. `x_digital`: the exact file sent to the DAC;
2. `x_reference`: the analogue voltage delivered to the DUT, sampled by ADC;
3. `y_wet`: the DUT output, sampled by ADC.

Use `x_reference` to verify level, dropouts, channel mapping, timing, and clock
drift. A production plug-in normally receives `x_digital`; if a model is trained
from `x_reference`, define and validate the front-end mapping needed at
inference. Never hide converter or tap response inside the hardware claim.

If playback and capture clocks differ, prefer correcting the clock topology.
When that is impossible, estimate time-varying drift from the simultaneous
reference and preserve the raw files. Version the resampler and report how it
changes phase, bandwidth, and nonlinear products.

## 3. Qualify levels and format

Use the user's declared calibration authority. For this user's MOTU capture
work, derive nominal dBu from the exact MOTU output reference/range, current
channel trim and the digital waveform convention; never require a true-RMS
meter or audio analyzer. When a terminal-voltage measurement is voluntarily
available, its conversion is:

```text
dBu = 20 log10(Vrms / 0.775 V)
```

State whether dBFS measurements are peak or RMS and whether the test waveform
is sine, noise, or program material. Do not infer dBu from a DAW fader label.
When the authority is the MOTU specification rather than terminal voltage,
label every level `MOTU-nominal dBu`, preserve the source/load assumption, and
keep an explicit safety margin. Do not peak- or loudness-normalize individual
captures.

The ADC determines analogue resolution and clipping. A 32-bit floating-point
file container does not add converter bit depth or recover overload. Choose 48,
96, or 192 kHz only after comparing loopback bandwidth, noise, distortion,
clocking, storage, and the final product rates. Preserve the highest qualified
raw rate; create lower-rate derivatives with one versioned resampler and filter
specification.

Some tube compressors can deliver more level than an interface input accepts.
Verify output headroom and add a characterized balanced pad when needed. Begin
with a conservative pilot and raise level only within the predeclared safe
limit. Never use converter clipping as a hardware-overload measurement.

## 4. Run chain gates in order

### Gate A: converter loopback

At every candidate sample rate, capture low and high levels through the full
converter path without the DUT. Measure level mapping, polarity, complex
response, noise, THD/IMD, channel mismatch, clipping margin, bulk delay, and
long-run drift.

### Gate B: DUT bypass

Capture the hardware bypass using the same cables and load. A hard-wire bypass
checks switching and end-to-end routing, but it does not replace the converter
loopback and does not characterize the active electronics.

### Gate C: DUT stabilization

Use the manufacturer's operating warm-up guidance as a minimum before active
measurements. Repeat one conservative short anchor until the chosen features
stop trending within a predeclared tolerance. Do not confuse random noise,
drift, and systematic calibration error.

### Gate D: active baseline and repeatability

With negligible gain reduction, measure the active path at several safe levels.
This reveals active response, transformer/tube drive, channel mismatch, and
noise before dynamic control is added. Repeat selected anchors later in the
session and after another thermal cycle.

### Gate E: pilot behavior map

Run a small set of settings that spans modes, gain-reduction depths, fastest and
slowest ballistics, drive extremes, side-chain states, and stereo coupling.
Only after the pilots pass should a long program-material campaign begin.

## 5. Use probes that isolate mechanisms

| Probe family | Primary question | Important limits |
|---|---|---|
| Low-reduction sweep/impulse/step | Complex active response, latency, LF/HF settling | A sweep during changing gain reduction is not an LTI measurement. |
| Slow up/down level sweep and stepped tones | Static curve, knee, effective ratio, hysteresis | Hold long enough for the selected recovery state; compare directions. |
| Level steps, bursts, interrupted bursts, AM carriers | Attack, recovery, multi-stage release, program dependence | Vary carrier frequency and over-threshold depth; preserve preceding state. |
| Single tones and sparse CCIF/SMPTE or custom multitones | Harmonics, IMD, modulation, overload recovery | THD alone does not define the nonlinear spectrum. |
| Repeated random-phase random-odd multisine | Excitation-dependent BLA and nonlinear detection lines | Use multiple steady periods and phase realizations; one realization does not separate noise and nonlinear variance. |
| Left-only/right-only/centered/unequal/correlated/anticorrelated/noise | Detector Link law, channel asymmetry, crosstalk, image stability | Mirror cases and keep both channel controls documented. |
| Long holds, silence, state-switch sequences | Recovery horizon, reset policy, thermal or slow state | End when a measured settling criterion is met, not an arbitrary file length. |
| Held-out program material | Distribution shift and perception | Keep whole passages and parameter groups out of training. |

A random-phase multisine yields a BLA for its particular spectrum, amplitude
distribution, operating level, and state. It is a local diagnostic, not the
device's unique linear transfer function. Detection-line interpretation
requires repeated periods and phase realizations.

## 6. Reduce the parameter space before sampling

Classify each control:

- **enumerated:** switch, relay, routing, mode, recovery detent;
- **continuous dynamic:** threshold, attack, side-chain weighting;
- **continuous audio-path:** input drive, bias or saturation control;
- **possibly separable:** output attenuation or makeup gain;
- **coupled:** stereo Link, M/S option, shared control voltage;
- **service-only:** calibration or internal trim, excluded from user controls.

Measure anchors, endpoints, centers, conventional settings, and suspected knee
or deep-reduction regions. Use Sobol or Latin-hypercube points only inside a
confirmed continuous subspace. Do not waste recordings on a separable output
gain or interpolate a physical switch.

Promote in stages:

1. **pilot:** prove the route, identity, state, and behavior axes;
2. **characterization:** fit simple feature maps and locate interactions;
3. **first training set:** cover declared controls with diverse program and
   diagnostic material;
4. **adaptive fill:** add settings only where held-out residuals, worst-case
   diagnostics, or independently trained models disagree;
5. **repeatability set:** repeat representative conditions within and across
   days without changing the test definition.

Use learning curves to decide whether more hours help. A dataset duration from
another compressor family is evidence that scale can matter, not a quota for
this unit.

## 7. Alignment without erasing the hardware

Estimate separately:

- integer delay and channel mapping;
- fractional delay;
- time-varying clock drift;
- polarity;
- converter/tap complex response;
- DUT group delay and level-dependent phase.

Use the reference or bypass path to remove transport delay. Do not circularly
shift, phase-equalize, or deconvolve away genuine DUT response. Keep the raw
comparison and the exact alignment transform used for each derivative.

## 8. Campaign completion gate

Release a capture set only when all included files have manifests and hashes,
the chain gates passed, repeats establish the measurement floor, splits are
leakage-resistant, no clipping/dropout is unresolved, and every claimed axis is
marked measured, assumed, intentionally idealized, or out of scope.
