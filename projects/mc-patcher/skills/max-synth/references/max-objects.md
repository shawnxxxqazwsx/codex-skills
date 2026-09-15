# Core Max (event) objects

Inlets below are 0-based as used by MaxMSPMCP `connect_max_objects`. When unsure, call `get_object_doc`. Object names never end in `~`.

## Event primitives

| Object | Role | Inlets | Outlets | Notes |
|---|---|---|---|---|
| `bang` / `button` | Manual or chained trigger | click / bang | bang | UI bang source |
| `toggle` | 0/1 latch | bang flips | 0 or 1 | Audio on/off UI; not DSP itself |
| `message` | Send literals | bang / prepend | message | Edit with MCP `set_message_text` |
| `comment` | Label | — | — | Document the voice |
| `loadbang` | Fire on open | — | bang | Init |
| `loadmess` | Send a message on open | — | that message | Prefer `startwindow` over `start` |
| `metro` | Periodic bangs | 0/1, interval ms | bang | Sequencer clock; not sample-accurate |
| `delay` | Delay a bang | bang, time | bang | Scheduler, not audio delay (`tapin~`) |
| `pipe` | Delay numbers | value, time | delayed value | |
| `clocker` | Elapsed time while on | 0/1 | ms | |
| `timer` | Interval between bangs | bang start/stop | ms | MIDI clock → LFO rate in [MIDI Tutorial 2](https://docs.cycling74.com/learn/articles/10_midichapter02/) |
| `select` / `sel` | Match values | input | bangs per match + unmatched | Route discrete states |
| `route` | Match list heads | list | per-selector + rest | Voice routing after `poly` |
| `gate` | Event switch | on/off, data | N outlets | Cold data, hot control on left |
| `switch` | Choose one inlet | selector, values | one | |
| `gswitch` / `ggate` | Graphical switch/gate | | | UI versions |
| `trigger` (`t`) | Ordered fan-out | anything | one per argument | Args `b i f l s` or constants. Outputs **right to left**. |
| `print` | Console | anything | — | Debug |

## Numbers and lists

| Object | Role | Gotcha |
|---|---|---|
| `int` / `float` | Store and output a number | Left inlet hot |
| `number` / `flonum` | UI number box | MCP `set_number` |
| `+` `-` `*` `/` `%` | Event arithmetic | Cold right inlet |
| `expr` | Math expression | `$i1`, `$f1` style |
| `scale` | Map ranges | MIDI 0–127 → Hz or 0–1 |
| `clip` | Limit range | |
| `random` | Integer 0..N-1 | Needs bang |
| `drunk` | Random walk | |
| `pack` | Build a list | **Only left inlet outputs.** Right inlets are cold. Args set types (`0.` vs `0` vs `foo`). |
| `pak` | Like pack but every inlet is hot | Use when any element should output |
| `unpack` | Split list | |
| `join` / `unjoin` | Concatenate | |
| `zl` family | List ops | `zl.len`, `zl.nth`, `zl.rot`, `zl.group`, … |
| `prepend` / `append` | Wrap messages | |
| `sprintf` | Format | |
| `bucket` | Shift register of floats | |
| `counter` | Count bangs | |
| `accum` | Running total | |
| `change` | Output only if value changed | Dedup MIDI |

## MIDI and pitch

| Object | Outlets / role |
|---|---|
| `notein` | pitch, velocity, channel. Note-off is velocity 0. |
| `noteout` | Send notes |
| `midiin` / `midiout` | Raw bytes |
| `midiparse` / `midiformat` | Decode/encode. Rightmost `midiparse` outlet feeds `poly~` `midievent`. |
| `mpeparse` / `mpeformat` | MPE → `mpeevent` for `poly~` |
| `ctlin` / `ctlout` | CC (mod wheel = CC1 in the MIDI synth tutorial) |
| `bendin` / `bendout` | Pitch bend |
| `pgmin` / `touchin` / `rtin` | Program, aftertouch, real-time clock |
| `makenote` | Pair note-on with delayed note-off |
| `stripnote` | Split note-on vs note-off |
| `flush` | Panic: send note-offs for held notes |
| `sustain` | Pedal hold |
| `poly` | Assign voice index to note-on/off. **Does not create oscillators.** Args: voices, steal flag. |
| `ddg.mono` | Last-note-priority mono from polyphonic input ([Polyphony](https://docs.cycling74.com/userguide/polyphony/)) |
| `kslider` | On-screen keyboard |
| `mtof` / `ftom` | MIDI note ↔ Hz (event). `mtof` `@base` default 440. For audio-rate pitch glide use `mtof~`. |
| `hz` | Related frequency helper (if present) |

Standard note path: `notein` → `poly` (optional) → `pack` → `route` per voice, or skip `poly` and send `midinote` into `poly~`.

## Data, state, patch structure

| Object | Role |
|---|---|
| `coll` | Indexed collection | presets, tunings |
| `table` / `itable` | Integer table | wavetable indices, sequences |
| `dict` | Dictionaries | |
| `pattr` / `pattrstorage` / `autopattr` | Parameters and presets | Max 9: `nodes` + `preset` interpolates |
| `preset` | Snapshot UI objects | |
| `value` / `pv` | Named shared numbers | |
| `send` / `receive` (`s`/`r`) | Wireless events | Pair with `send~`/`receive~` for audio |
| `pvar` | Named patcher vars | |
| `patcher` / `p` | Subpatcher | |
| `bpatcher` | Visible subpatcher | Front-panel |
| `thispatcher` / `pcontrol` | Script the patcher | |
| `poly~` | See [polyphony-midi-mc.md](polyphony-midi-mc.md) | MSP hybrid |
| `in` / `out` | Event I/O **inside** `poly~` | Indexed; not `inlet`/`outlet` |
| `param` | Named `poly~` attribute (Max 9 Parameter Connect) | |
| `function` | Breakpoint envelope editor | Drive `line~` with its list outlet |
| `umenu` / `chooser` | Menus | Osc/filter type |
| `slider` / `dial` / `rslider` | UI | Prefer `live.*` in Max for Live |
| `live.dial` `live.numbox` `live.slider` `live.gain~` | Live-styled parameters | Automation |
| `attrui` | Edit an object attribute | ABL / Gen Parameter Connect |

## Order recipes

Set frequency before triggering a note:

```text
pitch ──► t b f ──► (right out f) → mtof → osc frequency
              └──► (left out b)  → delayed via t, or pack with vel
```

Better: `trigger` with `t l b` after `pack pitch vel`, or send pitch to a cold inlet then bang the hot inlet.

`pack 0 0` then left-inlet pitch will output `[pitch, old-vel]` unless velocity was stored first. Store velocity (right inlet), then pitch (left), or use `pak`.
