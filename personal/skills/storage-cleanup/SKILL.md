---
name: storage-cleanup
description: Inspect and safely reclaim disk space from development build/test outputs, duplicate generated data, and archived Codex session data when the user requests cleanup or a recurring cleanup workflow. Do not activate for ordinary development, user document organization, or audio editing.
---

# Storage Cleanup

Establish the user's allowed paths and deletion authority first. This skill adds
no permission to delete files, conversations, history, or external resources.
Honor current project instructions and explicit item-level retention requests.

## Resolve candidates, rather than only measuring growth

Use allocated size to prioritize, then descend into a bounded batch of actual
files or data families. Read generators, manifests, outcome reports and current
inputs. A recurring run should advance a persisted audit queue instead of
repeating the same top-level `du` report and blanket retention reasons.

Separate conversation retention from artifact retention: an unarchived chat
does not automatically need every old generated output. An idle, paused or
unloaded chat is also not proof that its files are disposable.

Classify references by meaning. Current execution inputs, project links, active
readers/writers, locks and explicit retention contracts can require a file.
Historical reports, completed input inventories and old git-status listings
do not by themselves establish a current runtime dependency. Preserve original
reports and verdicts even when permitted derivative payloads are removed.

For duplicate candidates, prefilter by size, then fully hash both sides. Keep a
stable canonical copy of every distinct byte sequence and all unique evidence.
Confirm that no current input or project needs a proposed deleted path. A
report containing that path may instead require a small availability marker
and a canonical-to-deleted-path mapping for later replay. Do not silently add
hardlinks or symlinks that could alias future writes.

For build candidates, identify the owning target, lane, source and dependencies.
Distinguish reproducible objects and redundant public download archives from
frozen executables, unique source snapshots and measurement evidence. Extension,
age, similar names, or clean Git status alone never proves disposability.

## Execute a supported exact plan

For each selected item record its exact path, rationale, size, allocated bytes,
full content identity, stat identity, retained counterpart or generator, and
reference checks. Recheck nofollow paths, retained copies, readers/writers and
locks immediately before removal. Delete only the reviewed paths and keep an
incremental journal so a partial failure remains understandable.

Verify retained canonical files and protected material after execution. Report
logical bytes removed, allocated bytes removed, and system free-space change
separately; APFS clones, snapshots and concurrent work can make them differ.
Moving to Trash or creating database free pages is not physical reclamation.

For Codex history, use fresh application archive state and supported deletion
interfaces. Do not equate unloaded with archived, delete active history, edit a
running SQLite database, or unlink DB/WAL/SHM files. Do not remove Git refs,
reflogs, recovery snapshots, or unique evidence under a generic cache label.

## Make repeated runs useful

Keep a compact queue with reviewed families, decisions, evidence paths, next
missing check and revisit conditions. A zero-deletion run describes that batch,
not the entire disk. If zero-deletion runs repeat, investigate a previously
unreviewed family or supply a missing hash/reference/generator/ownership check;
do not restate broad assumptions or lower the safety gate to meet a quota.

Configure recurring execution through the application's scheduling tools when
requested, preserving the established interval and unrelated settings. Match
the user's reporting intent; ordinary growth of expected active artifacts is
not a cleanup result. Never interrupt healthy builds, live sessions or another
task merely to complete maintenance.
