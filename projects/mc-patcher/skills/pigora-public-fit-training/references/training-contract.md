# Pigora public-fit training contract

Use this contract before acquiring data, fitting a Pigora response, or judging
completion. The root `AGENTS.md` remains authoritative if this reference and
the repository diverge.

For the normalized executable inference/exclusion/rate adapter, read
[inference-validation.md](inference-validation.md). For diagnostic sampling and
distinct effective-state coverage, read [curve-coverage.md](curve-coverage.md).
These helpers do not change an existing frozen target or public decision.

## 1. Freeze one evidence domain per identity

Record before optimization:

- manufacturer, model, revision/serial family, and unambiguous Pigora identity;
- source URL, retrieval UTC time, archived URL when available, SHA-256, rights
  or retention limits, document revision, page, figure, trace, and legend;
- source rank: manufacturer numeric/vector data, manufacturer plot/manual,
  documented independent measurement, service document/schematic, patent, or
  corroborating specialist source;
- analyzer/plot conditions, control state, source/load, level, sample rate,
  bandwidth, smoothing, channel, and any unknown condition;
- axis calibration, digitization method, trace selection, point density,
  uncertainty in frequency and dB, rejected regions, and reason;
- eligible response rows, training/withheld/full split, supported sample rates,
  model family, free parameters, falsifier, primary/fallback feasibility receipt,
  and fixed per-row acceptance gate.

Prefer raw numeric or vector response data. A raster plot enters the 0.2 dB tier
only when its axes, legend, target trace, control state, and resolution make that
judgment defensible. It may enter the 0.5 dB fallback tier only through the
reviewed procedure below. Never increase apparent precision by exporting more
pixels or interpolated points than the source resolves.

## 1A. Image-derived curve target gate

After source search and before any fitting, create and freeze a complete finite
curve target. An optimizer must not calibrate a raster image, choose a trace, or
adjust DSP parameters while simultaneously judging the same response. Preserve
the original PDF/image, SHA-256, page/figure/crop, render resolution, target
trace/control state, and every rejected or occluded region. The target producer
must be a reproducible, versioned extraction pipeline, not an undocumented
manual screenshot calibration.

1. **Calibrate both axes.** Record every usable tick/grid anchor and its source
   coordinate. Use a log-frequency mapping when the source frequency axis is
   logarithmic and the source's dB mapping on the vertical axis. Require at
   least two anchors per axis and use three or more when available; solve the
   mapping from all accepted anchors and record max/RMS residuals. Freeze a
   dataset-specific `pixel_axis_match_tolerance` in pixels before extraction.
   Convert calibration residuals to pointwise frequency/dB uncertainty through
   the frozen axis mapping; an axis ambiguity or residual that cannot support
   the declared target gate invalidates that image region. Do not extrapolate
   outside calibrated anchors. Enlargement, screenshot pixels, and display
   interpolation never add evidence precision.
2. **Extract every declared curve.** Resolve legend, identity/revision, control
   state, polarity/sign, overlapping traces, and source conditions first. Extract
   the trace centerline with the frozen color profile, anti-alias/preprocessing
   pipeline, extraction algorithm and parameters, and source-supported adaptive
   point density. Do not smooth away extrema, bridge an occlusion, or silently
   select only convenient curves. Record an explicit rejection reason for each
   unusable segment. A gap may be bridged only by a separately named,
   source-bounded human-supplement transform and must receive a generated-row
   provenance label.
3. **Stabilize the target.** Use two independently parameterized extraction
   passes or one extraction plus an independent reviewer. Freeze
   `trace_pass_agreement_tolerance_db` in dB before extraction and use the centerline
   median only where passes represent the same trace and agree within that
   tolerance. Resolve or mark disagreements unresolved; never pick the prettier
   trace. Freeze the accepted centerline, pointwise frequency/dB uncertainty,
   calibration residual, trace-width/pass-spread components, and completeness
   manifest. For each target point, set `u_pass_spread_db` to the maximum
   absolute deviation of accepted passes from their median, convert calibration
   residual to `u_axis_db`, and set conservative target uncertainty to at least
   `u_axis_db + u_trace_width_db + u_pass_spread_db + u_source_digitization_db`.
   A raster target may enter the public 0.2 dB tier only when this
   uncertainty and resolution support it; uncertainty above 0.5 dB proves
   neither public tier.
