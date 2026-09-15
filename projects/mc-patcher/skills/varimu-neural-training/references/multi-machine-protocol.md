# Multi-machine staggered training protocol

## Two-plane layout

Git stores the lightweight coordination control plane:

```text
varimu-training/
  protocol-v1.json
  queue/<batch-id>/batch.json
  queue/<batch-id>/claim.json
  workers/README.md
  release-index/<batch-id>/<run-id>/
    completed-run.json
    completed-run-v1.json
    ANNOTATION.md
    package-manifest-v1.json
    training-ledger-receipt.json
```

Each machine stores its local working data under one configured root:

```text
varimu-training-workspace/
  batches/<batch-id>/batch.json
  active/<batch-id>/active-run.json
  completed/<run-id>/
    completed-run-v1.json
    ANNOTATION.md
    data/
    algorithm/
    evaluation/
    logs/
  logs/
  state/
```

Large capture packages and completed training folders live in immutable,
create-only GitHub Releases. They are zstd-compressed, split below the GitHub
Release per-asset limit, and inventoried by SHA-256. The Code page contains only
queue/claim files and lightweight completion annotations, manifests, ledger
receipts, hashes, and Release links. Git LFS and Code-page large blobs are
forbidden, and the removed `trained Data/` namespace must not be recreated. The
complete local run and verified local package parts must exist before remote
publication and remain after it.

## Ten-minute worker cycle

Every worker runs one short `watch-once` job every 600 seconds through launchd
or a systemd user timer:

1. acquire the machine-local monitor lock;
2. refuse new work if any local active record is CLAIMED, TRAINING, or
   FINALIZING;
3. list and validate every READY batch visible in the cycle;
4. verify the batch's immutable Release tag/URL and downloaded archive-manifest
   asset hash, plus the exact allowlist and READY ledger at their pinned
   metadata Code commit; an invalid batch is reported and does not prevent
   scanning later batches;
5. check every batch's completion, local-presence, and claim state, then order
   the available set strictly by `created_at_utc` from oldest to newest;
6. validate the chosen manifest and check that the batch is not locally present or
   remotely completed;
7. read the canonical `claim.json`;
8. if a claim exists, leave it untouched and examine the next-oldest batch;
9. claim the oldest unmarked batch by creating `claim.json` with create-only
   GitHub semantics containing
   machine name, stable machine ID, UTC timestamp, batch-manifest SHA-256,
   objective ID, repository, and branch;
10. only the successful creator writes the local active record. Losing workers
   wait for another batch.

The monitor claims ownership but does not execute an arbitrary training command.
The training runner must explicitly transition the local state and verify the
READY training ledger. This separation prevents a newly uploaded manifest from
executing repository-supplied code on every machine.

## Claim invariants

- One batch has one immutable canonical claim.
- Oldest-unclaimed-first is determined by `created_at_utc`; `priority` is
  audit-only and cannot let a newer batch jump the queue.
- No automatic lease expiry, overwrite, deletion, or takeover.
- Clock differences do not choose a winner; GitHub create-only success does.
- A stale/abandoned claim requires an explicit reviewed supersession record and
  a new batch ID. Never recycle the old ID silently.
- A machine cannot claim while it owns any active run.
- Machine display name is human-readable; stable machine ID is the identity.
- GitHub authentication is per OS user and must have private-repository write
  permission.

## Completion sequence

1. finish optimization and all per-version evidence;
2. assemble one local completed run folder;
3. validate hashes, annotations, machine/time fields, claim binding, data/model
   identity, and complete three-way evidence;
4. call the local training ledger `complete` command;
5. package the folder without changing it, retain the complete local folder and
   verified local parts, and never move/delete a unique copy;
6. upload the package manifest and all parts to the unique create-only Release
   tag `varimu-training-<run-id>`; if it already exists, byte-compare its
   manifest and verify or resume only missing assets without overwrite;
7. copy only lightweight manifests, annotation, training-ledger receipt,
   SHA-256 inventory, and Release link into a temporary publisher clone, then
   push one create-only Git commit under
   `varimu-training/release-index/<batch-id>/<run-id>/`;
8. close the local active record. Only then may the next ten-minute cycle claim
   another batch.

If Release upload or Code-page index creation fails, keep the local state
FINALIZING, preserve all local folders/parts, and retry idempotently. A Release
published before the Code commit is recovered through its byte-identical
package manifest; a Code commit published before local closure is recovered by
byte-comparing every lightweight file. Do not claim new work or report
completion before both planes agree.
