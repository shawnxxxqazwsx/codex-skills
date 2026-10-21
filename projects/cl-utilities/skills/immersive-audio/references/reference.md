# Immersive Audio Practice Reference

Use this file for format selection, production checks, tool choice, and real-time integration. Verify changing software capabilities on the linked official page.

## Contents

- Format matrix
- Ambisonic workflow
- Loudspeaker and binaural rendering
- Production and research tools
- Dolby Atmos workflow
- Game and real-time engines
- Decision guide

## Format matrix

| System | Representation | Common exchange or delivery | Key caution |
|---|---|---|---|
| Ambisonics / HOA | Scene-based spherical harmonics | AmbiX WAV/CAF, ADM HOA, engine-specific assets | File extension does not prove order, normalization, or axes |
| Dolby Atmos | Channel beds and objects | DAMF or ADM BWF masters; platform-specific E-AC-3/JOC, TrueHD, or AC-4 delivery | Production master and consumer encode are different layers |
| MPEG-H 3D Audio | Channels, objects, and HOA | Broadcast and streaming profiles | Name the ISO/profile and platform rather than only "MPEG-H" |
| MPEG-I Immersive Audio | Interactive 6DoF scene | ISO/IEC 23090-4 bitstream and scene metadata | Do not infer 6DoF from ordinary MPEG-H music |
| Sony 360 Reality Audio | MPEG-H object-music ecosystem | Sony-authoring and service delivery workflow | Ecosystem constraints are not a separate ISO codec |
| Auro-3D | Primarily layered channels; Auro-Cx adds NGA modes | Channel masters and Auro-Cx workflows | Check actual WAV map and product generation |
| DTS ecosystems | Object and channel production; MDA and DTS-UHD specifications | Cinema, packaged media, and device-specific delivery | Brand name, authoring metadata, and delivery bitstream are not identical |

## Ambisonic workflow

### Unknown-file checklist

```text
[ ] Determine full or mixed order and expected channel count
[ ] Identify ACN, FuMa, SID, or another channel order
[ ] Identify SN3D, N3D, FuMa, or another normalization
[ ] Identify axes, handedness, azimuth sign, and elevation definition
[ ] Check sample rate, alignment, head orientation, and any near-field compensation
[ ] Convert once into a documented internal convention
[ ] Choose and validate a target-specific decoder
```

Modern interchange defaults to AmbiX, meaning ACN plus SN3D. Use [libambix](https://iem-projects.github.io/ambix/apiref/format.html) or an equivalent tested matrix for conversion. Do not relabel channels manually unless the exact source and destination basis functions are known.

Rotation must use the same coordinate and spherical-harmonic convention as the encoder. Test front, left, up, and a known rotation before trusting automation or tracker data.

## Loudspeaker and binaural rendering

| Target | Useful baseline | Validation |
|---|---|---|
| Irregular loudspeaker layout | AllRAD or another decoder with explicit layout optimization | Speaker coordinates, triangulation, order, energy and localization maps, gain/delay calibration |
| Regular loudspeaker layout | Mode-matching, sampling, AllRAD, or another order-appropriate decoder | Listening-region behavior, timbre, spatial aliasing, and robustness |
| Headphones | MagLS, direct SH least squares, virtual speakers plus HRTFs, or BRIR rendering | HRTF set, order, spectral error, localization, externalization, head tracking, headphone EQ |

The [IEM AllRADecoder guide](https://plugins.iem.at/docs/allradecoder/) documents layout construction and the order/localization tradeoff. The [IEM BinauralDecoder description](https://plugins.iem.at/docs/plugindescriptions/) documents its MagLS path and fixed KU100 HRTFs. These are strong reproducible baselines, not proof that the same decoder is best for every experiment.

## Production and research tools

| Tool | Use | Official page |
|---|---|---|
| IEM Plug-in Suite | Ambisonic encoding, rotation, effects, AllRAD, and MagLS rendering | [plugins.iem.at](https://plugins.iem.at/) |
| SPARTA | Linear and parametric Ambisonic tools, including COMPASS-related workflows | [SPARTA](https://leomccormack.github.io/sparta-site/) |
| libambix | AmbiX file and adaptor-matrix support | [format reference](https://iem-projects.github.io/ambix/apiref/format.html) |
| pyfar | Python acoustics analysis | [pyfar](https://pyfar.org/), [documentation](https://pyfar.readthedocs.io/) |
| sofar | Read, write, and validate SOFA files in Python | [sofar documentation](https://sofar.readthedocs.io/) |
| SOFA conventions | File conventions for HRTF, BRIR, and related data | [sofaconventions.org](https://www.sofaconventions.org/) |

Inspect the installed tool version and documentation before generating a command or project file. Do not assume a plug-in supports a bus order simply because another tool in the same suite does.

## Dolby Atmos workflow

1. Define the intended deliverable: cinema, episodic, music streaming, game, packaged media, or another profile.
2. Route stable channel content to appropriate beds and individually positioned or moving content to objects when that improves the render.
3. Remember that objects do not expose a discrete LFE channel. Decide between spectral content, bed LFE, and monitoring-system bass management deliberately.
4. Monitor the renderer outputs needed by the deliverable and verify downmix and binaural metadata behavior.
5. Export the required master, then validate the separate encoding and platform step.

Use the [Dolby content-creator overview](https://professional.dolby.com/content-creation/Dolby-Atmos-for-content-creators/) and the current support documentation for the exact renderer and master format. Avoid copying a cinema object count into a game or consumer-endpoint design.

## Game and real-time engines

Unity's current public Ambisonic framework supports first-order sources, prefers ACN/SN3D, and requires a selected third-party or custom decoder rather than providing a built-in decoder by default. Verify against the [current Unity manual](https://docs.unity3d.com/Manual/AudioDevelopAmbisonicDecoder.html) because engine versions change.

[Steam Audio's Unity guide](https://valvesoftware.github.io/steam-audio/doc/unity/guide.html) describes first-order AmbiX clips, Ambisonic source handling, and supported SOFA constraints. Do not assume that arbitrary SOFA conventions are accepted by a runtime merely because the file parses in a research library.

For any engine:

- Test coordinate conversion with known directions.
- Separate point-source spatialization from an Ambisonic ambient bed.
- Budget tracker-to-audio latency and interpolate orientation safely.
- Define listener translation, room transitions, occlusion, and reverb behavior.
- Verify speaker, binaural, and fallback endpoints independently.

## Decision guide

```text
Rotate a captured or authored scene with head tracking -> Ambisonics / HOA
Place independent moving elements for a branded cinema or home workflow -> Atmos objects plus suitable beds
Combine channels, objects, HOA, and broadcast personalization -> MPEG-H profile
Build a walkable interactive acoustic scene -> MPEG-I or an equivalent 6DoF engine model
Deliver object-based immersive music in Sony's ecosystem -> 360 Reality Audio / MPEG-H workflow
Produce a fixed layered-channel master -> classic Auro-3D or another channel format
Compare open music arrays -> 3D-MARCo or ECHO
Compare receivers under controlled sources -> TU Berlin loudspeaker orchestra
Study ecological HOA scenes -> ARTE or EigenScape
Train real-scene SELD -> STARSS23
Convolve broadcast rooms or compare BRIR paths -> WDR spatial IRs
```

For ESMA-3D and PCMA-3D, use their channel-array design goals. Do not promise arbitrary Ambisonic rotation unless an explicit scene encoding step is added and evaluated.
