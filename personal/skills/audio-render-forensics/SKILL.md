---
name: audio-render-forensics
description: Compare same-program Original, Target, and Current audio renders with alignment, normalized residual, dynamics, spectral, stereo, loudness, plots, and machine-readable evidence. Use for forensic evaluation of mastering or DSP renders. For spatial audio, first freeze conventions with immersive-audio. This skill does not prove DAW routing, deployed binary identity, or live plug-in acceptance.
---

# Audio Render Forensics

Compare three renders without mistaking intended gain changes, latency, polarity,
or sub-sample offset for distortion. Preserve the source files and write all
analysis into a new output directory.

For a spatial pipeline, use `$immersive-audio` first to freeze channel/object/
scene representation, ordering and normalization, decoder or renderer, HRTF,
and comparable output format. For mc-patcher, this skill may measure captured
renders, but `$mc-patcher` still owns DAW→Bridge→Host routing, PDC/wet-return,
loaded-binary identity, and hosted acceptance.

## Required inputs

Obtain:

1. `Original`: the comparison-domain control, unprocessed by the target or
   candidate effect. Apply any required common domain transform first (for
   example, the frozen baseline decoder for a binaural comparison).
2. `Target`: the reference product/render to match or beat.
3. `Current`: the candidate algorithm/render under evaluation.

Require the same programme, sample rate, channel count, routing, automation,
start position, and intended processing settings. If durations differ, identify
whether the difference is silence/tail before interpreting metrics.

All three inputs must be in the same comparison domain. For AmbiX-to-binaural
work, use three same-format binaural renders: a control decoded through the
frozen baseline renderer, the target chain, and the current chain. Alternatively
use a matching AmbiX-domain triplet. Never use raw multichannel AmbiX as
`Original` against stereo binaural Target and Current renders.

## Core workflow

1. Record absolute paths, bytes, sample format, SHA-256, sample rate, channels,
   frames, LUFS-I/LRA, sample peak and reconstructed true peak.
2. Estimate output delay from pre-whitened programme edges, detect polarity, and
   report the parabolic fractional-delay estimate. Inspect
   `alignment_correlation.png` before accepting any residual result.
3. Align to the Original grid. Default to integer alignment. Use
   `--fractional-align sinc` only when the fractional remainder is material and
   explicitly report that interpolation was applied.
4. Exclude outer filter/PDC boundaries and source regions below the configured
   silence threshold.
5. Compute both global scalar-fit residue and local common-gain residue at
   100/50/20/5/1 ms. Treat the latter as a real-program nonlinearity proxy, not
   as pure-tone THD.
6. Infer the uncompressed gain plateau, GR distribution, GR event durations,
   5 ms versus 50 ms gain modulation, 1 ms gain slew, attack/release movement,
   lobe-to-lobe gain jumps, and residue conditioned by GR depth.
7. Compute coherence-qualified transfer magnitude/phase, residual spectra,
   frequency-band residue, stereo S/M width, L/R gain mismatch, crest change,
   and pairwise Target-versus-Current correlation under raw, equal-LUFS, and
   equal-true-peak normalizations.
8. Generate worst-window CSVs and time-matched excerpts. Listen to those excerpts
   before recommending an algorithm change.
9. For literal THD/THD+N/IMD or LTI frequency-response claims, run controlled
   tones/sweeps using [references/probe-suite.md](references/probe-suite.md).

Read [references/methodology.md](references/methodology.md) before changing any
formula or interpreting a new class of processor. Read
[references/output-contract.md](references/output-contract.md) when auditing a
run or assembling a report.

## Run the analyzer

First choose a Python containing `numpy`, `scipy`, `soundfile`, and
`matplotlib`. Also place `ffmpeg` on `PATH` for LUFS/LRA metadata.
Run the example from the skill directory that contains this `SKILL.md`, so the
relative `scripts/` path resolves to the bundled analyzer.

```powershell
python scripts/compare_audio_renders.py `
  --original "D:\audio\Original.wav" `
  --target "D:\audio\Reference.wav" `
  --current "D:\audio\Candidate.wav" `
  --target-label "Reference Limiter" `
  --current-label "Current Algorithm" `
  --output-dir "D:\analysis\candidate-vs-reference"
```

When the known transparent/static drive is +12 dB, pass it explicitly:

```powershell
  --target-static-gain-db 12 --current-static-gain-db 12
```

When the processor should leave source peaks below a known boundary untouched,
add `--below-boundary-dbfs <value>`; do not invent this boundary from the output.

Useful options:

- `--true-peak-factor 32`: independent high-resolution peak audit.
- `--fractional-align report|sinc`: report-only is the evidence-preserving default.
- `--silence-threshold-dbfs -65`: valid-programme gate.
- `--edge-ms 100`: outer-boundary exclusion.
- `--fft-size 16384`: Welch/CSD spectral resolution.
- `--baseline-percentile 99.9`: fallback GR baseline when static gain is unknown.
- `--no-excerpts`: omit copied listening excerpts when programme audio must not
  be duplicated.

## Interpretation rules

- Never compare raw nulls before alignment and polarity checks.
- Never call a LUFS or peak mismatch “distortion.” Compare raw, equal-LUFS, and
  equal-TP results separately.
- Never call music-derived residue “THD.” It combines nonlinear waveform change,
  phase/SRC error, fast modulation, and noise after removing a local gain model.
- Never call a low-coherence music bin “frequency response.” Use only qualified
  bins, then confirm with tones or a sweep.
- Treat inferred GR as a model. Supply explicit static gain when known.
- Report all window sizes and denominators. Residue normalized to output is not
  interchangeable with residue normalized to source.
- Separate global mastering difference from local waveform damage.
- Preserve machine-readable JSON/CSV, plots, hashes, and excerpt manifests.
- State direct evidence, inference, and listening judgment separately.

## Minimum delivery

Return:

- paths to `REPORT.md` and `analysis_metrics.json`;
- alignment delay/polarity/fractional remainder;
- LUFS-I and reconstructed TP for all three files;
- global plus 20/5/1 ms local residue for Target and Current;
- fast gain-modulation RMS, 1 ms gain-change p99, GR p99/max and >1 dB time;
- lobe jump p99, spectral-band residue, coherence-qualified transfer result,
  stereo width change, equal-LUFS correlation and RMS difference;
- the most diagnostic plot and listening-excerpt paths;
- a concise conclusion that respects the interpretation rules above.