4. **Complete the target before fitting.** If the image is sparse, under-
   resolved, or partially occluded but identity, topology, control mapping,
   anchors/endpoints, and a deterministic source-bounded transform are known,
   fill the entire declared finite target grid before optimization. Preserve
   `measured` and `image-digitized` anchors. Label generated values
   `human-supplemented-curve`, or use `human-supplemented-gain`/
   `human-supplemented-frequency` only when those exact contract transforms
   apply. Record the parent trace, transform/rationale, donor and recipient
   domain, reviewer, pointwise uncertainty, and rejected regions. Permitted
   transforms include frozen log-frequency interpolation, the authorized gain
   or frequency transfer, paired-baseline inference, and other explicitly
   source-bounded shape-preserving transforms; a human may choose among them,
   but may not invent an unsupported peak, topology, phase, interaction, or
   level dependence. If no unique transform is defensible, keep the public
   response withheld rather than manufacturing a public curve.
5. **Prove completeness and freeze provenance.** Every in-scope finite target
   point must be `measured`, `image-digitized`, or one of the labeled
   human-supplemented states, or have an explicit ineligible/rejected reason.
   There may be no silent holes. Freeze the target artifact/hash, calibration
   manifest, extraction/review receipt, full-grid counts, provenance, uncertainty,
   and rejected regions in the evidence ledger before fitting. The fitting
   configuration must include the exact `image_target_id` and `target_grid_hash`;
   a validator must reject a missing or mismatched hash. Human-supplemented
   values stay outside `public-fit-domain.csv`, in the separate inference target
   domain, and must pass the fixed 0.2 dB engineering gate at 48 kHz. A
   separately recorded `sample-rate-engineering-0.5` gate may be used only for
   rates strictly above 48 kHz after that baseline passes.

The image-target manifest must contain at least:

```text
image_target_id,source_sha256,page_figure_crop,render_resolution,trace_id,control_state,axis_mapping,axis_anchor_count,axis_residual_max,pixel_axis_match_tolerance,trace_pass_agreement_tolerance_db,target_grid_hash,point_count,rejected_region_count,target_provenance,uncertainty_db,reviewer,review_decision_id
```

`target_provenance` is `image-digitized` for accepted trace values and one of
the `human-supplemented-*` values for generated values. The target-grid hash,
point count, uncertainty, rejected regions, and review decision must bind to
the exact artifact consumed by fitting. The extraction manifest must also
record the renderer/version, color profile, preprocessing/extractor version,
parameter hash, resampling rule/version, and coordinate convention. The
point-level completeness manifest must contain at least:

```text
image_target_id,point_id,frequency_hz,target_value_db,status,target_provenance,parent_trace_id,transform,rejected_reason,uncertainty_db
```

`status` is `accepted`, `human-supplemented`, `rejected`, or `ineligible`; every
finite in-scope target point is accepted or human-supplemented, and every other
point has a non-empty rejection/ineligibility reason.

## 1B. Sample-rate-stratified engineering gate

This is a validation rule for the same frozen production target, not a public
evidence fallback. The exact baseline rate is 48,000 Hz. Before any relaxed
high-rate result can be accepted, every declared 48 kHz row for the same
identity, controls, target artifact/grid hash, and production response path must
pass the inclusive worst-row gate:

```text
baseline_rate_hz = 48000
baseline_gate_db = 0.2
abs(predicted_magnitude_db - target_magnitude_db) <= baseline_gate_db
```

For each independently tested `sample_rate_hz > 48000`, reuse the exact frozen
target artifact, target/grid hash, identity, control-state domain, and declared
frequency domain. The high-rate engineering gate may then be:

```text
gate_kind = sample-rate-engineering-0.5
gate_db = 0.5
abs(predicted_magnitude_db - target_magnitude_db) <= gate_db
```

The exception is strictly `sample_rate_hz > 48000`; it does not apply to 48 kHz,
lower rates, or a high-rate public-source claim. Test each high rate separately
and report its complete row count and worst row. A 48 kHz failure, target hash
mismatch, missing control/state row, or unresolved target provenance blocks the
relaxed gate. A high-rate failure at 0.5 dB remains a failure; do not average,
expand, or transfer the threshold from another rate. High-rate engineering
counts and `sample-rate-engineering-0.5` decision IDs remain separate from
public-fit counts, public splits, public `fallback-0.5` IDs, withheld counts,
and the inference base gate. If the high-rate rows themselves are admitted to
the public evidence domain, they must still use the public 0.2 dB contract.

