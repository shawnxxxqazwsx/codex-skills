# Manley Stereo Variable Mu capture profile

Use this profile only for the Manley Stereo Variable Mu Limiter Compressor. It
is not a generic vari-mu recipe. Manley's documented production changes and
optional modifications are large enough that an unidentified unit is not one
well-defined capture target.

## Identity gate

Do not generate the full parameter matrix until all material fields below are
confirmed from the target unit, its records, or Manley service:

- serial number and approximate production or service date;
- standard or Mastering version, including the actual control labels, detents,
  and number of positions;
- standard stereo wiring or optional M/S input/output modification;
- continuous or stepped Input control;
- 6386, 5670, or T-Bar gain-cell configuration, and the installed output-tube
  type when known from service records;
- HP SC controls and any other factory or later modification;
- last tube replacement, calibration/service status, and any observed channel
  mismatch, noise, hum, intermittent control, or meter error;
- intended operating mode: SEP/dual mono, stereo Link, or M/S;
- source impedance, load impedance, converter calibration, and the physical
  balanced patch path used for capture.

Photograph the front panel, rear panel, serial badge, and recall settings. Do
not ask the user to open the chassis to identify tubes or modifications. The
unit contains hazardous voltages; internal inspection, tube replacement, DC
balance, and other service work belong to Manley or another qualified service
technician.

If any identity field that changes the controls, gain cell, routing, or
calibration remains unknown, limit work first to identity documentation and
converter-chain preparation. Limited low-level DUT pilots may follow only after
the safe route and physical dBFS-to-dBu gates pass; they may identify the
unknown but cannot release a full matrix. Do not silently substitute a
universal Variable Mu grid.

## Documented topology and control variants

The standard unit is an all-tube, fully differential feedback compressor with
transformer-coupled balanced input and output. A remote-cutoff tube is re-biased
by a vacuum-tube-rectified side-chain control voltage. This supports a
feedback-aware dynamic model, but the official material does not disclose the
exact detector or Link combining law.

| Control or path | Standard unit | Mastering version | Capture consequence |
|---|---|---|---|
| Mode/ratio | COMPRESS is nominally 1.5:1 with a soft knee. LIMIT starts near 4:1 and can rise toward 20:1 at deep reduction. | Official current product material advertises the same nominal mode ratios. | Treat mode as discrete. Measure ratio and knee versus gain-reduction depth; do not condition on an invented continuous Ratio control. |
| Input | Since late 2011, a nine-position switch: `-8, -4, -2, -1, 0, +1, +2, +4, +8 dB`. Older units use a continuous dual-ganged potentiometer. | Five positions, 2 dB per step around `0`. | Enumerate switches. For an older pot, record physical position, direction of approach, and L/R tracking rather than assuming an ideal normalized value. |
| Threshold | Continuously variable per channel. | 24 steps; approximately 0.5 dB per step in LIMIT and 0.25 dB per step in COMPRESS. | Standard units need sampled interpolation coverage; Mastering units should first cover the real detents. Do not infer which endpoint means least compression from generic `MIN`/`MAX` wording: on a verified modern standard T-Bar unit, `MAX` was the highest-threshold/no-compression endpoint. Confirm the target unit and verify the endpoint with a conservative input-level ladder before labeling an active baseline. |
| Attack | Continuously variable, nominally about 25-70 ms. | 11 steps, approximately 15, 20, 25, 30, 35, 40, 50, 60, 70, 80, and 90 ms. | These are manufacturer nominal values without a stated percentage convention. Measure the actual attack trajectory at multiple reduction depths. |
| Recovery | Five positions: 0.2, 0.4, 0.6, 4, and 8 seconds. | The same five documented positions. | Recovery is not continuous. Capture every position and measure the full return trajectory rather than assuming a single exponential. |
| Output | Continuously variable attenuation per channel on the standard unit. | 0.5 dB steps; the manual describes the tube path and attenuator settings needed for unity. | Record both channels independently. Use Output compensation to separate drive effects from simple level changes. |
| HP SC | Switched gentle high-pass weighting in each side chain. Current material calls it about `-3 dB @ 100 Hz`; the manual gives approximate, tolerance-like figures rather than an exact transfer function. | Selectable. | Treat IN/OUT as discrete and identify the actual detector weighting on both channels. Do not implement an ideal 100 Hz brick-wall or assume exact matching. |
| Bypass | Hard-wire bypass. | Hard-wire bypass. | Bypass is useful for end-to-end level and delay checks, but it does not characterize the active transformers, tubes, or gain-control path. Preserve a separate converter loopback. |

### Production changes that block pooling

- Original units used a 6386 variable-gain tube. Manley changed to 5670 in
  June 1996.
- The T-Bar arrangement replaces one dual gain tube per channel with matched
  pairs of 6BA6/12BA6 tubes. The current product page both lists 5670 as
  standard or 6BA6 as T-Bar and says modern units receive T-Bar as standard;
  resolve this contradiction from the actual unit or Manley service.
- Current production uses 12BH7 output tubes from April 2016. Units before
  serial `MSLC94006` are documented with 7044 or 5687 output tubes.
- The stepped Input change is associated with late 2011 and serial
  `MSLC83273` in the manual. Older units used the harder-to-match dual pot.
- Channel gain balance adjustment is documented only for `MSLC82600` and
  later units.

These variants can change drive, distortion, matching, and deep-reduction
behavior. Keep captures from different variants in separate provenance groups
unless measured evidence justifies sharing model parameters.

## SEP, Link, and optional M/S

