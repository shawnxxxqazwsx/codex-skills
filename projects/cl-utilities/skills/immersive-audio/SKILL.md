---
name: immersive-audio
description: Analyze and plan spatial-audio formats, conventions, recording, rendering, evaluation, delivery, standards, papers, and datasets across channel-, object-, scene-, and sound-field-based systems. Use when a request has a spatial or immersive audio component; do not trigger for generic audio work or general paper searches.
---

# Immersive Audio

Keep paradigms separate, make signal conventions explicit, and support changeable claims with current primary sources.

## Route the request

Read this file first, then read each relevant reference file completely. Select only the files needed for the request.

| Need | Read |
|---|---|
| Books, surveys, foundational papers, reading path | [references/papers.md](references/papers.md) |
| Codec, bitstream, ADM, Atmos, Auro, DTS, 360RA, AmbiX standards | [references/specs.md](references/specs.md) |
| Open recordings, array comparisons, IRs, SELD corpora | [references/corpora.md](references/corpora.md) |
| Psychoacoustics, binaural, WFS, evaluation, arrays, DirAC/COMPASS, MPEG-I | [references/research.md](references/research.md) |
| Practical format choices, production tools, games, conversion checklist | [references/reference.md](references/reference.md) |

## Verify sources

- Browse before stating a current standard edition, renderer or codec limit, product capability, dataset availability, license, or delivery requirement.
- Prefer the current ITU, ISO, ETSI, SMPTE, EBU, Dolby, Fraunhofer, manufacturer, DOI, or dataset landing page. Cite the exact page that supports the claim.
- Treat vendor white papers as architecture or workflow evidence, not as neutral comparisons.
- Label paywalled AES, IEEE, SMPTE, and ISO material honestly. Do not imply that a source was fetched in the current task unless it was.
- Keep stable mathematics separate from time-sensitive implementation limits.

## Resolve the paradigm first

| Paradigm | Representation | Typical examples |
|---|---|---|
| Channel-based | Signals are bound to a reproduction layout | 5.1, 7.1.4, classic Auro layers |
| Object-based | Audio essence plus rendering metadata such as position, extent, and gain | Dolby Atmos objects, 360RA objects |
| Scene-based | A sound field represented with spherical-harmonic coefficients | Ambisonics / HOA |
| Sound-field synthesis | A physical field is reconstructed with distributed secondary sources | WFS research systems |

Do not treat an object as necessarily dry, HOA as a fixed speaker layout, or WFS as another Atmos brand.

## Core invariants and cautions

1. A complete three-dimensional Ambisonic order `N` has `(N + 1)^2` channels; FOA has four.
2. Modern AmbiX interchange means ACN channel order plus SN3D normalization. Confirm ordering, normalization, coordinate system, handedness, and channel count before combining files from different tools.
3. Convert FuMa, N3D, SID, or other conventions explicitly. Never silently mix them.
4. AllRAD is a strong loudspeaker-decoder baseline and MagLS is a strong binaural baseline, not a universal mandate. Choose a decoder from the array geometry, order, listening region, HRTF set, latency, and evaluation goal.
5. Dolby Atmos supports channel beds and audio objects. Objects do not have a discrete LFE channel; low-frequency energy in an object can still reach subwoofers through bass management. Distinguish the production master from consumer delivery.
6. Home Atmos may use E-AC-3 with JOC, but TrueHD and AC-4 are also relevant delivery paths. State the platform and deliverable.
7. MPEG-H 3D Audio carries channels, objects, and HOA. MPEG-I Immersive Audio adds a six-degree-of-freedom interactive scene and renderer model; ordinary MPEG-H music is not thereby 6DoF.
8. ADM, S-ADM, and IAB occupy different exchange layers. Name the exact recommendation or standard and the carriage context.

## Work method

1. State the playback target: loudspeakers, headphones, engine, broadcast chain, cinema, or 3DoF/6DoF XR.
2. Name the representation and convention: channel/object/scene/WFS, then AmbiX, ADM profile, Atmos master, or other concrete format.
3. Trace capture or authoring, exchange, rendering, and delivery as separate stages.
4. Identify the fragile assumptions: coordinate system, normalization, array order, decoder, HRTF/BRIR, head tracking, seat, room, or codec profile.
5. Recommend a reproducible pipeline or research anchor and include verification steps.
6. Cite current primary sources for mutable facts and foundational papers for theory.

## Evaluation discipline

- Specify the perceptual attribute instead of saying only "more immersive": localization, externalization, source width, listener envelopment, coloration, timbre, or quality impairment.
- Specify loudspeaker versus headphone playback, listener position, head tracking, room, and population.
- Use BS.1116 for subtle impairments and BS.1534/MUSHRA for intermediate-quality comparisons only when the test design fits their assumptions. See [references/research.md](references/research.md).
- Do not rank microphone arrays from a single metric. Combine controlled listening with relevant objective descriptors.
- For sample-level comparison of original, reference, and candidate renders, use
  `$audio-render-forensics` only after representation, channel convention,
  decoder/renderer, HRTF, routing, and output format are fixed and comparable.

## Response shape

Lead with the format and feasibility conclusion. Then give the recommended chain, convention checks, risks, and cited evidence. Match the user's language; define specialist abbreviations on first use.

## Reject these mistakes

- Equating Atmos objects with Ambisonic channels
- Calling HOA a fixed 7.1.4 layout
- Assuming an unknown B-format file is AmbiX
- Calling a spaced channel array such as ESMA-3D freely rotatable like Ambisonics
- Treating a generic HRTF render as a personalized BRIR
- Equating ADM, S-ADM, and IAB
- Repeating an old channel cap, renderer version, or platform requirement without checking it
- Declaring one array or renderer "best" without a use case and listening target
