# Hardware-emulation plug-in type map

Use this map to scope an unfamiliar device. It is a starting checklist, not proof that every listed mechanism exists in a specific unit.

## Equalization and filtering

| Type | Characteristic mechanisms | Measure/model | Common false shortcut |
|---|---|---|---|
| Parametric/console EQ | cascaded or parallel bands, constant/proportional Q, stepped controls, op-amp/transformer stages | complex response across combined controls and levels; control law; headroom per stage | matching isolated magnitude curves only |
| Passive program EQ | LC network, simultaneous boost/cut interaction, insertion loss, tube/solid-state makeup | source/load, interaction grid, phase, makeup-stage distortion | independent shelf filters plus generic tube |
| Baxandall/shelving tone control | feedback/passive shelf interaction and broad curves | boost/cut asymmetry, midpoint, load, phase | two unrelated RBJ shelves |
| Graphic EQ/filter bank | overlapping bands, tolerances, summing topology | combined-band ripple, band interaction, noise, phase | fitting every band independently |
| Tone stack | source/load-dependent passive network, nonlinear stages around it | full circuit loading and drive states | one static IR for all controls |
| Wah/auto-wah/envelope filter | time-varying resonant filter, pedal law or envelope detector, transistor/inductor behavior | control trajectory, Q, feedback, level dependence | LFO sweep of a clean biquad |
| Crossover/isolator/rotary mixer | complementary filters, phase, summing, kill/boost law | reconstruction sum, phase, control transitions | magnitude-only split |

## Colour, preamps, consoles, and summing

| Type | Characteristic mechanisms | Measure/model | Common false shortcut |
|---|---|---|---|
| Mic/line/instrument preamp | input/output transformer or electronically balanced stage, impedance, gain staging, rails, noise | gain positions, source/load, level/frequency, EIN/noise, overload/recovery | one waveshaper at nominal gain |
| Channel strip | ordered preamp, filters, EQ, dynamics, insert, output stage | interstage level and combined controls | separate “vintage” blocks with wrong order |
| Console channel/bus | channel amplifier, pan law, summing impedance, bus amp, crosstalk, shared supply/transformers | single and multi-channel drive, pan, crosstalk matrix, channel variance | saturating each channel identically then summing |
| Transformer/line colour | hysteresis, saturation, parasitics, loading, LF memory | multi-level H/IMD, impedance, phase, history | static tanh plus low shelf |
| Tube colour/valve line amp | bias, asymmetric transfer, feedback, supply, output transformer | multiple levels/frequencies, transfer both directions, recovery | “more H2” |
| Discrete op-amp/API-style stage | feedback, rails, slew, output drive, transformer option | level-frequency grid, transient recovery, load | soft clip after flat gain |
| Exciter/enhancer/vitalizer | dynamic high-frequency generation, phase/filter interaction, coupled controls | multitone, envelope, transient, control interaction | fixed high shelf and distortion |

For console/summing claims, test whether crosstalk and saturation occur before or after summing, whether bus behavior depends on active channel count, and whether random channel tolerances are measured.

## Dynamics

| Type | Characteristic mechanisms | Measure/model | Common false shortcut |
|---|---|---|---|
| VCA compressor/limiter | detector/ballistics plus VCA gain cell, often feedforward | static curve, attack/release, sidechain, gain-cell distortion | one generic compressor curve |
| FET compressor | feedback topology, FET gain reduction, amplifier/transformer coloration | program dependency, ratio modes, all-buttons states, recovery | fast VCA with saturation |
| Opto leveler/compressor | lamp/LED and photoresistor memory, multi-stage release | long history, light-dependent rise/decay, silence recovery | fixed dual-time-constant release |
| Vari-mu/tube compressor | tube bias and variable gain, transformers, feedback | level-dependent ratio/knee, harmonics during gain reduction | waveshaper after digital compression |
| Diode-bridge compressor | nonlinear bridge in control/audio path, transformers | bias, distortion versus gain reduction, attack/release | clean gain computer |
| PWM/FET/OTA limiter | switching or device-specific gain control | carrier/switch artifacts, control law, alias plan | interpolated gain only |
| Gate/expander | detector hysteresis, hold, range, floor, chatter behavior | threshold sweeps, bursts, release, key filter | hard binary gate |
| De-esser/dynamic EQ | split-band or wideband detection, crossover, detector | frequency/level matrix, band recombination phase | static notch |
| Transient designer | fast/slow envelope comparison, nonlinear control map | transient/decay families, stereo link | high-pass sidechain compressor |

