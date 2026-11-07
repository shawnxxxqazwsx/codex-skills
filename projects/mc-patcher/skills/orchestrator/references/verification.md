# Integrated verification

Use this reference when a task's acceptance depends on a running product,
interactive behavior, deployment, generated artifact, or external state. The
repository and applicable domain skills remain authoritative for exact commands
and acceptance criteria.

## Validate the reported path in layers

Stop at the first failing layer and fix the owning behavior before broadening
validation. Apply only layers that exist for the package:

1. Build or check the changed component.
2. Re-run the original observable signal.
3. Check one nearby unaffected behavior.
4. Run the focused suite, validator, or format check.
5. Exercise the integrated, hosted, deployed, or live path when that is what
   the report concerns, including verified route receipts for Argon, Gemini
   Flash, or other leased work.

A lower-level green result never proves an untested user-visible or live path.
State the exact untested layer rather than promoting a partial pass to closure.
For documentation, configuration, planning, or read-only review packages, the
applicable checks may instead be file format, schema, link/reference integrity,
decision-record completeness, and evidence traceability; do not require a
build or live exercise that the package cannot affect.

## Control mutable environments

Assign one controller for each mutable runtime, project, device, service, or
external account. Independent read-only analysis may continue, but serialize
actions that can change shared state, invalidate other artifacts, or alter the
environment under test. Prefer copies or scratch fixtures for mutating tests
unless the user explicitly authorizes changing the original.

## Identify what was actually tested

Record the source revision, built artifact, deployed destination when relevant,
runtime configuration, and any generated evidence. After an in-place update,
verify that the running process, host, or consumer loaded the intended artifact;
restart or reload only when authorized and necessary. Do not use a current
installation receipt as proof that an already-running process changed.

## Verify leased execution

Check the frontend exclusion before dispatch; a clean diff afterward cannot
justify sending a frontend write task to a delegated subagent. For eligible
backend-only Argon, DeepSeek, or Grok work, also inspect the actual diff and
generated outputs for forbidden frontend changes. If any appear, withhold
acceptance and arrange a local correction that preserves pre-existing work; do
not send the frontend correction to a subagent.

A leased worker's completion message is a claim, not acceptance. Inspect the
actual files, diff, command output, and raw failure text on disk. For every
`magpie-*` worker (Argon, DeepSeek, Gemini Flash) and each Grok worker, including read-only review and
research packages, read its entry in
`~/.claude/state/magpie-routing/<session_id>.json`; only `status: verified`
establishes the route that ran (see
[model-routing.md](model-routing.md#route-receipts)). A worker's self-report of
its model is not evidence, and `magpie-*` dispatches set no `effort`. For UI or
live actions, require before/after state, screenshots, and concrete action
receipts; a code-only report cannot establish an interaction. For fresh screen
or software-state capture, bind the observation to the target app/session and
capture time; a cached image cannot prove a later state. When a capability,
delivery, or action state is unknown or unavailable, record it and query status
before any retry instead of resending a task that may already have executed.

## Review claims separately from checks

For interaction, performance, visual, hardware, security, or external-service
claims, preserve the actual observation conditions and evidence. A unit test,
mock, screenshot, or static inspection may localize a problem without proving
the reported integrated behavior. The primary performs the final review. Add a
non-author reviewer only when the user explicitly asks for an independent
second review.
