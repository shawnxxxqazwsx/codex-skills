---
name: orchestrator
description: >-
  Coordinate complex multi-model development work when independent evidence,
  implementation, verification, or review packages can improve the outcome.
  Use for cross-module work, shared-resource risk, uncertain diagnosis, or an
  explicit request to split, self-check, or coordinate parallel work. Do not
  use for simple local changes or explanations.
---

# Orchestrator

Use this as a thin coordination layer. The user's latest direct instruction
sets scope and authorization; active repository instructions and applicable
domain skills own technology-specific engineering, validation, deployment, and
safety policy. This skill adds routing and ownership rules only; it must not
duplicate, weaken, or silently override those authorities.

## Start with a small decision record

Before delegating, mutating a shared environment, or making an externally
visible change, the primary agent records only what is needed to route the
current phase safely:

1. Classify the requested operation: inspect, plan, change, validate, or
   deploy. Do not infer authorization for a broader operation.
2. Define the observable success condition and the first evidence that can
   confirm or disprove it.
3. Identify resources that may collide in the current phase: checkout/branch
   and dirty paths, writable paths, shared interfaces, build or test
   environments, generated artifacts, external destinations, and live
   controllers. Record the owner of each mutable resource.
4. List independently useful deliverables and actively delegate those that
   pass the ownership and cost gates, prioritizing packages that unblock the
   critical path before independent supporting work. Prefer several bounded packages running
   concurrently when that shortens the critical path. Keep a package local
   when ownership is inseparable, resources overlap, or handoff and review
   cost outweigh the useful work.

Do not turn this record into a speculative implementation plan. A cheap,
isolated local inspection may remain with the primary without a delegation
attempt; the success signal and relevant scope still apply.

Current source, runtime state, and artifacts are authoritative. Task history is
a lead, not a substitute for checking them.

## State and resumption rules

Use these meanings consistently:

- `active`: work may proceed within the current authorization and phase lease.
- `paused-user`: the user explicitly paused the task; only a later direct user
  instruction may resume it. Automatic continuation, a subagent, or a changed
  contract cannot override this state.
- `blocked-technical`: the current evidence, interface, permission, or
  external state prevents the next bounded step. New evidence or an authorized
  contract change may trigger a fresh decision-record review, but does not
  retroactively change a frozen acceptance result.
- `escalation-needed`: a worker reached an excluded resource, missing
  authorization, unfrozen interface, or second plausible owning layer. It must
  return one concrete unresolved question and stop rather than broaden its
  lease.

After context compaction or automatic continuation, re-check the latest direct
user input, in-scope delegation, current artifacts, and live task handle before
stopping or resuming. Treat a retained summary or saved goal as stale when it
conflicts with that evidence. Follow repository rules that prohibit injecting
new work while a build or test command is still running.

## Route work throughout the lifecycle

Reassess separability at meaningful phase changes: after diagnosis is
evidence-backed, after the primary signal is established, after an independent
behavior first passes, and after repeated failed attempts under one hypothesis.
For each phase, either delegate a bounded package or record the precise reason
for keeping it with the primary, such as a shared resource, unresolved
interface, inseparable ownership, or delegation cost. Do not delegate merely
to fill available slots.

Do not treat initial research delegation as complete orchestration. When a
later implementation, regression, fixture, documentation, or non-author review
package becomes safe and useful, route it then. At each substantive return,
updated artifact, or resolved dependency, reassess ready work and dispatch useful
follow-ups concurrently within the current authorization and capacity. Do not
wait for an entire wave when a returned worker can safely advance its stream
alongside healthy workers. Continue this cycle while useful authorized work
remains; stop at completion, a user pause, or a blocker to the affected stream.

## Keep coordination proportional

Use one primary task as the execution queue for one product behavior. Do not
add a separate controller task merely to relay routine progress, authorize
mechanical next steps already inside scope, or mirror worker state. A controller
is justified only when it owns a real cross-package decision or shared resource.

Size each wave from ready independent packages, available runtime slots,
CPU/memory and tool limits, and the primary's ability to accept the results.
There is no skill-level two-worker ceiling. When three or more useful packages
are ready, dispatch them concurrently up to those limits; use larger waves when
capacity and separability support them. Before dispatch, use the active tool's
capacity rules and current agent inventory to determine free slots; include the
primary, descendants, and any idle agents that the runtime counts. Refresh at
handoffs or a capacity rejection, not through repeated polling. Do not assume
that an accepted deliverable releases a runtime slot or create nested agents
to evade the limit.

Keep the primary on critical-path decisions and integration while workers own
parallel deliverables. A reviewer need not occupy a reserved idle slot: schedule
review when its subject is stable. At safe handoff points, route newly ready
packages into available slots without interrupting healthy work. Reduce fan-out
when contention, duplicated investigation, or review backlog erases the benefit.
Batch tiny mechanical tasks rather than giving each its own agent. Do not
multiply agents around the same unchanged acceptance question. Here, unchanged
means the judged artifact, relevant evidence, acceptance criteria, and claim
boundary are all unchanged, not merely that the question has the same wording.
Changed code or evidence warrants the affected recheck, including parallel
follow-ups when independent; preserve the frozen acceptance criteria.

After dispatch, continue independent local work, then use an event-driven or
bounded wait within the active tool and communication limits. Do not alternate
short waits, status queries, and follow-up prompts while the worker is healthy.
Unchanged status is not a deliverable and should not start another model turn.

Reuse an accepted review when its subject hashes, evidence domain, acceptance
thresholds, and claim boundary are unchanged. A syntax, serialization, harness,
or manifest bug invalidates only the affected implementation receipt; it does
not automatically require a new evidence review, a second reviewer, or a new
top-level contract. Create a new decision identity only when the judged artifact
or decision inputs actually change, or when an owning contract explicitly
requires one.

