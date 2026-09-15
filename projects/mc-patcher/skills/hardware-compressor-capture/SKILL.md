---
name: hardware-compressor-capture
description: >-
  Plan, run, audit, and package calibrated input-output captures of physical
  analog compressors, limiters, and levelers for measured-response, gray-box,
  or neural plug-in modeling. Use for converter calibration, stimulus and
  parameter design, long-memory and stereo-link identification, dataset QA,
  repeatability, and model handoff. Do not use for ordinary compressor mixing
  advice, software-only preset matching, or DSP implementation after an
  accepted capture set already exists.
---

# Hardware Compressor Capture

Use this skill with the repository `AGENTS.md`, `mc-patcher`, and
`hardware-audio-emulation`. This skill owns the capture campaign and dataset
release gates; the hardware-emulation skill owns general model selection,
antialiasing, perception, and plug-in validation.

## Respect the requested operation

- For review or planning, inspect and write the protocol only. Do not operate
  the user's DAW, change hardware controls, power-cycle equipment, or start a
  capture.
- For capture execution, confirm the exact physical route and safe level limit
  before generating or playing high-level probes. Never open a tube unit or
  request internal measurements unless a qualified service technician owns
  that work.
- When the user freezes the converter control plane, treat that as a hard
  non-mutation boundary: do not change converter routing, patching, trims,
  gains, clock, sample rate, buffer size, presets, or any other converter
  state. Only read-only verification is allowed. A route diagnostic must never
  write converter state, even temporarily.
- When the user also stops converter discovery, do not enumerate, discover,
  probe, or refresh converter identity through CoreAudio, CueMix, AVB, USB,
  network discovery, or another device API. Treat the user-declared device
  name and channel contract as the only retained authority. If a capture is
  active when the stop arrives, interrupt it, quarantine any unpaired partial
  artifact, and never resume automatically; offline annotation, validation,
  packaging, and upload may continue without device access.
- Treat user-declared capture CLI channel numbers as literal arguments after
  confirming the tool's numbering convention. Do not pre-decrement or rebase a
  one-based declaration when the tool already performs that conversion. For
  this user's MOTU capture route, every capture invocation must pass output
  `33/34` and return `37/38` exactly, and the wrapper must fail closed if any
  other channel is requested. Retain but quarantine recordings made through a
  mismatched route; they are never training-eligible.
- Treat raw recordings as evidence. Never normalize, destructively denoise,
  overwrite, or discard them during alignment or dataset preparation. The only
  authorized deletion is the exact post-Release cleanup below, after remote
  upload verification has closed.

## Freeze the claim and unit identity first

Write the intended claim as a bounded behavior domain: unit and revision,
source/load conditions, sample rates, input levels, controls and modes, stereo
topology, warm-up state, and longest history to be reproduced. “Complete” or
“exact” capture is not an acceptance condition.

### User-specific Tegeler topology restriction

For this user's Tegeler capture work, do not enter, toggle, qualify, or capture
DualMono in any mode except an explicitly designated `Stereo Transformer` mode.
For every other mode, keep the unit in linked Stereo and do not touch the
DualMono controls. If `Stereo Transformer` mode is explicitly active and
DualMono is required, initialize both channel Threshold controls to the same
exact raw value and verify that equality before and after each operation; any
unexpected mismatch is a restore/stop condition. This restriction is
campaign-specific and does not generalize to other compressors or users. Where
a referenced Tegeler campaign document requests broader DualMono qualification,
this user-specific restriction takes precedence for this user's sessions.

### Capture-priority precision exception

When the user explicitly prioritizes completing the capture over exact control
precision, an unreachable raw target is not by itself a reason to abort the
round. Use the nearest value that the supported control path can set and hold
reliably, but record the requested target and the observed `/info` raw value
separately for every affected control. Base the canonical state identity on
the observed hardware value, never on the requested value; if it collides with
an existing state or creates an unplanned state, retain that disposition in the
ledger and do not silently deduplicate it. Mark the round and affected files
as precision-degraded/approximate, keep them out of exact-state claims and
training eligibility until independently reviewed, and preserve the normal
restore, clipping, busy, route, and provenance gates. This exception does not
permit unverified levels, unstable controls, hidden drift, DualMono use under
the Tegeler restriction above, or reporting an approximate capture as exact,
hardware-fit, or model-ready.

