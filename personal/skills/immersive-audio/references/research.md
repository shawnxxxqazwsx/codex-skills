# Immersive Audio Research Concepts

Use this file to frame a research question and choose evidence. Prefer causal language and state experimental conditions; perceptual outcomes rarely follow from a format name alone.

## Contents

- Localization, externalization, and immersion cues
- Binaural rendering
- WFS and HOA
- Subjective and objective evaluation
- Spherical arrays and HOA limits
- Parametric spatial audio
- MPEG-I 6DoF
- Terminology

## Localization, externalization, and immersion cues

| Cue or attribute | Research role | Caution |
|---|---|---|
| Interaural time difference | Strong lateral cue, especially at lower frequencies | The duplex theory is a useful approximation, not a hard crossover rule |
| Interaural level difference | Lateral cue shaped by head shadow and frequency | Depends on source spectrum and individual anatomy |
| Pinna and torso spectra | Elevation and front-back discrimination | Generic HRTFs can create spectral mismatch for an individual listener |
| Dynamic head motion | Disambiguates front/back and stabilizes the auditory world | Requires correct latency, coordinate transforms, and head-tracker integration |
| Early reflections and reverberation | Distance, room impression, and externalization | A room response alone does not guarantee externalization |
| Interaural coherence and lateral energy | Apparent source width and listener envelopment | Metric-to-percept mapping depends on time, band, content, and reproduction |
| Precedence effect | Fusion and localization in reflections | Delay, level, spectrum, and scene context matter |

Do not write that externalization simply "needs room plus individualized cues." It is influenced by HRTF match, headphone equalization, reverberation, head tracking, visual context, and listener adaptation, with different contributions across studies.

Good foundations are Blauert's *Spatial Hearing*, Begault's open NASA text, and current binaural reviews in [papers.md](papers.md).

## Binaural rendering

### Definitions

- An HRTF or HRIR describes direction-dependent transfer from a source in a specified acoustic condition to a listener's ears.
- A BRIR is a binaural room impulse response from a source or loudspeaker to both ears in a room. It contains source, listener, and room effects; it is not merely an HRTF label with reverb added.
- A directional room impulse response or spherical-microphone-array room response retains directional information that can be encoded or rendered in different ways.
- A SOFA file is a container governed by a convention. Inspect the convention, coordinate metadata, listener/source geometry, sampling rate, and data dimensions before using it.

### Ambisonic-to-binaural choices

| Approach | Idea | Tradeoff |
|---|---|---|
| Virtual loudspeaker decode plus HRTFs | Decode to a chosen speaker grid, then binauralize each virtual speaker | Simple and inspectable; result depends on grid, decoder, order, and HRTF sampling |
| Direct SH-domain least squares | Fit binaural filters in the spherical-harmonic domain | Compact direct path; order truncation and regularization shape timbre and localization |
| MagLS | Optimize complex response at lower frequencies and magnitude behavior above a transition region | Better high-frequency spectral fit at limited order; phase treatment must be described from the method, not reduced to "delete phase" |
| Order-truncation equalization | Compensate average spectral effects of missing spherical-harmonic orders | Can improve timbre but does not recover missing spatial detail |
| Measured or simulated BRIR path | Reproduce a specific room or loudspeaker setup binaurally | Useful for auralization; personalization and head movement remain separate questions |

Select the renderer with evidence from the target HRTF set, Ambisonic order, head tracking, latency budget, and perceptual goal. IEM's BinauralDecoder is a practical MagLS implementation using a fixed dummy-head HRTF set; it is not personalized by default. See the [IEM plug-in description](https://plugins.iem.at/docs/plugindescriptions/).

## WFS and HOA

Both WFS and HOA can be derived as sound-field synthesis methods, but they choose different representations and spatial sampling.

| Dimension | WFS | HOA / Ambisonics |
|---|---|---|
| Mathematical view | Approximate the Kirchhoff-Helmholtz boundary integral with distributions of secondary sources | Expand the field in circular or spherical harmonics and reproduce a finite set of modes |
| Common arrays | Dense enclosing, linear, or planar loudspeaker distributions, depending on dimensionality | Circular or spherical arrays, or irregular layouts with a decoder |
| Valid region | Extended region in the ideal continuous formulation; discretization creates aliasing and truncation artifacts | Order-limited region around the expansion center; decoder and layout alter practical behavior |
| Main limits | Loudspeaker sampling, array geometry, truncation, source model, room | Truncation order, listener radius/frequency, decoder, layout, and room |