Freeze a non-author-reviewed sample-rate receipt before judging the high-rate
candidate. It must bind `baseline_rate_hz`, the passing 48 kHz decision ID,
`sample_rate_hz`, target/grid hash, control/state coverage, conditions, row
counts, worst row, `gate_kind`, `gate_db`, and a unique high-rate decision ID.

## 2. Required web-research coverage

When establishing or materially revising a device/revision's source domain,
run and record at least these angles until the source set is saturated. For an
unchanged, archived, hash-bound domain, resumption, numerical adjudication, and
production integration reuse the accepted search receipt; repeat source work
only for a concrete provenance gap, changed identity/scope, conflicting evidence,
or an explicit request to refresh sources.

1. current manufacturer product/support/manual pages and direct downloads;
2. manufacturer or distributor archives plus the Internet Archive for removed
   manuals, plots, datasheets, and service documents;
3. exact model plus `frequency response`, `measurement`, `Audio Precision`,
   `service manual`, `schematic`, `circuit diagram`, drawing numbers, and known
   revision aliases;
4. patents, standards, technical papers, and documented independent analyzer
   captures with raw/vector data or enough stated conditions to reproduce them;
5. conflicts and revision drift, using a second identity anchor before merging
   sources.

During source acquisition, open every accepted URL in that source-search task.
Search snippets, marketing prose,
plug-in screenshots, forum recollection, and a competitor's emulation are not
quantitative targets. A secondary archive can preserve a manufacturer document,
but record both the document identity and archive provenance.

## 3. Measurement and circuit roles

Public response measurements define the magnitude target. A schematic may:

- identify series, parallel, feedback, passive, or boost/attenuate topology;
- bind switch positions and component networks to native controls;
- constrain plausible component values, poles/zeros, Q, stage order, loading,
  and parameter sharing;
- falsify a convenient but topologically incompatible model family.

A schematic alone does not prove the manufactured response when component
values, revisions, tolerances, transformers/inductors, source/load, calibration,
or surrounding stages are unknown. Use circuit simulation as a bounded prior or
candidate generator and accept it only against an external response target.

### 3A. Owner-authorized sparse gain and frequency inference

The project owner authorizes a deterministic human-supplemented target layer
for Pigora EQ magnitude fitting when the best accepted public source does not
measure every required gain step or native frequency. This rule completes a
sparse magnitude gain/frequency grid only within an already identified,
topology-compatible section and boost/cut family; it does not authorize
inference of a missing native mode, topology, interaction, phase, level
dependence, or complete hardware behavior. It does not turn generated values
into public measurements or public-fit rows. If the frozen public-fit domain
has zero eligible rows, use §3B instead of §3A.

If no same-path baseline/bypass measurement exists, first apply the strict
paired boost/cut midpoint method `paired-midpoint-median-v1` whenever a valid
pair exists. A valid pair must match device/revision, section/control family,
mode, topology/routing, measurement conditions, native frequency, and aligned
source vector vertices. Freeze the complete pairing key and the dataset-specific
`vertex_match_tolerance` before fitting. At each expected vertex, require
exactly one finite boost value and one finite cut value within that tolerance;
missing values and ambiguous duplicates invalidate that point and are never
silently interpolated or deduplicated. Its boost and cut gains must be finite,
nonzero, and equal in the frozen numeric gain units. At each
vector-frequency point compute:

```text
midpoint_db(f,r,G) = 0.5 * (boost_trace_db(f,r,+G) + cut_trace_db(f,r,-G))
baseline_db(f) = median({midpoint_db(f,r,G) for every valid (r,G) at f})
```

Pool the individual valid pair midpoints across native frequencies and gain
magnitudes at each vector-frequency point. Each pair contributes once; never
take a median of per-frequency medians. For even counts use the mean of the two
central sorted values. Freeze `baseline_aggregation=pooled-valid-pairs-v1`.
For example, groups `[0,0,0]` and `[0.4]` give `0 dB`, not `0.2 dB`.
Existing frozen targets keep their recorded values and actual aggregation;
correcting a different aggregation requires a reviewed new target version,
not retroactive modification or a silent change under an old target hash.

