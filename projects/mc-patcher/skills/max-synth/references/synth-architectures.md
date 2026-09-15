# Synthesizer architectures in Max

Build the voice as a short signal chain, then wrap it for MIDI/polyphony. Official tutorials: [Filter 3 analog oscs](https://docs.cycling74.com/learn/articles/08_filterchapter03/), [Filter 4 subtractive](https://docs.cycling74.com/learn/articles/08_filterchapter04/), [FM Tutorial 5](https://docs.cycling74.com/learn/articles/06_synthesischapter05/), [MIDI synth](https://docs.cycling74.com/learn/articles/10_midichapter02/).

## Subtractive (default)

Rich osc → filter → amp envelope.

```text
mtof → saw~ ──┐
mtof+detune → saw~ ─► +~ → lores~ / svf~(LP) → *~ ← adsr~ ← velocity
rect~ (PWM from LFO) ─┘
```

- Oscillators: `saw~` (all harmonics), `rect~` (odd, PWM), `tri~` (odd, weak), `cycle~` (almost no filter effect until cutoff < f0).
- Mix with `+~` then scale with `*~ 0.5` so two oscs stay in range.
- Filter: `lores~` cutoff + resonance 0–1; or `svf~` and take outlet 0 (LP). Modulate cutoff with a second `adsr~` or `cycle~` LFO (`*~` depth, `+~` base).
- Hard sync: `phasor~` at fundamental into `saw~`/`tri~`/`rect~` sync inlet; sweep slave frequency higher ([Filter Tutorial 3](https://docs.cycling74.com/learn/articles/08_filterchapter03/)).
- Noise: `noise~` or `pink~` → `lores~` with LFO on cutoff ([Filter Tutorial 4](https://docs.cycling74.com/learn/articles/08_filterchapter04/)).

## FM

Cycling '74 follows Moore: **harmonicity ratio = Fm / Fc**, **index = Am / Fm**. Sidebands at Fc ± k·Fm. Integer ratio → harmonic; non-integer → bells/drums. Envelope the **index** for brightness ([Tutorial 5](https://docs.cycling74.com/learn/articles/06_synthesischapter05/)).

```text
Fc ──────────────► +~ ──► cycle~ (carrier) ──► *~ ← amp adsr~
                    ▲
Fm = Fc * ratio     │
cycle~(Fm) → *~ ← (index * Fm)   // Am = index * Fm
```

Keep carrier and modulator as `cycle~` for Chowning-style predictability. Complex carriers are valid but less theoretically clean.

Max 9 shortcuts if ABL is installed: `abl.dsp.simplefm~`, `abl.dsp.harmonicfm~`, `abl.dsp.foldfm~`, `abl.dsp.fmbass~`.

## AM / ring modulation

```text
cycle~(Fc) → *~ ← cycle~(Fm)
```

For unipolar AM, scale modulator to 0–1 (`*~ 0.5`, `+~ 0.5`) then multiply. Ring mod (bipolar modulator) yields sum and difference frequencies only.

## Wavetable

- `cycle~` + named `buffer~` (`set` = first 512 samples; `setall` = entire buffer).
- `wave~` / `2d.wave~` for variable table size and 2D morph.
- Fill tables with `buffer~ fill sin`, or load files. Scan with `phasor~` into `wave~` for classic WT; use `line~` on start/end for positional morph.
- Anti-aliasing is the user's problem if the table is bright and f0 is high; consider `poly~` `up 2` or band-limited tables.

## Additive

N × `cycle~` with harmonic frequencies (`*~` 2, 3, …) and per-partial `*~` amplitudes from `line~` or `adsr~`. `oscbank~` or `mc.cycle~ @chans N` with `deviate` / `applyvalues` is the compact form. Expensive: mute unused partials or use `pfft~` only when needed.

## Sampler / granular-ish

`buffer~` + `groove~` (pitch via playback rate) or `play~`. Envelopes still via `adsr~` × `*~`. For looping noise grains, Max 9 `abl.dsp.noiseloop~` / `abl.dsp.extratone`-style `meldosc~` types if available.

## Physical / modal

`click~` or noise burst → `reson~` / `fffb~` / `comb~`. ABL: `abl.dsp.meldfilter~` membrane/plate resonator types when installed.

## Control layer (all architectures)

| Job | Objects |
|---|---|
| Keyboard | `notein`, `kslider` |
| Hz | `mtof` or `sig~` → `mtof~` (glide: `line~` on MIDI then `mtof~`) |
| Amp env | `adsr~` or `function` → `line~` |
| Filter env | second `adsr~` or `function` |
| LFO | `cycle~` at 0.1–20 Hz, or `phasor~` + shaping. Reset phase with MIDI start (`rtin` 250) as in MIDI Tutorial 2. |
| Pitch bend | `bendin` → `scale` to semitones → `+~` on MIDI then `mtof~` |
| Mod wheel | `ctlin 1` → `scale` → LFO depth or index |

Velocity: scale 0–127 to 0–1 exponentially when possible (`scale` or `expr pow($f1/127., 2)`), then into `adsr~` trigger so loud notes are taller envelopes ([MIDI Tutorial 2](https://docs.cycling74.com/learn/articles/10_midichapter02/)).

## Hybrid / Max 9

Use MSP for the voice you understand; drop in ABL macros for character (Meld osc/filter, Drift device) only after `get_object_doc` succeeds. `gen~` for one custom operator (cheap FM, analog-style tanh, formant) without leaving the audio graph.

## Always-on checklist

- [ ] Attenuation before `dac~`
- [ ] `*~` has a non-zero scale
- [ ] Cutoff/index/PWM are signals or ramped
- [ ] Note-off reaches the same voice (`poly~` + `thispoly~` or `poly`+`route`)
- [ ] Resonance and FM index cannot sit at maximum without a limiter/`clip~`/`gain~`
