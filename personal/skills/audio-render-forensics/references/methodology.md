# Audio render forensic methodology

## Contents

1. Evidence contract
2. Integrity and preflight
3. Delay, polarity and fractional alignment
4. Valid-programme mask
5. Gain normalization and fair comparisons
6. Global and local residual models
7. Inferred gain reduction and dynamic response
8. Nonlinear behaviour on real programme
9. Frequency-domain analysis
10. Stereo and multichannel behaviour
11. Loudness and true peak
12. Plots and diagnostic excerpts
13. Failure modes and interpretation boundaries

## 1. Evidence contract

Keep the three input files read-only. Record absolute path, byte count, SHA-256,
container subtype, sample rate, channel count, frame count and duration before
analysis. Do not silently resample, truncate channels, fold down, normalize, or
change sample format. Truncation to a common time range is allowed only when
reported.

Distinguish three questions:

- **Global mastering difference:** How different is the complete output after
  one best constant gain?
- **Dynamic/gain-law difference:** How does the time-varying fitted gain behave?
- **Waveform residue:** What remains after removing an explicitly defined local
  gain model?

These are not interchangeable. A limiter can have a large global difference
because it is louder while having a small short-window residue; another can have
matching LUFS but severe rapid gain modulation.

## 2. Integrity and preflight

Require equal sample rate and channel count. Prefer identical frame count and
start/end boundaries. When lengths differ, inspect the extra section for silence,
noise, encoder padding, or a real arrangement change. Analyze only a documented
common programme interval.

Use float64 for dot products, power sums, filter states and residual arithmetic,
even when the source is PCM24 or float32. This prevents long-program energy sums
from accumulating avoidable precision error.

## 3. Delay, polarity and fractional alignment

Average channels, differentiate the average, and cross-correlate the derivatives:

`x_d[n] = mean_ch(x[n]) - mean_ch(x[n-1])`

`y_d[n] = mean_ch(y[n]) - mean_ch(y[n-1])`

The derivative emphasizes transients and reduces domination by slow limiter gain.
Search only a bounded lag range. Select the maximum absolute correlation; its sign
determines polarity. Refine the integer lag on several long interior spans.

Estimate a fractional remainder by a parabola through the absolute correlation
at the best integer lag and its two neighbours:

`delta = 0.5 * (c[-1] - c[+1]) / (c[-1] - 2*c[0] + c[+1])`

Report this estimate even when applying only integer alignment. If the remainder
is more than roughly 0.02 sample, high-frequency null/residual measurements are
materially contaminated. Prefer a corrected rerender. A long windowed-sinc
fractional shift is an explicit fallback and must be disclosed because it is
itself an interpolation operation.

Do not infer a second delayed copy merely from a comb-like subjective impression.
Inspect the full correlation-vs-lag plot for secondary peaks.

## 4. Valid-programme mask

Compute 10 ms source power and retain samples above the configured threshold,
normally -65 dBFS. Intersect that mask with the valid aligned ranges of both
processed files. Exclude the outer 100 ms by default to remove file/PDC/filter
startup and shutdown. Do not let zero padding enter the residual denominator.

For windowed statistics, require at least 80% valid samples in a window. Preserve
silence and tail behaviour as a separate diagnostic rather than mixing it into
programme transparency metrics.

## 5. Gain normalization and fair comparisons

### Best global scalar

For source `x` and processed signal `y`, solve least squares:

`g = sum(x*y) / sum(x^2)`

`e = y - g*x`

This removes one constant gain but not compression, EQ, phase, stereo change or
time-varying gain.

### Equal loudness

Scale Current to Target by the LUFS-I difference. If LUFS is unavailable, use a
documented RMS fallback. Report the scale applied, correlation, and RMS difference.

### Equal true peak

Scale Current to Target by independently reconstructed true peak and report the
same pairwise metrics. Equal-LUFS and equal-TP comparisons answer different
questions and must both remain visible.

## 6. Global and local residual models

### Global fitted residue

`R_global = 100 * RMS(y - g*x) / RMS(y)`

This includes all dynamic-range change and therefore is a broad mastering
difference, not a pure nonlinearity score.

### Local common-gain residue

For each window length `W`, calculate a moving least-squares scalar shared by all
channels:

`g_W[n] = LPF_W(sum_ch(x*y)) / max(LPF_W(sum_ch(x^2)), epsilon)`

`e_W[n,ch] = y[n,ch] - g_W[n] * x[n,ch]`

`R_W = 100 * RMS(e_W[valid]) / RMS(y[valid])`

Use 100, 50, 20, 5 and 1 ms:

- 100/50 ms retain most compression-envelope behaviour.
- 20 ms is a useful musical-event comparison and window-ranking scale.
- 5 ms removes much of the intended envelope while preserving fast modulation,
  phase/SRC and waveform-change evidence.
- 1 ms approaches waveform shape but can explain away some rapid gain damage;
  lower 1 ms residue is not automatically better if 5-50 ms modulation is worse.

Also report residue normalized to source and SDR in dB. State the denominator.

### Per-channel fit

Fit each channel separately when diagnosing stereo link or imaging. The gap
between common-gain and per-channel residual reveals channel-dependent gain
behaviour that a common trajectory cannot explain.

## 7. Inferred gain reduction and dynamic response

Use the 5 ms common gain trace. When the known static drive is available, supply
it explicitly. Otherwise estimate the transparent plateau as a high percentile,
normally p99.9:

`G0 = percentile(gain_dB_5ms[valid], 99.9)`

`GR[n] = max(0, G0 - gain_dB_5ms[n])`

Report fractions above 0.1/0.5/1/2/3 dB, p50/p95/p99/max, and contiguous event
count plus p50/p95/max duration at 0.1/1/3 dB.

