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
4. List independently useful deliverables and decide whether each one merits
   delegation. Delegation is optional: if the primary keeps a package, record
   the concrete reason (inseparable ownership, resource overlap, insufficient
   handoff value, or setup/review cost).

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
package becomes safe and useful, route it then.

## Keep coordination proportional

Use one primary task as the execution queue for one product behavior. Do not
add a separate controller task merely to relay routine progress, authorize
mechanical next steps already inside scope, or mirror worker state. A controller
is justified only when it owns a real cross-package decision or shared resource.

Within one phase, prefer at most two independent workers and one non-author
reviewer in addition to the primary. This is a ceiling, not a target. Before
creating a replacement or another reviewer, require either an accepted artifact
from the prior assignment or a new acceptance question; do not multiply agents
around the same unchanged question.

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

Every subagent assignment states:

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

Use the smallest suitable context packet and the lowest capable advertised
model and reasoning effort. Read [references/model-routing.md](references/model-routing.md)
before the first subagent is spawned. Read-only research may return a useful
evidence artifact, but it is not delegated implementation unless the assignment
explicitly includes an implementation deliverable.

## Preserve ownership and safe concurrency

The primary owns decomposition, acceptance criteria, shared-interface
decisions, integration, final adjudication, externally visible state changes,
and the final claim. A non-author reviewer supplies an independent judgment
when required below; the primary may accept or reject it, but cannot relabel a
self-review as independent review. A subagent owns only its explicit package
and must stop rather than expand its scope when it reaches an excluded resource
or a new plausible owning layer.

Parallel work is safe only while its relevant resource manifests do not
intersect. A collision serializes that phase, not all other work. Read
[references/complexity.md](references/complexity.md) when the work is not
clearly local, and give each implementation or validation lane an isolated
environment whenever the active repository rules require one. Repository
rules take precedence over this skill; in `mc-patcher`, use the mandated
dedicated build-lane wrapper for routine build/test work and serialize only
the explicitly shared integration/deployment resources.

Use available concurrency for independent packages, not to fill slots. A
follow-up on the same task/thread is appropriate only for the same bounded
stream, unchanged authorization, and unchanged judgment role; use the current
platform's supported follow-up primitive rather than assuming an API name. Create
a new assignment when the role, judgment level, scope, or acceptance question
changes.

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
unless the user or owning evidence contract explicitly requires them.

Validate applicable layers in order: the changed component or artifact, the
original signal, a nearby unaffected behavior, the focused suite or validator,
and the integrated or live path when that is the reported path. A documentation,
configuration, planning, or read-only review package may omit inapplicable
build/live layers, but must validate its own links, schema, format, references,
and stated evidence. Stop at the first failing applicable layer. Read
[references/verification.md](references/verification.md) when live state,
deployment identity, interaction, or runtime acceptance matters.

Communicate changed facts rather than agent activity. Report accepted artifacts,
verified layers, deployment or external-state status, and remaining uncertainty.
If a learning or workflow-retrospective skill applies, invoke it at its own
documented safe checkpoint; it does not replace product validation.
