# Core MSP objects

Inlets are 0-based. Signal cords are striped. Confirm with `get_object_doc` when building an unusual object.

Primary sources: live Max reference via `get_object_doc`, [cycle~](https://docs.cycling74.com/reference/cycle~/), [adsr~](https://docs.cycling74.com/reference/adsr~/), [Filter Tutorial 3](https://docs.cycling74.com/learn/articles/08_filterchapter03/).

## I/O, level, meters

| Object | Role | Inlets | Notes |
|---|---|---|---|
| `dac~` | Hardware out + audio on/off | one per logical channel (default 1–2) | Signal must stay ~[-1, 1]. Messages: `start`, `stop`, `startwindow`. |
| `adc~` | Hardware in | | |
| `ezdac~` / `ezadc~` | Clickable I/O | | Fine for sketches |
| `gain~` | Fader, multiplies signal | audio in | Unity ~128. Goes above unity. |
| `live.gain~` / `mc.live.gain~` | Live-styled / MC | | |
| `meter~` / `levelmeter~` / `scope~` / `spectroscope~` | Meters | | Auto-adapt to MC |
| `loudness~` | EBU R 128 (Max 9) | | Metering, not a source |
| `plugin~` / `plugout~` | Max for Live / plug-in I/O | | |
| `mute~` | Mute a signal branch | | |

## Oscillators and noise

| Object | Sound | Inlets (typical) | Use |
|---|---|---|---|
| `cycle~` | Cosine / wavetable | 0 freq (Hz), 1 phase 0–1 | Default internal 16K cosine. `set` uses first 512 samples of a `buffer~`; `setall` uses the whole buffer. `reset` syncs phase. |
| `saw~` | Anti-aliased saw | 0 freq, 1 sync | Subtractive default. Sync: crossing 0.5 resets (drive with `phasor~`). |
| `tri~` | Anti-aliased triangle | freq, duty, sync | Odd harmonics, softer than square |
| `rect~` | Anti-aliased pulse | 0 freq, 1 duty 0–1, 2 sync | Duty 0.5 = square. Odd harmonics, stronger than triangle. |
| `phasor~` | Ramp 0→1 | freq/time, phase | **Control** oscillator: indexing, grain phase, sync master. Not a band-limited audio saw. |
| `triangle~` / `trapezoid~` | Shaped from a phase | | Waveshape a `phasor~` |
| `train~` | Pulse train | | |
| `click~` | Impulse | | Exciter / click |
| `noise~` | White noise | | Subtractive / percussion |
| `pink~` | Pink noise | | |
| `rand~` | Band-limited random | freq | Less harsh than `noise~` |
| `oscbank~` | Bank of partials | | Additive |
| `wave~` / `2d.wave~` | Buffer wavetable | phase or freq | More flexible than `cycle~` |
| `techno~` | Signal-driven step sequencer | | |

Do not substitute `phasor~` for `saw~` on an audible oscillator. Official analog-style tutorial uses `cycle~`, `tri~`, `saw~`, `rect~` into `lores~`.

## Signal math

| Object | Role | Default gotcha |
|---|---|---|
| `*~` | Multiply (VCA, mix scale, FM index) | **No argument and no right signal ⇒ multiply by 0** |
| `+~` `-~` `/~` | Add / subtract / divide | Mix oscs with `+~`; FM is `+~` into `cycle~` freq |
| `sig~` | Number → constant signal | Pitch glide, DC |
| `abs~` `clip~` `pow~` `log~` `sqrt~` | Shaping | Waveshape / compression |
| `tanh~` `overdrive~` | Saturation | |
| `<~` `>~` `==~` | Audio-rate logic | Pulse from `phasor~` |
| `sah~` | Sample and hold | |
| `delta~` / `change~` | Detect movement | |
| `snapshot~` | Signal → event | Meter numbers; not for audio path |
| `number~` | Signal number box | |
| `send~` / `receive~` | Wireless audio | |
| `gate~` / `selector~` / `matrix~` | Audio routing | |
| `begin~` | Mix bus begin | |

Amplitude envelope: `osc → *~ ← adsr~` (audio in left, envelope in right, or vice versa — both are signals).

## Envelopes, ramps, smoothing

| Object | Role |
|---|---|
| `line~` | Linear ramps. Left: target or `target time` lists (up to 128 pairs). Right: time (ms). Outlet 1 bangs when done. `stop` / `pause` / `resume`. |
| `curve~` | Curved ramps | Percussive decays |
| `adsr~` | ADSR. Args: attack, decay, sustain, release. Inlet 0 trigger: **nonzero = on** (amplitude), **0 = release**. Signal trigger needs a 0 before retrigger. Out 0 envelope; out 1 busy 0/1; out 2 mute messages for `thispoly~`. `@legato`, `@maxsustain 0` for ADR. Times use Max time format. |
| `function` + `line~` | Drawn envelopes | FM index vs amplitude as in [Synthesis Tutorial 5](https://docs.cycling74.com/learn/articles/06_synthesischapter05/) |
| `rampsmooth~` / `slide~` | Smooth incoming values | Portamento, zipper kill |
| `edge~` | Signal 0↔1 → bang | Sync Max events to audio |

## Filters

| Object | Type | Inlets | Outlets |
|---|---|---|---|
| `lores~` | Resonant lowpass | 0 audio, 1 cutoff Hz, 2 resonance 0–1 | filtered. Resonance near 1 clips; `clear` after blow-up. |
| `reson~` | Bandpass | similar | |
| `svf~` | State-variable (Chamberlin) | 0 audio, 1 cutoff Hz (default), 2 Q ~0.01–1 | **0 LP, 1 HP, 2 BP, 3 notch** simultaneously. Modes: `Hz` (default), `linear`, `radians`. Cutoff range in Hz mode: 0 to **¼ sample rate**. `clear` if unstable. |
| `onepole~` | Cheap 6 dB/oct | | |
| `biquad~` | Generic 12 dB biquad | audio + coefficients | Pair with `filtergraph~` or `filtercoeff~` |
| `cascade~` | Series of biquads (up to 24) | | Steeper / multi-peak EQ |
| `filtergraph~` | Visual coeff editor | | Drive `biquad~`/`cascade~` |
| `fffb~` | Parallel resonators | fixed band count | Vocoder / additive-from-noise |
| `comb~` / `allpass~` | Delay-based | | Physical / reverb building blocks |
| `buffir~` | FIR from `buffer~` | | |
| `degrade~` | Bitcrush / downsample | | Lo-fi |

Subtractive default: `saw~` or `rect~` → `lores~` or `svf~` LP. For independent LP/HP morph, `svf~`. For analog-style 24 dB, cascade two `lores~`/`svf~` or use ABL `abl.dsp.meldfilter~` if available.

## Delay, pitch, spectral

| Object | Role |
|---|---|
| `tapin~` / `tapout~` | Variable delay line pair | Must connect `tapin~` → `tapout~` |
| `delay~` | Fixed delay | |
| `pitchshift~` / `retune~` / `freqshift~` | Pitch / frequency shift | |
| `fft~` / `ifft~` / `pfft~` | Spectral | Heavy; mute unused voices |
| `vectral~` | Spectral processing | |

## Buffers and samplers

`buffer~` is named sample memory. Other objects refer to it by name (`cycle~`, `groove~`, `play~`, `wave~`, `lookup~`, `poke~`, `peek~`, `record~`).

| Object | Role |
|---|---|
| `buffer~` | Name + optional file, duration ms, channels. `read` / `replace` / `normalize`. Unique names. |
| `groove~` | Variable-speed player, loops | Sampler / wavetable scan |
| `play~` | Cue-point player | |
| `record~` | Record into buffer | |
| `wave~` | Oscillator from buffer | Wavetable synth |
| `lookup~` | Waveshape via table | |
| `poke~` / `peek~` | Write/read samples | |
| `sfplay~` / `sfrecord~` | Disk streaming | |
| `polybuffer~` | Many buffers | Drum kits |

## Polyphony helpers (MSP side)

| Object | Role |
|---|---|
| `poly~` | N instances of a patcher | See [polyphony-midi-mc.md](polyphony-midi-mc.md) |
| `thispoly~` | Busy + mute from inside a voice | Signal in: nonzero = busy |
| `in~` / `out~` | Signal I/O inside `poly~` | Indexed arguments |
| `in` / `out` | Event I/O inside `poly~` | |
| `mc.*~` | MC wrapper around an MSP object | `@chans` |
| `mcs.*~` | Single instance, multichannel in/out | |
| `gen~` | Compiled Gen DSP | Custom osc, cheap FM, waveshape. Max 9 Parameter Connect supported. |

## MC wrapper (short)

If object `xxx~` exists, `mc.xxx~` is usually N copies in one box with a multichannel cord ([MC Wrapper](https://docs.cycling74.com/userguide/mc/mc_wrapper/)). Exceptions: I/O (`mc.dac~`), some UI meters (auto-adapt), `mcs.*`. Set `@chans` when there is no MC input to adapt from. `deviate`, `setvalue`, `applyvalues` set per-voice parameters.

## Debug DSP

`dspstate~`, `adstatus`, `cpuclock`, `scope~`, `spectroscope~`. If nothing is heard: confirm audio on, `gain~` up, `*~` not at 0, `dac~` not clipped-and-muted by OS, and no other patch stealing `startwindow`.
