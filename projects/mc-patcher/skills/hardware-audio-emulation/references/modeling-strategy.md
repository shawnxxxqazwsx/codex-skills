# Modeling strategy and claim selection

Choose a model from evidence and behavior, not fashion.

## Decision matrix

| Evidence and target behavior | Prefer | Avoid or qualify |
|---|---|---|
| Only a magnitude plot or sparse manual anchors | Stable IIR/FIR response reconstruction with conservative interpolation | Claims about phase, saturation, noise, tolerances, or exact settings |
| Complex frequency response/IR at fixed states | IIR pole-zero fit, FIR, or IIR plus short residual FIR | Minimum-phase reconstruction when excess phase is present |
| Static transfer curve with weak memory | Pre-filter → memoryless nonlinearity → post-filter; Chebyshev/polynomial or table | Assuming sine harmonics predict music or IMD |
| Level-dependent harmonic responses | Generalized Hammerstein, dynamic convolution, or controlled parallel harmonic branches | One universal waveshaper without level and frequency checks |
| Known series of linear/nonlinear blocks | Wiener, Hammerstein, Wiener-Hammerstein, or block-oriented gray box | Arbitrary block order chosen only by fit score |
| Feedback, interacting components, or meaningful impedance | WDF, modified nodal/state-space, DAE, port-Hamiltonian, or topology-preserving discretization | Breaking the feedback into unrelated feedforward blocks |
| Known topology but uncertain component values | Differentiable white/gray box with bounded physical parameters | Unconstrained fit that produces nonphysical or unstable values |
| Long memory, controls, and enough representative I/O data | Causal RNN/TCN/S4 or hybrid neural gray box | Noncausal production inference, one sample rate, or training-only control states |
| Dispersive mechanical system | Modal, waveguide, finite-difference, or measured hybrid | One static IR when level/time variation is target behavior |
| Time-varying delay/filter | Explicit LFO/trajectory plus fractional delay/time-varying filter, or gray-box control estimator | Treating the system as LTI |

See [sources.md](sources.md) for primary literature behind these families.

## Linear response models

Use an IIR when low latency, minimum-phase behavior, sample-by-sample controls, and a compact state are central. Fit stable poles and zeros or a topology-aware parameterization.

Use an FIR when the target contains arbitrary phase, a measured IR, non-minimum-phase behavior, or a long response that cannot be reduced without audible loss. Budget latency and convolution state.

Use a hybrid when a low-order stable IIR captures the broad analog topology and a short FIR captures the measured residual. Validate the combined phase, not only magnitude.

## Block-oriented nonlinear models

- **Hammerstein:** static nonlinearity followed by linear memory; useful when harmonic envelopes are filtered after generation.
- **Wiener:** linear conditioning before a static nonlinearity.
- **Wiener-Hammerstein:** preconditioning, static nonlinearity, then output filtering.
- **Generalized Hammerstein:** parallel nonlinear basis functions with an order-dependent linear filter; useful for separated higher-harmonic responses.
- **Volterra:** principled weakly nonlinear memory model, but coefficient count and identification burden grow quickly.

Use the residual on withheld music, multitone, and level transitions to decide whether the assumed block order is false.

## Circuit and physical models

Prefer circuit-derived models when component interaction is the sound:

- WDF for modular, passive, impedance-aware networks and certain nonlinear one-ports;
- nodal/state-space/MNA/DAE for general circuit topology and multiple nonlinearities;
- topology-preserving or zero-delay-feedback methods for resonant feedback filters;
- port-Hamiltonian or energy-based methods when passivity and multiphysics matter;
- magnetic hysteresis models for transformers/tape when history dependence is measured;
- modal/waveguide/finite-difference methods for speakers, springs, plates, scanners, and resonators.

State the numerical solver, convergence bound, failure behavior, stability argument, discretization error, and aliasing plan. A solver that converges offline is not automatically realtime safe.

## Neural and differentiable models

Use black-box neural models only with enough coverage of:

- device controls and their trajectories;
- signal classes, levels, silence, transients, and sustained tones;
- warm-up/initial state and long memory;
- hardware revision and channel;
- training and production sample rates;
- withheld devices or settings if generalization is claimed.

Require causal inference for zero-lookahead hardware unless declared latency is part of the product. Persist recurrent state across blocks and test resets, preset changes, transport starts, and silence.

Prefer a gray-box design when interpretable modules are known. Learn only uncertain control trajectories, component values, residual filters, or long-memory blocks. Constrain differentiable parameters to stable, passive, or physically plausible regions.

## Model-selection falsifiers

Write one before implementation:

- “A static waveshaper is false if the up/down level sweep produces different output at the same instantaneous input.”
- “Minimum phase is false if measured group delay cannot be explained by the fitted magnitude and bulk delay.”
- “A single channel model is false if L/R crosstalk or shared detector behavior changes with the other input.”
- “An LTI IR is false if response changes with level, temperature, time, or recent history.”
- “The selected neural context is too short if release, hysteresis, or wow trajectories remain in the residual.”

After two failed edits under one model hypothesis, add a diagnostic or revisit ownership instead of stacking corrections.

## Fidelity budget

Allocate error by perceptual and product relevance:

- protect transient timing, pitch stability, feedback behavior, alias suppression, and dry/wet coherence first;
- preserve intentional unit asymmetry or bandwidth limitation when measured;
- do not spend large CPU on noise below a credible floor while leaving control behavior wrong;
- report creative idealizations—lower noise, wider headroom, stable clock—as product choices rather than hardware accuracy.
