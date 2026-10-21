# Antialiasing, multirate design, latency, and realtime performance

Every nonlinearity creates bandwidth. Antialiasing is part of the model, not a final polish.

## Perform an alias audit

For each nonlinearity record:

- maximum input bandwidth and internal level;
- expected harmonic/order bandwidth;
- whether it sits in feedforward, feedback, or a state update;
- sample rate and state-update rate;
- chosen mitigation and residual test;
- latency and phase contribution.

Audit waveshapers, hard switches, rectifiers, limiters, nonlinear filters, feedback saturation, parameter modulation, neural activations, resampled delays, and discontinuous oscillators.

## Choose among complementary methods

### Oversampling

Use when the nonlinearity is complex, stateful, feedback-connected, learned, or difficult to integrate analytically. Design interpolation and decimation jointly. A larger factor with a weak decimator can perform worse than a smaller factor with a better filter.

Useful structures include cascaded half-band FIR/IIR stages, polyphase FIR, and deliberately specified passband/stopband filters. Compare linear-phase latency against nonlinear-phase low-latency error.

### Antiderivative antialiasing

ADAA is effective for analytically integrable memoryless waveshapers and piecewise polynomial functions. Handle the near-equal-input limit numerically; direct quotient forms can lose precision. Higher-order or stateful extensions add constraints and delay.

Stateful ADAA can reduce aliasing in some scalar-nonlinearity systems and feedback structures, but it is not a universal drop-in. Validate state update and output equations, coefficient compensation, stability, and any induced low-pass effect.

### Bandlimited discontinuity methods

Use BLEP/polyBLEP for steps and BLAMP/polyBLAMP for slope discontinuities in oscillators, clipping corners, and switched systems. Match method order to the discontinuity. Hard sync and BBD clock events may require specialized treatment.

### Bandlimited harmonic generation

For controlled Chebyshev or parallel-harmonic models, prefilter the fundamental and omit or suppress each order above its valid band. This prevents impossible target fitting but still requires a decimator if processing occurs at a higher rate.

### Continuous-time convolution or hybrid methods

Continuous-time-inspired convolution and antiderivative methods can reduce aliasing without very high oversampling for selected waveshapers and nonlinear filters. A hybrid—modest oversampling plus ADAA/BLEP—often yields a better CPU/quality tradeoff.

## Oversampling is a complete timed path

Specify:

1. input interpolation response;
2. nonlinear/state processing rate;
3. control and detector rate;
4. output decimation response;
5. integer/fractional group delay;
6. reported host latency;
7. bypass and dry/wet delay;
8. transition when quality factor changes.

Never sum an oversampled round-trip path with an undelayed path. Verify impulse alignment and a harmonics-on/off fundamental null. Keep every parallel module and analyzer path on the same reference time.

For dynamics, decide whether attack/release coefficients represent seconds at the internal rate or are intentionally held at host rate. For recurrent neural models, changing sample rate without adapting state dynamics changes the model.

## Filter design checklist

- Define audible passband, ripple, transition band, stopband, and attenuation from an artifact target.
- Inspect interpolation images and decimation folds separately.
- Test near-Nyquist fundamentals, not only low-frequency tones.
- Include worst-case drive, feedback, and combined modules.
- Check phase and latency, not just alias level.
- Measure at 44.1/48 kHz and every supported high rate.
- Use double-precision offline reference or a much higher-rate render for comparison.
- Avoid claiming inaudibility from visual FFT darkness alone.

Explicit probes should include order/fold pairs such as a high-frequency H3 and a lower-frequency high-order product near host Nyquist.

## Perceptual alias evaluation

Report raw alias-to-signal ratio and a masking-aware measure such as noise-to-mask ratio when suitable. Masking metrics depend on their psychoacoustic model and test signal; confirm critical cases by blind listening.

Aliased nonlinear products are often inharmonic and may be more salient than desired high harmonics. Inspect low-frequency folds, modulation sidebands, and time-varying “birdies.”

## Realtime design for mc-patcher

- Allocate and design coefficients in prepare/setup paths, never the audio callback.
- Precompute tables and filter coefficients; bound solver iterations or use a proven non-iterative form.
- Store contiguous per-channel state and consider channel batching/SIMD.
- Share immutable coefficients, not mutable channel state.
- Disable denormal penalties with the project's established JUCE/CPU mechanism.
- Avoid locks, logging, file I/O, model loading, and unbounded loops on the audio thread.
- Check the smallest relevant block size; large-block benchmarks can hide callback overhead and neural latency.
- Measure maximum supported channel count, maximum oversampling, highest sample rate, worst drive/feedback, and automation.
- Profile before replacing accurate math. Approximate expensive functions with bounded-error tables or splines only after an audio-domain error test.

For neural models, compare RNN, TCN, S4, and gray-box hybrids by causal latency, state size, operations per sample, block-size sensitivity, and control coverage—not parameter count alone.

## Realtime acceptance

Pass all of:

- no allocation, locks, or unbounded solver behavior in processing;
- finite output and bounded state at extreme input/control;
- stable reset and sample-rate/block-size changes;
- correct latency report and bypass/dry/wet time alignment;
- alias probes and desired-harmonic preservation;
- CPU headroom on target hardware and channel count;
- deterministic regression output;
- hosted VST3/DAW path when the affected behavior lives there.

The oversampling, ADAA, BBD, sample-rate-independent neural, and optimization papers are indexed in [sources.md](sources.md).