## Distortion and nonlinear creative effects

| Type | Characteristic mechanisms | Measure/model | Common false shortcut |
|---|---|---|---|
| Overdrive/distortion/fuzz | pre/post filters, diode/BJT/op-amp feedback, bias and recovery | transfer, H/IMD, control grid, guitar impedance | bare tanh/clip |
| Rectifier/octaver | switching/rectification, filters, tracking | subharmonics, zero crossings, aliasing | absolute value only |
| Wavefolder | piecewise folds, asymmetric stages, filtering | fold transitions, high-order alias, control law | modulo function without AA |
| Ring modulator | diode bridge/multiplier balance, carrier leakage, transformers | sidebands, leakage, level/control | ideal multiplication |
| Bit crusher/early digital | quantizer, sample/hold clock, converter filters, truncation/dither | code transfer, clock, reconstruction, noise | reduce bit depth/sample rate abstractly |
| Clipper/limiter hardware | diode/rail topology, overshoot and recovery | intersample behavior, pulse response, THD/IMD | memoryless threshold |

## Magnetic and recording media

| Type | Characteristic mechanisms | Measure/model | Common false shortcut |
|---|---|---|---|
| Reel/cassette tape recorder | record/play filters, bias, hysteresis, head losses, transport, hiss | level/speed/bias grid, delay trajectory, noise | head bump plus soft clip |
| Tape echo | magnetic record/play plus moving transport, multiple heads, feedback electronics | pitch response to speed change, feedback decay, head paths | modulated digital delay |
| Wire recorder | magnetic medium, head and transport limits | level/speed response, noise, time variance | tape preset with different EQ |
| Vinyl/disc/cutting chain | RIAA/pre-emphasis, cutter/playback mechanics, tracing distortion, eccentricity, surface noise | inner/outer groove, level, channel, speed, noise events | EQ plus crackle sample |
| Optical film/sound-on-film | optical modulation, bandwidth, nonlinear light/sensor, transport | transfer, modulation, noise, wow/flutter | lo-fi bandpass |

## Delay and modulation

| Type | Characteristic mechanisms | Measure/model | Common false shortcut |
|---|---|---|---|
| BBD delay | variable-rate analog sampling, fixed stages, filters, compander, clock artifacts | clock/delay relation, insertion loss, noise, distortion, feedback | fractional delay with LFO |
| Early digital delay | ADC/DAC, fixed-point memory, companding, clock, reconstruction | quantization, rate, filters, overflow, modulation | clean modern delay |
| Chorus/flanger/vibrato | modulated BBD/delay, feedback, stereo LFO, compander | time-varying transfer and control trajectory | sine-LFO fractional delay |
| Phaser | cascaded time-varying all-pass stages, nonlinear control elements, feedback | notch trajectories, phase, LFO, level | moving notch EQ |
| Tremolo/vibrato amp | bias modulation or optical gain element | envelope shape, level dependency, asymmetry | multiplying by a sine |
| Rotary/Leslie | Doppler, amplitude/directivity modulation, crossover, horn/drum inertia, room/mics | speed ramps, stereo geometry, spectral modulation | stereo autopan plus chorus |
| Scanner vibrato/chorus | electromechanical tap scanner and LC ladder | interpolation, tap law, scanner trajectory | ordinary chorus |

## Reverberation and resonators

