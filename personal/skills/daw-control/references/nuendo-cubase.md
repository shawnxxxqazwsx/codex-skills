# Nuendo and Cubase

These hosts share many concepts, but labels and available post-production/
immersive features differ by edition and version. Trust the currently visible
workspace and project configuration over remembered menu paths.

## Establish project and routing context

- Confirm the active project, project/sample rate, Control Room state when
  relevant, transport/record mode, selected track(s), and the focused window
  (Project, MixConsole, Audio Connections, VST Plug-in Manager, or plug-in
  editor).
- Read Audio Connections and channel/bus format before changing routing. Track
  output assignment, Direct Routing, sends, cue/Control Room paths, and channel
  configuration can each explain an apparent missing return.
- For surround/immersive work, verify the bus format, speaker configuration,
  panner/rendering path, and plug-in I/O. Do not change a project to Stereo,
  alter a renderer, or reinterpret a bed/object path merely to make a plug-in
  appear active.

## Make targeted edits

- Use track names plus their visible type and output assignment; folder/VCA/
  group/FX/monitor tracks are not interchangeable audio paths.
- In MixConsole, distinguish channel strip, insert slot, pre/post-fader send,
  direct output, and Control Room/Cue monitoring. Confirm the actual insert
  slot before opening/replacing a plug-in.
- Verify automation's target parameter, touch/latch/write/read state, and
  punch/range boundaries before enabling Write. Stop and disarm Write after the
  requested pass. Do not leave a project globally writing automation.
- For offline processing, render-in-place, freeze, bounce, or export, check
  source track/event selection, range, tail, channel layout, output location,
  and whether the action replaces originals. Prefer a new version if the
  requested destination is unclear.

## Reload and diagnostic boundaries

- An installed or scanned plug-in can remain different from the loaded
  instance. If the project is untitled or has unsaved changes, ask the user to
  save it and resolve the Save As destination before exiting or rescanning.
  After the required restart/rescan, verify a fresh in-project instance, its
  visible version/build when available, buses, and pins/sidechain.
- Treat the Project window, MixConsole, and Control Room as separate evidence
  surfaces. A correct insert list does not prove the correct output endpoint;
  a meter does not prove a speaker/hardware path or subjective sound.
- Capture versioned project backups before broad visibility, routing, profile,
  workspace, key-command, or device setup changes. Project-level work does not
  authorize changing global preferences or studio hardware settings.

## Nuendo-specific post work

For ADR, video, loudness, field recorder, Direct Offline Processing, Atmos,
object/beds, or renderer tasks, identify the target event/clip, timecode range,
and delivery configuration before acting. Do not export, conform, alter sync,
or activate a physical monitoring/renderer path without explicit authority and
the exact delivery/device scope.