For the user's Tegeler Audio Manufaktur Schwerkraftmaschine Mode 5 deep
black-box campaign only, read
[references/tegeler-schwerkraftmaschine-deep-blackbox.md](references/tegeler-schwerkraftmaschine-deep-blackbox.md)
before inventory closure, parameter-design freeze, capture, or Release sync.
Its 800-state floor, two-round phase gate, and second-round 12-hour cadence are
campaign-specific and must not be generalized to other compressors.

Do not generate a full matrix until the unit identity, control topology, safe
headroom, and service state are known. Record serial, revision, modifications,
tube or gain-cell state when documented, recent service, control detents,
source/load impedance, and channel condition. For a Manley Stereo Variable Mu,
read [references/manley-variable-mu.md](references/manley-variable-mu.md).

## Qualify the chain before the device

Read [references/capture-protocol.md](references/capture-protocol.md) before
designing routing, calibration, stimuli, or parameter coverage.

Require these gates in order:

1. converter loopback and monitor-path headroom;
2. the user's declared converter calibration authority and safe-level mapping;
3. bypass plus integer/fractional delay, polarity, channel mapping, and drift;
4. declared warm-up and stabilization check;
5. active no/low-gain-reduction baseline and repeatability anchors;
6. static, dynamic, nonlinear, stereo/link, and recovery pilots.

Stop at the first failed gate. A green engineering script cannot compensate for
clipped converters, an unidentified revision, an unstable unit, or a missing
declared safe-level mapping.

For this user, use the MOTU output calibration/specification and current output
trim as the level authority. Never require an external true-RMS meter or audio
analyzer as a prerequisite. Record the exact MOTU model, output range/reference,
channel trims, digital waveform convention, load assumption, and safety margin;
label the result `MOTU-nominal dBu`, not terminal-measured absolute dBu. Verify
the usable range with conservative loopback, bypass, ADC-headroom and clipping
checks. Missing terminal-voltage measurement narrows the analogue-level claim
but does not stop capture when those MOTU-based gates pass.

Preserve three different signals when available: the original digital
stimulus, a simultaneous analogue-input reference tap, and the wet output. The
digital stimulus is normally the production model's canonical input; the tap
is evidence for delivered level, timing, drift, and converter behavior. Do not
train on the tap and then silently feed pre-DAC samples to the plug-in.

## Design the campaign by behavior, not duration

Start with a pilot, then characterize the axes that actually vary, then record
the first training set, and add settings only after residuals or model
disagreement identify a gap. Do not prescribe a universal number of hours.

Separate controls by function before sampling:

- enumerate switches, detents, ratio modes, side-chain filters, and routing;
- sample continuous attack, threshold, drive, and other nonlinear controls
  only after their measured law and repeatability are known;
- test whether output attenuation is a separable gain or a loading-dependent
  analogue behavior before adding it to a neural parameter space;
- keep input drive and threshold distinct when one changes audio-path
  coloration and the other changes side-chain action;
- treat stereo Link as a measured control-state coupling, not automatically as
  summed audio, left-master behavior, or an arbitrary M/S matrix.

Use multiple stimulus families because no single sweep or noise file identifies
all layers: low-reduction complex response, steady transfer curves, stepped and
interrupted envelopes, tones and sparse multitones, periodic random-phase
multisines with repetitions, asymmetric stereo/link probes, recovery/settling
sequences, and held-out program material. Label each probe by the hypothesis it
tests and the observation that would reject it.

## Preserve state and provenance

Read [references/data-contract-and-qa.md](references/data-contract-and-qa.md)
before recording production data or releasing a dataset. Copy
`assets/capture-session.template.json` for each session and validate it with
`scripts/validate_capture_manifest.py`.

Paths beginning with `assets/`, `references/`, or `scripts/` in this skill are
relative to the directory containing this `SKILL.md`. Run those commands from
that directory, or resolve the path explicitly before invoking them.

Keep canonical original recordings under `campaign/raw/<session-id>/`; do not
mix them with derivatives, reports, training products, or sync packages. For
training or remote synchronization, also read
[references/training-consumption-and-sync.md](references/training-consumption-and-sync.md).
Create an exact claim under `campaign/training/ready/<dataset-id>/` before a
training run and seal its receipt and artifacts under
`campaign/training/completed/<training-run-id>/` afterward. Mark consumed raw
evidence with SHA-256 sidecars under `campaign/training/ledger/`; never mark or
rewrite the audio file itself. A loader or new training run must fail closed
when the same raw hash has already completed the same training objective.