The median is taken per vector-frequency point, not as one global scalar. Use
the paired median wherever at least one valid pair covers the point. If a point
has no valid pair, use flat `0 dB` only at that point, set
`baseline_provenance=assumed-paired-boost-cut-midpoint-median+assumed-flat-0dB-uncovered`,
and record its uncovered-point count; if no valid pair covers the target grid,
use the full flat fallback with `baseline_provenance=assumed-flat-0dB`. Use only measured pair support; do not pair
mismatched gains, conditions, identities, topologies, or unaligned vertices,
and do not extrapolate beyond the pair's measured gain/frequency support. Record
`baseline_provenance=assumed-paired-boost-cut-midpoint-median`,
`baseline_method_version=paired-midpoint-median-v1`, pair counts, native
frequency count, source curve IDs, conflict MAD, and uncertainty. Define
pointwise conflict MAD as the median absolute deviation of all valid pair
midpoints at that vector-frequency point; record the ledger-level
`baseline_conflict_mad_db` as the maximum of those values over the finite target
grid. For finite source uncertainties `u_boost` and `u_cut`, use the conservative
per-pair propagated bound `0.5 * (u_boost + u_cut)` and set the recorded baseline
uncertainty to at least the larger of that bound and the conflict MAD. A flat
fallback must carry a separately frozen finite assumption uncertainty; it is not
implicitly zero. A measured
baseline or accepted evidence takes precedence; resolve any conflict before
fitting. The inferred baseline is not public evidence, cannot enter
`public-fit-domain.csv`, and cannot change the public-fit/evidence-policy state.

Only when no strict valid pair exists may the inference layer use the last-resort
default `baseline_db(f) = 0 dB` over the finite target grid. Record
`baseline_provenance=assumed-flat-0dB` and the reason no pair was available, and
include that assumption in inference uncertainty. Missing baseline measurement
alone is therefore not a stop condition, but an unresolved conflict or
materially different plausible baseline remains a stop condition.

For a measured boost or cut trace, with the declared baseline (same-path
measured, strict paired, or the permitted uncovered-point flat fallback), derive
a lower absolute gain step by percentage scaling in the dB domain. The baseline, measured trace,
`measured_gain_db`, and `requested_gain_db` must be finite, and
`abs(measured_gain_db) > 0`:

```text
measured_delta_db(f) = measured_trace_db(f) - baseline_db(f)
gain_scale = abs(requested_gain_db) / abs(measured_gain_db)
target_delta_db(f) = measured_delta_db(f) * gain_scale
```

- Require `0 <= gain_scale <= 1` (equivalently,
  `0 <= abs(requested_gain_db) <= abs(measured_gain_db)`); extrapolation beyond
  the largest measured absolute gain needs a separate owner decision.
- Keep boost and cut as separate donor families. Preserve the neutral state at
  zero baseline-normalized dB.
- When several gain steps are measured, freeze measured ratios or interpolate
  between adjacent bracketing steps; prefer the closest bracketing pair.
- The donor gain magnitude must be numerically identifiable. A qualitative
  `boost` or `cut` label alone cannot define a percentage unless the owner makes
  and records an explicit numeric assignment.

When gain/attenuation steps are sufficiently sampled at a measured frequency or
frequency family but another documented native frequency is missing, reuse the
same frozen gain percentages at the missing frequency. Evaluate the production
section at the documented recipient frequency. The donor supplies the
gain/attenuation law; do not silently copy an absolute-frequency curve or merge
distinct identities. Record the donor frequency/family, recipient frequency,
section kind, frequency mapping, and topology-compatibility basis.

Before optimization, export a separate UTF-8 inference ledger with one row per
generated curve/control state and at least:

```text
target_id,target_provenance,product_use_state,baseline_provenance,baseline_method_version,baseline_pair_count,baseline_native_frequency_count,baseline_source_curve_ids,baseline_conflict_mad_db,baseline_uncertainty_db,baseline_uncovered_point_count,baseline_selection_reason,vertex_match_tolerance,parent_source_claim_id,parent_curve_id,donor_frequency_hz,recipient_frequency_hz,measured_gain_db,requested_gain_db,gain_scale,transform,uncertainty_db,reviewer,decision_id
```

For newly frozen paired-baseline targets also record
`baseline_aggregation=pooled-valid-pairs-v1`. Existing target versions retain
their actual aggregation and are not rewritten to satisfy a new schema.

