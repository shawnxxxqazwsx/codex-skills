---
name: max-synth
description: >-
  Build synthesizers in Cycling '74 Max / Max 9 with Max (event) and MSP
  (audio) objects: oscillators, filters, envelopes, MIDI, poly~, MC wrapping,
  gen~, and Max 9 ABL DSP. Use when the user asks to patch a synth in Max,
  MaxMSP, MSP, Max for Live, or mentions cycle~, saw~, adsr~, poly~, dac~,
  subtractive/FM/wavetable synthesis, or the MaxMSPMCP tools. Do not use for
  JUCE/VST C++ synths, generic DAW mixing, or Jitter-only visuals.
---

# Max Synthesizer Patching

Design and patch synthesizers in Max as signal networks plus event control, not as general-purpose programs. Prefer objects that exist in the user's live Max instance. Look up inlet/outlet order before connecting.

Official docs: [Max Documentation](https://docs.cycling74.com/), [What's New in Max 9](https://docs.cycling74.com/userguide/new_in_max9/), [Ableton DSP](https://docs.cycling74.com/userguide/abl/).

## Route the request

Read this file first. Then read only the references the current task needs.

| Need | Read |
|---|---|
| Event vs signal, hot/cold, amplitude, Max 9 deltas | [references/fundamentals.md](references/fundamentals.md) |
| Max (non-tilde) objects for control, MIDI, lists, UI | [references/max-objects.md](references/max-objects.md) |
| MSP oscillators, filters, envelopes, buffers, math | [references/msp-objects.md](references/msp-objects.md) |
| Subtractive / FM / AM / wavetable / additive / noise | [references/synth-architectures.md](references/synth-architectures.md) |
| MIDI, poly~, thispoly~, MC, MPE | [references/polyphony-midi-mc.md](references/polyphony-midi-mc.md) |
| Max 9 ABL devices and DSP macros | [references/max9-abl.md](references/max9-abl.md) |
| Building or editing the open patch via MaxMSPMCP | [references/mcp-patching.md](references/mcp-patching.md) |

If MaxMSPMCP is connected, follow [references/mcp-patching.md](references/mcp-patching.md) instead of describing a patch the user must recreate by hand.

When an object's inlets, arguments, or messages are uncertain, call `get_object_doc` (or open the Cycling '74 reference). Do not invent inlet order.

## Classify the instrument

Capture and state:

```text
Architecture: subtractive | FM | AM/ring | wavetable | additive | noise/filter | hybrid
Voicing: mono | poly~ | MC wrapper
Control: MIDI notes | MPE | UI only | sequencer
Oscillators:
Filter / waveshape:
Envelopes / LFOs:
Max 9 ABL allowed?: yes if get_object_doc succeeds
```

Default when unspecified: **MIDI subtractive voice** (anti-aliased osc → resonant lowpass → ADSR amplitude), then wrap in `poly~` if more than one note is needed.

## Invariants

These change patching decisions. Details and sources are in the reference files.

1. **MSP names end in `~`.** Striped cords carry signals at the audio rate. Plain Max objects sit idle until an event arrives.
2. **`dac~` expects roughly `-1.0` to `1.0`.** Put `gain~` or `*~` attenuation before output. Oscillators at full scale into `dac~` clip and can be dangerously loud. Official test-tone tutorial: [MSP Basics Tutorial 1](https://docs.cycling74.com/learn/articles/05_mspbasicchapter01/).
3. **`*~` with no argument and no right-inlet signal defaults to multiplying by 0.** Always give `*~` an argument, a number, or a connected control signal.
4. **Left inlet is hot.** Other inlets store. Use `trigger` (`t`) when order must be explicit; Max fans out right-to-left.
5. **Audio-rate modulation needs a signal.** A float into a signal inlet is sampled, not interpolated. Use `line~`, `sig~`, `adsr~`, or another `~` object to avoid zipper noise. ABL objects are an exception: they smooth event-rate attribute changes ([Ableton DSP](https://docs.cycling74.com/userguide/abl/)).
6. **`start` / `stop` on any `dac~`/`adc~` affect every open patch.** Prefer `startwindow` while iterating.
7. **Anti-aliased analog oscs are `saw~`, `tri~`, `rect~`.** `phasor~` is a 0–1 control ramp, not a band-limited audio oscillator ([Filter Tutorial 3](https://docs.cycling74.com/learn/articles/08_filterchapter03/)).
8. **Polyphonic notes need voice allocation.** `poly` only assigns voice numbers. Sounding voices require `poly~` + `thispoly~`, or MC + `mc.noteallocator~` ([Polyphony](https://docs.cycling74.com/userguide/polyphony/)).

## Default voice (subtractive)

```text
notein / kslider
    → unpack or route pitch + velocity
pitch → mtof (or mtof~ after sig~) → saw~ / rect~ / tri~  [and optional detuned twin]
    → *~ mix
    → lores~ or svf~          cutoff + resonance from UI or second envelope
velocity scaled 0–1 → adsr~   trigger; 0 = release
    → *~  (audio * envelope)
    → gain~
    → dac~
```

For more than one simultaneous note, put the oscillators/filter/envelope inside a `poly~` abstraction with `in`/`out`/`in~`/`out~`, and connect `adsr~` outlet 1 (busy) or outlet 2 (mute) to `thispoly~` as in the official polyphony guide.

## Work order

1. If MaxMSPMCP is connected and a patch is open, inspect it (`get_objects_in_patch` / selected objects) before adding anything. Otherwise work from the supplied `.maxpat`, screenshot, or specification and report that live patch/audio verification was not run.
2. Classify architecture and voicing. State the signal chain in one short block like the default voice above.
3. Confirm critical objects with `get_object_doc` when inlet order is not already in the reference tables.
4. If ABL objects are desired, probe with `get_object_doc` on `abl.dsp.basicshapes~` or `abl.device.drift~`. On a Max 8 install or a Max 9 without the Ableton DSP package they will fail — fall back to MSP.
5. Patch control first (MIDI → Hz, velocity → trigger), then oscillators, then filter, then amplitude, then `gain~` → `dac~`.
6. Keep unused voices muted (`thispoly~` / MC busy map). Keep resonance and FM index from exploding; `lores~` near resonance `1` can clip ([lores~](https://docs.cycling74.com/reference/lores~/)).
7. When the build or test request reasonably includes local audition and the output path is known, set output gain low and verify with `startwindow`: one note, polyphony, and modulation. If the request does not include audition or the output path is uncertain, leave DSP off, verify patch structure and control readback, and report that audio was not heard.

## What not to do

- Do not use raw `phasor~` as the audible saw of a subtractive synth; use `saw~`.
- Do not treat `poly` as a substitute for `poly~`.
- Do not send `start` while debugging if other patches may also make sound.
- Do not design Jitter/OpenGL visuals unless the user asked; Max 9 `jit.fx` / geometry are out of scope for this skill.
- Do not implement a JUCE/VST C++ instrument here; that is a different product path.
