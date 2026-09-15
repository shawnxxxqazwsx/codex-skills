# Measurement and system identification

The measurement plan defines what can be claimed. Save raw captures, scripts, settings, and calibration before fitting.

## Capture manifest

Record:

- manufacturer, model, serial/revision, firmware, channel, warm-up time, supply, temperature if relevant;
- complete control positions, switches, internal calibration, and previous state;
- balanced/unbalanced topology, source and load impedance, cable and patch path;
- converter models, loopback response, clocking, sample rate, bit depth, bandwidth, and gain;
- dBu/dBV/voltage to dBFS mapping and whether amplitude is peak or RMS;
- stimulus file hash, duration, fade, repetitions, and analyzer configuration;
- raw input/output and a bypass or loopback capture.

If an analogue calibration is missing, calibrate only to the known digital stimulus and say so.

## Decompose the capture campaign

### Linear behavior

Measure complex `H(f)`, not only magnitude:

- synchronized sweep and impulse response;
- phase, unwrapped phase, group delay, and bulk latency;
- step response, DC offset, LF/HF extension, ringing, and settling;
- control endpoints and interior positions;
- channel mismatch, crosstalk, polarity, and Mid/Side behavior;
- noise spectrum with input terminated and with representative source impedance.

Repeat at several levels to test whether the “linear” response is level-dependent.

### Static nonlinearity

Capture:

- slow transfer curve in both directions;
- positive/negative symmetry, bias, dead zone, rails, and recovery;
- single-tone H2–Hn versus frequency and level;
- two-tone IMD, multitone, and crest-factor variation;
- intersample peaks and overload recovery.

THD alone discards order, phase, and frequency. Do not reconstruct a harmonic signature from a single THD number.

### Dynamic memory

Use stepped levels, bursts, tone-on/tone-off sequences, amplitude ramps in both directions, impulses at different operating points, and program material. For dynamics processors include:

- attack/release at several over-threshold amounts;
- peak, RMS, log/linear detector behavior;
- feedforward/feedback clues;
- knee and ratio;
- sidechain filters, stereo link, and autorelease;
- recovery after silence and state initialization.

For magnetic, opto, thermal, or speaker systems include history loops, long holds, return trajectories, and temperature/time-scale tests.

### Time variance

For tape, BBD, chorus, phaser, rotary, mechanical scanners, and clocks:

- record long enough to observe slow drift;
- estimate delay or filter trajectory separately from audio transformation;
- measure LFO waveform, phase, rate, depth, startup, and stereo relationship;
- characterize wow, flutter, scrape flutter, clock bleed, and noise stationarity only if present;
- distinguish deterministic modulation from stochastic variation.

## Swept-sine rules

Exponential and synchronized swept sine can separate higher-harmonic impulse responses efficiently. Use synchronization when phase of the higher-harmonic responses matters.

Observe these limits:

- a separated order `n` is meaningful only where `n f <= Fs/2`;
- a fitted order is valid only over the excitation amplitude and frequency domain;
- time variance or changing detector state violates the assumed measurement model;
- sweep rate can interact with release, thermal, or peak-estimator time constants;
- regularize deconvolution outside the excited band;
- preserve the noise margin per order and reject bins close to the floor.

Validate an ESS-derived model with independent stepped sines, multitone, and music. The sweep used for fitting is not a withheld test.

## Multitone and intermodulation

Use multitone to expose simultaneous-frequency behavior and intermodulation that single-tone harmonic tests miss. Choose phases and crest factor deliberately. Leave empty spectral bins or use a dual-channel/noncoherence method so generated components are separable.

For feedback and multiband devices, vary tone spacing and level distribution. A match to harmonics with poor IMD indicates a wrong basis, block order, or missing memory.

## Dataset design for gray-box or neural models

Split by behavior, not random adjacent frames:

- withhold entire control positions, levels, signal classes, and long state trajectories;
- include silence, low-level detail, high crest factor, DC-safe transients, overload, and recovery;
- balance control coverage instead of letting neutral settings dominate;
- include sufficient preroll to set state, and specify reset policy;
- keep hardware and digital paths sample-aligned without circularly correcting away genuine group delay;
- never leak the same sweep or adjacent capture segments across train and test.

Use multiple metrics: time-domain error, multi-resolution spectral error, loudness/envelope error, modulation spectrum for time-varying effects, and artifact-specific alias/noise tests. Retain a listening set that was not optimized against.

## Fit discipline

1. Remove only documented converter/loopback behavior; keep a raw comparison.
2. Fit physical or topology parameters within bounded plausible ranges.
3. Weight frequency and level by the declared use case, but publish the weighting.
4. Penalize instability, discontinuity, non-monotonic controls, implausible poles, and excess CPU.
5. Compare residuals by frequency, level, control, and time—not a single average.
6. Inspect worst cases and direction changes; low RMS can hide a narrow notch or temporal artifact.
7. Lock a deterministic fixture before translating the fit to realtime code.

## Acceptance package

Deliver:

- capture manifest and raw data location;
- evidence/claim ledger;
- fitted parameters and versioned generation script;
- plots for training and withheld data;
- order-validity and noise masks;
- latency and alignment report;
- alias, IMD, state-transition, and extreme-control tests;
- hosted-plug-in or DAW result when relevant;
- explicit missing evidence and nonclaims.

Primary research for ESS, multitone, nonlinear identification, and transfer-curve measurement is indexed in [sources.md](sources.md).
