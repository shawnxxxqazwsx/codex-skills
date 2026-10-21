---
name: hardware-audio-emulation
description: "Research, design, implement, review, and validate hardware-inspired or hardware-matched audio DSP in mc-patcher: EQ and tone stacks, colour stages, dynamics, tape, transformers, amplifiers, cabinets, analog delay/modulation, electromechanical reverb, converters, and synth circuits. Use for measured-response, source-constrained, behavioral, circuit-informed, gray-box, or neural virtual-analog work. Do not use for clean utility DSP, hosting/IPC/routing, GUI-only work, or generic audio research without a hardware-emulation target."
---

# Hardware Audio Emulation

Use this skill together with the repository `AGENTS.md` and the `mc-patcher` skill. This skill supplies hardware-emulation research and decision rules; repository guidance still owns build, test, deployment, realtime, and multichannel policy.

## Load only the references the task needs

Always read [project-baseline.md](references/project-baseline.md) before changing an existing hardware model.

- Read [modeling-strategy.md](references/modeling-strategy.md) when choosing or challenging a model family or fidelity claim.
- Read [measurement-and-identification.md](references/measurement-and-identification.md) before capture, fitting, dataset construction, or measurement interpretation.
- Read [eq-linear-systems.md](references/eq-linear-systems.md) for EQ, tone stacks, filter controls, phase, impedance, or convolution.
- Read [nonlinear-dynamics.md](references/nonlinear-dynamics.md) for saturation, harmonics, compression, tape, transformers, tubes, transistors, hysteresis, noise, or time variance.
- Read [antialiasing-realtime.md](references/antialiasing-realtime.md) whenever a nonlinearity, resampler, feedback loop, neural model, dry/wet path, or oversampled branch is involved.
- Read [perception-and-validation.md](references/perception-and-validation.md) when defining acceptance, listening tests, perceptual claims, or artifact thresholds.
- Read [plugin-type-map.md](references/plugin-type-map.md) when scoping an unfamiliar hardware category.
- Read [sources.md](references/sources.md) when citing, extending, or auditing the research basis.

## Establish the claim before the algorithm

Choose the strongest claim the evidence actually supports, and put it in the task notes:

1. **Hardware-inspired:** borrows a mechanism or control idea; does not claim a match.
2. **Source-constrained:** reconstructs documented controls, plots, limits, or partial measurements.
3. **Measured response:** matches stated captures over their documented conditions.
4. **Behavioral emulation:** matches input/output behavior over a declared level, frequency, control, state, and sample-rate domain.
5. **Circuit-informed gray box:** preserves known topology while identifying unknown components or residuals.
6. **Circuit-level physical model:** derives and validates the relevant electrical, magnetic, or mechanical equations.

Do not silently upgrade a source-constrained curve into a component-level claim. Record the target unit, revision, calibration, source/load impedance, converter path, bandwidth, control state, temperature or warm-up state, and missing evidence.

## Follow the modeling workflow

1. **Define the behavior axes.** List frequency, phase/group delay, level, controls, time, history, stereo coupling, noise, sample rate, and latency. Mark each axis measured, sourced, assumed, intentionally idealized, or out of scope.
2. **Prove a baseline.** For a bug, reproduce the user-visible failure before editing. For a new model, preserve a hardware capture or a deterministic source-derived fixture before implementation.
3. **Decompose the device.** Separate linear response, static nonlinearity, dynamic memory, stochastic noise, time variance, channel coupling, and control law. Preserve their physical order and feedback where evidence requires it.
4. **Choose the least complex defensible model.** Use the decision matrix in [modeling-strategy.md](references/modeling-strategy.md). State one observation that would falsify the choice.
5. **Calibrate internal level.** Define the mapping between dBFS and the measurement domain. If dBu, impedance, or converter calibration is absent, say so and avoid an analogue-level claim.
6. **Design antialiasing and timing as part of the model.** Specify interpolation, decimation, internal rate, state-rate behavior, latency, bypass, dry/wet alignment, and host reporting before approving nonlinear output.
7. **Fit on training conditions and test withheld conditions.** Hold out levels, controls, signals, and state trajectories; a fit to the same sweep is not independent validation.
8. **Validate in layers.** Compile the changed target, rerun the primary signal, run one adjacent regression, run the impacted suite, then exercise the hosted plug-in or DAW path when the report lives there.
9. **Report evidence boundaries.** Separate objective match, artifact checks, realtime/format checks, listening results, deployment, and untested paths.

## Require an evidence ledger

For each modeled feature, keep a compact row containing:

- feature and signal-chain location;
- evidence source and conditions;
- selected model and free parameters;
- training and withheld fixtures;
- metric and threshold;
- claim level;
- known alternatives or uncertainty.

If no evidence supports noise, crosstalk, hysteresis, compression, wow/flutter, or unit variation, omit it or label it clearly as a creative option. Never infer a harmonic spectrum from THD alone.

## Preserve mc-patcher constraints

- Keep processing allocation-free and lock-free on the audio thread.
- Preallocate all delay, oversampling, solver, convolution, and neural state.
- Verify supported sample rates, block sizes, channel layouts, Stereo/Mid-Side behavior, and the repository's high-channel-count path.
- Define whether paired channels share hardware state, detector state, noise, tolerance, or modulation; do not accidentally couple independent channels.
- Smooth controls without erasing hardware ballistics or creating zippering. Reset basis-dependent state when routing domains change.
- Measure CPU at maximum channels, maximum drive, smallest relevant block, and highest supported sample rate. Optimize the owning layer after profiling.
- Keep wrapper latency, bypass, dry/wet, analyzer, and production paths on the same time base.

## Stop and request evidence when needed

After a time-boxed attempt, stop broad trial-and-error if hardware identity, calibration, sweep conditions, control state, sample rate, block size, analyzer capture, or hosted reproduction is missing and materially changes the model. Provide the exact capture or metadata needed next. Do not say “matched” or “fixed” until the reported path passes.

## Research discipline

Prefer manufacturer service documentation, standards, author or publisher copies of papers, and user-provided measurements. Open every cited source. Distinguish peer-reviewed papers, conference papers, preprints, manuals, and secondary measurements. Link claims close to sources, preserve raw-capture provenance, and never invent a DOI, URL, measurement condition, or hardware behavior.
