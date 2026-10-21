# Verified research index

This index was assembled on 2026-08-26. Sources were opened and checked before inclusion. Prefer the linked author, institution, standards body, publisher, or official conference archive over summaries.

Evidence labels:

- **Standard:** normative or test-method authority.
- **Journal:** peer-reviewed journal article or its institutional record/author copy.
- **Conference:** published proceedings; useful evidence, but usually a device/method case study rather than universal proof.
- **Preprint:** current research not treated as settled.
- **Technical tutorial/manual:** primary engineering documentation, not an independent validation.

## Search coverage

The research used 27 numbered technical search rounds, exceeding the requested 20. The rounds covered:

1. virtual-analog overviews and distortion pedals;
2. WDF and nonlinear circuits;
3. state-space, modified nodal analysis, and circuit solvers;
4. Hammerstein, Wiener, Volterra, and nonlinear identification;
5. neural black-box models;
6. differentiable white/gray-box models;
7. exponential and synchronized swept sine;
8. multisine, best linear approximation, IMD, and noncoherence;
9. EQ decramping and prescribed Nyquist gain;
10. direct-domain EQ and higher-order shelving;
11. oversampling and multirate filter design;
12. antiderivative antialiasing;
13. BLEP/BLAMP, piecewise waveshapers, and continuous-time convolution;
14. perceptual alias evaluation;
15. nonlinear-distortion psychoacoustics and timbre;
16. compressors, detectors, gain cells, and vactrols;
17. physical and neural magnetic tape;
18. transformer and magnetic hysteresis;
19. op-amp, tube, BJT, JFET, and OTA component models;
20. loudspeakers, cabinets, and transducers;
21. spring/plate electromechanical reverberation;
22. BBD and tape-like variable-speed delay;
23. phaser, chorus, flanger, Hammond scanner, and rotary effects;
24. nonlinear synth filters and alias-controlled oscillators;
25. consoles, summing, crosstalk, and channel strips;
26. realtime solvers, SIMD, multichannel, and neural efficiency;
27. formal listening-test and loudness standards.

## Foundations and model families

