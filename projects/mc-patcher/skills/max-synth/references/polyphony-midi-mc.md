# MIDI, polyphony, MC

Sources: [Polyphony](https://docs.cycling74.com/userguide/polyphony/), [poly~](https://docs.cycling74.com/reference/poly~/), [MIDI Tutorial 2](https://docs.cycling74.com/learn/articles/10_midichapter02/), [MC](https://docs.cycling74.com/userguide/mc/), [MC polyphony](https://docs.cycling74.com/userguide/mc/mc_poly_without_polytilde/).

## Choose a voicing system

| Need | Use |
|---|---|
| Last-note mono | `ddg.mono` into one voice |
| Few voices, teaching / simple MIDI | `poly` (event) + N copies of an abstraction + `route` |
| Proper synth, CPU mute, MPE | **`poly~` + `thispoly~`** |
| Many identical oscs, unison, additive | **MC wrapper** (`mc.cycle~ @chans N`) |
| MIDI-allocated MC voices | `mc.noteallocator~` / `mc.voiceallocator~` + `@usebusymap` |

`poly` only stamps a voice number onto pitch/velocity. It does not instantiate DSP. For a real instrument prefer `poly~`.

## poly~ voice patcher

Arguments: `poly~ voice.maxpat 8` (patcher name, instance count 1–1023). Optional `up 2` / `down 2` (power of two), `args …` last.

Inside the loaded patcher:

| Object | Purpose |
|---|---|
| `in 1`, `in 2`, … | Event inlets of the `poly~` box (index, not left-to-right position) |
| `in~ 1`, … | Signal inlets |
| `out 1`, … / `out~ 1`, … | Event / signal outlets. `poly~` **sums** `out~` across voices |
| `thispoly~` | Busy + mute. `1`/`0` or a **signal** (nonzero = busy). `adsr~` out 1 (busy) or mute outlet is the documented pattern |
| `polymidiin` | `midievent` / MPE bytes |
| `param` | Named attributes on the `poly~` box (Max 9 Parameter Connect) |

Host messages (do not confuse with messages meant for `in` objects — prefix with `list` if they collide):

- `midinote pitch vel` — vel ≠ 0 allocates a free voice; vel 0 finds that pitch
- `note …` — first free voice (busy map)
- `target N` — subsequent messages to voice N; `target 0` = all
- `setvalue N msg` — one voice (0 = all), does not change `target`
- `notemessage …` — to the voice currently holding a pitch; needs **signal** into `thispoly~` or note-off frees immediately
- `mpeevent …` / `midievent …` — MPE / raw MIDI
- `mute N 1` — stop DSP for voice N; `mute 0 1` all
- `steal 1` — steal busy voices (can click)
- `voices N`, `open N`, `allnotesoff`
- `@parallel 1` — split voices across cores; restart DSP; not in Live host; useful at larger vector sizes

Default voice assignment since Max 8 is least-recently-used (`@legacynotemode 0`).

### adsr~ + thispoly~

`adsr~` outlet 1 is 1 during attack/decay/sustain and 0 otherwise. Outlet 2 sends mute messages. Connecting the envelope (or busy outlet) to `thispoly~` both marks the voice busy and lets unused voices skip DSP ([Polyphony](https://docs.cycling74.com/userguide/polyphony/)).

## MIDI into poly~

```text
notein → pack / midiformat → midievent → poly~
                 or
notein → unpack → midinote $1 $2 → poly~
```

`ctlin` / `bendin` usually go to **all** voices (`target 0`) or via `notemessage` for per-note expression. MPE: `mpeparse` → `mpeevent`.

Classic alternative (MIDI Tutorial 2): `poly 4 1` → `pack` → `route 1 2 3 4` → four `synthvoice~` abstractions. Steal flag `1` recycles the oldest note.

## MC instead of poly~

One patcher, wrapper objects with `@chans` = voice count. `mc.noteallocator~` maps MIDI to channels; `@usebusymap 1` on each wrapped object so idle channels skip DSP. `mc.poly~` keeps per-voice channels (does not sum). `mcs.poly~` packs all `in~`/`out~` indices into one MC inlet/outlet.

Unison / swarm: `mc.saw~ @chans 7`, `deviate 10 440` on frequency, `mc.mixdown~` or `mc.*~` + mix.

## Glide, bend, MPE

- Glide: `line~` on MIDI note number (or Hz) before the oscillator; time from UI.
- Bend: scale 0–127 (or 14-bit) to ±N semitones, add to note, `mtof~`.
- Per-voice pressure / slide: MPE into `poly~`, or `notemessage` while `thispoly~` is held by the envelope signal.
