# Completed run contract

A completed run is an immutable folder, not merely a checkpoint. Copy
`assets/completed-run.template.json` to `completed-run-v1.json` and fill every
field before publishing.

## Required contents

```text
<run-id>/
  completed-run-v1.json
  ANNOTATION.md
  data/
    dataset-and-split-manifest.json
    normalization-and-derivative-manifest.json
  algorithm/
    model weights or export
    model-card.md
    inference configuration/source identity
  evaluation/
    baseline-original-target/
    three-way/<candidate-version>/
    controlled-probes/
    withheld/
    listening/
  logs/
    training configuration and immutable log/export
```

All persistent files except the root manifest itself appear in its artifact
inventory with relative path, role, byte size, and SHA-256. Symlinks, absolute
paths, path traversal, hash mismatch, duplicate paths, unlisted files, and files
outside the run folder block publication.

`ANNOTATION.md` records purpose, source batch and claim, exact eligibility
policy, model architecture, controls/domain, training and validation splits,
losses, seeds, best-checkpoint rule, all forensic and probe gates, listening,
known failures, excluded claims, reproduction steps, machine name/ID, start and
completion UTC timestamps, and operator/reviewer.

## Acceptance requirements

- at least one `data_manifest`, one `model`, one `model_card`, one
  `training_config`, one `training_log`, one `training_ledger_receipt`, one
  `metric_registry`, one passing `metric_completeness`, and one
  `three_way_forensics` artifact;
- the three-way artifact directory contains the complete output contract from
  `audio-render-forensics`, including report, JSON, CSV, PNG, worst windows, and
  time-matched excerpts unless an explicit evidence/privacy exception is
  reviewed;
- the metrics registry reports every comparable statistic and every exclusion;
- source, allowlist, split, READY ledger, code commit, environment lock,
  checkpoint, and rendered audio hashes are recorded;
- run and candidate statuses distinguish measured pass, pilot, failed,
  rejected, and not tested;
- no hardware-fit/product-ready wording beyond passed independent evidence.

Run the validator before packaging:

```bash
python3 scripts/validate_completed_run.py /absolute/completed/<run-id> --check-files
```

The publisher first retains and verifies the complete local folder and package
parts, then uploads the large package to the unique
`varimu-training-<run-id>` GitHub Release. The Code-page
`varimu-training/release-index/` folder is only a lightweight immutable index
containing the completion receipt, annotation, root/run package manifests,
training-ledger receipt, SHA-256 asset inventory, and Release URL. Never commit
package parts, use Git LFS, or recreate the removed `trained Data/` namespace.