Use [Spors and Ahrens' comparison](https://www.int.uni-rostock.de/fileadmin/user_upload/publications/spors/2008/AES125_Spors_WFS_HOA.pdf) before making broad claims about sweet area or aliasing. WFS is not a delivery branding synonym for Atmos or DTS:X.

## Subjective and objective evaluation

### Subjective methods

| Method | Intended use | Official source |
|---|---|---|
| ITU-R BS.1116 | Double-blind assessment of small impairments using trained listeners and tightly controlled conditions | [ITU series](https://www.itu.int/rec/R-REC-BS.1116/en) |
| ITU-R BS.1534 / MUSHRA | Multi-stimulus assessment of intermediate audio quality with a hidden reference and anchors | [ITU series](https://www.itu.int/rec/R-REC-BS.1534/en) |
| Attribute elicitation and rating | Discover and compare attributes such as width, envelopment, depth, naturalness, or locatedness | Choose a published method appropriate to the content and population |

Do not choose BS.1116 or MUSHRA only because the acronym is familiar. Define the hypothesis, attribute, reference, anchor, listener expertise, training, room, reproduction system, randomization, repetitions, and statistical plan.

### Objective descriptors

Common descriptors in array and rendering studies include:

- Interchannel crosstalk or separation
- Time-varying interaural level and time differences
- Interchannel or interaural correlation
- Direct-to-reverberant ratio
- Localization error, source width, spectral deviation, and energy-vector behavior

The [3D-MARCo objective study](https://doi.org/10.17743/jaes.2021.0038) is a useful example. Never turn a single descriptor into a universal quality score. Validate that the descriptor predicts the perceptual attribute under the tested conditions.

## Spherical arrays and HOA limits

For a complete three-dimensional expansion, order `N` contains `(N + 1)^2` components. A microphone with `Q` capsules cannot recover more than `Q` independent channels, but capsule count alone does not establish a usable acoustic order.

Practical limits include:

- Array radius and the frequency-dependent radial transfer functions
- Spatial sampling and aliasing
- Capsule position and directivity errors
- Sensor self-noise and low-frequency radial-filter amplification
- Calibration, regularization, equalization, and robustness to mismatch
- Scattering from rigid versus open array structures

The 32-capsule Eigenmike is commonly used for complete fourth-order output, and the 19-capsule Zylia ZM-1 for complete third-order output, but verify the actual manufacturer or dataset encoder and do not infer quality from nominal order alone.

Encoding means applying an array model and regularized filters to raw capsule signals. The resulting HOA stream still needs an explicit ordering, normalization, coordinate convention, and frequency validity range.

## Parametric spatial audio

| Method | Model | Use |
|---|---|---|
| DirAC | Estimate direction and diffuseness in time-frequency regions, then synthesize for the target reproduction | Low-order capture enhancement and flexible rendering |
| Sector or SH-domain analysis | Analyze directional sectors or spatial covariance in a spherical-harmonic basis | Higher-order decomposition and spatial filtering |
| COMPASS | Estimate multiple directional components and a non-isotropic ambient residual | Sharper or more editable rendering of Ambisonic or array scenes |

Primary starting points are the [Politis thesis](https://aaltodoc.aalto.fi/handle/123456789/22499), [COMPASS paper](https://doi.org/10.1109/ICASSP.2018.8462608), [SPARTA project](https://leomccormack.github.io/sparta-site/), and [COMPASS reference code](https://github.com/polarch/COMPASS-ref).

Parametric analysis is not an interchange convention. Document whether output remains a linear Ambisonic scene, a synthesized loudspeaker feed, a binaural render, or a proprietary parameter stream.

## MPEG-I 6DoF

[ISO/IEC 23090-4:2025](https://www.iso.org/standard/84711.html) specifies technology for real-time interactive rendering while the user moves with six degrees of freedom. It defines scene and acoustic metadata plus a bitstream syntax. A [Fraunhofer overview](https://www.iis.fraunhofer.de/content/dam/iis/en/doc/ame/Whitepaper/mpeg-i/MPEG-I_Immersive_Audio%E2%80%94The_ISO_MPEG_Standard_for_Virtual_Augmented_Reality_Audio.pdf) provides accessible context.

- 3DoF usually means head orientation at a fixed position.
- 6DoF adds translation through the scene.
- A renderer may need geometry, source extent, occlusion, diffraction, room and material properties, and level-of-detail behavior.
- MPEG-H audio coding can be part of the waveform path, but an MPEG-H music stream by itself is not a 6DoF scene.

## Terminology

| Term | Concise meaning |
|---|---|
| AmbiX | ACN ordering plus SN3D normalization for Ambisonic interchange |
| FuMa | Legacy B-format channel order and weights, mainly first order |
| AllRAD | Ambisonic loudspeaker decoder using a virtual regular layout and VBAP |
| MagLS | Magnitude least-squares Ambisonic binaural rendering family |
| DRR | Direct-to-reverberant ratio; use 直达声/混响声比 in Chinese |
| ADM / S-ADM | Audio Definition Model / Serial ADM |
| IAB | Immersive Audio Bitstream under SMPTE ST 2098-2 |
| SMA | Spherical microphone array |
| SELD | Sound event localization and detection |
| 3DoF / 6DoF | Rotational freedom / rotational plus translational freedom |

Avoid presenting "高阶立体声" as a universal Chinese translation of Ambisonics. Keep `Ambisonics` or `高阶 Ambisonics` and explain it as a spherical-harmonic scene representation when terminology matters.