Accepted source rows are `measured` or `image-digitized`; generated rows must be
`human-supplemented-gain`, `human-supplemented-frequency`, or
`human-supplemented-curve`. Image-digitized rows may enter the public domain
only when the image target gate and declared public error tier pass. All
human-supplemented rows remain in the separate inference domain.
`product_use_state` is reported independently from public-fit/evidence-policy
state and may be `product-selectable — inference-derived` only after identity,
control mapping, finite declared grid, baseline provenance, boundaries,
engineering, and safety/integration checks pass. Freeze measured/inferred counts,
the declared finite native gain/frequency grid, a fixed 0.2 dB worst-row
engineering target at 48 kHz, and any separately recorded
`sample-rate-engineering-0.5` targets above 48 kHz before fitting. This is an
engineering consistency gate against the deterministic inferred target, not
external public evidence. A
non-author reviewer checks every donor, recipient, scale, generated state, and
omission.

Keep this ledger and its evaluation outside `public-fit-domain.csv`. Inference
evaluation uses a separate schema and must not use public-domain split labels,
public gate decision IDs, or public withheld counts. Generated rows do not
receive primary/fallback public-fit decision IDs, do not count as public-fit
passed rows, do not change point-response public-fit/evidence-policy state, and
cannot dilute a measured public worst row. The public 0.5 dB fallback never
applies to inference rows. Report their hashes, counts, errors, and regression
status separately as `inference-derived/source-informed approximation`.

Sparse gain or frequency coverage therefore does not stop the authorized
product implementation/engineering fit when this rule produces a unique target.
If its separate engineering and integration gates pass, the result may be
product-selectable while remaining `public-fit withheld/partial` or
`not publicly specified`. Public-fit/evidence-policy state and product
usability are separate states; `public-fit withheld` does not by itself mean
`product-ineligible`. Stop the inference layer too when the donor gain magnitude
is unknown, an observed baseline contradicts the declared flat-baseline default
without a defensible resolution, topology/sign mapping is unresolved, the
implementation is unsafe, or materially different targets remain possible after
the authorized transform. Missing baseline measurement alone is not a stop
condition because the declared flat-baseline default applies.

The sample-rate receipt must be separate from the inference ledger and contain
at least:

```text
sample_rate_gate_id,identity_id,baseline_rate_hz,baseline_gate_db,baseline_decision_id,sample_rate_hz,target_grid_hash,control_state_coverage,condition_id,row_count,worst_error_db,gate_kind,gate_db,decision_id,status
```

Use `gate_kind=sample-rate-engineering-0.5` only for `sample_rate_hz > 48000`
after the 48 kHz receipt passes. Do not use `fallback-0.5` for this rule.

### 3B. Owner-authorized donor-curve inference-only contract

Use this contract when the required source search is complete and the frozen
public-fit domain has **zero eligible rows**, or when the owner explicitly
scopes a named identity subset to inference-only engineering. It covers hardware
EQ cases where public evidence is too sparse for any public-fit row but one or a
few official or public magnitude curves can still support a deterministic
engineering target. It is separate from §3A sparse-grid completion, which
requires at least one accepted measured or image-digitized public row inside an
already identified section; §3B never creates public-fit rows and never upgrades
public-fit status from an inference pass.

#### Preconditions

1. Record the completed source search, conflicts, and why zero rows enter
   `public-fit-domain.csv` or why named identities are inference-only.
2. Freeze per-identity public-fit/evidence-policy states before inference work.
3. Obtain explicit owner authorization naming device/revision, in-scope
   identities, excluded submodules, donor sources, transforms, finite native
   gain/frequency grid, engineering gates, and the claim boundary
   (`inference-derived/source-informed approximation` only).
4. Do not invoke this contract merely because public-fit optimization is
   inconvenient or because a plot failed the public 0.2 dB or reviewed 0.5 dB
   fallback tiers.

#### Scope and exclusions

Declare every in-scope native identity and every excluded submodule, stage, or
control family before target generation. Export a UTF-8 exclusion ledger with at
least:

```text
identity_key,module_type,model_name,point_kind,selector,fixed_frequency_hz,exclusion_scope,exclusion_reason,public_fit_state,product_use_state,decision_id
```

Excluded identities retain their frozen public-fit/evidence-policy states.
The exclusion ledger contains every excluded identity; the point-specific
withheld ledger contains only identities whose evidence-policy decision is
`withheld`. Exclusion alone does not change an NPS identity's policy. Excluded
identities receive no inference target rows and are not
`product-selectable — inference-derived`.
Documented control ranges, nominal slopes, or qualitative descriptions alone
do not authorize inference for an excluded or unscoped identity. Example
(non-normative): a high-pass filter section may be excluded when only range and
nominal slope are public and no numeric donor exists.

