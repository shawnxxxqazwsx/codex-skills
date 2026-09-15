# Complete neural training plan

## Objective

Given Original `x`, hardware Target `y`, control state `c`, and model render
`y_hat = F(x, c, state)`, minimize a vector of differences between `y_hat` and
`y`. At minimum, every statistic exposed by `audio-render-forensics` that is
numerically comparable between Target and Current remains in the metric
registry. Missing, non-finite, low-coherence, or unsupported values stay visible
and cannot silently disappear from the denominator.

Use two coupled objectives:

1. direct signal agreement in raw, equal-LUFS, and equal-true-peak domains;
2. behavior agreement between Original-to-Current and Original-to-Target for
   residual, gain reduction, dynamics, nonlinear residue, qualified transfer,
   stereo image, correlation, peak, loudness, and controlled-probe metrics.

Normalize metric distance by independently measured hardware repeatability when
available. Otherwise declare an engineering floor and keep the claim at pilot.
Select on the full distance vector and critical no-regression gates. A weighted
Huber mean plus worst-tail CVaR may rank candidates, but it cannot hide a failed
critical metric.

## Data construction

- Consume only exact allowlist entries and verify their hashes at load time.
- Preserve raw-v1 as the primary target. Run permitted deembedded targets only
  as separately named comparison objectives.
- Split whole capture, session, programme family, adjacent excerpt, thermal
  cycle, and derived siblings together before chunking.
- Keep independent withheld programmes, settings, sessions, and probe families
  outside optimization and early stopping.
- Align and document transport delay without rewriting raw evidence. Store every
  derivative's parents, code commit, delay/drift, resampler, trim, gain, and
  output hash.
- Train on long sequences with carried state. The initial pilot requires at
  least 10 seconds of visible history and resets only at documented round
  boundaries.

## Model ladder

Train and retain these baselines first:

1. identity;
2. best static common gain;
3. evidence-constrained gray-box detector/envelope/gain model;
4. a small causal recurrent or dilated-convolution model;
5. a hybrid learned detector/state model plus an optional bounded audio-rate
   nonlinear residual stage.

Prefer the smallest model that clears the frozen gates. A practical hybrid is:

- optional fixed/calibrated linear front end;
- causal control-rate TCN, GRU, or structured state model for attack, recovery,
  hysteresis, and programme-dependent gain;
- explicit smooth time-varying gain stage;
- small conditioned causal residual network for GR-dependent waveform change;
- permutation-symmetric stereo-link state with independent SEP paths and a
  declared LINK coupling law;
- bounded output, denormal protection, deterministic reset, and no lookahead
  unless the hardware contract explicitly contains it.

Do not collapse native COMPRESS/LIMIT, SEP/LINK, attack, recovery, threshold,
sidechain HP, input, or output identities to suit a model abstraction.

## Loss stack

Freeze loss versions and weights before a comparable run:

- time-domain Huber/L1 after frozen alignment;
- multi-resolution complex STFT and log-magnitude loss;
- 100/50/20/5/1 ms local common-gain residual agreement;
- fitted gain and inferred-GR trajectory loss, including attack/release slew,
  event duration, and 5-minus-50 ms modulation;
- transient/step trajectory loss for attack depth, overshoot, recovery, and
  quiet-segment unity;
- GR-conditioned residual and zero-crossing lobe-transition penalties;
- coherence-qualified transfer magnitude/phase and band-residue losses;
- stereo M/S width, L/R gain mismatch, link leakage, and correlation losses;
- loudness, sample/true-peak, crest, DC, NaN/Inf, and stability penalties.

Literal THD, THD+N, IMD, aliasing, monotonicity, and link behavior come from
controlled probes, not music-derived residue labels.

## Curriculum and search

1. bypass/low-level and level ladders for linear/static behavior;
2. steady tones and multitone for level dependence and nonlinear structure;
3. low-high-low steps, bursts, asymmetric stereo, and long recovery sequences;
4. whole programme sequences with state carry;
5. unseen programmes and settings for model selection;
6. final withheld sessions/probes, touched once after freezing.

Use deterministic seeds and log data order, chunk boundaries, warm-up, state
detach policy, optimizer, scheduler, precision, device, library lock, code
commit, and every checkpoint hash. Hyperparameter workers may receive distinct
batches or explicitly distinct objective shards; two machines never train the
same claimed batch implicitly.

## Per-version validation

Every usable algorithm version must produce the same frozen Original render and
the full three-way forensic artifact set. Compare against identity, static gain,
gray-box, previous accepted model, and the hardware repeatability floor.

Promotion requires:

- no missing comparable metrics;
- better declared aggregate and worst-tail scores than the promotion baseline;
- no critical metric beyond its frozen regression budget;
- all controlled-probe, state, determinism, block-size, and numerical gates;
- independent withheld improvement without train/validation leakage;
- level-matched listening review on time-matched worst windows;
- realtime CPU/latency and plug-in/DAW validation before product claims.

Failed candidates remain annotated audit evidence. Do not publish them as
completed/accepted algorithms.