| Type | Characteristic mechanisms | Measure/model | Common false shortcut |
|---|---|---|---|
| Spring reverb | dispersive torsional/longitudinal modes, transducers, drive electronics | dispersion, decay by frequency, shock, drive | one generic IR |
| Plate/foil/gold-foil | dense 2D modes, damping, pickup positions, preamp | modal density, decay, geometry, drive | algorithmic hall preset |
| Chamber/room/echo chamber | source/loudspeaker, room, mic positions and electronics | multichannel IR, level, air/room change | mono convolution only |
| Early digital reverb | fixed-point algorithm, modulation, quantization, bandwidth | topology, word length, time variation | modern FDN with dark EQ |
| Resonator/filter hardware | feedback network, modal losses, nonlinear drive | impulse decay, stability, drive | static comb filter |

## Amplifiers, speakers, microphones, and radios

| Type | Characteristic mechanisms | Measure/model | Common false shortcut |
|---|---|---|---|
| Guitar/bass amplifier | cascaded gain stages, tone stack, phase inverter, power supply, transformer, speaker load | stage/control/level grid, load interaction | one neural snapshot with no controls |
| Cabinet/speaker | motor/suspension/cone/cabinet, electrical back-EMF, thermal memory, mic/room | multi-level electrical/acoustic response | IR equals full cabinet |
| Microphone | capsule mechanics, polar pattern, transformer/FET/tube electronics, proximity | angle, distance, SPL, impedance, self-noise | on-axis EQ |
| Ribbon microphone | ribbon mechanics, transformer, preamp loading | angle, SPL, load, LF excursion | dark EQ |
| Carbon/telephone/radio | granular contact nonlinearity, band limits, AGC, modulation/demodulation, noise | level, envelope, carrier/channel, noise | bandpass plus distortion |
| Megaphone/PA/intercom | transducer resonance, limiter, acoustic feedback, horn | SPL/angle/distance, limiter, enclosure | telephone EQ |

## Synthesizer and electromechanical instrument circuits

| Type | Characteristic mechanisms | Measure/model | Common false shortcut |
|---|---|---|---|
| Analog oscillator | discontinuous waveform, temperature/tuning drift, sync, FM, waveshaping | pitch/control map, spectrum, reset, drift | naive saw/square |
| VCF | nonlinear OTA/diode/transistor ladder, resonance feedback, self-oscillation | cutoff/resonance/level grid, stability, alias | clean biquad plus tanh |
| VCA/ring mod | OTA/transistor/device law and control feedthrough | control/audio matrix, leakage, noise | ideal multiply |
| Envelope/LFO | capacitor charge/discharge, retrigger, control bleed | segment law, level/time dependence, reset | linear digital ramp |
| Low-pass gate | vactrol memory couples amplitude and spectrum | history, strike response, control | low-pass and VCA with shared knob |
| Tonewheel/organ/chorus | electromechanical generation, leakage, scanner, LC network | drawbars, key click, leakage, scanner | additive synth plus chorus |

## Conversion, clock, and playback chains

| Type | Characteristic mechanisms | Measure/model | Common false shortcut |
|---|---|---|---|
| Vintage ADC/DAC | converter architecture, analog filters, code errors, clipping, dither/noise | code/level response, impulse, jitter sensitivity, filters | bit-depth reduction |
| Sampler/workstation | converter plus resampler, interpolation, memory word length, analog I/O | pitch/rate, reconstruction, truncation, voice path | sample-rate reduction only |
| Codec/compander | analysis/synthesis bands, quantization, bit allocation, error concealment | rates, transients, cascades, noise | static spectral loss |
| Clock/jitter effect | sampling-time variation and clock spectrum | clock-correlated sidebands under controlled conditions | random pitch modulation |
| Phono/tape playback preamp | equalization, overload, source impedance, noise | cartridge/head load, level, phase | RIAA/EQ curve only |

## Scope questions before implementation

For any type answer:

1. Is the target a specific unit/revision, a family, or an inspired processor?
2. Which parts are included: electronics, transducer, medium, room, converter, noise?
3. Which controls and time-varying trajectories must remain editable?
4. Which channel interactions are intentional?
5. Is the evidence linear-only, single-level nonlinear, multilevel behavioral, or circuit-complete?
6. What is explicitly excluded?
7. Which hosted and realtime paths must pass?

Use [modeling-strategy.md](modeling-strategy.md) to select the model and [measurement-and-identification.md](measurement-and-identification.md) to design the capture.
