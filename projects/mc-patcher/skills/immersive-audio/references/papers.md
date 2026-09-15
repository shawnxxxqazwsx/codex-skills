# Immersive Audio Reading Map

Use this list to choose a small, goal-driven reading path. Open the linked landing page before citing it, and label paid access honestly.

## Contents

- Foundations and books
- Ambisonics and binaural rendering
- Codecs, parametric rendering, and 6DoF
- WFS
- Evaluation, metadata, and data formats
- Recording arrays and corpora
- Suggested paths

## Foundations and books

| Priority | Work | Access | Use |
|---|---|---|---|
| Core | Zotter and Frank, *Ambisonics: A Practical 3D Audio Theory for Recording, Studio Production, Sound Reinforcement, and Virtual Reality* (2019) | [Open-access DOI](https://doi.org/10.1007/978-3-030-17207-7) | HOA mathematics, panning, decoding, production flow, spherical arrays |
| Core | Paterson and Lee, eds., *3D Audio* (2022) | [Routledge](https://www.routledge.com/3D-Audio/Paterson-Lee/p/book/9781138590069) | Recording, broadcast, film, height perception, and production practice |
| Core | Politis, *Microphone Array Processing for Parametric Spatial Audio Techniques* (2016) | [Aalto repository](https://aaltodoc.aalto.fi/handle/123456789/22499) | DirAC, spatial covariance, spherical-harmonic-domain array processing |
| Background | Blauert, *Spatial Hearing*, revised edition | [MIT Press](https://mitpress.mit.edu/9780262024136/spatial-hearing/) | Localization and spatial-hearing psychoacoustics |
| Background | Begault, *3-D Sound for Virtual Reality and Multimedia* | [NASA PDF](https://ntrs.nasa.gov/api/citations/20010044352/downloads/20010044352.pdf) | Historical binaural and virtual-auditory-display foundations |
| Background | Rumsey, *Spatial Audio* (2001) | Publisher or library | Multichannel and spatial production before current object-audio ecosystems |

## Ambisonics and binaural rendering

| Work | Access | Why it matters |
|---|---|---|
| Zotter and Frank, All-Round Ambisonic Panning and Decoding (2012) | [AES eLibrary landing](https://aes2.org/publications/elibrary-page/?id=16554) | AllRAD and AllRAP foundation; may require paid access |
| Schörkhuber, Zaunschirm, and Höldrich, Binaural Rendering of Ambisonic Signals via Magnitude Least Squares (2018) | [DAGA PDF](https://pub.dega-akustik.de/DAGA_2018/data/articles/000301.pdf) | Direct HOA-to-binaural magnitude least-squares method |
| Rafaely et al., review of binaural reproduction of sound scenes (2022) | [Acta Acustica](https://acta-acustica.edpsciences.org/articles/aacus/full_html/2022/01/aacus220021/aacus220021.html) | HRTF order limits, equalization, rendering choices, and evaluation |
| Brinkmann et al., Masked MagLS (2025 preprint) | [arXiv](https://arxiv.org/abs/2501.18224) | A newer MagLS-family approach; identify it as a preprint when cited |
| Nachbar et al., AmbiX: A Suggested Ambisonics Format (2011) | [IEM PDF](https://iaem.at/Members/zotter/publications/2011_NachbarZotterSontacchiDeleflie_ambix.pdf) | ACN plus SN3D interchange convention |

Do not summarize MagLS as simply "discarding HRTF phase." It changes the optimization objective above a transition region so magnitude can be fitted without forcing unreliable high-frequency phase matching; cite the paper for the exact formulation.

## Codecs, parametric rendering, and 6DoF

| Work | Access | Use |
|---|---|---|
| Herre and Quackenbush, MPEG-H 3D Audio overview (2022) | [Open PDF](https://www.jstage.jst.go.jp/article/ast/43/2/43_E2168/_pdf), [DOI](https://doi.org/10.1250/ast.43.143) | Channel, object, HOA, personalization, and delivery architecture |
| Quackenbush and Herre, MPEG standards for immersive audio | [DOI](https://doi.org/10.1109/JPROC.2021.3075390) | MPEG-H and MPEG-I context; access may be paid |
| Pulkki, Directional Audio Coding (DirAC), JAES 55(6), 2007 | AES eLibrary | Parametric direction-and-diffuseness reproduction |
| Politis, McCormack, and Pulkki, COMPASS | [Author PDF](http://research.spa.aalto.fi/projects/sparta_vsts/publications/politis2019compass.pdf), [DOI](https://doi.org/10.1109/ICASSP.2018.8462608) | Multiple directional sources plus non-isotropic ambient model |
| ISO/IEC 23090-4:2025, MPEG-I Immersive Audio | [ISO landing](https://www.iso.org/standard/84711.html) | Normative 6DoF immersive-audio scene and bitstream; standard text is paid |
| MPEG-I overview | [Fraunhofer white paper](https://www.iis.fraunhofer.de/content/dam/iis/en/doc/ame/Whitepaper/mpeg-i/MPEG-I_Immersive_Audio%E2%80%94The_ISO_MPEG_Standard_for_Virtual_Augmented_Reality_Audio.pdf) | Accessible architecture overview, not a substitute for the standard |

## WFS

| Work | Access | Use |
|---|---|---|
| Spors and Ahrens, comparison of WFS and HOA, AES 125 (2008) | [Author PDF](https://www.int.uni-rostock.de/fileadmin/user_upload/publications/spors/2008/AES125_Spors_WFS_HOA.pdf) | Common mathematical framework and different spatial-sampling behavior |
| Spors and Ahrens, spatial sampling artifacts of WFS and HOA (2007) | [Author PDF](https://www.int.uni-rostock.de/fileadmin/user_upload/publications/spors/2007/ICA2007_WFS_HOA_sampling.pdf) | Aliasing and sampling comparison |

## Evaluation, metadata, and data formats

| Work | Official source | Use |
|---|---|---|
| ITU-R BS.1116-3 | [ITU recommendation](https://www.itu.int/rec/R-REC-BS.1116/en) | Controlled subjective assessment of small impairments |
| ITU-R BS.1534-3 | [ITU recommendation](https://www.itu.int/rec/R-REC-BS.1534/en) | MUSHRA for intermediate audio quality |
| ITU-R BS.2076-3 | [ITU recommendation](https://www.itu.int/rec/R-REC-BS.2076-3-202502-I/en) | Audio Definition Model |
| ITU-R BS.2125 series | [ITU search](https://www.itu.int/rec/R-REC-BS.2125/en) | Serial ADM |
| SMPTE ST 2098-2 | [SMPTE public committee draft repository](https://github.com/SMPTE/st2098-2) | Immersive Audio Bitstream; confirm the published edition with SMPTE |
| AES69 / SOFA introduction, Majdak et al. | [DOI](https://doi.org/10.17743/jaes.2022.0026) | Spatially oriented acoustic data and SOFA conventions |

## Recording arrays and corpora

| Work | Access | Use |
|---|---|---|
| Lee, Multichannel 3D Microphone Arrays: A Review | [DOI](https://doi.org/10.17743/jaes.2020.0069) | Taxonomy and perceptual design of spaced 3D arrays |
| Lee, Capturing 360-degree Audio Using ESMA | [DOI](https://doi.org/10.17743/jaes.2018.0068) | Equal-segment channel-array design |
| Lee and Johnson, 3D-MARCo database | [Author manuscript](https://pure.hud.ac.uk/ws/portalfiles/portal/18503381/AES_147EB_3D_mic_array_AAM.pdf), [dataset](https://doi.org/10.5281/zenodo.3477602) | Simultaneous array comparison |
| Lee and Johnson, objective measurements of 3D arrays | [DOI](https://doi.org/10.17743/jaes.2021.0038) | ICXT, ILD/ITD, correlation, and direct-to-reverberant descriptors |
| Ackermann et al., loudspeaker orchestra and multi-receiver recordings | [Paper DOI](https://doi.org/10.17743/jaes.2022.0059), [data DOI](https://doi.org/10.14279/depositonce-15774) | Controlled comparison of spherical arrays and binaural receivers |
| Weisser et al., ARTE database | [DOI](https://doi.org/10.3813/AAA.919349), [dataset](https://doi.org/10.5281/zenodo.2261633) | Ecological HOA environments |
| Green and Murphy, EigenScape | [DOI](https://doi.org/10.3390/app7111204), [dataset](https://doi.org/10.5281/zenodo.1012809) | Outdoor fourth-order Ambisonic scenes |

## Suggested paths

```text
Learn HOA theory and production -> Zotter and Frank
Design a loudspeaker decoder -> AllRAD paper + target-layout evaluation
Render HOA to headphones -> MagLS paper + Rafaely review + chosen HRTF evidence
Compare orchestral arrays -> Lee review + 3D-MARCo or ECHO
Study parametric rendering -> Politis thesis + DirAC + COMPASS
Compare WFS and HOA -> Spors and Ahrens papers
Design a listening test -> the applicable ITU recommendation + attribute literature
Build 6DoF audio -> ISO/IEC 23090-4 + current Fraunhofer overview
```