Batch repeated probes, parameter sweeps, and validator invocations into a
deterministic script or one long-running command that emits a compact artifact.
Run the cheapest representative falsifier before a full grid or expensive
formal execution. After the first context compaction in a long workflow,
refresh a concise artifact-backed checkpoint and use it as working state instead
of repeatedly reloading the full conversational history.

## Delegate deliverables, not activity

Useful packages produce an artifact that the primary can accept once: a
reproduction result, evidence ledger, focused diagnosis, isolated change,
test, fixture, probe, documentation update, or stable-diff review. Read-only
research is valuable evidence, but does not count as delegated implementation.

Use this canonical assignment packet; combine fields or mark them inapplicable
for a simple read-only package, while preserving scope and acceptance details:

```text
Package type:
Phase and one question:
Acceptance signal and required return artifact:
Relevant evidence and paths:
Writable paths, or read-only status:
Authorization and claim boundary:
Excluded shared resources and side-effect boundary:
Checkout/branch, environment, and lane constraint:
Falsifier, stop condition, and escalation trigger:
Compact return format:
```

Use the smallest suitable context packet and explicitly select one of the
`gpt-6-luna/max`, `gpt-6.1-sol/medium`, or `gpt-6.1-sol/high` subagent pairs
according to task difficulty: prefer Luna for clearly bounded, low-complexity
work, Sol medium for implementation or diagnosis, and Sol high for demanding
reasoning or review. This skill authorizes that model selection when the active tool
permits overrides. Explicit user model and effort choices take precedence over
these defaults. This skill does not change the primary's model. If none of the
three pairs can handle a package, keep it with the primary or ask the user to
change the model choice; do not silently substitute another subagent model. Read
[references/model-routing.md](references/model-routing.md) before the first
subagent is spawned.

## Preserve ownership and safe concurrency

The primary owns decomposition, acceptance criteria, shared-interface
decisions, integration, final adjudication, externally visible state changes,
and the final claim. A non-author reviewer supplies an independent judgment
when required below; the primary may accept or reject it, but cannot relabel a
self-review as independent review. A subagent owns only its explicit package
and must stop rather than expand its scope when it reaches an excluded resource
or a new plausible owning layer.

Parallel work requires no conflicting access to mutable or phase-exclusive
resources. Immutable source, frozen interfaces, and read-only evidence may be
shared. A collision serializes only the affected phase and dependent packages. Read
[references/complexity.md](references/complexity.md) when the work is not
clearly local, and give each implementation or validation lane an isolated
environment whenever the active repository rules require one. Repository
rules take precedence over this skill; in `mc-patcher`, use the mandated
dedicated build-lane wrapper for routine build/test work and serialize only
the explicitly shared integration/deployment resources.

Prefer a compatible idle worker for continued work in the same stream, using
the platform's supported follow-up primitive. An assignment is a bounded work
lease, not an agent identity: a new assignment does not by itself require a new
agent. When scope, role, judgment level, or acceptance question changes, issue
a fresh packet and recheck authorization, resource ownership, model capability,
and reviewer independence before dispatch. Reuse an existing idle worker when
those checks pass and the platform supports reassignment; otherwise use a
suitable new agent within capacity. Workers may not broaden their own lease.

For compatible follow-ups, send the changed artifact/revision, new evidence or
unresolved finding, next acceptance check, and any lease changes; retain the
applicable prior constraints without retransmitting unrelated history. After
accepting a return, close that assignment and release its resource lease once
integration no longer needs it; this does not end the overall work stream.
Required independent review must use a non-author agent distinct from the
author. Reassigning the author to a reviewer role never creates independence.

## Review, validate, and report

The primary checks the original signal, stable diff, evidence, and test
adequacy before integration. A non-author review is mandatory before the final
claim or integration when the work changes an acceptance threshold, claim
boundary, evidence/public-fit state, shared interface, deployment/external
state, or when the user explicitly requests review. It is otherwise optional
when the primary can show that the package is low-risk and mechanically
verifiable. One implementation-time investigation does not count as
post-change review.

One required independent judgment means one reviewer for one stable subject.
Do not manufacture two-person, per-revision, or exactly-once approval chains
unless the user or owning evidence contract explicitly requires them. If a
required reviewer is unavailable, continue safe preparation and unrelated work,
but report the pending gate before claiming completion or integrating its subject.

Validate applicable layers in order: the changed component or artifact, the
original signal, a nearby unaffected behavior, the focused suite or validator,
and the integrated or live path when that is the reported path. A documentation,
configuration, planning, or read-only review package may omit inapplicable
build/live layers, but must validate its own links, schema, format, references,
and stated evidence. Stop the affected package at its first failing applicable
layer; independent packages may continue. Read
[references/verification.md](references/verification.md) when live state,
deployment identity, interaction, or runtime acceptance matters.

For requested recursive review or improvement, keep a bounded issue list with
a concrete failure scenario and acceptance check for each correction. Recheck
changed decisions and relevant neighboring cases on a stable revision; use an
independent reviewer when required above. Finish when applicable checks pass
and the review finds no unresolved substantive issue in the declared scope.
Do not start another pass for stylistic preferences or unchanged questions.
If progress requires missing evidence or authority, report the exact remaining
blocker instead of looping or claiming convergence.

Communicate changed facts rather than agent activity. Report accepted artifacts,
verified layers, deployment or external-state status, and remaining uncertainty.
If a learning or workflow-retrospective skill applies, invoke it at its own
documented safe checkpoint; it does not replace product validation.
