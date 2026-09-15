# Training consumption and Release synchronization

Use this contract when capture evidence is prepared for model training or
uploaded to an immutable GitHub Release.

## Highest-priority storage rule

Local capture evidence is staging until remote publication is verified. Before
every GitHub write, SHA-256 verify the unchanged local source and package. A
remote re-download is not required. Keep every local file until the Release is
published, every required asset reports `uploaded`, the provider-exposed size
and SHA-256 digest match each local package asset, and every current local
source member matches the exact package-manifest path, size, and SHA-256. A
failed or incomplete package, transfer, provider comparison, source hash check,
Code receipt, or process-ownership check leaves all local data intact and stops
the workflow.

After that gate closes, permanently delete the locally completed capture
payload files and local package parts covered by the verified manifest. This is
a standing user instruction; do not request a second confirmation. Use only an
explicit path-and-SHA deletion allowlist inside the declared capture/package
roots. Never use a broad recursive target, and never delete an uncovered,
changed, active, or lightweight metadata file. Keep the Release index,
annotations, manifests, hashes, training ledgers, restore instructions, and an
append-only deletion receipt. The receipt supersedes an earlier historical
`declared_retained: true` audit without rewriting that old receipt; never claim
that a deleted local copy is still present.

Large capture and training data belong in immutable GitHub Releases. The Code
page stores only lightweight indexes, annotations, training ledgers, asset
hashes, and Release download/restore instructions. Do not commit WAV/AIFF/FLAC,
split archives, checkpoints, or other large evidence to Git history or Git LFS.

## Fixed directory contract

```text
campaign/
  raw/<session-id>/...                         # immutable originals
  stimuli/...
  derived/<pipeline-version>/...
  reports/...
  training/
    ready/<dataset-id>/training-consumption-v1.json
    completed/<training-run-id>/
      training-consumption-v1.json
      ...model, metrics, logs, and frozen configuration...
    ledger/by-source-sha256/<prefix>/<sha256>/<objective-id>.json
```

While local capture payload exists, `raw/` is its only canonical
original-audio namespace. Derivatives and model inputs remain outside it even
when their filenames contain “raw”. Published Releases preserve the same
hierarchy under `capture-data/raw/` and package the raw archive family
separately from campaign support material. After verified local cleanup, the
Release and its content-addressed lightweight index are the canonical retrieval
authority. The Code-page receipt must identify every Release asset, size,
SHA-256, source snapshot or round, device/session scope, and restore command so
other agents can retrieve the exact training inputs without guessing from
filenames.

## Claim before training

Before a training process reads data, create one exact `READY` claim with:

- dataset ID, training-objective ID, and model family;
- every canonical raw parent path, size, and SHA-256;
- every actual derived training input path, size, and SHA-256;
- the exact split/allowlist manifest path and hash;
- a policy that blocks already-consumed evidence.

Dataset loaders consume this pinned claim or its pinned allowlist. They do not
recursively discover audio. A claim is not proof that the capture dataset is
`RELEASED` or that all hardware-fidelity gates passed.

Use `tools/mc_capture_training_ledger.py claim`. It requires each
`--raw-source` to be inside `campaign/raw/` and refuses to overwrite an
existing claim.

## Complete and mark without touching audio

After training finishes and retained outputs are frozen, put the model,
metrics, logs, and configuration under
`training/completed/<training-run-id>/`, then run
`tools/mc_capture_training_ledger.py complete`. Completion:

1. re-hashes the pinned raw sources, training inputs, and split manifest;
2. writes an immutable `COMPLETED` consumption receipt;
3. writes one sidecar marker per raw SHA-256 and training objective;
4. links the `READY` claim to the completed receipt.

Never write training status into WAV, AIFF, FLAC, CAF, or other evidence
metadata. Before any later run, use the ledger `check` command. The same raw
SHA-256 cannot complete the same objective twice. Intentional retraining,
fine-tuning, or a changed loss/target requires a distinct objective ID and a
documented reason; it does not erase the prior marker.

## Sync only closed rounds to Releases

The Release sync gate is:

1. `round-file-annotations-v1.json` is `COMPLETE`;
2. `ROUND_NOTES.md` exists;
3. `validate_round_annotations.py --check-files` passes with no unresolved
   gate;
4. manifest and notes have passed the configured stability interval;
5. all files remain size/mtime stable while hashing and packaging;
6. the complete local package exists and matches its `SHA256SUMS`;
7. every Release asset matches local size and the provider-exposed SHA-256;
8. every current local source member matches the exact package-manifest path,
   size, and SHA-256;
9. the lightweight Code-page receipt and download/restore annotation identify
    the verified Release before local sync state is advanced;
10. no capture, validator, trainer, or other process is using a deletion target.

Use `tools/mc_capture_release_sync.py sync-ready --upload` after closure.
Initial archive seeding uses `snapshot --upload`, writes
`RAW_AUDIO_INDEX.json`, and separates the `raw-audio` archive family from
campaign support. Incremental uploads are content-addressed, so an already
covered SHA-256 is not uploaded again. Never upload a large capture or training
file to the Code page as a substitute for a Release.

After the gate passes, delete only the exact locally covered payload and
package paths, then write the append-only lightweight deletion receipt. If any
target changed after verification or any deletion fails, stop, record the
partial result precisely, and do not broaden or retry the target implicitly.
Deleted data is recoverable only by restoring the verified GitHub Release.
Remote synchronization and local cleanup never change QA state, training
eligibility, claim tier, or dataset release status.
