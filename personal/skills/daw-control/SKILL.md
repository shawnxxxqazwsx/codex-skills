---
name: daw-control
description: Safely inspect, operate, troubleshoot, and verify common DAWs, especially REAPER and Nuendo/Cubase. Use for project, track, routing, plug-in, transport, rendering, and DAW-based validation tasks; not for changing source code or modeling hardware DSP by itself.
---

# DAW Control

Use the DAW as the live host, not as an assumed state. Favor the application's
current semantic UI, scripts/APIs that the user has already authorized, and
observable readback over coordinates, memorized menu paths, or file-name
guesses.

## Establish the live state first

Before changing anything, identify and report only what matters to the request:

- DAW/version, foreground project and whether it is saved, transport state,
  project sample rate and applicable recording/render bit depth, audio device,
  and active project tab.
- The selected track(s), bus/routing context, channel layout, and whether an
  armed/monitoring/record-enabled path is involved.
- The exact target plug-in/clip/marker/automation lane, including a visible
  instance name and format when relevant.
- Whether the task needs visual/UI proof, signal/routing proof, a render, or
  a human listening decision. These are different acceptance layers.

Refresh the relevant surface after each mutation. Bind UI automation to visible
application/window/element identity, not a stale window ID, fixed coordinate,
or merely the first similarly named plug-in. If another task may be driving a
DAW window, stop on ambiguity rather than stealing focus or sending blind keys.

Read [REAPER guidance](references/reaper.md) for REAPER work and
[Nuendo/Cubase guidance](references/nuendo-cubase.md) for Nuendo or Cubase.
Read [host-neutral safety and verification](references/common-daws.md) for
other DAWs, recording, hardware, routing, render, or recovery work.

## Act in a reversible, narrow scope

The user's task authorizes only its necessary DAW actions. Prefer one visible,
reversible change, then inspect its resulting state before batching equivalent
changes. Preserve unrelated selection, routing, plug-in chains, automation,
media, project preferences, and global DAW settings.

Use the DAW's project undo/history when it is trustworthy, but do not describe
an action as reversible until that action has actually entered the project's
undo history. Before destructive operations (replacing source media, deleting
tracks or plug-ins, flattening/freeze/commit, overwriting a render, changing
session-wide rate/tempo, or saving over another version), resolve the exact
targets and make a recoverable copy/version when the user's request authorizes
the operation. Ask for direction if the target/version is ambiguous.

Never start recording, playback through an unknown physical path, loudness
calibration, hardware control, audio-device/clock/routing changes, or external
export/upload merely because a DAW is open. These require explicit scope that
covers the affected device, destination, and program. A stopped transport is
not evidence that monitoring or hardware output is safe.

## Plug-ins, reloads, and multichannel paths

For plug-in work, record the in-host instance and the track/bus/channel layout
before changing its controls. Preserve the host's pin/bus mapping and do not
silently collapse surround, Atmos, Ambisonics, sidechain, or discrete channels
to stereo. Confirm the format through host-visible I/O/pin information when it
matters; a plug-in's own channel labels are not sufficient evidence.

An installed VST3/AU build, file hash, scan result, or offline host test does
not prove that a running DAW loaded it. If the project is untitled or has
unsaved changes, ask the user to save it and resolve the Save As destination
before any restart/rescan. Then restart or rescan as appropriate and verify the
loaded instance's identity/version. Keep the old in-memory instance and the
reloaded instance distinct in the report.

For a Chlora/Bridge-style hosted graph, establish both DAW-side bus negotiation
and the host/graph's wet return. A visible editor or a green scan is not proof
of audible return, latency, or multichannel routing.

## Validate the requested claim

Choose the smallest evidence that actually addresses the task:

| Claim | Minimum observation |
|---|---|
| UI/control operation | Visible control readback and intended target identity |
| Track/bus routing | Both sending and receiving endpoints, channel mapping, and meter/signal observation when safe |
| Plug-in load/reload | Host-visible instance after the required rescan/restart, with its active format/layout |
| Automation/edit | Affected lane/item and at least one changed point/range readback; preserve untouched regions |
| Offline render/export | Exact output path, render bounds/source, format, and completion result; do not overwrite by default |
| Audio behavior | A controlled signal/result or an explicitly stated human listening observation |
| Recording/hardware path | Explicit device authority plus armed source/destination, safe monitoring, take/file receipt, and post-stop state |

Do not promote screenshots, menu state, meters, automation writes, or a
successful render to an unperformed listening, DAW reload, physical-device, or
release claim. State the remaining layer plainly.

## Recovery and reporting

If the live state diverges, stop issuing actions, capture the visible error and
the last confirmed state, then use the narrowest DAW-native recovery: cancel a
dialog, undo the known operation, disable only the failing target, or reopen a
saved project version. Do not restart a DAW with an untitled project or discard
unsaved changes without the user's direction.

Report the DAW/project context, exact targets/actions, verified result, and any
unperformed acceptance layer. For a failure, include a reproducible sequence,
the observed surface/log/message, and the next safe diagnostic rather than
guessing at routing, plug-in compatibility, or hardware.
