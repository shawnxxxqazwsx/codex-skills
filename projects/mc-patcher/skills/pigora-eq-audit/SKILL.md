---
name: pigora-eq-audit
description: >-
  Audit deployed Pigora EQ plug-ins with a detailed, reproducible control and
  response matrix. Use for post-deployment verification, comprehensive module
  audits, or targeted rechecks of user-reported curve defects. Covers Bell,
  shelves, HPF/LPF, native modes, interpolation, automation and installed audio.
  Do not use for routine fitting, automatic full audits after every build, or
  GUI-only review.
---

# Pigora deployed EQ audit

Own the audit plan, execution and adjudication, not fitting or remediation.
Read root `AGENTS.md`, [matrix.md](references/matrix.md), and the `mc-patcher`
Pigora handoff reference before execution. `pigora-public-fit-training` owns
frozen targets and evidence gates. Reuse their bound artifacts; do not repeat
source research or rewrite targets to explain a failed audit. Consult
[history-patterns.md](references/history-patterns.md) when selecting representative
failures; these are historical examples, not current module status.

## Scope and ownership

A request to design a matrix or edit this skill does not authorize running the
plug-in audit. For an authorized audit, record requested modules, installed
format, host, rates, modes and mutable resources. Do not silently expand to all
modules. A comprehensive audit uses the full profile below; a reported defect
uses its exact state, local neighborhood and implicated shared paths first.
Do not run a full profile merely because training or deployment completed.

Use an isolated host instance/session where possible; preserve and restore user
state. Respect active host-control and deployment ownership. Build helpers in a
dedicated wrapped lane; never rebuild, deploy, change the global audio device,
or interrupt another task merely to obtain an audit slot. When an installed
binary changes, invalidate only receipts whose identity no longer matches.

## Execute in evidence order

1. Inventory every native identity × filter type × mode, including exclusions,
   slope settings and Off. Freeze the matrix and guard definitions before
   judging results. Use the reduced gain set, 17-position continuous tracks and
   adaptive acquisition in matrix.md; keep all native detents and historical
   failures. Reuse compatible prior rows with canonical effective-state keys.
2. Bind the installed binary and prove the test host loaded it. Run one known
   failure or representative state through actual audio to validate acquisition.
   Wrong binary, parameter mismatch or acquisition failure blocks that path;
   fix the harness before expanding the matrix.
3. Execute the 48 kHz static matrix, control tracks and type-specific shape
   checks in batches. On failure preserve the exact state and localize it;
   pause dependent acceptance stages for that unit and retain its repair packet.
   For a comprehensive audit, continue independent units so an early Bell
   failure does not omit shelves or pass filters; stop broader execution only
   for compromised acquisition integrity, safety, ownership or a user pause.
   A targeted defect audit stops at its declared scope.
4. Run other-rate checks, dynamic tracks and integration/state probes defined
   in the matrix. Reuse existing matching results rather than duplicate work.
5. Have one independent reviewer adjudicate the stable receipt and unresolved
   flags before an audit PASS. Use `orchestrator` for this bounded review; do
   not add per-row reviewers or duplicate evidence reviews.

No GUI curve, mathematical fit or separately compiled source probe establishes
installed-path acceptance. Label each result by its actual execution path.
Never report unsampled controls or untested host paths as passing.

## Close the audit

Write one plan, one machine-readable state/result table, compact worst-case
plots, and one receipt as specified in matrix.md. The visualization pack in
[matrix.md §7](references/matrix.md#7-required-visualization-pack) is mandatory,
including for failed or partial audits. Render and visually inspect the actual
images; embed the overview and most relevant detail in the final answer using
absolute local image paths, with links to the remaining images and raw data.
Do not deliver only JSON/CSV or file paths without image previews.
Report independently:
`target-fit`, `production-model`, `installed-static`, `installed-dynamic`,
`controls/state`, and any physical-gesture check. Overall PASS requires all
in-scope required layers; missing evidence is PENDING, measured failures FAIL.
Historical public-fit and inference statuses remain separate.

Return failures to training with exact reproduction and artifact identities.
Do not edit DSP, loosen a guard, redeploy, or begin an unrequested repair.
This skill defines a workflow; a new host adapter or detector must be implemented
and verified before it can supply executable evidence. No universal harness is
assumed to exist.