If a “must remain untouched” source boundary is known, calculate the fraction of
those source regions that receive more than 0.1 dB inferred GR. Never derive the
boundary from the candidate output.

### Fast gain modulation

`M_fast[n] = gain_dB_5ms[n] - gain_dB_50ms[n]`

Report RMS, p95/p99 absolute and maximum. This exposed the earlier Pellucid issue:
its 1 ms residue was lower than the reference while 5-50 ms modulation was much
higher, matching the more audible pumping/roughness.

Sample the 5 ms gain trajectory every 1 ms and report absolute change p95/p99/max.
Separate negative change (attack/deeper reduction) from positive change
(release/recovery). This detects gain stair-steps that averaged residual misses.

## 8. Nonlinear behaviour on real programme

### Residue conditioned by GR

Partition valid samples into GR bins: 0-0.1, 0.1-0.5, 0.5-1, 1-2, 2-3, 3-6 and
at least 6 dB. For each bin report programme share and local-residual energy as a
percentage of output energy. This shows whether distortion rises only under deep
limiting or contaminates nearly untouched material.

### Zero-crossing lobe audit

Split each source channel at sign changes. For every nontrivial lobe, fit one
scalar and calculate within-lobe residue. Compare scalar gain between adjacent
valid lobes. Report lobe residue median/p95/p99 and gain-jump median/p95/p99/max,
plus the largest time locations.

Large adjacent-lobe jumps are a direct marker for a limiter that applies different
gain to neighbouring half-waves. They correlate with roughness and rapid gain
modulation, but remain a programme statistic rather than a standard THD number.

### Literal THD, THD+N and IMD

Use controlled steady probes, not music:

- Fit the fundamental by least squares on sine/cosine bases.
- Fit harmonics below Nyquist individually.
- `THD = sqrt(sum(A_h^2, h>=2)) / A_1`.
- Remove DC and fitted fundamental; `THD+N = RMS(residual) / RMS(fundamental)`.
- For CCIF 19/20 kHz, fit the 1 kHz difference product and third-order products
  `2f1-f2` and `2f2-f1` relative to the two fundamentals.
- For SMPTE 60 Hz/7 kHz, fit sidebands `7 kHz +/- n*60 Hz`.

State level, drive, threshold, sample rate, window, discarded settling time and
which harmonics/products fit below Nyquist. Do not compare THD numbers produced
with different definitions.

## 9. Frequency-domain analysis

Use Welch PSD and cross spectral density with a Hann window and 50% overlap:

`Pxx = PSD(x)`

`Pyy = PSD(y)`

`Pxy = CSD(x,y)`

`H(f) = Pxy / Pxx`

`coherence(f) = |Pxy|^2 / (Pxx*Pyy)`

`residue_ratio(f) = 10*log10(Pee/Pyy)`

Aggregate channel PSDs before calculating band energy. Mark a transfer bin valid
only when source PSD is above the selected floor (the script uses max minus 80 dB)
and magnitude-squared coherence is at least 0.90. Plot invalid bins as gaps.

For each frequency band report median/p10 coherence, valid-bin fraction, transfer
median/p05/p95 and residual energy percentage. A music-derived transfer estimate
is conditional on programme excitation and processor state. Confirm response with
stepped tones or a sweep before describing an SRC/filter response as flat or
rolled off.

## 10. Stereo and multichannel behaviour

For stereo:

`M = (L+R)/2`, `S = (L-R)/2`, `width = 20log10(RMS(S)/RMS(M))`.

Report global width change, 50 ms local width-change median/p95/max and time of
the maximum, input/output L/R correlation, and local fitted L/R gain mismatch.

For more than two channels, keep the common-gain residue across the whole group
and add per-channel fits. Do not call an arbitrary first pair representative of
9.1.6; report channel-wise values and known bed/object grouping.

## 11. Loudness and true peak

Use ffmpeg ebur128/loudnorm or an equivalent BS.1770 implementation for LUFS-I
and LRA. Record the implementation. Reconstruct each channel at 32x with a
documented high-quality kernel for an independent audit peak. Exclude only the
outer reconstruction support, not interior peaks. This 32x audit is an analysis
reference; it is not automatically identical to every commercial meter.

## 12. Plots and diagnostic excerpts

Always generate:

1. Alignment correlation versus lag.
2. 10 ms envelope, 5 ms gain, and 5-minus-50 ms modulation timeline.
3. 20 ms local residue timeline.
4. Spectral coherence and residue/output PSD.
5. Coherence-qualified transfer magnitude and phase.
6. GR timeline, CDF, and fast-modulation distribution.
7. GR-bin occupancy and conditioned residue.
8. Stereo width-change timeline when applicable.

Rank 20 ms windows by Current-minus-Target residue and by absolute Current
residue. Choose separated events and write equal-time Original/Target/Current
excerpts without normalization. Preserve an excerpt manifest with hashes.

## 13. Failure modes and interpretation boundaries

- **False distortion from PDC:** fix alignment first.
- **False polarity catastrophe:** detect sign from absolute correlation.
- **Fractional-delay high-frequency residue:** report remainder; rerender or use
  disclosed high-quality correction.
- **Boundary inflation:** exclude startup/shutdown support.
- **Silence denominator:** gate by source power.
- **Different loudness called distortion:** include equal-LUFS and equal-TP pairs.
- **Local fit hides pumping:** inspect 5-50 ms modulation and GR events.
- **1 ms residue used alone:** compare 20/5/1 ms together.
- **Music transfer called frequency response:** require coherence and probes.
- **GR overclaim:** mark it inferred unless actual gain telemetry is supplied.
- **One scalar hides stereo damage:** inspect per-channel gain and S/M width.
- **Metrics replace listening:** use time-matched excerpts and blind level matching.
