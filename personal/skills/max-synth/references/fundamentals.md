# Max / MSP fundamentals

Primary sources: [MSP Basics Tutorial 1](https://docs.cycling74.com/learn/articles/05_mspbasicchapter01/), [Max User Guide](https://docs.cycling74.com/userguide/), [What's New in Max 9](https://docs.cycling74.com/userguide/new_in_max9/), [Max 9.0.0 notes](https://cycling74.com/releases/max/9.0.0).

## Two clocks in one patcher

| Layer | Objects | When it runs | Cords |
|---|---|---|---|
| Max (event) | `metro`, `pack`, `notein`, `mtof`, `trigger` | On bang, MIDI, click, scheduler tick | Solid |
| MSP (signal) | names ending `~` | Continuously while audio is on, at the sampling rate (commonly 44100+ samples/s) | Striped |

An MSP network is an **instrument formula**: every `~` object is always computing the current sample. A Max network is idle until an event arrives. They coexist in the same patcher.

`dac~` / `adc~` / `ezdac~` / `ezadc~` / `adstatus` can start and stop the audio network. `start` and `stop` apply to **all open patchers**. `startwindow` starts only the current window and its subpatchers.

## Amplitude

- Generators such as `cycle~` output a normalized range of about `-1` to `1`.
- `dac~` treats that range as full scale; exceeding it clips.
- Never connect a full-scale oscillator straight to `dac~`. Insert `gain~` or `*~` with a factor well below 1.
- `gain~` unity is step 128; the slider goes well above unity and will distort.

## Messages, hot inlets, order

- A **bang** means “do it now” with no payload.
- **Left inlet is hot**: it triggers computation using the last values stored in the other (cold) inlets.
- Fan-out without `trigger` fires connections **right to left**. Use `trigger` (`t b i f l s`) when pitch must be set before velocity, or when a list must be packed in a known order.
- `loadbang` / `loadmess` initialize on open. Do not auto-start DSP with `loadmess start` or `loadmess startwindow`; trigger `startwindow` only after the output path and low gain are confirmed and the task covers auditioning.

## Numbers into signals

A float into a signal inlet is generally sampled at the vector rate, which produces zipper noise on amplitude, cutoff, and FM index. Convert or smooth:

- `sig~` — constant signal from a number
- `line~` — ramp to a target in N ms (lists of target-time pairs)
- `curve~` — exponential/curved ramps
- `adsr~` — gated ADSR
- `mtof~` — MIDI note to Hz at signal rate (after `sig~` or another `~`)

Max 9 **ABL** objects additionally apply a short ramp when float attributes change at event rate. Connecting a signal to that inlet disables the attribute and the extra smoothing ([Ableton DSP](https://docs.cycling74.com/userguide/abl/)).

## Max 9 deltas that matter for synths

From [What's New in Max 9](https://docs.cycling74.com/userguide/new_in_max9/) and [9.0.0 notes](https://cycling74.com/releases/max/9.0.0):

- **ABL** — `abl.device.*~` (full Live devices) and `abl.dsp.*~` (oscillators, filters, modulators). Probe before use; they are Max 9 / Ableton DSP package objects.
- **Parameter Connect** — UI to attributes without cords, on ABL, Gen, `jit.fx`, `jit.gl.slab`. Inside `poly~`, use the `param` object.
- **v8 / v8.codebox** — modern JS. Legacy `js` remains ES5.
- **`loudness~`** — EBU R 128 metering (LUFS), not a synth source.
- **Global Record** — toolbar capture of patcher audio.
- **Illustration Mode** — slow-motion event debugging.
- Jitter geometry / `jit.fx` — visuals; ignore unless requested.

Confirm the running version from the user's Max (About Max, or object availability). Do not assume ABL exists: `get_object_doc` on `abl.dsp.basicshapes~` is the check.

## Layout convention

Top to bottom: MIDI/UI → pitch math → oscillators → mix → filter → amplitude envelope → `gain~` → `dac~`. Modulation sources (LFO, second `adsr~`) sit to the side and tap cutoff, pulse width, or FM index. Leave space; overlapping boxes are hard to connect via MCP.
