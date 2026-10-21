# Immersive Audio Standards and Delivery

Use normative standards for syntax and limits. Use vendor material for workflows and ecosystem-specific constraints. Re-open official pages before stating that an edition, profile, channel cap, or delivery requirement is current.

## Contents

- AmbiX, ADM, S-ADM, IAB, and SOFA
- Dolby Atmos and Dolby delivery codecs
- MPEG-H, MPEG-I, and 360 Reality Audio
- Auro-3D and Auro-Cx
- DTS, MDA, and DTS-UHD

## AmbiX, ADM, S-ADM, IAB, and SOFA

| Topic | Authority | Engineering use |
|---|---|---|
| AmbiX | [Original paper](https://iaem.at/Members/zotter/publications/2011_NachbarZotterSontacchiDeleflie_ambix.pdf), [libambix format reference](https://iem-projects.github.io/ambix/apiref/format.html) | ACN channel order, SN3D normalization, BASIC/EXTENDED interchange |
| ADM | [ITU-R BS.2076-3](https://www.itu.int/rec/R-REC-BS.2076-3-202502-I/en), [EBU ADM guidelines](https://adm.ebu.io/) | Metadata model for channel, object, HOA, matrix, and binaural content; often carried with BW64/BWF workflows |
| S-ADM | [ITU-R BS.2125 series](https://www.itu.int/rec/R-REC-BS.2125/en) | Serial form for live and emission workflows |
| Emission profile | [ITU-R BS.2168-0](https://www.itu.int/rec/R-REC-BS.2168-0-202502-I/en) | Constraints for ADM and S-ADM emission use |
| ADM renderer | [ITU-R BS.2127 series](https://www.itu.int/rec/R-REC-BS.2127/en) | Rendering model for advanced sound systems |
| IAB | [SMPTE ST 2098-2 public draft repository](https://github.com/SMPTE/st2098-2) | Immersive Audio Bitstream for cinema and interchange; confirm the published SMPTE edition |
| SOFA | AES69 and [SOFA conventions](https://www.sofaconventions.org/) | HRTF, BRIR, and other spatial acoustic data |

ADM is a metadata model, not a synonym for a particular Atmos master. S-ADM is not simply a smaller ADM file. IAB is a bitstream and is not interchangeable with ADM XML by renaming a container.

### Ambisonic interchange checklist

1. Confirm complete or mixed order and expected channel count.
2. Confirm ACN versus FuMa or another ordering.
3. Confirm SN3D, N3D, or FuMa normalization.
4. Confirm coordinate axes, handedness, and azimuth/elevation conventions.
5. Convert once at a controlled boundary and document the result.
6. For ADM HOA, inspect `order`, `degree`, `normalization`, and near-field information. The [EBU HOA element reference](https://adm.ebu.io/reference/adm_elements/audio_channel_format_hoa.html) documents SN3D as the default when normalization is omitted.

## Dolby Atmos and delivery codecs

| Document | Authority and scope |
|---|---|
| [Dolby Atmos for content creators](https://professional.dolby.com/content-creation/Dolby-Atmos-for-content-creators/) | Current public overview of the production path from beds and objects to a renderer and master |
| [Dolby Atmos Master ADM Profile](https://dolby.my.site.com/professionalsupport/s/article/Dolby-Atmos-ADM-Profile-specification) | Vendor profile and download hub; check for the current profile revision |
| [Overview of Atmos master file formats](https://dolby.my.site.com/professionalsupport/s/article/Overview-of-Dolby-Atmos-Master-File-Formats) | ADM BWF versus DAMF and supported workflows |
| [ATSC A/52:2018](https://www.atsc.org/wp-content/uploads/2021/04/A52-2018.pdf) | AC-3 and E-AC-3 syntax; use only with awareness of later amendments or platform profiles |
| [ETSI TS 102 366](https://www.etsi.org/deliver/etsi_ts/102300_102399/102366/01.04.01_60/ts_102366v010401p.pdf) | AC-3 and Enhanced AC-3 syntax |
| [ETSI TS 103 420](https://www.etsi.org/deliver/etsi_ts/103400_103499/103420/01.01.01_60/ts_103420v010101p.pdf) | Backward-compatible object-audio carriage with E-AC-3, commonly associated with JOC delivery |
| [Dolby AC-4 white paper](https://professional.dolby.com/siteassets/technologies/dolby_atmos_ac-4_whitepaper.pdf) | Vendor architecture for AC-4 and Advanced JOC; not a substitute for a normative AC-4 specification |

Production guidance:

- A bed is channel-based; an object carries audio plus metadata. A project may use either or both according to the deliverable.
- Objects have no discrete LFE send. Do not confuse that limitation with bass management, which can reproduce their low-frequency energy through subwoofers.
- A 7.1.2 bed and the familiar 128-input/118-object accounting are workflow-specific Dolby limits, not universal limits for every consumer endpoint. If a user needs a cap, check the exact current renderer, profile, platform, and endpoint documentation.
- Keep the authoring session, master file, encode, transport, and endpoint render as separate layers.
- E-AC-3 with JOC is one common home or streaming route; Dolby TrueHD and AC-4 cover other delivery contexts.

## MPEG-H, MPEG-I, and 360 Reality Audio

| Topic | Primary source | Key distinction |
|---|---|---|
| MPEG-H 3D Audio | ISO/IEC 23008-3; accessible overview via [Herre and Quackenbush](https://doi.org/10.1250/ast.43.143) | One codec framework for channels, objects, and HOA, with interactivity and personalization |
| ATSC carriage | [ATSC A/342 Part 3](https://www.atsc.org/wp-content/uploads/2022/04/A342-3-2022-03-MPEG-System.pdf) | MPEG-H system constraints in ATSC 3.0; check the ATSC standards catalog for updates |
| MPEG-I Immersive Audio | [ISO/IEC 23090-4:2025](https://www.iso.org/standard/84711.html) | Interactive 6DoF scene rendering, geometry, acoustics, metadata, and bitstream syntax |
| MPEG-I overview | [Fraunhofer white paper](https://www.iis.fraunhofer.de/content/dam/iis/en/doc/ame/Whitepaper/mpeg-i/MPEG-I_Immersive_Audio%E2%80%94The_ISO_MPEG_Standard_for_Virtual_Augmented_Reality_Audio.pdf) | Accessible implementation context; vendor-authored |
| Sony 360 Reality Audio | [Sony creator hub](https://www.sony.co.jp/en/Products/create360RA/), [Sony Music submission guidance](https://mediaguide.sonymusic.com/audio/audio-submission-guidelines/) | Music-facing object workflow built on MPEG-H; ecosystem rules come from Sony |

Do not call 360RA a separate ISO codec, and do not call a head-rotatable MPEG-H music render 6DoF without a translational scene model.

## Auro-3D and Auro-Cx

| Document | Use |
|---|---|
| [Auro-3D Engine white paper](https://www.auro-3d.com/wp-content/uploads/2023/08/Auro-3D_Engine_v3_2_White_Paper_Rev6.pdf) | Classic layered-channel decoding, upmixing, and headphone architecture; verify newer vendor revisions |
| [Auro-Cx white paper](https://www.auro-3d.com/wp-content/uploads/2023/08/Auro-Cx-White-Paper-rev1-20230714.pdf) | Newer NGA path supporting channel, object, and scene content |
| [Auro-3D in multichannel WAV](https://www.auro-3d.com/wp-content/uploads/2024/04/Auro-3D-in-multi-channel-WAV-White-Paper-20240419.pdf) | Channel-map and WAV/WAVEFORMATEXTENSIBLE details |

Classic Auro-3D is primarily a channel-and-height-layer production system. Do not infer a WAV channel order from a DAW label; cite the vendor map for the actual carrier.

## DTS, MDA, and DTS-UHD

| Document | Use |
|---|---|
| [ETSI TS 103 223](https://www.etsi.org/deliver/etsi_TS/103200_103299/103223/01.01.01_60/ts_103223v010101p.pdf) | MDA object metadata and reference renderer model |
| [ETSI TS 103 491](https://www.etsi.org/deliver/etsi_TS/103400_103499/103491/01.02.01_60/ts_103491v010201p.pdf) | DTS-UHD delivery of channel, object, and Ambisonic content |
| [SMPTE RDD 43:2016](https://doi.org/10.5594/SMPTE.RDD43.2016) | MDA bitstream mapping; access may be paid |

Treat MDA as a metadata and creation lineage and DTS-UHD as a delivery specification. Do not equate either one-to-one with every consumer product branded DTS:X; name the actual authoring, exchange, or delivery layer.
