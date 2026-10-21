# EQ and linear-system emulation

An EQ becomes hardware-like through topology, complex response, control law, impedance, and stage interaction—not by appending a generic saturator to a magnitude fit.

## Fit the correct quantity

Fit complex response `H(f)` whenever measurements permit. Compare:

- magnitude in dB with both RMS and maximum local error;
- unwrapped phase after a separately reported bulk delay;
- group delay and step/impulse behavior;
- DC, Nyquist, and out-of-band behavior;
- response at every measured control node;
- cascaded and combined-band states, not only one band at a time.

Magnitude determines phase only for a causal stable minimum-phase system. Do not use minimum-phase reconstruction as a default when transformers, parallel paths, crossover networks, all-pass sections, converter filters, cabinets, or acoustic paths may add excess phase.

## Preserve topology

Establish whether the hardware is:

- a series cascade;
- a parallel additive/subtractive filter path;
- a passive network with insertion loss and makeup gain;
- a feedback tone-control network;
- a proportional-Q or constant-Q bank;
- a boost-and-attenuate interaction such as a passive program EQ;
- a Mid/Side or stereo matrix around the EQ;
- switched/stepped or continuously variable;
- loaded by preceding and following stages.

Topology affects interaction, phase, headroom, and the level seen by nonlinear components. Matching isolated curves while changing topology is a source-constrained approximation, not a circuit match.

## IIR, FIR, and hybrid choices

### IIR

Use IIR for compact minimum-phase responses and low latency. Prefer cascaded second-order sections, state-space, or a stable state-variable structure. Check coefficient quantization and pole movement across every sample rate and parameter extreme.

Do not linearly interpolate arbitrary direct-form coefficients. Use a parameterization with stable intermediate states—frequency/Q/gain, pole radius/angle, state-space interpolation with stability constraints, or a time-varying-stable filter structure.

### FIR

Use FIR or partitioned convolution for arbitrary phase or a measured impulse response. Trim only after inspecting time-domain energy, low-frequency resolution, and pre/post ringing. State whether the IR includes converters, room, microphone, cabinet, or bulk delay.

### Hybrid

A broad IIR plus a short residual FIR can reduce latency and CPU while retaining measured phase detail. Fit and validate the cascade jointly.

## Prevent high-frequency cramping

The bilinear transform warps frequency near Nyquist. Conventional second-order digital EQs can become narrower or roll off too quickly at high frequencies. Evaluate:

- Orfanidis-style prescribed Nyquist gain;
- direct digital-domain parametric designs;
- analog-matched prewarping such as Massberg's low-pass approach;
- higher-order shelf structures;
- higher internal rate when the analog curve must remain meaningful near host Nyquist.

Do not assume one prewarped center frequency fixes the complete width and shape. Compare at 44.1, 48, 88.2, 96, and 192 kHz when supported.

## Make control behavior hardware-like

Capture and reproduce:

- mechanical or electrical pot taper;
- stepped frequency positions, detents, dead zones, and end stops;
- gain-dependent Q or bandwidth;
- boost/cut asymmetry;
- interaction among adjacent bands;
- mode switches that change topology, not just coefficients;
- bypass location and makeup gain;
- click, slew, or transition behavior if it is intentional and safe.

Fit measured anchor states first. Interpolate a topology-aware parameterization and verify monotonicity, stability, and absence of zippering between anchors. More anchor points are needed where the real control law bends.

## Model source/load and component effects only when relevant

Passive tone stacks, inductors, transformers, pickups, microphones, and vintage outputs can change with source/load impedance. A fixed digital `H(f)` represents only one termination.

For a behavioral model, offer impedance or drive controls only if measured. For a circuit model, preserve component interaction and tolerances. Unit variation can be represented as deterministic seeded tolerance sets after measurements from multiple units—not as unbounded random drift.

## Place nonlinear behavior at the owning stage

Different orders produce different results:

- input transformer → passive EQ → makeup amplifier;
- pre-emphasis → saturation → de-emphasis;
- band filter → nonlinear gain stage → summing bus;
- passive loss → tube or op-amp makeup;
- shared output transformer after the entire EQ.

Measure per-band overload and combined-band overload. If only line-stage THD is known, label a conservative generic line-stage option; do not imply each band saturates independently.

## EQ validation grid

At minimum test:

- all sample rates and control endpoints;
- every measured node plus between-node interpolation;
- single bands, adjacent bands, and maximum combined states;
- boost/cut symmetry or intentional asymmetry;
- impulse/step, complex response, and group delay;
- multiple input levels to expose level-dependent response;
- bypass/null and dry/wet or parallel-path alignment;
- automation at the fastest supported rate;
- Stereo/Mid-Side and multichannel independence/coupling;
- non-finite, DC, denormal, and extreme-Q stability.

Use the research on analog-matched digital EQ, higher-order shelves, and time-varying filter structures in [sources.md](sources.md).