#### Inference donors

Accept one or a few official or public magnitude curves per section/control
family. Each donor record must freeze:

- source artifact URL or archive path, SHA-256, page/figure/crop, trace identity;
- section/control family, boost/cut family, topology/routing basis;
- donor native frequency, finite donor gain magnitude, baseline method;
- extraction or digitization pipeline, conditions, point density, uncertainty;
- recipient identity, frequency mapping rule, and topology-compatibility basis.

Donor provenance is `inference-donor`. Donor curves stay outside
`public-fit-domain.csv` even when extracted from the same PDF or plot that
failed the public target gate. When legend or gain labels are missing, the owner
may record one reviewed donor binding with numeric assignment, rationale, added
uncertainty, reviewer, and decision ID. If two or more donor bindings remain
materially plausible, stop rather than selecting the prettier trace.

#### Permitted transforms

From each frozen donor and declared baseline:

1. **Gain scaling.** Use the §3A baseline-normalized percentage rule with
   separate boost/cut families, neutral zero row, and no extrapolation beyond
   the largest measured absolute gain without a separate owner decision.
2. **Frequency transfer.** Move a donor shape to another documented native
   frequency detent by direct frequency shift of the donor center or corner
   frequency to the recipient native frequency, preserving shape in the log-
   frequency domain unless the source specifies otherwise. Alternatively apply a
   separately declared frequency mapping such as catalog center frequency to
   documented panel center frequency; freeze the mapping rule, reviewer,
   uncertainty, and every affected recipient identity.
3. **Baseline.** Reuse measured same-path baseline, strict paired boost/cut
   midpoint `paired-midpoint-median-v1`, or declared flat `0 dB` exactly as in
   §3A. A measured baseline takes precedence over any inferred baseline.

Do not invent peaks, topology, interaction, phase, level dependence, or
continuous controls beyond the declared finite native grid.

#### Inference-only ledger and evaluation

Before optimization, export a separate UTF-8 inference-only ledger extending the
§3A schema with at least:

```text
contract_kind,target_id,target_provenance,product_use_state,public_fit_state_unchanged,inference_donor_id,inference_donor_binding_reason,excluded_identity,donor_frequency_hz,recipient_frequency_hz,frequency_mapping_rule,measured_gain_db,requested_gain_db,gain_scale,transform,baseline_provenance,baseline_method_version,baseline_pair_count,baseline_conflict_mad_db,baseline_uncertainty_db,uncertainty_db,reviewer,decision_id
```

Accepted values:

- `contract_kind = donor-curve-inference-only`
- `target_provenance = inference-donor`, `human-supplemented-gain`,
  `human-supplemented-frequency`, or `human-supplemented-curve`
- `product_use_state = pending_engineering_gate` until gates pass, then
  `product-selectable — inference-derived`
- `public_fit_state_unchanged` records the frozen public state, for example
  `not publicly specified` or `public-fit failed/withheld`

Evaluate only against this separate inference target grid. Use the fixed 0.2 dB
worst-row engineering gate at 48 kHz. High rates strictly above 48 kHz may use
only the separately recorded `sample-rate-engineering-0.5` gate after the 48 kHz
inference baseline passes. Do not use public-domain split labels, public gate
decision IDs, public withheld counts, or the public 0.5 dB fallback for these
rows. Report hashes, counts, worst rows, and regressions separately as
`inference-derived/source-informed approximation`.

#### Reporting separation

| Layer | Typical state while §3B proceeds | May inference pass change it? |
|---|---|---|
| Public-fit / evidence policy | `not publicly specified` or `public-fit failed/withheld` | No |
| Withheld ledger | Exactly evidence-policy-withheld points; not all inference exclusions | No |
| Product use (in-scope) | `product-selectable — inference-derived` after engineering gates | Yes, product layer only |
| Product use (excluded) | Not product-selectable for inference | No |
| Claim tier | `inference-derived/source-informed approximation` | Never upgrades to public-source fit |

#### Stop conditions

Stop the §3B layer when:

- donor gain magnitude or donor native frequency cannot be bound;
- revision, topology, control-sign, or boost/cut family mapping is unresolved;
- the frequency mapping is not uniquely declared;
- an excluded submodule would be silently filled;
- measured baseline evidence conflicts with the declared baseline without
  resolution;
- two or more materially different targets remain after the authorized transform;
- a hard safety or authorization boundary blocks the next isolated step.

