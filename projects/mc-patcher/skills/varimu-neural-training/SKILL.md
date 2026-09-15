---
name: varimu-neural-training
description: Plan, coordinate, execute, audit, package, and publish neural or hybrid training for the captured Manley Variable Mu data. Use when preparing a training-ready batch, selecting a causal model and losses, coordinating multiple machines through GitHub claims, monitoring for new capture batches, validating each usable model with Original/Target/Current audio-render forensics, or sealing a completed model/data/annotation bundle. Do not use to grant dataset eligibility, to mix primary and comparison-only targets, or to claim hardware equivalence without independent withheld evidence.
---

# Vari-Mu neural training

Treat training as an evidence pipeline, not as permission to recursively consume
audio. The exact dataset allowlist is the sole eligibility authority. Preserve
raw hashes and route every consumed source through the repository training
ledger.

## Required order

1. Read [references/current-manley-policy.md](references/current-manley-policy.md)
   and resolve the exact batch, device state, target variant, objective ID, and
   claim tier. Stop on any unresolved eligibility conflict.
2. Validate the capture package with the `hardware-compressor-capture` skill.
   Completed capture payload may have been deleted locally after verified
   Release publication; in that case restore only the pinned Release members
   into the claimed workspace and verify every source hash before creating the
   READY receipt.
   Create the local READY receipt with `tools/mc_capture_training_ledger.py
   claim` before optimization. Do not infer eligibility from folders, names, or
   split labels.
3. For a newly captured batch with no candidate algorithm, run the paired
   Original/Target baseline in [references/forensic-validation.md](references/forensic-validation.md).
   This is a two-signal characterization; do not invent a Current render.
4. Read [references/training-plan.md](references/training-plan.md), freeze the
   split, metric registry, normalization floors, baselines, model budget, and
   acceptance gates, then train in a local claimed workspace.
5. For every usable checkpoint or algorithm version, render the frozen
   Original through it and run the complete three-way Original/Target/Current
   forensic comparison plus `audit_forensic_metric_completeness.py`. Report
   every comparable statistic and all missing or non-comparable fields. Never
   select from one aggregate score alone.
6. Validate the completed run directory, seal the local training ledger, retain
   the complete local folder plus verified package parts, publish the large
   immutable package as create-only GitHub Release assets, then publish only
   hashes, annotations, the ledger receipt, and the Release link under
   `varimu-training/release-index/` in one create-only Git commit.

## Multi-machine rule

Read [references/multi-machine-protocol.md](references/multi-machine-protocol.md)
before installing or operating a worker. Each machine runs `watch-once` every
600 seconds. A worker may claim only when it has no local active run. The
canonical `queue/<batch-id>/claim.json` is created with create-only semantics;
concurrent losers must not overwrite, rename, delete, or take over the claim.

Run the following relative `scripts/` commands from the skill directory that
contains this `SKILL.md`, or resolve their paths explicitly first.

Use:

```bash
python3 scripts/varimu_training_coordinator.py watch-once --config /absolute/config.json
```

Install the ten-minute monitor with:

```bash
python3 scripts/install_monitor.py install \
  --repo-root /absolute/path/to/mc-patcher \
  --repo shawnxxxqazwsx/mc-patcher \
  --branch main
```

The Git repository Code page is the lightweight coordination and index plane.
Large capture/training audio, derived data, checkpoints, reports, and package
parts must not be committed there and must not use Git LFS. They are hashed,
compressed, split below GitHub's per-asset limit, and uploaded to a unique
create-only GitHub Release. `varimu-training/release-index/` contains only the
completion receipt, detailed annotation, manifests, ledger receipt, SHA-256
inventory, and Release link. Packaging and publication copy from the complete
local run and verified local parts; they never move or delete unique local
evidence. The removed `trained Data/` namespace must never be recreated.

## Stop conditions

Stop before training or publishing when any of these is true:

- the exact allowlist and file annotations disagree;
- a validation/withheld/rejected/superseded file is offered to optimization;
- primary and comparison-only target variants are mixed in one objective;
- raw sources or split manifests changed after the READY ledger claim;
- the batch already has another machine's claim;
- the local worker already has a CLAIMED, TRAINING, or FINALIZING run;
- a candidate lacks the complete three-way forensic artifact set;
- completion annotations omit the machine name, machine ID, UTC timestamps,
  source hashes, code/environment identity, model artifacts, or known limits;
- the GitHub Release tag/assets or Code-page completion index would overwrite
  or disagree with existing evidence;
- the local complete folder or verified split-package backup is missing.

## Evidence and claim language

Follow [references/completed-run-contract.md](references/completed-run-contract.md).
Training success establishes only the frozen gates that actually passed.
Hardware-fit or product-ready claims additionally require independent withheld
captures, controlled probes, listening, realtime engineering gates, and the
declared plug-in/DAW path.