- **Conference:** [Yeh, Abel, and Smith — Simplified, Physically-Informed Models of Distortion and Overdrive Guitar Effects Pedals](https://dafx.labri.fr/main/papers/p189.pdf). Demonstrates a defensible filter–nonlinearity–filter simplification derived from circuit analysis, and documents where it remains approximate.
- **Journal record:** [Pakarinen and Yeh — A Review on Digital Techniques for Modeling Vacuum-Tube Guitar Amplifiers](https://research.aalto.fi/en/publications/a-review-on-digital-techniques-for-modeling-vacuum-tube-guitar-am/). Maps block-based, circuit, and physical approaches for tube amplifiers.
- **Conference:** [Pakarinen, Tikander, and Karjalainen — Wave Digital Modeling of the Output Chain of a Vacuum-Tube Amplifier](https://dafx.de/paper-archive/2009/papers/paper_16.pdf). Couples triode, transformer, loudspeaker, electrical, mechanical, and acoustic subsystems.
- **Conference:** [Bernardini et al. — Towards Inverse Virtual Analog Modeling](https://www.dafx.de/paper-archive/2019/DAFx2019_paper_8.pdf). Contains a concise white-box/gray-box taxonomy and WDF framing.
- **Conference:** [Esqueda, Kuznetsov, and Parker — Differentiable White-Box Virtual Analog Modeling](https://dafx.de/paper-archive/2021/proceedings/papers/DAFx20in21_paper_39.pdf). Learns uncertain component values while retaining circuit structure.
- **Conference:** [Kuznetsov, Parker, and Esqueda — Differentiable IIR Filters for Machine Learning Applications](https://www.dafx.de/paper-archive/2020/proceedings/papers/DAFx2020_paper_52.pdf). Shows differentiable recursive filters in a Wiener-Hammerstein pedal model.
- **Peer-reviewed conference record:** [Damskägg et al. — Deep Learning for Tube Amplifier Emulation](https://research.aalto.fi/en/publications/deep-learning-for-tube-amplifier-emulation/). Establishes a data-driven tube-amplifier case with DOI and publication metadata.

## Measurement and nonlinear identification

- **AES convention preprint:** [Farina — Simultaneous Measurement of Impulse Response and Distortion with a Swept-Sine Technique](https://angelofarina.it/Public/Papers/134-AES00.PDF). Foundational ESS separation of linear and higher-order responses; the document itself notes it is an unreviewed convention preprint.
- **Journal:** [Novak, Lotton, and Simon — Synchronized Swept-Sine: Theory, Application and Implementation](https://imdea.ant-novak.com/_static/TM/biblio/Novak%20-%202015%20-%20JAES%20-%20Synchronized%20Swept-Sine%20-%20Theory,%20Application,%20and%20Implementation.pdf). Explains synchronization required for reliable higher-harmonic phase and provides implementation guidance; DOI 10.17743/jaes.2015.0071.
- **Journal:** [Novak et al. — Nonlinear System Identification Using Exponential Swept-Sine Signal](https://www.ant-novak.com/publications/papers/2010_ieee_novak.pdf). Formal nonlinear identification treatment; DOI 10.1109/TIM.2009.2031836.
- **Conference:** [Rébillat et al. — Modeling of Nonlinear Audio Systems Using Swept-Sine Signals](https://www.dafx.de/paper-archive/2009/papers/paper_14.pdf). Builds parallel nonlinear-basis/filter models and states the order-dependent frequency and amplitude validity domain.
- **AES convention preprint:** [Temme and Brunet — Measuring Distortion Using Multitone and Non-Coherence](https://www.listeninc.com/wp/media/2023/06/paper_121AES_non_coherent_distortion_Listen_Inc.pdf). Explains why multitone exposes IMD and simultaneous-frequency behavior absent from single-tone tests.
- **Conference archive:** [Möller, Gromowski, and Zölzer — A Measurement Technique for Highly Nonlinear Transfer Functions](https://www.dafx.de/paper-archive/details/ar1jK6DdEpOJpuoTYJcQGw). Transfer-curve estimation for tube/distortion stages.
- **Conference archive:** [Schaefer — Electronic Musical Tone Production by Nonlinear Waveshaping](https://secure.aes.org/forum/pubs/journal/?elib=1489). Classic Chebyshev relationship between a waveshaper and sinusoidal harmonic content.

## EQ, phase, and time-varying filters

- **Journal/author copy:** [Orfanidis — Digital Parametric Equalizer Design with Prescribed Nyquist-Frequency Gain](https://octovoid.com/wp-content/uploads/2017/11/orfanidis.pdf). Shows why conventional bilinear designs cramp near Nyquist and adds a Nyquist-gain constraint.
- **AES convention paper record:** [Massberg — Digital Low-Pass Filter Design with Analog-Matched Magnitude Response](https://secure.aes.org/forum/pubs/conventions/?elib=16077). Prewarps analog prototypes to improve high-cutoff magnitude matching.
- **Conference:** [Holters and Zölzer — Parametric Higher-Order Shelving Filters](https://eurasip.org/Proceedings/Eusipco/Eusipco2006/papers/1568980789.pdf). Provides adjustable higher-order shelves and gain/frequency parameterization.
- **Conference:** [Holters and Zölzer — Graphic Equalizer Design Using Higher-Order Recursive Filters](https://dafx.de/paper-archive/2006/papers/p_037.pdf). Addresses inter-band interaction and complementary edges with higher-order shelves.
- **Review:** [Välimäki and Reiss — All About Audio Equalization: Solutions and Frontiers](https://www.mdpi.com/2076-3417/6/5/129). Broad review of audio EQ design, implementation, and open problems.

## Oversampling and alias reduction

- **Journal/author copy:** [Kahles, Esqueda, and Välimäki — Oversampling for Nonlinear Waveshaping: Choosing the Right Filters](https://acris.aalto.fi/ws/portalfiles/portal/34665796/ELEC_Kahles2019_Oversampling_JAES.pdf). Compares interpolation/decimation choices using a masking-aware alias metric; shows decimation-filter choice is material.
- **Conference:** [Parker, Zavalishin, and Le Bivic — Reducing the Aliasing of Nonlinear Waveshaping Using Continuous-Time Convolution](https://dafx.de/paper-archive/2016/dafxpapers/20-DAFx-16_paper_41-PN.pdf). Develops antiderivative/continuous-time-inspired alias mitigation and treats nonlinear feedback examples.
- **Conference:** [Holters — Antiderivative Antialiasing for Stateful Systems](https://www.dafx.de/paper-archive/2019/DAFx2019_paper_4.pdf). Extends the approach to selected stateful systems and explains scalar-nonlinearity and feedback limitations.
- **Conference archive:** [Antialiasing Piecewise Polynomial Waveshapers](https://www.dafx.de/paper-archive/details/cu51KU_JsiXj1cvMi-2DOw). Applies ADAA to piecewise-polynomial and piecewise-linear waveshapers.
- **Journal record:** [Antiderivative Antialiasing for Chebyshev-Based Generalized Hammerstein Models](https://scholarship.miami.edu/esploro/outputs/journalArticle/Antiderivative-Antialiasing-for-Chebyshev-Based-Generalized-Hammerstein/991032795993402976). Connects per-order Chebyshev behavioral models with alias reduction.
- **Preprint:** [Carson et al. — Resampling Filter Design for Multirate Neural Audio Effect Processing](https://arxiv.org/abs/2501.18470). Compares FIR/IIR half-band cascades, latency, operations, desired-harmonic preservation, and alias metrics.
- **Preprint:** [Carson et al. — Sample Rate Independent Recurrent Neural Networks for Audio Effects Processing](https://arxiv.org/abs/2406.06293). Shows that recurrent state dynamics need explicit treatment across sample rates and oversampling factors.

## Psychoacoustics and listening

- **Journal record:** [Tan, Moore, and Zacharov — The Effect of Nonlinear Distortion on the Perceived Quality of Music and Speech Signals](https://secure.aes.org/forum/pubs/journal/?elib=12197). Compares multiple nonlinearities, program material, subbands, multitone metrics, and subjective ratings.
- **Journal:** [Harrison and Pearce et al. — Timbral Effects on Consonance Disentangle Psychoacoustic Mechanisms](https://pubmed.ncbi.nlm.nih.gov/38369535/). Large behavioral study showing that timbre, harmonicity, roughness, and beating interact; useful evidence against simple even/odd folklore.
- **Standard:** [ITU-R BS.1116 — Methods for the Subjective Assessment of Small Impairments in Audio Systems](https://www.itu.int/rec/R-REC-BS.1116-3-201502-I/en). Reference/hidden-reference method, expert listeners, listening conditions, statistics, and reporting.
- **Standard:** [ITU-R BS.1534 — Method for the Subjective Assessment of Intermediate Quality Level of Audio Systems](https://www.itu.int/rec/r-rec-bs.1534/en). MUSHRA framework for multi-stimulus intermediate-quality evaluation.
- **Standard:** [ISO 532-1:2017 — Zwicker Loudness Method](https://www.iso.org/standard/63077.html). Standardized stationary and time-varying loudness estimation; use as one descriptor, not a complete hardware-fidelity metric.

## Dynamics and long-memory models

- **Journal:** [Giannoulis, Massberg, and Reiss — Digital Dynamic Range Compressor Design: A Tutorial and Analysis](https://aes2.org/publications/elibrary-page/?id=16354). Canonical comparison of peak/RMS, feedforward/feedback, linear/log detection, static curve, and ballistics.
- **Conference archive:** [Najnudel et al. — Power-Balanced Dynamic Modeling of Vactrols](https://dafx.de/paper-archive/details/FQ0s5ZsffVCpJ_T1Far3GA). Physically motivated, program-dependent opto component model.
- **Preprint:** [Steinmetz and Reiss — Efficient Neural Networks for Real-Time Modeling of Analog Dynamic Range Compression](https://arxiv.org/abs/2102.06200). Causal long-context compression model, compute/latency analysis, control conditioning, and a listening study.
- **Preprint:** [Yin et al. — Modeling Analog Dynamic Range Compressors Using Deep Learning and State-Space Models](https://arxiv.org/abs/2403.16331). Uses structured state-space layers for long compressor memory; treat quality claims as preprint evidence.

## Tape, transformers, and electronic components

- **Conference:** [Chowdhury — Real-Time Physical Modelling for Analog Tape Machines](https://www.dafx.de/paper-archive/2019/DAFx2019_paper_3.pdf). Separates record/play filtering, hysteresis, transport irregularity, hiss, and circuit limitations.
- **Conference:** [Mikkonen et al. — Neural Modeling of Magnetic Tape Recorders](https://www.pure.ed.ac.uk/ws/portalfiles/portal/408817262/DAFx23_paper_51.pdf). Gray-box separation of hysteretic/filter behavior, fluctuating delay, and noise.
- **Conference:** [Holters and Zölzer — Circuit Simulation with Inductors and Transformers Based on the Jiles–Atherton Model](https://www.hsu-hh.de/ant/wp-content/uploads/sites/699/2017/10/Holters_jamodel_DAFx16.pdf). History-dependent magnetic model for inductors/transformers.
- **Conference archive:** [Müller and Hélie — A Minimal Passive Model of the Operational Amplifier](https://www.dafx.de/paper-archive/details/LWCBgVLLDCVpN_fvlLcEUg). Includes saturation and asymmetric supplies in a passive behavioral component model.
- **Journal:** [Emulation of Junction Field-Effect Transistors for Real-Time Audio Applications](https://www.jstage.jst.go.jp/article/elex/13/12/13_13.20160288/_article). Nonlinear JFET component model embedded in WDF examples.

## Loudspeakers, cabinets, and electromechanics

- **Technical tutorial:** [Klippel — Loudspeaker Nonlinearities: Causes, Parameters, Symptoms](https://www.klippel.de/fileadmin/klippel/Files/Know_How/Literature/Papers/Loudspeaker%20Nonlinearities_Causes,Parameters,Symptoms_06.pdf). Detailed map of motor, suspension, thermal, and perceptual large-signal behavior.
- **Conference:** [Yeh and Smith — Nonlinear Modeling of a Guitar Loudspeaker Cabinet](https://dafx.de/paper-archive/2008/papers/dafx08_17.pdf). Shows why a cabinet IR is only the linear layer and evaluates nonlinear large-signal modeling.
- **Conference archive:** [Spring Reverberation: A Physical Perspective](https://www.dafx.de/paper-archive/details/MBjqiMDVjnAseoN9C-fzBw). Frames spring reverb as a complex dispersive mechanical system for which standard analog-circuit methods are insufficient.
- **Conference:** [Bilbao, Ducceschi, and Webb — Large-Scale Real-Time Modular Physical Modeling Sound Synthesis](https://dafx.de/paper-archive/2019/DAFx2019_paper_22.pdf). Energy/stability-aware physical modeling, non-iterative speedups, C++ timing, and vectorization.

## Analog delay, modulation, and synthesizer circuits

- **Conference:** [Raffel and Smith — Practical Modeling of Bucket-Brigade Device Circuits](https://www.dafx.de/paper-archive/2010/DAFx10/RaffelSmith_DAFx10_P42.pdf). Covers BBD filters, compander, variable clock, noise, distortion, and insertion response.
- **Conference:** [Holters and Parker — A Combined Model for a Bucket Brigade Device and Its Input and Output Filters](https://dafx.de/paper-archive/2018/papers/DAFx2018_paper_12.pdf). Treats BBD and surrounding filters as one variable-rate system.
- **Conference:** [Huovilainen — Enhanced Digital Models for Analog Modulation Effects](https://www.dafx.de/paper-archive/2005/P_155.pdf). Circuit-informed phaser stages, BBD delay-time warping, and compander approximation.
- **Conference archive:** [Zavalishin and Parker — Efficient Emulation of Tape-Like Delay Modulation Behavior](https://www.dafx.de/paper-archive/details/HeLd0OAtZr6hPw_63LViZg). Analyzes tape-like pitch response and computation during speed changes.
- **Conference archive:** [Werner, Dunkel, and Germain — A Computational Model of the Hammond Organ Vibrato/Chorus Using WDF](https://www.dafx.de/paper-archive/details/nd_rFZKONvryB6uA-7xKrg). Combines an LC ladder and electromechanical scanner.
- **Conference archive:** [Disch and Zölzer — Modulation and Delay-Line-Based Digital Audio Effects](https://www.dafx.de/paper-archive/details/U0QyREn-tXZ76ItfJA-tDQ). Includes rotary-speaker and vibrato mechanisms.
- **Conference:** [Martínez-Ramírez et al. — A General-Purpose Deep Learning Approach to Model Time-Varying Audio Effects](https://dafx.de/paper-archive/2019/DAFx2019_paper_12.pdf). Covers chorus, flanger, phaser, tremolo, vibrato, ring modulation, Leslie, and long temporal dependencies.
- **Peer-reviewed record:** [Neural Modeling of Phaser and Flanging Effects](https://research.aalto.fi/en/publications/neural-modeling-of-phaser-and-flanging-effects/). Gray-box control/LFO measurement and realtime model evaluation.
- **Conference archive:** [Huovilainen — Non-Linear Digital Implementation of the Moog Ladder Filter](https://www.dafx.de/paper-archive/details/UervgvkeeDC1a4sWDluM4Q). Derives a realtime nonlinear ladder from the circuit differential equation.
- **Conference:** [Köper et al. — A Virtual Analog Model of the EDP Wasp VCF](https://www.dafx.de/paper-archive/2022/papers/DAFx20in22_paper_34.pdf). Shows OTA/CMOS rail behavior, source impedance, feedback, and resonance require topology-specific component models.
- **Conference archive:** [Timoney et al. — Virtual Analog Oscillator Hard Synchronisation](https://www.dafx.de/paper-archive/details/C3p4ljTQMk9GMtSpRIU8-A). Measurement-informed, efficient hard-sync synthesis alternative.

## Realtime implementation and skill placement

- **Conference archive:** [Miklanek and Schimmel — Fast Temporal Convolutions for Real-Time Audio Signal Processing](https://www.dafx.de/paper-archive/2022/papers/DAFx20in22_paper_43.pdf). Optimizes dilated convolution for realtime nonlinear audio models.
- **Conference archive:** [Ringhofer, Gnoss, and Schiele — Balancing Error and Latency of Black-Box Models](https://www.dafx.de/paper-archive/2024/papers/DAFx24_paper_44.pdf). Hardware-aware architecture search illustrates that error, latency, and target hardware are joint design variables.
- **Official OpenAI documentation:** [Build skills](https://developers.openai.com/codex/skills). Defines progressive disclosure, `SKILL.md`/`references`/`agents/openai.yaml` structure, trigger descriptions, and repository-level `.agents/skills` discovery.

## How to extend this index

When adding a source:

1. search by mechanism and device type, not only product name;
2. prefer the author/publisher/manufacturer/standards-body page;
3. open the full source and verify title, authors, year, evidence type, and method;
4. record what engineering decision the source changes;
5. label preprints and convention preprints;
6. avoid copying long passages, figures, or proprietary schematics;
7. do not generalize a single-device case study to all hardware of that class.
