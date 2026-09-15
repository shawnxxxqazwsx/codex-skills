# Current Manley Variable Mu policy

This is the current fixed-state pilot policy as of 2026-08-31. Revalidate the
live manifests before every batch; this document never overrides a newer exact
allowlist or rejection manifest.

## Eligibility truth source

`aligned-program-pairs/dataset-allowlist-v1.json` is the sole machine-readable
training-eligibility authority. File annotations must agree with its exact path
and SHA-256 decisions. The loader consumes only its explicit eligible members;
recursive discovery and filename inference are forbidden.

The former blanket-false conflict came from reading only
`training_eligible` while the allowlist expressed `eligible_for_training`.
Cross-check both documents with:

```bash
python3 .agents/skills/hardware-compressor-capture/scripts/validate_round_dataset_eligibility.py \
  path/to/round-file-annotations-v1.json \
  path/to/aligned-program-pairs/dataset-allowlist-v1.json \
  --check-files
```

## Accepted objective separation

- SEP `raw-v1`: primary objective.
- SEP `motu-deembedded-v2`: comparison-only, independent objective. It must not
  be mixed with the SEP primary target in training, validation, normalization,
  early stopping, checkpoint selection, or reported aggregate metrics.
- LINK `raw-v1`: primary objective.
- LINK `motu-deembedded-v2`: rejected while the frozen zero-skew gate fails
  because the measured alignment is L=-11 and R=-12 samples.
- Validation and withheld members are never optimization inputs, even when
  their files have accepted QA status.

The current claim tier is a 48 kHz, 110 V, fixed-state, uncalibrated
digital-domain pilot. It is not an absolute dBu, voltage-causality, complete
control-surface, or hardware-equivalence claim.

## Required start gate

Before a trainer reads one sample:

1. validate round annotations and the exact allowlist;
2. freeze whole-group splits and leakage keys;
3. create a new objective ID that names SEP/LINK and target variant;
4. run `tools/mc_capture_training_ledger.py claim` for every raw source and
   derived training input;
5. bind the queue batch manifest to the immutable source Release repository,
   tag, URL, archive-manifest asset/hash, the pinned Code commit holding the
   exact allowlist and READY receipt, and the training objective ID.

An upload or GitHub claim does not make a dataset model-ready.
