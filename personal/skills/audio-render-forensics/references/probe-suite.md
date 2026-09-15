# Controlled probe suite for literal distortion and response claims

Use this procedure when the real-program comparison identifies a problem that
must be separated into THD, IMD, SRC/filter response, transient behaviour, or
gain-law behaviour.

## Render contract

Render the exact same float source through Target and Current with:

- identical sample rate and block size;
- identical input drive, output trim, ceiling and channel link;
- automation disabled unless under test;
- all dither, normalization and export limiting disabled;
- enough pre-roll for declared PDC and enough tail for recovery;
- float32 or float64 export where available;
- hashes and complete plug-in state recorded.

Do not concatenate probes without a silence/settling interval longer than the
processor memory under test.

## Recommended probes

### Frequency/THD grid

- Sample rates: 44.1, 48 and 96 kHz.
- Frequencies: 20, 50, 100, 200, 500, 1k, 2k, 5k, 10k, 15k, 18k, 20k,
  plus safe near-Nyquist points appropriate to the rate.
- Input/drive states: clearly below threshold, threshold-adjacent, 1/3/6/9 dB
  nominal gain reduction, and deep-overload diagnostic.
- Duration: at least one second steady after settling; use fades only outside
  the analysis region.

Fit sine and cosine at the known fundamental and every harmonic below Nyquist.
Report fundamental gain/phase, THD, THD+N, sample peak and independent true peak.
Do not count a harmonic that aliases above Nyquist as if it remained at its
unaliased frequency; report aliases separately.

### CCIF IMD

Use equal-amplitude 19 and 20 kHz tones at 48/96 kHz. Report 1 kHz difference,
`2f1-f2`, `2f2-f1`, total fitted products, and THD+N after removing fundamentals.

### SMPTE IMD

Use 60 Hz and 7 kHz at the documented SMPTE amplitude ratio. Fit sidebands at
`7 kHz +/- n*60 Hz`, at least n=1..5, relative to the high-frequency carrier.

### Multitone

Use deterministic logarithmically distributed tones with random fixed phases
and sufficient crest factor. Report new spectral lines, residual spectrum,
crest change and intermodulation energy outside occupied bins.

### Static transfer and monotonicity

Use a 1 kHz level ladder from near silence through deep overload. Fit input and
output fundamental level on every plateau. Plot output versus input, gain versus
input, inferred GR, and verify that a louder input never becomes quieter than a
lower input unless the product intentionally defines that behaviour.

### Dynamic response

Use low-high-low plateaus, isolated bursts, impulses, alternating loud/quiet
events, and stereo-asymmetric events. Measure:

- latency and pre-attenuation;
- attack depth and overshoot;
- first recovery sample;
- 10/50/90/99% recovery time;
- low-segment unity error;
- maximum gain step;
- opposite-channel attenuation at each Link setting.

### SRC/filter response

First run a below-threshold logarithmic sweep so the limiter gain law is inactive.
Measure transfer magnitude, phase and group delay after exact latency alignment.
Then repeat at controlled active levels. A response change only under limiting is
part of the nonlinear gain/safety path, not the transparent SRC response.

## Plots

Produce:

- gain and phase versus frequency for each level;
- THD and THD+N versus frequency and GR;
- CCIF/SMPTE product bars;
- static input/output and GR curves;
- time-domain attack/release trajectories;
- residual spectra with occupied bins marked;
- true-peak margin versus frequency/GR.

Keep axes, rate, level, threshold, drive, window and normalization visible in
every figure or its caption.
