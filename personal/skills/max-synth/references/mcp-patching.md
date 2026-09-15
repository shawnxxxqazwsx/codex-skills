# MaxMSPMCP patching

Use the live Max connection. Do not dump a textual patcher the user must rebuild unless MCP is missing or Max is closed.

Discover schemas with the `user-MaxMSPMCP` tools already listed in the session. Typical names: `get_objects_in_patch`, `get_objects_in_selected`, `get_avoid_rect_position`, `add_max_object`, `remove_max_object`, `connect_max_objects`, `disconnect_max_objects`, `get_object_doc`, `list_all_objects`, `get_object_attributes`, `set_object_attribute`, `set_message_text`, `set_number`, `send_bang_to_object`, `send_messages_to_object`.

## Loop

1. `get_objects_in_patch` (or `get_objects_in_selected` if the user pointed at boxes). Read `varname`, `maxclass`, `patching_rect`, box text, and existing cords.
2. `get_object_doc` for any object whose inlet index you cannot state from the skill tables.
3. `get_avoid_rect_position` → place new boxes **outside** that rect (right or below, ~80–140 px gaps). Top-to-bottom signal flow.
4. `add_max_object` with a unique `varname` (`osc_saw`, `filt_lp`, `env_amp`, `dac_main`). `args` is the typed arguments list (frequency, patcher name, etc.).
5. `connect_max_objects` with 0-based `outlet_idx` / `inlet_idx`.
6. Set UI values (`set_number`, `set_message_text`) and attributes (`set_object_attribute`). One attribute per `send_messages_to_object` call.
7. Re-read `get_objects_in_patch` to confirm cords. Do not `remove_max_object` unless replacing or the user asked.

## Placement

- Control/MIDI highest Y-small (top of patcher).
- `dac~` / `ezdac~` lowest.
- Modulation to the right of the audio chain.
- Never stack on the avoid rect.

## Object creation hints

| Want | `obj_type` | `args` example |
|---|---|---|
| Saw 220 Hz | `saw~` | `[220]` |
| Pulse | `rect~` | `[220, 0.5]` |
| Cosine | `cycle~` | `[440]` |
| VCA | `*~` | `[0.2]` |
| ADSR | `adsr~` | `[10, 200, 0.7, 300]` |
| Lowpass | `lores~` | `[1200, 0.3]` |
| SVF | `svf~` | `[1000, 0.2]` |
| Audio out | `dac~` | `[]` or `[1, 2]` |
| MIDI in | `notein` | `[]` |
| Hz | `mtof` | `[]` |
| Poly host | `poly~` | `["voice", 8]` — patcher must exist on disk |
| Message | `message` | then `set_message_text` |
| Comment | `comment` | label via attribute/text tools available |

If `add_max_object` fails, the name may be invalid on this Max (`abl.*` on Max 8, typos, missing package). Fall back to MSP.

## Connecting a default MIDI subtractive voice

```text
notein pitch(0)  → mtof(0)
mtof(0)          → saw~(0)
saw~(0)          → lores~(0)
notein vel(1)    → scale or * → adsr~(0)
lores~(0)        → *~(0)
adsr~(0)         → *~(1)
*~(0)            → gain~(0)
gain~(0)         → dac~(0) and dac~(1)
```

Exact `scale` wiring depends on arguments; look up `scale` if used. Velocity 0 must reach `adsr~` for release (`notein` already sends 0 on note-off).

## Audio on

After confirming the output path and audition scope, keep `gain~` low (`set_number`) and send `startwindow` to `dac~` / `ezdac~` via `send_messages_to_object`, not `start`. Otherwise leave DSP off and verify the patch graph and control readback only.

## When MCP is absent

Write a compact object list + connection table using the same varname style, and tell the user to open Max and reconnect MCP. Do not invent `.maxpat` JSON.
