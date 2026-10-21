# Capture data contract and quality gates

Use this reference when recording, aligning, splitting, or releasing capture
data. Raw evidence is immutable in content: it remains unchanged locally until
the post-Release deletion gate closes, after which the verified Release,
lightweight hashes, annotations, restore instructions, and deletion receipt are
the preservation authority. Processed derivatives are reproducible products
with their own manifests.

## Required artifacts

For every session preserve locally before publication, and preserve in the
verified Release plus lightweight Code metadata after authorized local cleanup:

- the exact digital stimulus and SHA-256 hash;
- simultaneous input-reference and wet recordings when available;
- converter loopback, DUT bypass, and active baseline anchors;
- one session manifest derived from
  `../assets/capture-session.template.json`;
- control photographs or recall sheets;
- alignment/drift report and processing command/version;
- a log of aborts, clipping, dropouts, operator changes, and retakes.

Keep raw files read-only after ingestion. Derivatives belong under a versioned
processing directory; never replace a raw file with an aligned, resampled,
trimmed, normalized, or denoised render.

## Manifest semantics

The template separates:

- `unit`: physical identity and service state;
- `session`: clock, sample format, warm-up, environment, and operator;
- `routing`: balanced path, source/load, tap, pads, and channel map;
- `calibration`: voltage/reference mapping and chain anchors;
- `stimulus`: immutable source identity and family;
- `control_state`: exact physical controls and approach direction;
- `history`: preceding condition, preroll, reset, and settling;
- `files`: digital, reference, wet, and optional bypass paths;
- `alignment`: delay, drift, and method without deleting raw evidence;
- `split`: whole-group assignment and leakage key;
- `quality`: clipping, dropout, polarity, and operator review.

Run from the skill directory:

```bash
python3 scripts/validate_capture_manifest.py path/to/session.json
```

The validator checks structure and obvious contradictions. It does not verify
the audio, calibration instrument, or truth of operator-entered values.

## Per-round file annotations and handoff gate

At the end of every physical capture round, create both:

- `round-file-annotations-v1.json`, copied from
  `../assets/capture-round-annotations.template.json`; and
- `ROUND_NOTES.md`, a short reading-order summary for the next agent.

These are sidecars. Do not add or rewrite metadata inside raw WAV, FLAC, AIFF,
CAF, or other evidence files. The annotation manifest records the immutable
file hash instead.

The JSON inventory covers every persistent file created or relied on by the
round: digital stimuli, raw captures, input-reference taps, extracted regions,
aligned pairs, derivatives, analysis tables, plots, manifests, allowlists, and
quarantined or superseded products. It may reference files outside the round
directory, such as `campaign/raw/<session-id>/...`, but those files still need
their own entries. Exclude only transient caches, build products, and logs that
the round intentionally does not retain.

Each file annotation records:

- path and SHA-256;
- role, capture/condition identity, and channel layout;
- stimulus, raw parent, or other provenance reference;
- physical-control-state reference and processing state;
- `ACCEPTED`, `PILOT`, `REJECTED`, or `SUPERSEDED` QA status;
- whether training use is allowed, intended uses, exclusions, and a concise
  plain-language note explaining what another agent should know.

`ROUND_NOTES.md` does not duplicate the machine inventory. It gives the round's
purpose, exact physical state and route, capture order, anomalies or operator
changes, passed/failed gates, accepted/rejected boundary, recommended reading
order, and next action. Link the session manifest and annotation sidecar.

Validate before saying that the round is complete or handing it to another
agent:

```bash
python3 scripts/validate_round_annotations.py \
  path/to/round-file-annotations-v1.json \
  --check-files \
  --inventory-root path/to/round-directory
```

`--inventory-root` is repeatable. It proves that supported persistent data
extensions inside a self-contained round directory are not omitted. Files
stored elsewhere must still be listed explicitly and are verified by
`--check-files`. A missing file, hash mismatch, duplicate path, unresolved gate,
unreviewed annotation, or training-eligible rejected/superseded artifact blocks
round closure. If a round aborts, annotate the retained evidence as `REJECTED`
or `PILOT`, state the reason, and hand it off as incomplete rather than leaving
unexplained files.

### Cross-check dataset eligibility

If `aligned-program-pairs/dataset-allowlist-v1.json` or another exact dataset
allowlist exists, it is the machine-readable authority for training
eligibility. The file-level annotations must agree with every exact accepted
path and SHA-256:

- an allowlisted training file is `training_eligible: true`, is `ACCEPTED`,
  names an explicit training use, and does not also exclude direct/model
  training;
- validation and withheld members remain false even when their files and QA
  are accepted;
- rejected, quarantined, superseded, or excluded-prefix files remain false;
- no annotation may grant eligibility to a file absent from the exact
  allowlist;
- when primary and comparison target variants are both permitted, their
  `use_for` and `exclude_from` fields must make separate objectives and the
  no-mixing rule explicit.

