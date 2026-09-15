# Other DAWs and shared safety

## Map comparable concepts, not menu names

For Pro Tools, Logic Pro, Studio One, Ableton Live, Digital Performer, Bitwig,
or another host, first locate the current equivalents of project/session, track
type, channel format, I/O/routing, insert/device chain, automation mode,
transport/record state, and render/bounce. Do not substitute a similar-looking
command from a different DAW.

- Pro Tools: distinguish track I/O, bus, aux, routing folder, VCA, clip gain,
  inserts/sends, and playback/record engines.
- Logic Pro: distinguish channel strip, bus/aux, Track Stack, Smart Controls,
  take folder, and project versus global settings.
- Studio One: distinguish track/channel, bus/FX channel, Event/Part, Console
  inserts/sends, and song/project/mastering pages.
- Ableton Live: distinguish Session and Arrangement, track/device chain,
  return track, clip/scene launch, external instrument, and capture/record.

## Live audio and recording

When the task explicitly authorizes live operation, do a brief preflight:

1. Resolve the input/source, recording target/path, monitoring destination,
   clock/sample rate/buffer readback, and current transport/arm state.
2. Confirm only the authorized tracks are armed and only the authorized outputs
   are enabled. Keep monitor level and any physical patching inside the stated
   scope.
3. Make the requested action, then stop transport/recording and verify the
   resulting take/file and final arm/monitor state.

If any device, channel, monitoring state, or destination is unknown, report it
as the blocker. Do not use a new take, rendered audio, or a meter as a claim of
calibrated, hardware-correct, or subjectively approved sound.

## Minimum troubleshooting record

For an issue that persists, record: host/version; project rate/block and audio
engine; project saved state; selected track/bus and layout; plug-in format and
loaded identity; exact steps; visible error/log; and whether playback, a meter,
or a human listener was actually used. This lets the next attempt reproduce the
same host path without expanding control of the user's studio.
