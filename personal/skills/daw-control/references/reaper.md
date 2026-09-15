# REAPER

## Orient before editing

- Confirm the active project tab and its saved path. REAPER can have several
  project tabs and open FX windows; a title or plug-in name alone is not a
  unique target.
- Inspect the Track Control Panel, Mixer, Routing window/Matrix, and FX chain
  needed for the request. Check record arm, input, monitoring, mute/solo,
  parent send, receives/sends, hardware outputs, and track channel count.
- For media edits, distinguish the source file, take, item, active take,
  take FX, item FX, track FX, and render target. They are separate layers.

## Operate with REAPER-native semantics

- Use track/item/envelope identities and the visible action outcome rather than
  numeric track indexes or coordinates: reordering and folder nesting change
  indexes. Avoid global actions when a selected-item/selected-track action is
  available.
- Inspect the Routing window or Matrix for both ends of a send/receive. Confirm
  source and destination channel pairs, send mode (including sidechain), and
  that parent send is deliberately enabled/disabled. Use the I/O pin connector
  for plug-in channel mapping; do not infer a multichannel configuration from
  a stereo meter.
- In the FX chain, distinguish bypass, offline, wet/dry, parameter automation,
  and preset state. For a plug-in replacement, preserve routing/pins and record
  the old/new instance state before removal.
- When changing envelopes, reveal the correct lane and verify the time range,
  point shape, and target parameter. Avoid moving underlying items unless the
  task says to ripple or move them.

## Rendering, reload, and verification

- Before rendering, read the Render dialog's source, bounds, tail, sample rate,
  channels, format, output location, and filename policy. A source selection
  can render a master mix, stems, selected tracks, or selected media.
- Treat ReaScript/OSC as a mutating control plane. Use it only when the user
  authorized the task and scope the script to resolved project/track/item IDs;
  re-read state afterwards.
- After installing a VST3, if the project is untitled or has unsaved changes,
  ask the user to save it and resolve the Save As destination before closing or
  reopening REAPER. Confirm a fresh instance in the FX browser/chain, its
  architecture/version if shown, and the actual I/O/pin arrangement. A rescan
  or FX-browser listing alone does not establish a live audio-path result.

## Useful diagnostic split

When a plug-in or route "does nothing," separately test whether it is:

1. Not receiving audio (source, arm/monitor, item/take, mute/solo, send).
2. Receiving but bypassed/offline/at zero wet gain.
3. Processing into the wrong channels or a non-audible return.
4. Running an old in-memory binary/instance.
5. Producing signal that requires listening or a real-time meter to judge.

Do not begin playback or alter audio hardware merely to distinguish these
without the user's explicit live-audio authority.
