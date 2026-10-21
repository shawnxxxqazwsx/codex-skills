# Nonlinearity, dynamics, magnetic memory, and time variance

Separate mechanisms before choosing a model. “Saturation” is not one behavior.

## Static and weak-memory nonlinearities

Characterize:

- symmetry and DC bias;
- threshold, knee, rail shape, dead zone, and slew;
- harmonic amplitude and phase by order;
- frequency and level dependence;
- IMD under multitone input;
- recovery and state dependence.

A Chebyshev basis can control individual harmonic orders for sinusoidal input. A generalized Hammerstein model can add an order-dependent filter. These are useful behavioral tools, but they do not by themselves reproduce arbitrary-program IMD, feedback, or history.

For H2–H9:

- retain a per-order valid-frequency mask;
- require a noise-floor margin;
- validate several input levels and crest factors;
- compare IMD and music residuals;
- band-limit or antialias every generation path;
- document whether harmonic phase is measured or assumed.

Avoid the shortcut “even is warm, odd is harsh.” Audibility depends on order, level, spectral overlap, masking, time envelope, source timbre, and inharmonic alias/IMD products.

## Electronic device mechanisms

### Diodes and waveshapers

Include pre/post filtering and any nonlinear feedback around the diode. A static clip curve is adequate only if state and frequency tests support it. Model asymmetric bias and recovery when measured.

### Operational amplifiers

Possible signatures include input/output saturation, asymmetric supply rails, current limiting, finite bandwidth, gain-bandwidth interaction, slew rate, recovery, and DC behavior. Do not add all of them automatically.

### Tubes, BJTs, JFETs, and OTAs

Bias point, surrounding impedances, local/global feedback, device capacitance, and supply rails shape the result. Use a physically motivated component model or identify a bounded behavioral block in its circuit context. Validate control/current dependence for OTAs and gate/bias behavior for JFETs.

### Transformers and inductors

Relevant axes can include:

- source/load impedance and winding ratio;
- leakage inductance and parasitic capacitance;
- LF saturation, level-dependent inductance, and HF loss;
- hysteresis and remanence;
- asymmetric flux or DC offset;
- thermal behavior and interwinding coupling.

Use a Jiles–Atherton or other hysteretic model only when history-dependent behavior is in scope and measured. A static transfer curve cannot reproduce a hysteresis loop.

## Dynamic range processors

Decompose a compressor, limiter, leveler, gate, expander, de-esser, or transient processor into:

1. sidechain input and filtering;
2. level detector: peak/RMS, linear/log, rectifier, averaging;
3. static curve: threshold, ratio, knee, range;
4. ballistics: attack, release, hold, autorelease, program dependency;
5. control-to-gain mapping and gain cell;
6. feedforward or feedback topology;
7. lookahead/delay if digital;
8. stereo link, channel coupling, and external sidechain;
9. gain-cell and amplifier distortion/noise.

Measure steady-state curve separately from ballistics. Use bursts and stepped envelopes at several over-threshold levels. A detector time constant estimated at one level may not describe an opto, vari-mu, FET, diode bridge, or PWM/VCA design.

Vactrols are program-dependent multiphysics elements; their rise/decay can depend on illumination history. Transformer/tube gain stages around a detector may have their own nonlinear memory. Keep these blocks separate unless a black-box model is explicitly trained to absorb them.

## Tape and magnetic recording

A full tape machine may require separate modules for:

- record amplifier and pre-emphasis;
- bias oscillator and bias-dependent operating point;
- magnetic hysteresis, saturation, dead zone, and remanence;
- record/play head gap and spacing losses;
- head bump and speed-dependent response;
- playback electronics and de-emphasis;
- time-varying transport delay: wow, flutter, scrape flutter, drift;
- hiss, modulation noise, print-through, dropout, crosstalk, and channel variation.

Do not call a head-bump curve plus waveshaper a physical tape model. It may be a valid source-constrained tape-colour model if named honestly. Capture fluctuating delay and stochastic noise separately when possible; they need different validation and random-state handling.

## Amplifiers, cabinets, and transducers

A guitar/bass amp chain can include conditioning filters, multiple nonlinear gain stages, tone stack, phase inverter, power stage, output transformer, electrical speaker load, nonlinear driver, cabinet, microphone, and room. Order and feedback matter.

An IR describes an LTI cabinet/microphone snapshot. Large-signal motor, suspension, cone, thermal, and back-EMF behavior changes with level and history. If the product claims level-dependent cabinet behavior, measure it at multiple drive levels and distinguish electrical, mechanical, acoustic, microphone, and room contributions.

## Analog delay and modulation

### BBD

A BBD is a variable-clock sampled analog system. Relevant blocks include input/reconstruction filters, fixed stage count, variable clock, compander, insertion loss, noise, distortion, aliasing, clock bleed, and feedback. A conventional fractional delay with a triangle LFO misses clock-rate warping and surrounding circuitry.

### Tape delay

Model variable transport speed and record-to-play spacing, feedback path filtering/saturation, head selection, splice behavior, and noise only when supported. Tape-like pitch response during delay-time changes differs from simply moving a read pointer.

### Phaser, chorus, flanger, vibrato, tremolo, rotary

Preserve:

- the actual time-varying mechanism: all-pass stages, BBD delay, amplitude modulation, scanner, or Doppler path;
- LFO waveform, control law, phase, startup, and stereo relationship;
- feedback polarity and location;
- embedded nonlinear stages and compander;
- moving-filter or moving-delay interpolation artifacts;
- dry/wet phase and latency.

For gray-box or neural modeling, expose or estimate the control trajectory and evaluate modulation spectrum, not only sample error.

## Electromechanical reverb

Spring and plate reverbs are dispersive, multi-modal mechanical systems with transducers and often nonlinear drive/recovery electronics. Options include:

- measured convolution for a fixed linear state;
- modal or waveguide models for interpretable dispersion/decay;
- finite-difference/energy-based physical models;
- hybrid early response plus parametric/modal tail;
- neural residual for device-specific behavior.

Validate frequency-dependent decay, dispersion, modal density, input/output transducer response, drive-level dependence, stereo pickup geometry, shock/excitation behavior, and realtime stability.

## Stochastic components

Keep noise separate from deterministic response:

- estimate PSD, nonstationarity, correlation, modulation, and channel coupling;
- use deterministic seeds in tests and independent/random seeds only by product design;
- ramp noise state across preset or bypass changes;
- do not use noise to hide deterministic mismatch;
- do not reproduce converter or analyzer noise as hardware without a bypass baseline.

Primary papers for these mechanisms are indexed by category in [sources.md](sources.md).