In SEP/dual-mono operation, the two channels have independent gain reduction.
In stereo Link, Manley says both channels participate and both receive the same
gain change; the unit combines side-chain DC control signals rather than
summing the L/R audio into one detector. The two meters remain independent, and
the manual requires similar settings on both sides. Linking one side in
COMPRESS and the other in LIMIT is not a supported operating state.

Model this first as two audio paths plus a constrained, measured control-state
coupling. Do not begin with a freely learned L/R-to-M/S matrix or assume the
left channel is the master. Determine the unknown Link law with asymmetric
stereo probes.

The optional M/S modification is a different, explicit routing topology. It
uses separate input and output switches that rewire the transformers rather
than an active matrix. With both switches in M/S, Channel 1 processes Mid and
Channel 2 processes Side before decoding back to L/R. In SEP, different Mid and
Side reduction can change width; Link removes that independent width control.
Capture each installed switch state explicitly. Do not add M/S behavior to a
unit that lacks the modification.

The current Mastering product page describes a stereo-only Link arrangement,
while the general manual also covers standard dual-mono and optional M/S
models. The physical unit and its applicable documentation decide which modes
exist.

## Electrical, thermal, and service boundaries

- Balanced XLR is Pin 2 hot. Manley specifies nominal 600 ohm balanced input
  and output for this generation.
- Published maximum output is `+30 dBu` and published maximum gain is `35 dB`.
  These figures do not establish a safe universal maximum stimulus or the
  headroom of the user's converters.
- Record converter dBFS-to-dBu calibration, source impedance, load impedance,
  cabling, loopback response, and active-path level for every campaign. Do not
  normalize individual files.
- The manual recommends about 30 minutes to stabilize for operation and at
  least 45 minutes before internal/service calibration. It specifies a longer
  burn-in before final service calibration after new tubes. External converter
  dBFS-to-dBu calibration is a separate chain measurement. Use a repeatable DUT
  warm-up protocol and log elapsed time; warm-up does not prove either internal
  unit calibration or external chain calibration is correct.
- DC balance can affect distortion, and tube age or replacement can change the
  target response. If calibration, abnormal heat/noise, or tube state is in
  doubt, stop high-level capture and refer the unit to qualified service.
- Do not infer a maximum input level from an old specification, maximum output,
  or converter range. Establish safe pilot levels with calibrated equipment
  and monitor both the hardware and converters before extending the range.

## Manley-specific pilot probes

Run these pilots before committing to a long program-material campaign:

1. **Repeatability and active-path baseline:** after the declared warm-up,
   record converter loopback, hard-wire bypass, and active IN with negligible
   gain reduction at the exact intended source/load conditions. Repeat both
   channels and at least one capture after a fresh thermal cycle.
2. **Input-drive separation:** at safe levels, step through the installed Input
   positions and compensate with Output. Compare active frequency response,
   harmonics, IMD, noise, and channel mismatch with little or no reduction.
3. **Mode and depth:** measure steady transfer curves in COMPRESS and LIMIT in
   both directions at several Input and Threshold settings. Confirm how knee,
   effective ratio, and distortion change beyond modest reduction.
4. **Ballistics:** exercise every Recovery position. Sample the full continuous
   Attack range on a standard unit, or every Attack detent on a Mastering unit.
   Use more than one over-threshold depth, long holds, interrupted bursts, and
   silence long enough to observe the actual multi-stage return.
5. **Link law:** with matched controls, compare left-only, right-only, centered,
   unequal-envelope, correlated, anti-correlated, and uncorrelated stereo
   stimuli. Record both outputs. Treat the GR meters as auxiliary observations:
   log manual readings for steady states or use synchronized video with a stated
   timing/annotation method for trajectories. Do not use meter motion as
   gain-reduction ground truth unless it is independently calibrated. Repeat
   mirrored cases to expose channel asymmetry.
6. **HP SC:** compare IN/OUT with low-frequency-dominant, high-frequency-
   dominant, two-tone, and amplitude-modulated probes. Estimate detector
   weighting and channel tolerance rather than fitting only the audio-path
   response.
7. **Optional M/S:** only when the modification is present, verify each input
   and output switch combination at low level before dynamics tests. Then
   compare independent Mid/Side reduction in SEP with coupled behavior in
   Link.

Any pilot that reveals unstable calibration, unexplained drift, clipping,
intermittence, or a different control topology stops full matrix generation
until the unit identity or service condition is resolved.

## Official sources and known uncertainty

- [Manley current Variable Mu product page](https://www.manley.com/products/pro-audio/dynamics/variable-mu)
  gives the current topology, control ranges, electrical specifications, tube
  revision markers, and the internally inconsistent current T-Bar wording.
- [Manley Variable Mu Owner's Manual, Rev. 5.2](https://www.manley.com/s/VARIABLE-MU-MANUAL-WEB-REV-521.pdf)
  documents front-panel behavior, the feedback and Link descriptions,
  Mastering and M/S modifications, T-Bar history, warm-up, and service-related
  revision markers. Treat its timing and filter figures as nominal until the
  target unit is measured.
- [Manley current Mastering Variable Mu product page](https://www.manley.com/products/pro-audio/mastering/variable-mu-mastering)
  distinguishes the current Mastering control surface and stereo-only Link
  positioning. Confirm the actual hardware because the general manual covers
  several generations and modifications together.

Manufacturer documentation constrains the capture topology; it does not prove
the response of the user's individual unit. Preserve raw measurements and
report any conflict between the target hardware and these sources instead of
silently choosing one description.