Missing public-fit rows alone is not a stop condition once §3B is authorized.
Missing donor identity, exclusion discipline, or a unique transform still is.
A failing engineering gate rejects the candidate and blocks release, not the
authorized fitting task. Preserve its receipt and follow §5 with the next
bounded, defensible hypothesis. An unsafe realization cannot ship; isolated
remediation may continue only within the safety boundary. If no defensible next
hypothesis remains, report the engineering blocker. Never override protected
holdout access, a user pause, or an explicit attempt limit to continue.

## 4. Evaluation domain and CSV

Export a frozen UTF-8 domain CSV containing every eligible target row with
exactly these columns:

```text
identity_id,source_claim_id,curve_id,split,sample_rate_hz,control_state,frequency_hz,target_magnitude_db,source_uncertainty_db,gate_db,gate_decision_id
```

Export a separate evaluation CSV with exactly these columns:

```text
identity_id,source_claim_id,curve_id,split,sample_rate_hz,control_state,frequency_hz,target_magnitude_db,predicted_magnitude_db,source_uncertainty_db,gate_db,gate_decision_id
```

- `split` is `training`, `withheld`, or `full`.
- `gate_db` is exactly `0.2` or `0.5`. `gate_decision_id` binds the row to the
  frozen primary or reviewed fallback receipt.
- The public domain CSV uses only public-fit gate decisions. High-rate
  `sample-rate-engineering-0.5` rows belong in the separate sample-rate receipt
  and engineering evaluation output; they do not change public-fit status.
- Domain numbers must be finite and `source_uncertainty_db` must be between
  0 and that row's `gate_db` inclusive. A source more uncertain than 0.5 dB
  cannot prove either tier.
- Each domain row is unique by source claim, curve, split, sample rate,
  control state, and frequency.
- One curve/control-state partition belongs to only one of `training`,
  `withheld`, or `full`; never relabel adjacent points from the same curve as an
  independent holdout.
- `target_magnitude_db` is the frozen public target. `predicted_magnitude_db`
  comes from the production response path, not the fitting helper's duplicate
  formula.
- Normalize only by a reference/bypass rule frozen before fitting. Do not apply
  a post-hoc per-curve gain or frequency shift unless that transformation is
  explicitly part of the source contract and is applied identically to every
  candidate.
- For vector/numeric sources, retain all defensible source samples or a frozen
  anti-aliased resampling rule. For raster sources, use only independently
  resolvable rows; interpolated display pixels are not new evidence.
- Exclude frequencies outside the source plot, below its noise/resolution mask,
  or at/above the supported digital Nyquist boundary. Record them as ineligible
  with a reason in the ledger; they do not enter the frozen domain CSV.

The validator requires the evaluation to match the frozen domain row-for-row,
including targets and uncertainty. It rejects missing, added, or duplicate rows,
then requires every row to satisfy `abs(error) <= gate_db` and reports primary
and fallback counts plus the global worst row. It also checks the domain against
the SHA-256 recorded by a non-author
coverage review. Before optimization, that reviewer must compare the domain
against every declared source fixture/trace, record included and excluded counts
per identity/curve/control/rate, and reject convenient omissions. This prevents
a passing run from shrinking the domain to one easy row.

## 5. Search-fit persistence

On a failed gate:

1. sort failures by absolute error and inspect the worst local region;
2. decide whether evidence extraction, topology, control mapping, interpolation,
   sample-rate conversion, or production translation owns it;
3. state a falsifiable candidate and change only its owning layer;
4. rerun the affected curve, then all eligible curves if it passes;
5. after two failed changes under the same hypothesis, preserve the evidence,
   add a diagnostic, and reassess the model family or source interpretation.

Continue while at least one defensible model/source hypothesis remains. Do not
stop merely because optimization converged, training loss flattened, the
average is green, or only a narrow frequency region fails.

## 6. Reviewed 0.5 dB fallback

This section governs only the public evidence fallback. The separate
`sample-rate-engineering-0.5` rule in §1B is not a public fallback and must not
use this receipt or decision ID. For public fitting, the fallback is a lower
evidence floor, not an automatic second attempt. Start
every row at 0.2 dB. A row may move to 0.5 dB only when a non-author reviewer
records one of these before the fallback candidate is judged:

- the best verified public plot/data has quantified uncertainty above 0.2 dB
  but no greater than 0.5 dB after source search and digitization audit; or