Close every capture round with file-level handoff annotations. Copy
`assets/capture-round-annotations.template.json` into the round directory as
`round-file-annotations-v1.json`, add one entry for every persistent raw,
stimulus, derivative, analysis, accepted, rejected, or superseded data file
created or relied on by the round, and write a concise `ROUND_NOTES.md` for
human readers. Never write annotations into raw audio metadata because that
changes the evidence hash. Validate the sidecar with
`scripts/validate_round_annotations.py --check-files`; when the round has a
self-contained output directory, also pass it as `--inventory-root`. A round is
not complete and its capture/live-resource ownership is not released for
handoff until all retained files have a purpose, control/provenance reference,
QA state, training eligibility, exclusion note where applicable, and verified
hash. `PENDING`, `UNKNOWN`, or unreviewed annotations are an explicit handoff
blocker.

When a round publishes an exact dataset allowlist, treat that allowlist as the
training-eligibility authority and mirror its per-file booleans in the round
annotations. Validation and withheld files remain ineligible; rejected,
quarantined, and superseded files remain ineligible. If primary and comparison
target variants are both eligible, give them distinct training uses and
explicitly forbid silent mixing. Before closing or syncing the round, run
`scripts/validate_round_dataset_eligibility.py --check-files` in addition to
the ordinary round annotation validator. A validator that reads only one of
the two files cannot close this gate.

After the round sidecars pass file-hash validation and are stable, sync the
closed round to an immutable GitHub Release. GitHub Releases are the required
remote target for large capture and training data; the repository Code page
stores only lightweight indexes, annotations, ledgers, and Release download
instructions. Keep the local source unchanged while packaging and uploading,
and never sync a half-written round. Remote re-download is not required. The
deletion gate is: the Release is published, every required asset reports
`uploaded`, each provider-exposed size and SHA-256 digest matches the locally
verified package asset, the exact package manifest matches every current local
source member path, size, and SHA-256, and the lightweight Code receipt and
restore instructions identify that same Release. Also confirm that no capture,
validation, or training process is using the local files.

After all of those checks pass, permanently delete the locally completed
capture payload files and local package parts covered by that exact verified
manifest. This is a standing user instruction and does not require a second
confirmation. Delete only an explicit path-and-SHA allowlist under the declared
capture/package roots; never delete a directory recursively, a changed file,
an uncovered file, an active file, or lightweight annotations, manifests,
hashes, ledgers, and restore instructions. Write an append-only lightweight
deletion receipt under the authoritative Release index with each deleted path,
size, SHA-256, Release tag/assets, remote-verification time, deletion time, and
result. A failed or partial upload, provider digest/size comparison, source
hash comparison, Code receipt, or process-ownership check deletes nothing.
Release upload and
local deletion do not promote a round or dataset to `RELEASED` or model-ready
status.

Keep session order, preceding stimulus, preroll, reset method, silence, and
thermal cycle in the manifest. Split train/validation/test by whole program,
setting groups, stimulus families, and capture sessions; adjacent chunks from
one recording never cross splits. Estimate deterministic behavior and
stochastic noise/drift separately from multiple repeats.

## Hand off evidence before choosing the final model

Read [references/model-handoff.md](references/model-handoff.md) when the user
asks for training, architecture choice, or plug-in acceptance. The capture does
not pre-authorize a large neural architecture. Compare at least one simple
compressor gray-box baseline with justified recurrent, convolutional, or
state-space candidates. Add audio-rate nonlinear residuals, output feedback,
multirate paths, or joint stereo state only when the pilots falsify the simpler
model.

Do not use a two-repeat scalar inequality as proof of equivalence. Predeclare
metrics and practical tolerances, estimate hardware repeatability distributions
from multiple repetitions, compare systematic bias separately, and retain an
independent listening set.

## Stop conditions

Stop full capture and report the missing evidence when any of these applies:

- unit identity or a behavior-changing modification is unresolved;
- the required dBu level exceeds verified DAC, ADC, pad, cable, or DUT margin;
- loopback/bypass polarity, clipping, drift, or channel mapping is unresolved;
- repeated pilots show unexplained thermal, service, or intermittent behavior;
- two campaign revisions fail under the same modeling hypothesis;
- a derived gain-reduction target is being treated as ground truth without a
  validated control-voltage or envelope measurement.

## Report the result by evidence layer

Report the exact unit and route, calibrated domain, raw-data location and
hashes, passed/failed capture gates, parameter and stimulus coverage, repeated
conditions, split policy, alignment/drift method, known exclusions, and the
strongest justified claim. Keep capture integrity, offline model metrics,
realtime plug-in tests, DAW tests, listening, and deployment as separate
statuses.