Run the cross-file gate after both documents are final:

```bash
python3 scripts/validate_round_dataset_eligibility.py \
  path/to/round-file-annotations-v1.json \
  path/to/aligned-program-pairs/dataset-allowlist-v1.json \
  --check-files
```

Do not infer eligibility from the split name alone, and do not let a generic
annotation backfill overwrite an existing exact allowlist decision.

## File and group identity

Use stable IDs rather than encoding all meaning in long filenames. One capture
ID identifies one uninterrupted recording under one physical control state.
One condition ID groups repetitions of the same declared setting. One thermal
cycle ID groups captures since a cold start. One stimulus group keeps variants
or adjacent excerpts together for split purposes.

Recommended directory shape:

```text
campaign/
  raw/<session-id>/
  manifests/<capture-id>.json
  stimuli/
  calibration/<session-id>/
  derived/<pipeline-version>/<capture-id>/
  splits/<split-version>.json
  reports/
  training/
    ready/<dataset-id>/training-consumption-v1.json
    completed/<training-run-id>/training-consumption-v1.json
    ledger/by-source-sha256/<prefix>/<sha256>/<objective-id>.json
```

The `raw/` tree is the canonical, immutable original-audio namespace and is
packaged separately for direct archive access. Do not place aligned, trimmed,
resampled, denoised, or normalized files there. See
`training-consumption-and-sync.md` for training receipts and remote sync.

## Alignment and derivative provenance

Every processed file records:

- raw parents and hashes;
- software/tool version or source commit;
- integer and fractional delay;
- drift curve or ppm estimate;
- resampler and filter specification;
- trim/fade boundaries;
- gain operation, normally unity;
- output hash.

Reject unexplained sample-count mismatch, missing parents, non-finite samples,
clipping, silent/duplicated channels, swapped polarity, or a drift correction
that is not supported by the reference track.

## Split without leakage

Assign splits before slicing model chunks. Keep all adjacent material and all
renders derived from one raw capture in the same split. Hold out across four
axes when the claim includes parameter interpolation:

1. seen settings with unseen whole programs;
2. unseen setting groups with seen program families;
3. unseen settings with unseen programs;
4. different sessions or thermal cycles.

Keep entire diagnostic families out when testing structural generalization.
Do not tune a model or loss against the final listening set.

For a packaged neural or hybrid dataset, make split and derivative eligibility
machine-enforceable rather than relying on directory names:

- publish one exact allowlist of accepted manifests and audio files with hashes,
  roles, variants, splits, and training eligibility; dataset loaders must consume
  it directly and must not recursively discover WAVs or manifests;
- audit both unique source IDs and whole-project, song-family, session, or other
  declared leakage keys across splits; distinct files from one leakage group do
  not become independent examples;
- bind every pair annotation to the pinned program manifest and require product
  and segment eligibility to equal the declared split policy;
- make verifier child evidence non-vacuous: require the expected product set,
  exactly the required input/target file records, non-empty segment records,
  all child pass flags, and the exact manifest path and hash. Never accept a
  summary status through `all()` over a missing or empty child list;
- when a derived set is rejected, preserve it under a quarantine directory with
  a rejection manifest that overrides any historical `ACCEPTED` or
  training-eligible fields, inventories every quarantined file and hash, and is
  path-disjoint from the accepted allowlist. Keep superseded QA reports in a
  similarly marked audit-only location.

## Repeatability and the hardware floor

Repeat representative conditions multiple times within a stabilized session
and across thermal cycles. Use enough repetitions to estimate a distribution;
two files give only a weak pairwise difference.

For each metric and behavior region:

1. align using the frozen transport method;
2. estimate the repeated hardware mean or deterministic feature;
3. estimate within-condition random noise and drift separately;
4. report confidence intervals or quantiles;
5. compare the model's systematic residual with a predeclared practical margin.

The inequality `d(model, y1) <= d(y2, y1) + epsilon` is only an intuition. It
is asymmetric, metric-dependent, and may be overly permissive because two
noisy hardware recordings contain the noise of both repeats. It cannot prove
equivalence or replace mechanism-specific tests.

## Dataset release gates

Mark the dataset `REJECTED`, `PILOT`, or `RELEASED`.

`RELEASED` requires:

- unit identity and claim domain frozen;
- all included manifests structurally valid;
- calibrated levels and source/load conditions recorded;
- raw hashes and derivative provenance complete;
- chain/bypass/active anchors present;
- alignment and drift accepted at every session;
- no unresolved clipping, dropouts, channel swaps, or retakes;
- repeatability anchors present;
- split leakage audit passed;
- control and stimulus coverage report complete;
- every included round has validated file-level annotations and `ROUND_NOTES.md`;
- exclusions and nonclaims explicit.

Do not call a dataset model-ready because its total duration is large.
