# mc-patcher hardware-model baseline

Read this before changing an existing model. It records project-specific lessons that generic virtual-analog literature does not know.

## Existing source hierarchy and claim language

The current Hardware Lab ledger defines an evidence order of user measurements, manufacturer plots/tables, manufacturer control specifications, then specialist historical sources. Preserve that order and its explicit exclusions:

- [Hardware model ledger](../../../../plugins/silk_tape/HARDWARE_MODELS.md)
- [Silk/Tape measurement notes](../../../../plugins/silk_tape/MEASUREMENT.md)
- [Response verification fixture](../../../../tests/silk_tape_response_verify.cpp)
- [Production processor](../../../../plugins/silk_tape/McSilkTapeProcessor.cpp)
- [Model implementation](../../../../plugins/silk_tape/McHardwareEqModels.cpp)

The implemented EQ collection is mostly **frequency-response behavior**, not component-level reconstruction. A Distortion switch is available only where separate evidence exists. Preserve “source-constrained,” “measured,” “manual-anchor,” and “creative headroom law” distinctions in code, tests, UI text, and reports.

## Lessons from the MBP Silk work

### Magnitude is only one axis

A visually close EQ curve can still miss:

- phase and group delay;
- parallel-additive versus series topology;
- boost/cut asymmetry and inter-band interaction;
- interstage operating level;
- source/load impedance;
- location of nonlinear stages;
- stereo or Mid/Side coupling.

The SFE implementation is a concrete example: `output = original + amount * filtered` recreates a different transition shape from a conventional series EQ because the filtered path's phase participates in the sum.

### Harmonic measurements have a valid domain

At sample rate `Fs`, an order `n` measured from a fundamental is valid only while `n f <= Fs/2`. At 48 kHz, H9 is therefore limited to about 2.67 kHz. Treat higher-frequency rows as folded, rejected, or noise-contaminated—not as a target curve.

Screen H2–H9 per order, frequency, input level, control state, and margin over the measured noise floor. Never fit the analyzer's noise floor as a hardware signature. A missing bypass capture prevents clean separation of the unit from converters and the rest of the measurement chain.

### Analyzer interaction can masquerade as hardware behavior

The earlier dynamic peak estimator used a hold/release time constant. During sweeps and Plugin Doctor-style tests it created low-rate amplitude modulation, skirts, and vertical noise that looked like nonlinear device behavior. The current project notes explain why a scale-invariant, locally estimated peak law was chosen as a creative headroom rule.

Before accepting a low-frequency bump, notch, skirt, or ripple:

1. bypass one model block at a time;
2. repeat with a steady sine, impulse, and sweep;
3. freeze or reset dynamic state;
4. compare offline and hosted analyzer paths;
5. test multiple block sizes and sweep speeds.

### Oversampled branches must share time

The oversampling FIR round trip delays the nonlinear branch. Summing it with an undelayed fundamental caused comb filtering near 5–6 kHz even though the harmonic generator itself looked correct. The production fix aligns the complete dry and nonlinear paths, reports integer latency to the host, and keeps the Harmonics-off path delayed without unnecessarily running the 8x filters.

For every parallel branch verify:

- impulse peak alignment;
- harmonics-on versus harmonics-off fundamental response;
- bypass and dry/wet alignment;
- host latency report and PDC;
- parameter transition with state reset;
- combined Blue/Red or multi-module states, not only isolated modules.

### Lower-layer tests do not prove the hosted report

The engineering regression may pass while Plugin Doctor or a DAW exposes a wrapper, state, latency, or routing problem. Keep the failure hierarchy explicit:

1. mathematical or offline model;
2. processor fixture;
3. plug-in wrapper;
4. analyzer or hosted plug-in;
5. real DAW and production routing.

Say exactly which layer passed.

## Existing acceptance signals worth preserving

The Silk/Tape fixture already demonstrates useful patterns:

- absolute response comparison against all measured curves;
- H2–H9 order checks and per-order bandwidth awareness;
- headroom checks across -24 to +12 dBFS;
- explicit alias probes such as 10 kHz H3 and 5 kHz H5;
- maximum-settings non-finite and clipping checks;
- combined-module impulse smoothness;
- steady-sine fundamental comparison with harmonics on/off;
- state-transition sideband measurement;
- sample-rate-specific checks including 192 kHz where a high-order target is otherwise out of band.

Extend the nearest signal instead of building a second overlapping acceptance harness.

## Project interpretation rules

- The scale-invariant distortion law is intentional product behavior, not a verified analogue compression curve.
- No multi-level MBP sweep currently proves compression, hysteresis, or a clipping transition.
- The 542 model does not claim tape hiss, hysteresis, wow/flutter, or scrape flutter.
- Historic and manual-derived EQs should not gain invented transformer/tube signatures from a THD headline.
- Orthonormal Mid/Side routing and even multichannel layouts must remain deterministic; define unpaired-channel behavior explicitly.
- Do not deploy or build McHost for changes confined to this skill.
