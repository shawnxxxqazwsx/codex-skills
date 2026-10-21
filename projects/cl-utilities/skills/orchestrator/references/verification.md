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
   the report concerns.

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

## Review claims separately from checks

For interaction, performance, visual, hardware, security, or external-service
claims, preserve the actual observation conditions and evidence. A unit test,
mock, screenshot, or static inspection may localize a problem without proving
the reported integrated behavior. Use a non-author reviewer where an
independent judgment is part of the acceptance contract.
