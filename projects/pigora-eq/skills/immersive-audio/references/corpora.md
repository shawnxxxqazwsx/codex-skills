# Immersive Audio Corpora

Choose a corpus from the research question, not from the largest channel count. Open the current record before reuse and confirm the record version, file inventory, license, and attribution requirements.

## Contents

- Corpus picker
- 3D-MARCo
- ECHO
- TU Berlin loudspeaker orchestra
- ARTE
- EigenScape
- STARSS23
- WDR spatial impulse responses
- DEMAND
- ESMA and PCMA interpretation

## Corpus picker

| Corpus | Best for | Do not use it as |
|---|---|---|
| 3D-MARCo | Same-take music comparisons across spaced 3D, conventional, FOA, and HOA capture | A complete orchestral Atmos production workflow |
| ECHO | Large orchestral capture, multiple contemporary 3D arrays, and engineer-produced Atmos masters | A lightweight SELD benchmark |
| TU Berlin loudspeaker orchestra | Controlled receiver, spherical-array, dummy-head, and binaural-render comparisons | Evidence of natural acoustic-instrument radiation without the loudspeaker reproduction step |
| ARTE | Ecological HOA environments and hearing research | A classical microphone-technique bake-off |
| EigenScape | Outdoor fourth-order Ambisonic scenes and acoustic-scene features | Multitrack music production |
| STARSS23 | Real-room sound-event localization and detection with labels | Judging musical array aesthetics |
| WDR spatial IRs | Room convolution, spherical-array IRs, and BRIR research | Same-take live-music microphone comparison |
| DEMAND | Multichannel noise robustness and beamforming | Ambisonic music or spherical capture |

## 3D-MARCo

The 3D Microphone Array Recording Comparison was recorded in St Paul's Hall at the University of Huddersfield. Its value is simultaneous capture: many arrays and auxiliary microphones observe the same performances.

| Item | Published record |
|---|---|
| Capture | 71 simultaneously recorded microphones, with array parts that can be recombined into more than 250 configurations |
| Material | Chamber music, solo instruments, vocal material, organ, and virtual-ensemble room responses |
| Arrays | OCT-3D, PCMA-3D, 2L-Cube, Decca Cuboid, Hamasaki variants, Eigenmike HOA, AMBEO FOA, conventional arrays, dummy head, spots, and ambience |
| Research use | Perceptual comparison, interchannel-crosstalk analysis, ILD/ITD, correlation, and direct-to-reverberant balance |

