# Airwindows EQ DSP as a model-design reference

Use this reference only when an Airwindows implementation is relevant to a
Pigora EQ model or runtime problem. Source reviewed: the official
[Airwindows repository](https://github.com/airwindows/airwindows) at commit
`d22a25b7f7c0c8c05e9f3ae480e7f1da9769f49d`, under
`plugins/LinuxVST/src/`. Recheck the selected source file and revision when
using a different checkout. Airwindows code is evidence of *its own*
implementation, not a measured target for RND, WesAudio, SPL, or another named
device. Do not copy its coefficients, control laws, nonlinear stages, or
branding into a hardware fit without independent evidence and a separate
compatibility and license review.

## Transferable hypotheses

| Source file | Observed implementation | Pigora use and falsifier |
|---|---|---|
| [SmoothEQ3/SmoothEQ3Proc.cpp](https://github.com/airwindows/airwindows/blob/d22a25b7f7c0c8c05e9f3ae480e7f1da9769f49d/plugins/LinuxVST/src/SmoothEQ3/SmoothEQ3Proc.cpp) | Splits bass, mid, and treble with two cascaded crossover passes, subtracts filtered signals to form residual bands, and applies separate band gains. Crossover coefficients depend on sample rate; its simplified biquad assumes a fixed Q. | Try a low-order split/recombine model when the frozen source supports broad overlapping tone bands. Check unity reconstruction, control direction, crossover shoulders, phase, and full response against the same target. Do not replace a documented adjustable Q with the fixed-Q shortcut. |
| [PearEQ/PearEQProc.cpp](https://github.com/airwindows/airwindows/blob/d22a25b7f7c0c8c05e9f3ae480e7f1da9769f49d/plugins/LinuxVST/src/PearEQ/PearEQProc.cpp) | Repeatedly subtracts nested filtered bands and recombines them with independent levels; its frequency factors depend on sample rate. | Consider residual-band decomposition when a serial Bell/shelf stack cannot express a source-supported broad curve. Test gain interaction, neutral state, exterior response, and order/CPU cost. Its fixed band positions and level law are not native Pigora hardware controls. |
| [Baxandall3/Baxandall3Proc.cpp](https://github.com/airwindows/airwindows/blob/d22a25b7f7c0c8c05e9f3ae480e7f1da9769f49d/plugins/LinuxVST/src/Baxandall3/Baxandall3Proc.cpp) | Uses sample-rate-normalized low-pass biquads, derives a treble residual by subtraction, and couples filter frequency to gain. It also surrounds the EQ with nonlinear `sin`/`asin` processing. | Test gain-dependent frequency or parallel low/high paths only when target curves or documented controls support that interaction. Evaluate linear magnitude separately from level-dependent behavior; the nonlinear wrapper cannot be inferred from magnitude plots. |

`SmoothEQ3` is a product name, not proof of click-free parameter automation:
the inspected code calculates coefficients at block entry. Any Pigora
automation-smoothing proposal still needs its own time-domain transition and
host-block tests.

## How to evaluate a borrowed idea

1. Name the exact Pigora section, frozen target/grid hash, failing curve or
   behavior, and the structural hypothesis suggested by the source file.
   Compare a cheap isolated prototype with the current model before changing
   production DSP. Keep source-backed native modes and controls intact.
2. Check boost, cut, neutral, control midpoints, crossover or detent edges,
   near-Nyquist regions, and each declared sample rate. A passing average or a
   smooth coefficient trajectory cannot hide a local response excursion.
   Interpolation between fitted rate banks must be screened at the bank
   boundaries *and inside* each interval; preserve stage identity or justify
   another topology-aware realization rather than blending unrelated stage
   indices.
3. Re-run the unchanged public or inference row gate, the separate control
   shape gate, stability/finite-output checks, actual `processBlock` agreement,
   and realtime stage, CPU, memory, channel-count, and block-size limits.
   Report any improvement and any extra cost separately. A sample-rate or
   automation smoothness win does not establish better hardware fidelity.

The reference is optional model-family guidance. It never adds Airwindows
response rows to `public-fit-domain.csv` or an inference ledger, changes a
frozen tolerance, or upgrades a public-fit or product-use state.
