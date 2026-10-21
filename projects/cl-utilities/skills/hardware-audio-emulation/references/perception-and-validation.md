# Psychoacoustics and validation

Objective fidelity and perceptual fidelity overlap, but neither replaces the other.

## Reject one-dimensional distortion folklore

Do not encode “even harmonics are warm” or “odd harmonics are harsh” as a design rule. Perception depends on:

- harmonic order and absolute/relative level;
- whether products fall below, inside, or above the source spectrum;
- masking, critical-band interaction, roughness, and beating;
- harmonic versus inharmonic products;
- source pitch, timbre, crest factor, and temporal envelope;
- transients, attack/release, and modulation;
- listening level, reproduction chain, room, and listener training;
- stereo correlation and spatial location.

Even/odd balance can be one measured descriptor, not a perceptual verdict.

## Distinguish diagnostics from perceptual metrics

Use THD, THD+N, per-order harmonics, IMD, coherence, alias-to-signal ratio, and residual spectra to diagnose mechanisms. They do not directly rank preference or transparency.

Useful additional views include:

- log-spectral and multi-resolution spectral error;
- time-aligned error-to-signal ratio;
- group-delay and transient residual;
- envelope or gain-reduction error for dynamics;
- modulation-spectrum error for time-varying effects;
- noise-to-mask ratio for alias/noise screening;
- loudness and specific-loudness comparison;
- spectral centroid and attack/rise-time descriptors;
- stereo image, correlation, and crosstalk.

Publish gain, delay, polarity, and bandwidth alignment performed before a null or residual metric. Do not optimize away an intentional hardware signature.

## Use the right listening question

Separate:

- **Identity:** does the model sound like the target?
- **Detectability:** can listeners distinguish model and target?
- **Quality:** which version has fewer objectionable artifacts?
- **Preference:** which sound is preferred?
- **Usefulness:** does it behave musically across controls and material?

A preferred cleaner version may be less accurate. A detectable difference may still be acceptable. State the product question before the test.

## Listening-test patterns

### Small impairments

Use a double-blind reference/hidden-reference method inspired by ITU-R BS.1116 for subtle mismatch. Train listeners on relevant artifacts, use critical program material, allow rapid switching, and report listener screening and confidence intervals.

### Intermediate quality or multiple candidates

Use a MUSHRA-style multi-stimulus test inspired by ITU-R BS.1534. Include a real reference and meaningful anchors when possible. Do not invent an anchor that changes a different mechanism from the one being studied.

### ABX/detection

Use level- and delay-matched ABX when the question is distinguishability. Randomize trials, preregister stopping/statistics where practical, and include enough trials/listeners for the claimed effect size.

For all tests:

- level-match independently of the modeled gain signature when the question requires it;
- use multiple genres, speech, isolated instruments, transients, sustained tones, and sparse/dense mixes;
- include critical levels and controls plus neutral settings;
- prevent clipping and sample-start cues;
- retain original hardware captures and deterministic model renders;
- report headphones/speakers, listening level, room, and listener expertise.

## Artifact-focused listening

Use targeted stimuli before broad music:

- high-frequency sine sweeps and two-tone probes for aliasing;
- exposed bass and sustained notes for modulation skirts and beating;
- impulses and percussion for pre-ringing, latency, and recovery;
- stepped levels for compressor pumping/release;
- piano/guitar decay for noise modulation and hysteresis;
- stereo ambience for correlation/crosstalk;
- automation sweeps for zippering and time-varying instability.

Then confirm on representative program material. Passing a synthetic probe proves only that artifact path.

## Acceptance hierarchy

1. **Evidence fidelity:** the model does not claim unmeasured behavior.
2. **Mechanism fidelity:** topology, controls, state, and time variance are represented at the declared level.
3. **Artifact freedom:** aliasing, comb filtering, instability, zippering, clicks, and unintended modulation are bounded.
4. **Objective match:** training and withheld measurements meet declared thresholds.
5. **Perceptual result:** the listening question is answered with a suitable test.
6. **Integration:** wrapper, latency, routing, automation, preset/state, and real DAW path pass.
7. **Realtime:** worst-case CPU and memory remain within product limits.

Do not average these into one “analog score.”

## Reporting template

Report:

- target hardware/capture and claim tier;
- test signals, material, levels, controls, sample rates, and state;
- alignment and calibration;
- objective metrics with worst cases;
- listening method, listeners, statistics, and uncertainty;
- artifact probes;
- hosted/DAW and realtime paths;
- limitations and creative deviations.

Listening standards, nonlinear-distortion perception studies, loudness standards, and perceptual alias research are indexed in [sources.md](sources.md).
