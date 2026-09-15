# Max 9 Ableton DSP (ABL)

Sources: [Ableton DSP guide](https://docs.cycling74.com/userguide/abl/), [What's New in Max 9](https://docs.cycling74.com/userguide/new_in_max9/), [Max 9.0.0](https://cycling74.com/releases/max/9.0.0), object pages under `https://docs.cycling74.com/reference/abl.*`.

ABL is a Max 9 package: **10 Live-style devices** (`abl.device.*~`) and **55 DSP macros** (`abl.dsp.*~`). It is not part of classic MSP. If `get_object_doc` on `abl.dsp.basicshapes~` or `abl.device.drift~` fails, skip this file and use [msp-objects.md](msp-objects.md).

## Rules that differ from MSP

- **device vs dsp:** `abl.device.utility~` ≈ Live Utility; `abl.dsp.ramp~` ≈ one Meld modulator; `abl.dsp.shimmer~` ≈ Hybrid Reverb component.
- **Inlet vs attribute:** Many params are attributes *or* signals. A signal on that inlet disables the attribute until disconnected ([guide](https://docs.cycling74.com/userguide/abl/)).
- **Internal smoothing:** Event-rate float attribute changes are ramped (anti-zipper). Signal-rate control is *not* extra-smoothed.
- **Parameter Connect:** UI objects can bind to ABL attributes without cords. Inside `poly~`, expose `param` objects.

## Devices (verified reference pages)

| Object | Role |
|---|---|
| `abl.device.drift~` | Drift synthesizer (voices, analog-style variation) |
| `abl.device.roar~` | Three-stage saturator with LFO/env/noise modulation matrix |
| `abl.device.compressor~` | Compressor (threshold, ratio, attack, release, gain) |
| `abl.device.limiter~` | Limiter / maximizer (ceiling, lookahead, true peak) |
| `abl.device.reverb~` | Reverb, pseudo-stereo from mono |
| `abl.device.utility~` | Gain, mute, mono, imaging, DC |
| `abl.device.redux~` | Downsample / bit reduce |

9.0.0 lists ten devices (Drift, Roar, Compressor, Limiter, Reverb, “and more”). Look up additional names with `list_all_objects` or the [reference](https://docs.cycling74.com/reference/) rather than guessing.

Use devices as **complete instruments or FX** on a bus. For a custom architecture, prefer `abl.dsp.*~` building blocks plus MSP envelopes (`adsr~` still required — ABL oscs do not include a note ADSR).

## DSP oscillators (from `abl.dsp.meldosc~` see-also)

| Object | Role |
|---|---|
| `abl.dsp.meldosc~` | Meld meta-oscillator (many types: Chip, Dual Basic Shapes, Harmonic FM, Swarm*, Sub, …) |
| `abl.dsp.basicshapes~` | Morph sine–tri–saw–pulse; shape-dependent effect (fold / detune / PWM) |
| `abl.dsp.dualbasicshapes~` / `abl.dsp.noisyshapes~` | Dual / noisy shapes |
| `abl.dsp.simplefm~` / `abl.dsp.harmonicfm~` / `abl.dsp.foldfm~` / `abl.dsp.fmbass~` | FM macros |
| `abl.dsp.subosc~` / `abl.dsp.swarm~` / `abl.dsp.chip~` / `abl.dsp.squaresync~` / `abl.dsp.squarefifth~` | Subs, swarms, chip, sync |
| `abl.dsp.filterednoise~` / `abl.dsp.noiseloop~` / `abl.dsp.crackle~` / `abl.dsp.rain~` / `abl.dsp.shepard~` / `abl.dsp.tarp~` / `abl.dsp.bubble~` / `abl.dsp.bitgrunge~` | Noise / special |

`abl.dsp.harmonicfm~` `@ratio` 0–1 fades a **preset ratio set** (not a raw Fm/Fc). Below 0.5 emphasizes subharmonics.

## DSP filters and FX

| Object | Role |
|---|---|
| `abl.dsp.meldfilter~` | Meld filters: comb±, DFM crunch, Filther, SVF 12/24, vowel, phaser, modal plate/membrane, Redux, … |
| `abl.dsp.dfm~` | Analog-modeled lowpass |
| `abl.dsp.filther~` | Distorted lowpass |
| `abl.dsp.saturator~` / `abl.dsp.waveshaper~` | Drive |
| `abl.dsp.shimmer~` | Hybrid-reverb-style shimmer |

## DSP modulators

| Object | Role |
|---|---|
| `abl.dsp.ramp~` | Ramp / transform (clip, fade, slew, …) |
| `abl.dsp.modulator~` / `abl.dsp.wander~` / `abl.dsp.alternate~` | LFOs / wander |
| `abl.dsp.euclid~` / `abl.dsp.pulsate~` | Rhythmic gates |
| `abl.dsp.transform~` | Signal transformer |

These replace some `cycle~` LFO + `scale` graphs. Note envelopes for keyboard voices are still typically `adsr~` or `function`/`line~`.

## When to pick ABL vs MSP

| Goal | Prefer |
|---|---|
| Teach / portable Max 8 patch | MSP only |
| Analog subtractive with PWM/sync | `saw~` `rect~` `lores~` or `abl.dsp.basicshapes~` + `abl.dsp.meldfilter~` |
| Character FM without patching operators | `abl.dsp.simplefm~` / `harmonicfm~` |
| Finished Drift-like instrument | `abl.device.drift~` |
| Custom Chowning ratios and two envelopes | MSP `cycle~` FM ([Tutorial 5](https://docs.cycling74.com/learn/articles/06_synthesischapter05/)) |
