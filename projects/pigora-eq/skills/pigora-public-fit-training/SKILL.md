---
name: pigora-public-fit-training
description: >-
  Research, fit, and validate Pigora hardware-EQ magnitude responses against
  frozen public evidence or owner-authorized inference targets. Use for target
  extraction/completion, coefficient or control-law fitting, and response
  acceptance. Keeps public-fit, inference engineering, and product readiness
  separate. Do not use for GUI-only work or private-capture training.
---

# Pigora public-fit training

This skill owns target provenance, the fitting loop, and response adjudication.
The current root `AGENTS.md` is authoritative. Never weaken a frozen target,
threshold, native identity, control mapping, or claim to make a candidate pass.

## Route by the current phase

Read the applicable reference completely before acting. Reuse instructions
already read in this context when unchanged; after resumption verify the current
artifact and authorization before rerunning work. Do not redo a completed source
search or refit solely because a task resumed.

| Current phase | Required guidance |
|---|---|
| Status or handoff inspection | Current artifact-backed receipt, scope, hashes, and root contract; load further guidance only to judge a disputed result |
| New source search, extraction, or target completion | [training-contract.md](references/training-contract.md); `web-research` for live source work |
| Model/control-law choice or fitting | Training contract, [fit-efficiency.md](references/fit-efficiency.md), [curve-coverage.md](references/curve-coverage.md), and `hardware-audio-emulation` |
| Public response adjudication | Training contract and the public validator below |
| Inference or sample-rate engineering adjudication | Training contract and [inference-validation.md](references/inference-validation.md) |
| Post-fit measurement, smoothness, or owner 0.5 dB fallback | [smoothness-execution.md](references/smoothness-execution.md) for plan/preflight; [measurement-acceptance.md](references/measurement-acceptance.md), [smoothness-gate.md](references/smoothness-gate.md), training contract §1D/§6, and the production control-shape gate |
| Runtime scope inventory or architecture feasibility | Training contract §1C for the rate-dependent support matrix; [fit-efficiency.md](references/fit-efficiency.md) for bounded feasibility probes |
| Production integration, build, or hosted verification | Training contract §1C, `mc-patcher` and its Pigora handoff reference; `vst-plugin-ui` only if editor/binding work is in scope |

When a fitting or runtime design explicitly draws on Airwindows EQ code, read
[airwindows-eq-dsp.md](references/airwindows-eq-dsp.md). It supplies candidate
filter structures and falsifiers, never a target curve, native-control claim,
or shortcut around the frozen Pigora acceptance gates.

Use `orchestrator` for authorized independent packages and shared-resource
coordination, not to add a controller or repetitive approval turns. An existing
module-specific validator may be reused through the documented normalized
adapter; this skill does not authorize rewriting its frozen artifacts.

## Keep the acceptance layers separate

- **Public-fit:** every eligible row passes inclusive absolute error
  `<= 0.2 dB`, or a separately reviewed and predeclared public `fallback-0.5`
  under training-contract §6. Compute inconvenience is not a fallback reason.
- **Inference engineering:** separate target/ledger, primary `<= 0.2 dB` at
  48,000 Hz. The distinct reviewed owner measurement fallback may admit
  `<= 0.5 dB`; it is not public fallback and uses no public splits or public
  withheld counts. Preserve legacy strict-validator results.
- **Higher-rate engineering:** only after complete 48 kHz success, each
  separately declared rate strictly above 48 kHz may use
  `sample-rate-engineering-0.5`. Reuse the exact target/grid and scope;
  lower rates do not receive this exception. A high-rate public-source claim
  still requires the applicable public gate. A 48 kHz measurement fallback
  cannot unlock this named exception; use separate per-rate measured acceptance.
- **Measured response and smoothness:** contract
  `pigora-eq-measurement-acceptance-20261001-v1` requires a complete actual
  production-audio certificate before fitting/module/product validation PASS.
  Every required measured row starts at inclusive worst-row `<= 0.2 dB`,
  and objective smoothness must also pass. After recorded bounded corrections
  and diagnosis show 0.2 dB remains unattainable, prioritize the separately
  reviewed exact 0.5 dB fallback. It never waives smoothness or upgrades
  inference provenance. Read measurement-acceptance for coverage, receipts and
  the prospective exception to older unconditional 0.2 dB-only wording.