- two bounded, topology-compatible fitting attempts plus sensitivity analysis
  show that the public source cannot identify a unique response within 0.2 dB,
  while it can support a 0.5 dB bound without inventing behavior.

The receipt identifies exact rows, failed 0.2 results, sources/searches,
uncertainty or sensitivity evidence, reviewer, UTC time, and a unique
`gate_decision_id`. Re-freeze and re-hash the domain after changing those rows.
Do not lower an entire curve or module when only named frequency points need the
fallback. Current code architecture, compute cost, elapsed training time, or one
poor candidate is not a valid fallback reason. A 0.5 dB pass must be reported as
`fallback-0.5`; never present it as a 0.2 dB pass.

## 7. Point-specific withheld ledger

Export UTF-8 CSV with exactly these columns:

```text
identity_key,module_type,model_name,point_kind,selector,fixed_frequency_hz,catalog_claim_status,public_fit_state,evidence_policy_reason,reason_code,source_claim_id,missing_evidence,decision_id
```

- `identity_key` is exactly `module_type:point_kind:selector` and joins one row
  in the frozen native point catalog.
- `module_type`, `model_name`, `point_kind`, `selector`,
  `fixed_frequency_hz`, and `catalog_claim_status` must exactly match that
  catalog row. `fixed_frequency_hz` must be finite and positive.
- One row represents one EQ module/filter/selector frequency point. No wildcard,
  `all`, model-wide pseudo-row, range, empty selector, or duplicated identity is
  allowed. If the whole module lacks evidence, enumerate all its catalog points.
- `public_fit_state` and `evidence_policy_reason` must match the point-response
  evidence policy. Only policy-withheld identities appear; the ledger must cover
  all of them and no allowed identity.
- `reason_code` is one of `missing_numeric_response`,
  `source_uncertainty_over_fallback`, `identity_revision_ambiguous`,
  `source_conflict`, `control_state_unbound`, `fallback_gate_failed`, or
  `unsafe_or_unexpressible`.
- `source_claim_id` names the blocking source claim, or literal `none` after the
  required search finds none. `missing_evidence` states the smallest concrete
  numeric curve, control-state binding, or revision artifact needed.
- `decision_id` binds the point to a reviewed withholding decision. Passing one
  point removes only that exact row; neighboring points remain unchanged.

Run `validate_withheld_points.py` against the frozen catalog and authoritative
point-response evidence CSV. A broad prose status is not a substitute.

## 8. Severe evidence deficiency test

The exceptional stop is allowed only when all applicable search angles above
were attempted and at least one of these prevents even an honest 0.5 dB
fallback judgment:

- target identity or revision remains ambiguous;
- public sources materially conflict and no ranked resolution is defensible;
- no quantitative response exists for an in-scope control state or trace;
- plot/digitization uncertainty exceeds 0.5 dB in the required region;
- missing axes, legend, conditions, loading, or calibration permit materially
  different curves inside the requested domain;
- the available schematic is incomplete or revision-ambiguous and the unknown
  parameters admit responses differing by more than 0.5 dB, with no public
  measurement capable of identifying them.

Produce an evidence-block report with the exact identity/control/region,
verified URLs and retrieval results, source conflicts, quantitative uncertainty
or sensitivity bounds, searches exhausted, and the smallest missing artifact
that would unblock training. Withhold only the unsupported response; do not turn
an unpublished out-of-scope axis into failure for an otherwise passing public
subset. When zero public-fit rows exist but explicit owner authorization and
§3B preconditions are satisfied, continue the separate donor-curve inference
layer without changing public-fit status.

## 9. Acceptance statement

A completion statement names:

- number of identities, curves, eligible rows, sample rates, and control states;
- training, withheld, and full counts and whether an independent holdout exists;
- primary/fallback row counts, each fallback decision ID, and global worst
  absolute magnitude error with its source/curve/state/rate/frequency/gate;
- withheld counts by module/filter kind and exact point-ledger validator result;
- exact validator and targeted regression results;
- claim tier `public-source fit` and every not-publicly-specified axis;
- separate measured-public and inference-derived row counts, hashes, worst
  errors, decision IDs, and regressions whenever sparse-grid completion (§3A)
  or donor-curve inference-only work (§3B) is used;
- explicit §3B exclusion-ledger coverage and unchanged public-fit states for
  excluded identities whenever donor-curve inference-only work is used;
- production/deployment/hosted status as separate facts.

Never shorten this to unqualified `100% hardware fit`.
