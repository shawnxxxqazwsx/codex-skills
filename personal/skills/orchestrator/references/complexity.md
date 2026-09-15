# Independent-workstream rubric

Use this reference when a task is not clearly local. Delegate only a package
that can return a useful artifact without colliding with another active phase.

## Make a phase-scoped resource manifest

For each concurrent lane, record:

```text
Deliverable and acceptance signal:
Phase and immutable context:
Authorization and claim boundary:
Checkout/branch/revision and dirty paths:
Writable paths and shared interfaces:
Build, test, or execution environment and lane:
Generated artifacts and external destinations:
Live state or controller, if any:
Handoff artifact and integration owner:
```

Two lanes are independent only when their manifests do not overlap for the
phase being run. A shared repository or product is not itself a collision; a
shared interface, mutable environment, output artifact, deployment destination,
or live controller may be.

Use the narrowest lease that protects the resource. If one resource collides,
defer only that phase and continue unrelated read-only or isolated work.

## Apply the separability and cost gates

A candidate package is safe to delegate when all are true:

- It answers one precise question and returns a concrete artifact.
- Its writable paths and transitive interfaces are exclusive or frozen.
- Its authorization and claim boundary are explicit and no broader mutation is
  implied.
- Its required environment cannot change underneath it.
- Its side effects do not conflict with another live controller, artifact, or
  external destination.
- Its result can be accepted at a handoff point without continuous
  coordination.
- Its expected evidence or delivery value exceeds delegation and review cost.

Risk or uncertainty can justify an independent review, but does not by itself
make implementation parallel. If the work is inseparable, keep one writer and
schedule review after the artifact stabilizes.

## Choose useful delivery types

Good independent packages include:

- reproducing one reported signal from existing artifacts;
- tracing one stated hypothesis to its owning layer;
- implementing an isolated component behind a frozen interface;
- adding a focused regression, fixture, probe, or migration artifact;
- preparing a bounded evidence, documentation, or release artifact;
- reviewing a stable diff against named acceptance questions.

Do not delegate cheap listing, routine user communication, shared integration,
or a task whose only outcome is a generic recommendation. The primary should
perform cheap ownership inspection directly.

## Reassess and hand off

Reapply the gates after diagnosis, first green behavior, and repeated failed
attempts. Discovery, implementation, and review are distinct assignments.
Before accepting a handoff, inspect the artifact, its evidence, changed paths,
and validation result. Release the lane only after integration no longer needs
its resources.

## Assignment contract

Every assignment includes the package type, one question, acceptance signal,
scope, authorization boundary, forbidden resources, stopping condition, and
return format. For a writing package, also include exclusive paths, checkout or
branch, a stable environment, and the handoff point. Workers escalate rather
than broadening their lease.