- **Product acceptance:** production response, control mapping, numerical and
  realtime safety, integration, and required hosted checks are additional gates.
  Numeric, serialization, or installed-binary passes do not prove them all.
  Before module/product PASS, run the mandatory compact control-shape gate in
  [curve-coverage.md](references/curve-coverage.md#compact-production-control-shape-gate).
  Count Bell, Low Shelf, High Shelf, HPF and LPF as separate acceptance units
  wherever supported, with their native modes and applicable controls.
  Owner addendum `pigora-eq-compact-extrema-smoothness-20261006-v2` requires
  exact maximum boost/cut combined with frequency and Q/shape limits, actual
  audio for each required matrix state, and a frozen numeric smoothness profile.
  Reduced interior sampling cannot omit extrema. Report `compact_matrix_status`
  separately; original fitting gates, matrix and smoothness must all pass for
  new fitting/module/product acceptance. See the references for scope and metrics.
  Construct the required [execution plan](references/smoothness-execution.md):
  admitted/excluded units, exact track contexts/near-zero steps, explicit rates,
  applicable metrics and numeric profiles. Missing inputs mean PENDING; READY
  is not acceptance. Preserve legitimate neutral-feature NOT_APPLICABLE reasons,
  and aggregate confirmed FAIL before PENDING before PASS. Candidate-generated
  explanations cannot close a diagnostic finding without permitted evidence.
  Unresolved shape findings block that PASS even when target rows pass; keep
  public-fit adjudication separate.
- **Realtime deployment scope:** applies uniformly to every Pigora EQ
  curve-fitting identity, full module and point adapter. Follow
  [training-contract §1C](references/training-contract.md#1c-realtime-deployment-support-matrix)
  and root `AGENTS.md`, contract `pigora-eq-realtime-support-20261001-v2`: 44.1/48 kHz
  must support through **64 channels at 128 samples**; 88.2/96 kHz through
  **32 channels at 256 samples**. Guarantee one complete native EQ per instance
  with its admitted native topology and all sections available together in
  each tested mode; verify mutually exclusive modes separately. A point/section
  pass cannot replace complete-module capacity. Include steady processing and
  control transitions. All four boundary cases require independent production-path
  validation. Smaller buffers, rates outside this matrix, higher channel counts
  and expanded EQ/instance counts are stress/extension tests, whose performance
  failures alone do not block deployment. Preserve fidelity and safety gates;
  record missing runtime coverage separately from numerical passes. This
  timing/capacity carveout does not erase frozen response or explicit workload
  commitments and grants no new execution or paused-task resumption authority.

Report public identities as `public-fit passed`, `public-fit partial`,
`public-fit failed/withheld`, or `not publicly specified`. An authorized
inference subset may become `product-selectable — inference-derived` only
after its engineering and integration gates pass; it never upgrades public-fit.
No result here establishes unseen phase, distortion, loading, tolerance, unit
variation, or physical-hardware equivalence.

## Freeze before fitting

Use the training contract for the complete source, image-calibration,
extraction/review, uncertainty, target-grid, and ledger requirements. Prefer
numeric/vector data. Do not fit while axis calibration, trace binding, baseline,
or completion transforms are changing. Verify the actual consumed input against
the reviewed hash and permitted row membership before optimization.

Sparse completion (§3A) preserves accepted public anchors and labels generated
rows separately. Zero public rows or an explicitly inference-only identity
requires named owner authorization under §3B, including donors, transformations,
finite scope, and exclusions. Lack of public data alone is not authorization.
Resolve donor gain/frequency, sign, revision, topology, and baseline conflicts
before generating targets. No invented native mode, phase, or interaction.

Use a measured baseline first, otherwise strict paired boost/cut midpoints
where available, pooled per frequency point as defined in §3A. Flat 0 dB is
only the declared uncovered-point fallback. Never silently regenerate a frozen
target under the clarified aggregation rule.

### Owner-authorized flat reference for sparse dBu plots

When a public EQ plot reports output level in dBu but lacks a same-path bypass
or zero-control trace, and no strict measured boost/cut pair can establish its
baseline, the owner authorizes a **declared flat reference** for curve-shape
modeling: map the plot's flat 0 dBu line to the plug-in's 0 dB gain and set the
zero-control response to flat 0 dB. Subtract that declared reference from the
plotted level at each frequency; retain the original dBu values and the exact
normalization in the target ledger. This is an assumed baseline, not a measured
bypass response. Do not use it when measured baseline evidence conflicts, or
to infer missing native modes, control laws, phase, interactions, or level
dependence. Preserve source conditions that remain unknown and the image's
pointwise uncertainty. The normalized rows belong in a separate inference
target, not `public-fit-domain.csv`; the primary 48 kHz 0.2 dB gate,
explicit owner measurement fallback and independent review apply.

For the WesAudio _Prometheus Rev4 manual's HF CUT maximum-setting plot, this
authorization applies to the four plotted 4/8/12/20 kHz endpoint curves.
Their color-to-detent assignment is a reviewed order inference, not a printed
legend. Freeze that binding, the accepted finite frequency domain, excluded
overlaps, target hash, and control mapping before formal optimization. This
authorization supplies the reference only; it does not by itself authorize
lower CUT steps, other sections, or a product/public-fit claim.

The owner subsequently expanded the **_Prometheus-specific inference-only
scope** to all EQ bands. For the Rev4 manual's maximum-setting plots, bind LF
BOOST, LF CUT, and HF BOOST to the corresponding existing plug-in control's
10 endpoint; retain the earlier HF CUT=10 binding. Bind the manual's HF BOOST
High-Q/full-clockwise and Low-Q/full-counterclockwise plots to the two
Bandwidth endpoints. Generate lower gain settings by proportional scaling of
each frozen, baseline-normalized dB donor curve; generate intermediate
Bandwidth settings only by a reviewed, source-bounded interpolation between
the two endpoint families. Check the manual's simultaneous maximum LF
BOOST/CUT plots as a separate interaction target rather than assuming the
individual LF curves add. The native detent and color/trajectory bindings,
interpolation, uncertainty, finite frequency/control grid, and exclusions must
be frozen and independently reviewed before fitting. These are owner-authorized
modeling assumptions, not measured gain laws or public-fit rows. Keep the
inference-only primary 48 kHz per-row 0.2 dB gate, explicit owner measurement
fallback and the product/public-fit boundaries.

The owner also authorized a separate **WesAudio _Hyperion REV3 inference
mapping** for the existing 500-series parametric EQ identity. Use the official
REV3 manual's twelve LF/LMF-HMF/HF ±15 dB endpoint traces and two 150 Hz HPF
slopes as donors, retaining their protected source holdout. Keep Bell and Shelf,
boost and cut, and the two mid-band Q endpoints separate; the 1 kHz mid-band
plot is one shared LMF/HMF donor family, not two independent measurements.
Generate lower gain states by baseline-normalized dB percentage, map the ±5 dB
Range to one third of the signed ±15 dB knob gain, and transfer native band and
HPF frequencies by the declared donor/recipient center-frequency ratio only
within the source-supported finite domain. Generate interior mid Q curves by
interpolating the endpoint **dB target curves**, separately for boost and cut,
with `t = log(Q / 0.2) / log(3.2 / 0.2)`. For a simultaneously active full EQ,
sum the separately normalized band and HPF dB targets as a declared engineering
idealization. Zero controls align with the authorized flat 0 dB reference when
no valid strict paired or measured baseline covers a point. Freeze each exact
donor, baseline, trace/Q binding, transform, control grid, observation domain,
uncertainty and target hash with independent review before fitting. These
generated rows are `inference-derived/source-informed approximation` only,
must meet the separate primary 48 kHz per-row 0.2 dB gate or reviewed owner
measurement fallback, and do not promote public-fit.
Output transfer, THD, phase, and genuine analog inter-band interaction remain
unverified axes rather than inferred hardware claims. High-rate engineering may
use the named high-rate exception only after the full 48 kHz 0.2 dB pass;
owner measurement fallback decisions remain separate.

An independent coverage review binds the complete domain and omissions before
optimization. Keep protected holdouts inaccessible to the fitter. Use whole
curve/state partitions when defensible; otherwise evaluate every eligible row
and disclose that no independent within-source holdout exists.

## Execute a bounded, evidence-led loop

1. Inventory scope, native controls, current public/product state, authorization,
   artifact hashes, and writer/build ownership.
2. Run the input preflight and cheapest representative falsifier. Pilot solver
   cost and budget escalation as described in the efficiency reference.
3. Fit only permitted rows. Check intermediate controls and between-anchor
   frequencies, not just more samples along one axis. The coverage reference
   provides pole-aware probes, extremum refinement, and effective-state counts.
4. Evaluate the complete frozen domain with the appropriate validator. Separate
   target/control-law error from translation/runtime error. Before release,
   reproduce predictions through the production path.
5. On failure, preserve the result, identify the owning layer and one falsifier.
   After two failed changes under one hypothesis, diagnose or change the model
   family instead of stacking patches.
6. Once applicable response gates pass, follow the Pigora production handoff
   and repository staged validation. Reuse unchanged passing receipts.

A candidate failure or solver budget exhaustion ends that attempt, not the
authorized task. It blocks release while the next bounded hypothesis is tested.
Stop and escalate when the target remains ambiguous, authorization/safety blocks
the next step, or no defensible next hypothesis remains. An explicit user pause,
protected holdout, or owning attempt limit always takes precedence.

## Review without approval churn

Exploration on synthetic and permitted representative data is repeatable and
diagnostic only. Freeze a viable formal candidate with exact target, code,
configuration, environment, and output identities; retain failed formal results.
One required non-author judgment concerns one stable subject. Reuse the evidence
review while its target, rows, thresholds, transforms, and claim are unchanged.
A harness or serialization fix requires targeted revalidation of affected
receipts, not an automatic new evidence contract. Final independent evaluation
and the required stable-candidate review still apply. Do not invent exactly-once
or two-reviewer chains absent an explicit owning contract.

## Deterministic checks

Public response gate:

```bash
python3 .agents/skills/pigora-public-fit-training/scripts/validate_public_fit.py \
  --domain-sha256 <reviewed-domain-sha256> <domain.csv> <evaluation.csv>
```

Point-policy withholding:

```bash
python3 .agents/skills/pigora-public-fit-training/scripts/validate_withheld_points.py \
  --catalog <point_catalog.jsonl> --evidence-policy <identity_response_evidence.csv> \
  <withheld-response-points.csv>
```

Use the inference-validation reference for the separate engineering CLI and
negative tests. Use curve-coverage for diagnostic sampling and aggregation tests.
Neither tool creates public evidence or replaces independent source review.

When changing policy-ledger handling, run
`python3 .agents/skills/pigora-public-fit-training/scripts/test_withheld_empty_scope.py`:
a policy with no withheld points permits an empty withheld ledger, not invented
rows for inference exclusions.

The exclusion ledger records every excluded inference identity. The public
withheld ledger records exactly evidence-policy-withheld native point tuples,
not every exclusion or NPS identity. No wildcards or module-wide pseudo-rows;
retain the frozen catalog identity and report unmeasured continuous intervals
as nonclaims rather than inventing infinite points.

## Completion

Retain sources and extraction receipts, target/ledger hashes and coverage review,
configuration and fitted parameters, row-for-row evaluation and worst rows,
shape/coverage reports, independent review, production/hosted receipts, and
point-specific withholding. Report distinct effective control-state coverage,
per-rate gates and counts, independent-holdout availability, measured versus
inferred provenance, failed/pending layers, and explicit nonclaims. Report stage
timing separately from summed parallel work. Do not collapse this into an
unqualified “100% hardware fit” or “ready” statement.
