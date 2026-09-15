# Forensic validation stages

## Stage A: before any algorithm exists

Characterize only Original and captured Target. Use
`scripts/run_original_target_baseline.py`; it invokes the frozen three-role
analyzer with a disclosed Target identity sentinel, then emits a separate
`baseline_metrics.json` and `BASELINE_REPORT.md` containing only the real pair.
The duplicate sentinel is an implementation adapter, never an algorithm render.

```bash
python3 .agents/skills/varimu-neural-training/scripts/run_original_target_baseline.py \
  --original /absolute/Original.wav \
  --target /absolute/HardwareTarget.wav \
  --output-dir /absolute/baseline-forensics
```

Accept the baseline only after inspecting alignment, fractional remainder,
valid-programme coverage, all residual windows, inferred GR/dynamics,
GR-conditioned residue, coherence-qualified spectra, stereo/correlation, LUFS,
true peak, plots, and paired listening excerpts. Do not call programme residue
THD or low-coherence transfer a frequency response.

## Stage B: every usable algorithm version

Render the same Original through the candidate with frozen state, rate, block
size, drive, routing, controls, preroll, tail, and export settings. Then run:

```bash
python3 .agents/skills/audio-render-forensics/scripts/compare_audio_renders.py \
  --original /absolute/Original.wav \
  --target /absolute/HardwareTarget.wav \
  --current /absolute/AlgorithmRender.wav \
  --target-label "Hardware Target" \
  --current-label "model-id@checkpoint" \
  --output-dir /absolute/three-way-forensics
```

The first pass uses report-only integer alignment. A sinc fractional correction
is a disclosed secondary branch when the remainder exceeds 0.02 sample. Keep
both results when correction changes a promotion decision.

Required categories are complete residuals, inferred GR and dynamics, fast gain
modulation, zero-crossing lobes, GR-conditioned nonlinear residue,
coherence-qualified transfer magnitude/phase, spectral residue, stereo image,
correlation, LUFS/LRA, sample/true peak, crest, worst windows, plots, and matched
excerpts. Add the controlled probe suite for literal THD/THD+N/IMD, static
transfer, attack/recovery, link, monotonicity, aliasing, and SRC/filter claims.

`analysis_metrics.json` is the metric truth source. Freeze an objective registry
from `assets/forensic-objective.template.json`; enumerate every comparable
Target/Current numeric leaf and list exclusions with a reason. A missing value
is a failed completeness gate, not zero error.

Audit the entire numeric metric surface after every three-way run:

```bash
python3 .agents/skills/varimu-neural-training/scripts/audit_forensic_metric_completeness.py \
  /absolute/three-way-forensics/analysis_metrics.json \
  --registry /absolute/frozen-forensic-objective.json \
  --output-json /absolute/three-way-forensics/metric-completeness.json \
  --output-csv /absolute/three-way-forensics/metric-distance-vector.csv \
  --require-pass
```

The audit automatically enumerates matching Target/Current numeric leaves plus
direct raw, equal-LUFS, and equal-true-peak Target/Current distances. Every
active metric needs a frozen normalization floor; report-only alignment fields
and explicit exclusions remain visible.
