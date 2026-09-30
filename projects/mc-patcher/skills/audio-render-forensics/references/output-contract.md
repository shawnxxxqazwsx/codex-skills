# Output contract

## Required files

`compare_audio_renders.py` writes:

- `REPORT.md`: human-readable comparison and interpretation boundary.
- `analysis_metrics.json`: complete metadata, alignment, metrics and warnings.
- `window_metrics_20ms.csv`: time-aligned Target/Current local residue.
- `worst_current_vs_target_windows.csv`: largest Current disadvantage windows.
- `worst_current_windows.csv`: largest absolute Current residue windows.
- `target_spectral_bands.csv`, `current_spectral_bands.csv`.
- `spectral_curves.csv`: frequency, coherence, transfer, phase and residue PSD.
- `target_distortion_by_gr.csv`, `current_distortion_by_gr.csv`.
- `target_largest_lobe_gain_jumps.csv`, `current_largest_lobe_gain_jumps.csv`.
- `excerpt_manifest.csv` and matched excerpts unless `--no-excerpts` is used.
- `alignment_correlation.png`.
- `envelope_and_gain_timeline.png`.
- `local_residue_timeline.png`.
- `coherence_and_residue_spectrum.png`.
- `transfer_frequency_response.png`.
- `gain_reduction_and_dynamics.png`.
- `distortion_conditioned_by_gr.png`.
- `stereo_width_change.png` for stereo or wider inputs.

## Audit checklist

Before accepting a report:

1. Confirm all three hashes and metadata.
2. Confirm sample rate/channel count match.
3. Inspect lag plot and aligned correlation.
4. Resolve fractional remainder warnings.
5. Confirm valid programme fraction is plausible.
6. Confirm LUFS/TP normalizations are explicitly identified.
7. Compare global, 20, 5 and 1 ms residue together.
8. Compare fast modulation and 1 ms gain slew.
9. Confirm GR baseline is explicit or clearly marked inferred.
10. Inspect GR-conditioned residue and below-boundary touch if applicable.
11. Inspect lobe jump p99/max and top timestamps.
12. Reject low-coherence frequency-response claims.
13. Inspect stereo width/gain mismatch.
14. Listen to matched excerpts.
15. Preserve JSON, CSV, plots, report and command line.

## Evidence language

Use:

- “Measured” for direct file/hash/sample/energy results.
- “Inferred” for audio-derived gain reduction or causal diagnosis.
- “Consistent with” for a metric that matches a listening symptom.
- “Listening preference” for subjective ranking.

Avoid:

- “THD” for music-derived local residue.
- “frequency response” for unqualified music bins.
- “bit exact” when any alignment, resampling, quantization or normalization was
  applied.
- “better sounding” from one scalar metric.

## Comparison table minimum

Include Target and Current columns for:

- LUFS-I;
- independent true peak;
- global fitted residue;
- 20/5/1 ms local residue;
- fast gain modulation RMS;
- 1 ms gain-change p99;
- GR >1 dB fraction, p99 and max;
- lobe gain-jump p99;
- crest change;
- stereo width change;
- 8-20 kHz or suitably split high-frequency residue;
- equal-LUFS Target/Current correlation and RMS difference.

Then list at least five worst Current-minus-Target windows with timestamps and
source level.
