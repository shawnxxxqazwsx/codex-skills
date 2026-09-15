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
| Production integration, build, or hosted verification | `mc-patcher` and its Pigora handoff reference; `vst-plugin-ui` only if editor/binding work is in scope |

Use `orchestrator` for authorized independent packages and shared-resource
coordination, not to add a controller or repetitive approval turns. An existing
module-specific validator may be reused through the documented normalized
adapter; this skill does not authorize rewriting its frozen artifacts.

## Keep the acceptance layers separate

- **Public-fit:** every eligible row passes inclusive absolute error
  `<= 0.2 dB`, or a separately reviewed and predeclared public `fallback-0.5`
  under training-contract §6. Compute inconvenience is not a fallback reason.
- **Inference engineering:** separate target/ledger, fixed `<= 0.2 dB` at
  48,000 Hz. No public fallback, public splits, or public withheld counts.
- **Higher-rate engineering:** only after complete 48 kHz success, each
  separately declared rate strictly above 48 kHz may use
  `sample-rate-engineering-0.5`. Reuse the exact target/grid and scope;
  lower rates do not receive this exception. A high-rate public-source claim
  still requires the public 0.2 dB gate.
- **Product acceptance:** production response, control mapping, numerical and
  realtime safety, integration, and required hosted checks are additional gates.
  Numeric, serialization, or installed-binary passes do not prove them all.
  Before module/product PASS, run the mandatory compact control-shape gate in
  [curve-coverage.md](references/curve-coverage.md#compact-production-control-shape-gate).
  Count Bell, Low Shelf, High Shelf, HPF and LPF as separate acceptance units
  wherever supported, with their native modes and applicable controls.
  Unresolved shape findings block that PASS even when target rows pass; keep
  public-fit adjudication separate.

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