- [Dataset concept DOI](https://doi.org/10.5281/zenodo.3477602)
- [AES eBrief author manuscript](https://pure.hud.ac.uk/ws/portalfiles/portal/18503381/AES_147EB_3D_mic_array_AAM.pdf)
- [Project page](https://apl-hud.com/3d-marco-3d-microphone-array-recording-comparison/)
- [Objective-measurement paper](https://doi.org/10.17743/jaes.2021.0038)

Do not collapse the results into one winning array. Source type, listening position, layout, and perceptual attribute all change the result.

## ECHO

The ECHO project extends simultaneous array research to a professional orchestral session at AIR Studios with industry mixing deliverables.

| Item | Published record |
|---|---|
| Session | London Contemporary Orchestra in Lyndhurst Hall, recorded in December 2024 |
| Production views | Circular 360-degree and traditional frontal layouts |
| Arrays | 2L Prism, AirCage, ESMA-3D, P3H variants, PAMA, PCMA-3D v2, PentaSphere, plus Eigenmike, KU100, spots, and ambience |
| Deliverables | Multitracks, array documentation, and engineer-produced Dolby Atmos ADM/BWF mixes |

- [Project hub](https://apl-hud.com/echo/)
- [Database hub](https://apl-hud.com/echo-database/)
- [Array rationales](https://apl-hud.com/echo-arrays/)
- [Dataset concept DOI](https://doi.org/10.5281/zenodo.15268470)
- [ESMA-3D and PCMA-3D mix notes](https://apl-hud.com/wp-content/uploads/2025/05/ECHO-Mix-ESMA3D-PCMA3D.pdf)

The database can evolve. Check the hub and DOI record for the current files and reuse license.

## TU Berlin loudspeaker orchestra

This dataset reproduces anechoic chamber-orchestra material over an 18-channel loudspeaker orchestra in two venues while multiple receivers capture the same reproduced field. The experimental advantage is controlled source radiation, room, and receiver position.

Receivers include dummy heads and first- through higher-order spherical microphone arrays. The dataset also contains per-emitter impulse responses, anechoic source material, and SOFA data.

- [Paper DOI](https://doi.org/10.17743/jaes.2022.0059)
- [DepositOnce dataset DOI](https://doi.org/10.14279/depositonce-15774)

Use it to compare receiver and rendering paths. State clearly that the orchestra is reproduced by loudspeakers rather than captured as a live ensemble in each venue.

## ARTE

The Ambisonics Recordings of Typical Environments database captures realistic Sydney environments with a purpose-built 62-channel array and publishes a 31-channel mixed-order representation: full three-dimensional components through order four plus additional horizontal components through order seven.

It includes environment recordings, directional room responses, binaural renders, calibration information, and MATLAB helpers. The record explicitly limits some audio use, so inspect the current rights statement before redistribution.

- [Dataset concept DOI](https://doi.org/10.5281/zenodo.2261633)
- [Dataset record and description](https://zenodo.org/records/3386569)
- [Paper DOI](https://doi.org/10.3813/AAA.919349)

## EigenScape

EigenScape contains outdoor and urban recordings captured with an Eigenmike and released in fourth-order Ambisonics. The published design comprises eight scene classes, eight locations per class, and ten-minute recordings, with a smaller first-order edition also available.

- [Dataset DOI](https://doi.org/10.5281/zenodo.1012809)
- [Paper DOI](https://doi.org/10.3390/app7111204)

Use it for acoustic-scene classification, spatial feature extraction, and Ambisonic rendering experiments, not as multitrack music stems.

## STARSS23

The STARSS23 development dataset provides real-room spatial sound scenes from Tampere and Tokyo, event and distance labels, and simultaneous first-order Ambisonic and tetrahedral-microphone signal formats. Optional panoramic video supports audiovisual localization work.

- [Dataset DOI](https://doi.org/10.5281/zenodo.7880637)

Use it for SELD and tracking. Distinguish the Ambisonic `FOA` representation from the raw tetrahedral `MIC` representation even when both originate from the same device.

## WDR spatial impulse responses

The WDR compilation publishes directional room impulse responses from open and rigid spherical arrays and KU100 binaural room impulse responses in broadcast studios and control rooms, with SOFA files.

- [Dataset DOI](https://doi.org/10.5281/zenodo.3930833)

Use it for convolution, room analysis, spherical-array encoding, or renderer comparison. It is not a simultaneous live-performance stem set.

## DEMAND

DEMAND contains environmental noise captured with a 16-channel planar array. It supports multichannel noise reduction, beamforming, and robustness tests.

- [Dataset DOI](https://doi.org/10.5281/zenodo.1227121)
- [JASA paper DOI](https://doi.org/10.1121/1.4806631)

Do not call the planar raw recordings Ambisonics without a justified encoding model.

## ESMA and PCMA interpretation

ESMA-3D and PCMA-3D are spaced channel-array families, not Ambisonic scene encoders.

- ESMA relates microphone subtended angles to the reproduction loudspeaker base angles. It aims for continuous 360-degree channel imaging when capture and playback geometry are coordinated.
- PCMA separates localization and ambience or direct-to-reverberant perspective through array geometry and mix balance.
- Height microphone spacing, polar pattern, main-to-height level, and mapping are design variables, not universal constants. Use the exact paper or session notes for a chosen configuration.
- A channel-array recording can be remapped or processed, but it is not inherently freely rotatable like a complete Ambisonic scene.

Foundational sources: [ESMA paper](https://doi.org/10.17743/jaes.2018.0068), [3D array review](https://doi.org/10.17743/jaes.2020.0069), and the ECHO array and mix notes above.
