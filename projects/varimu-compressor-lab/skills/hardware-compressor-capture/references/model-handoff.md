# Model and plug-in handoff

Use this reference only after the capture set passes its data gates. It prevents
the campaign from locking an attractive architecture before the device has
falsified simpler alternatives.

## Build the evidence ledger

For each claimed feature record:

| Feature | Evidence and conditions | Candidate owner | Falsifier | Withheld test | Metric/margin | Status |
|---|---|---|---|---|---|---|
| Active complex response | no/low-GR multilevel captures | stable IIR/FIR or measured residual | level changes phase/response beyond repeats | withheld level/session | complex error | open |
| Static curve/knee | steady up/down levels | explicit gain computer | direction/history changes output at equal level | withheld depth/mode | GR/curve error | open |
| Ballistics | steps/bursts/recovery | detector/state module | residual depends on earlier history beyond state | withheld trajectory | envelope error | open |
| Audio-rate nonlinearity | tone/IMD/multitone at several states | pre/gain/post nonlinearity | one block order fails IMD or GR-dependent spectra | withheld tone/music | harmonic/IMD error | open |
| Stereo Link | asymmetric stereo probes | dual detector plus measured coupling | arbitrary other-channel envelope is not predicted | mirrored withheld probes | GR/image/correlation | open |
| Noise/drift | terminated and repeated captures | optional stochastic module | noise is converter- or session-owned | other session | PSD/correlation | open |

## Compete model families in stages

Start with the least complex defensible candidates:

1. explicit compressor gray box with measured static curve, detector,
   ballistics, and separable input/output response;
2. small recurrent or causal convolutional model conditioned on controls;
3. long-memory TFiLM, encoder-decoder, or structured state-space candidate;
4. hybrid gray box with learned state or nonlinear residual;
5. distributed/joint stereo model only when control coupling or audio-path
   interaction requires it.

TFiLM and structured state-space models have useful compressor precedents, but
the best architecture depends on device, time constant, material, controls, and
metric. Existing LA-2A or software-compressor results do not establish the best
Vari-Mu architecture.

Treat a proposed `pre filter -> dynamic gain -> post filter + neural residual`
structure as a hypothesis. It is false if transformer/tube response changes
with drive or gain-reduction state in a way the block order cannot reproduce.
Treat output feedback as a hypothesis even when the hardware is documented as
feedback: a learned `previous output -> next state` connection can create
teacher-forcing leakage or unstable free-running inference. Train and validate
the same causal feedback path used in production.

For stereo Link, prefer two measured audio paths and an explicit constrained
control-state coupling. Add M/S only when the hardware has an M/S route or the
measurements independently require that basis.

## Train with state continuity

- Keep recurrent state across adjacent chunks and truncate gradients without
  resetting physical history.
- Derive preroll and reset length from measured settling; do not assume 5-30
  seconds covers an eight-second or multi-stage recovery.
- Split by whole conditions and sessions before chunking.
- Stratify by mode, control region, drive, gain-reduction depth, recovery tail,
  and material.
- Do not demand sample-perfect prediction of uncorrelated hardware noise.
- A gain-reduction loss is optional unless a calibrated control-voltage or
  independently validated envelope target exists. Wet/reference division alone
  is contaminated by phase, distortion, noise, and output attenuation.

Use sample/time-domain, complex and magnitude multi-resolution spectral,
envelope, static-curve, harmonic/IMD, stereo, and state-stability terms only
when the associated target is observable. Publish weighting; inspect worst
cases rather than one aggregate loss.

## Make antialiasing and rate part of the candidate

A neural or analytic nonlinearity can generate bandwidth even when trained on
anti-aliased hardware recordings. Decide internal rate, state-update rate,
interpolation/decimation, latency, bypass, and dry/wet alignment per candidate.
Do not prescribe 2x or 4x merely by convention. Test near-Nyquist tones, sparse
IMD, worst drive, every supported production rate, and desired-harmonic
preservation.

## Acceptance layers

Keep these results separate:

1. capture/data integrity;
2. objective behavior match on held-out settings, programs, probes, and days;
3. artifact bounds: alias, instability, clicks, zippering, state reset, image;
4. perceptual identity or detectability under a predeclared blind test;
5. realtime CPU, memory, latency, block size, and sample-rate behavior;
6. VST3/host/DAW integration and automation;
7. deployment and loaded-binary identity.

Hardware repeatability supplies a measurement floor, not an all-purpose pass
threshold. Define practical equivalence margins per metric and test systematic
bias separately. “No significant difference” without power or an equivalence
design does not prove a match.

## Research anchors

- [Comunità et al., TFiLM for black-box audio effects, ICASSP 2023](https://arxiv.org/abs/2211.00497)
- [Yin et al., S4 dynamic-range-compressor modeling, 2024 preprint](https://arxiv.org/abs/2403.16331)
- [Wright and Välimäki, gray-box dynamic-range compression, DAFx 2022](https://www.dafx.de/paper-archive/details.php?id=Oz5HVaU0tKAjfD3ivOlv5g)
- [Gu et al., Solid State Bus-Comp, DAFx 2025](https://www.dafx.de/paper-archive/2025/DAFx25_paper_13.pdf)
- [Schoukens, Vaes, and Pintelon, nonlinear distortion and BLA](https://arxiv.org/abs/1804.09587)
- [BIPM/JCGM VIM, measurement repeatability](https://jcgm.bipm.org/vim/en/2.21.html)

Use these as method precedents with their device and experiment limits, not as
proof that one architecture, data volume, or tolerance transfers to the target.
