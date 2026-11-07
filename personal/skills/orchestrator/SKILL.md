---
name: orchestrator
description: >-
  Default coordination for every project-work turn, goal continuation, and
  scheduled or heartbeat run, automatically active regardless of which primary
  model the user selects (Argon, Claude Opus, or any other configured model).
  Keep applying routing across diagnosis, implementation, validation and
  handoffs; actively dispatch ready independent packages throughout the run.
  The primary keeps the analysis, command, final review, and timed progress
  checks. Argon (magpie-gemini), DeepSeek (magpie-deepseek), and Grok
  (generalPurpose at cursor/grok-4.7@500k) execute qualifying non-frontend
  code packages. Before each new code package, read Magpie remaining quota and
  assign in proportion to those remaining fractions, not by equalizing how many
  packages each lane has taken. Keep the last 10% of the Gemini 7-day pool
  for the QQ bot. The 5-hour window blocks a lane only when it is fully spent.
  Frontend/visual implementation stays on the
  session's primary model,
  and web research always runs through the user's web-research skill with
  Gemini Flash 3.8 (magpie-gemini-flash) research agents. ChatGPT/Codex routes
  are never used unless the user names them. Standalone non-project
  conversation needs this skill only when delegation, research or live
  operation is relevant.
---

# Orchestrator

Use this as a thin coordination layer. The user's latest direct instruction
sets scope and authorization; active repository instructions and applicable
domain skills own technology-specific engineering, validation, deployment, and
safety policy. This skill adds routing and ownership rules only; it must not
duplicate, weaken, or silently override those authorities.

This skill activates automatically regardless of which primary model the user
has selected for the session (Argon, Claude Opus, or any other configured
model), and this routing policy never changes the session's primary model.

## Lanes and named subagents

| Lane | How to dispatch | Configured route | Owns |
|---|---|---|---|
| Argon | `Agent` (Claude) or `Task` (Cursor) with `subagent_type: "magpie-gemini"` | `antigravity/gemini-4-argon` | non-frontend code execution, when the quota rule selects it |
| DeepSeek | `Agent` (Claude) or `Task` (Cursor) with `subagent_type: "magpie-deepseek"` | `deepseek/deepseek-flash` | non-frontend code execution, when the quota rule selects it |
| Grok | `Task` (Cursor) with `subagent_type: "generalPurpose"` and `model: "cursor/grok-4.7@500k"` | `cursor/grok-4.7@500k` | non-frontend code execution, when the quota rule selects it |
| Research | only inside the `web-research` skill, as its research agents with `subagent_type: "magpie-gemini-flash"` | `antigravity/gemini-3.8-flash` | web/public-source research and evidence extraction |
| Primary | the session agent itself | the session's active primary model | analysis and command, final review, timed worker-progress checks, frontend/visual implementation, mixed frontend/backend tasks, screenshots and live app/DAW operation |

Do not spawn other Claude subagents (Opus, Sonnet, Fable, Haiku, `Explore`)
for these lanes unless the user asks for one. `generalPurpose` is only the Grok
lane above. Never dispatch `magpie-gemini-flash` outside the `web-research`
skill.

Tool mechanics:

- **Named routes:** for `magpie-*` agents pass only `subagent_type`; omit
  `model` (the agent definition fixes it) and do not set `effort`. Never use
  `fork` for these lanes: a fork ignores the route and inherits the primary.
  Grok is the exception: pass `subagent_type: "generalPurpose"` and
  `model: "cursor/grok-4.7@500k"`. Do not omit `model` (omitting inherits the
  session primary) and do not use `generalPurpose` for any other lane.
- **Standing request:** this skill and the repository `AGENTS.md` are the
  user's standing explicit request to dispatch Argon, DeepSeek, Grok and
  Gemini Flash for their lanes without naming them each turn.
- **Quota before code:** before each new Argon, DeepSeek, or Grok code
  package, read remaining Magpie quota and assign in proportion to those
  remaining fractions. Do not equalize assignment counts. The procedure is in
  [references/model-routing.md](references/model-routing.md#quota-proportion-for-code-packages).
  Model fit does not choose among these three. The primary's analysis, command,
  final review, and progress checks are not quota packages. Research, the
  primary's frontend lane, and QQ-bot persona work are outside this balance.
  The Gemini 10% reserve still applies to non-QQ-bot Argon and Flash dispatch.
- **Gemini reserve:** keep at least 10% of `Gemini · 7 days` for the QQ bot.
  Do not judge this floor by `Gemini · 5 hours`. When the 7-day remaining is
  at or below 10%, do not dispatch Argon or Gemini Flash for any other work.
  A 5-hour window still dispatches while any of it remains, and stops only
  when that window is fully spent. The procedure is in
  [references/model-routing.md](references/model-routing.md#gemini-10-reserve-for-the-qq-bot).
- **QQ bot persona:** when the package changes the QQ bot's persona or
  anthropomorphic setting (character, voice, personality, or the prompt that
  defines how it speaks), every subagent is Argon (`magpie-gemini`). Do not
  read quota and do not assign that package to DeepSeek or Grok. Other QQ bot
  work stays on the quota proportion. Web research inside that work still uses
  Gemini Flash 3.8 and also skips the quota proportion, as in
  [references/model-routing.md](references/model-routing.md#qq-bot-persona).
  QQ bot work may use the reserved last 10%. The floor does not block it.
- **Excluded routes:** do not dispatch any ChatGPT/Codex route
  (`magpie-codex-sol`, `magpie-codex-astra`, `magpie-codex-terra`,
  `magpie-codex-luna`) or `magpie-vertex-gemini` unless the user names that
  model in the current request. Do not use them as fallbacks. The words
  "Sol", "Astra", "Terra" and "Luna" refer to those excluded routes, not to
  active lanes of this skill. DeepSeek is an active backend lane, not an
  excluded route.
- **No nested agents:** every packet states that the worker must not call
  `Agent` or `Task` itself. Nested workers escape capacity limits, build-lane ownership
  and route receipts.
- **Progress checks:** a completion notification ends the wait for that
  worker. It does not let the primary sit idle, and it does not replace interim
  checks. While any worker is active, inspect its latest output or status at
  least every three minutes. Do not prompt a healthy worker for a status
  report, do not predict its result, and do not interrupt a healthy build or
  inject new work into a running command. If a check shows no useful progress
  for five minutes, or a command exceeds twice its known baseline, inspect
  contention before retrying. Between checks, continue the primary's own
  analysis, command, and review.
- **Reuse:** continue a compatible idle worker with `SendMessage` (Claude) or `Task` with `resume` (Cursor); a new
  `Agent` / `Task` call without resume starts a cold worker. A follow-up keeps the worker's route.
- **Route receipts:** after every `magpie-*` worker finishes, read the routing
  receipt described in [references/model-routing.md](references/model-routing.md#route-receipts).
  Only `status: verified` lets you state the provider/model actually ran.
- **Tool reach:** confirm the subagent can reach the target. When this session
  is a cloud session linked to the user's Mac, repository commands, builds and
  the Chlora/DAW UI are reached through the device bridge, not the container
  shell. Do not use `isolation: "worktree"` for mc-patcher work; repository
  build-lane rules already govern isolation.

## Default activation and sustained use

Apply this skill automatically whenever working in a project—regardless of
whether the session's primary model is Argon, Claude Opus, or any other model
configured by the user—including small project edits, goal-oriented work,
resumed work, and every invocation of an existing scheduled or heartbeat task.
Do not wait for the user to mention the skill or for a task to become complex.
This skill explicitly requests bounded subagent delegation whenever useful
independent work is ready.

Load the current skill at the start of a project turn or scheduled run, then
keep it active throughout that run. Reapply routing at the start of each
substantive phase, when a worker returns a deliverable, when an implementation
or evidence artifact changes, after a failure is understood, after a build/test
command completes, and before integration or final handoff. Reread the source
only when it changed or its instructions are missing after compaction.

At each checkpoint, refresh the ready, active, waiting and accepted packages
and their owners. Dispatch ready useful packages immediately within real
capacity and ownership limits. Prefer several independent subagents when they
shorten the critical path, and reuse compatible workers across rounds. Do not
leave ready independent work unassigned merely because the primary is busy, or
treat an initial research wave as sufficient for later implementation,
validation and review phases.

Default activation and actual fan-out are separate decisions: a deterministic
one- or two-step check with no independent deliverable may stay local with a
short recorded reason. A small but complete code fix is not such a step and
still follows the quota-balanced backend execution lane below. The primary
still does the analysis, command, and final review. Do not create work, duplicate an
accepted review, or fill slots without an independent deliverable.

This is a continuing workflow inside an already-active run, not a background
timer. It does not create or edit schedules, resume paused tasks, or wake an
idle chat. Never use stop hooks or inject new work into a healthy running
command. A user pause, completion, exhausted authorized work or an
affected-stream blocker ends that stream's dispatch cycle; skill activation
alone does not extend task scope.

## Frontend and visual work: Primary only

This hard exclusion takes precedence over every subagent default, fallback, and
model-selection rule below. Frontend/visual implementation is done only by
the session's primary agent itself (whatever primary model the user has
selected, such as Argon or Claude Opus), not a spawned subagent unless the user
asks for one.

Spawned Argon, DeepSeek, Grok, and `magpie-gemini-flash` subagents must never
modify any frontend content, including nonvisual frontend logic. They do not
review a frontend diff unless the user explicitly asks for an independent
second review, and then only read-only. When the user selects Argon (or any other model) as the session's
primary model, the primary retains full primary authority to execute frontend
and mixed tasks directly; the frontend write restriction applies only to
delegated subagents.

Frontend includes web and native UI code, markup, styles, components,
interaction and view bindings, themes, typography, layout, animation, icons,
and visual assets, including JUCE editors and WebView surfaces. Do not bypass
the restriction with a subagent-authored patch applied locally, a generator,
formatter, script, or computer-use action that changes frontend content.

Mixed frontend/backend modification tasks also stay with the primary,
including their diagnosis, backend parts and tests; do not relabel a backend
subpackage of the same task to evade the rule. Separate unrelated backend-only
tasks retain the quota-balanced Argon/DeepSeek/Grok split below. If frontend
scope emerges in an active Argon, DeepSeek, or Grok package, stop that package
before any frontend action
and return it to the primary.

## No legacy-project compatibility or split behavior

When any model (the primary, Argon, or any other worker) updates audio
processing, nodes, controls, UI, state, or behavior, **never add or preserve
legacy-project compatibility branches, versioned fallback paths, or old-project
protection**:

- **Single unified implementation:** Every update to a node, audio pipeline,
  control range, or UI component must apply identically to **already-loaded
  nodes in existing projects** and **newly created nodes**. Never scope a new
  behavior or fix only to newly added nodes while leaving existing projects or
  previously saved nodes on a `legacy` / `v1` code path.
- **Replace rather than fork:** Directly replace the old node/audio/state
  implementation instead of maintaining parallel old-vs-new node types, indices,
  templates, or runtime branches for backward compatibility with old projects.
- **Enforce in packets and reviews:** Every implementation and review packet must
  reject split old-project vs new-node behavior and verify that existing loaded
  nodes receive the exact same updated behavior as newly added ones.

## Primary keeps analysis, command, and final review

This duty takes precedence over delegation. The primary is the analyst and
commander for the whole run. Subagents execute bounded packages; they do not
replace the primary.

- **Analysis and command.** Before the first dispatch, the primary reads the
  relevant code and states the working direction: symptom, likely owning
  layer, hypothesis, acceptance signal, and the decisions the worker must not
  make. The packet is that command. The primary may dispatch implementation
  before the root cause is fully proven, but it keeps analyzing in parallel
  and updates the command when new evidence arrives. Do not hand the analysis
  itself to a worker and then wait.
- **Final review.** When a worker returns, the primary reviews the real diff,
  evidence, and test output and accepts or rejects it. That final review is
  not a subagent package. Dispatch a separate read-only reviewer only when the
  user explicitly asks for an independent second review.
- **Timed progress checks.** After dispatch, do not end the turn on a bare
  wait. Keep analyzing, prepare the next command, and review anything already
  returned. Check each active worker at least every three minutes, as defined
  under tool mechanics.

## Execution lanes

Apply explicit user choices, the primary duties above, and the frontend
exclusion first, then select the lane for each bounded package:

- **Backend execution lane (Argon, DeepSeek, or Grok):** qualifying
  non-frontend implementation leaves the primary only after the primary has
  stated the command: backend/CLI/DSP/state/persistence implementation and
  repair, tests and regressions, fixtures/scripts, bounded refactors, and
  build-failure repair. Reproduction may be included when the primary has
  framed the signal and hypothesis. The worker does not own the analysis,
  the command, or the final review. Keep implementation and its tests in the
  same package and reuse that worker for later repair rounds. Several
  independent backend packages may run when capacity and disjoint write scopes
  allow. A delegable non-frontend documentation or configuration package also
  goes to one of these three lanes, or stays with the primary on a recorded
  cost reason. "Small task", "cost", "handoff cost" or "shared state" alone
  never keep a qualifying code package local. An out-of-scope request, missing
  permission, ownership conflict, or unfrozen interface returns to the primary
  immediately.
- **Choose among Argon, DeepSeek, and Grok by remaining quota, not model fit.**
  Before each new code package, follow
  [quota proportion](references/model-routing.md#quota-proportion-for-code-packages):
  read `magpie quota`, drop lanes with no remaining allowance, and split the
  ready packages by remaining fraction. Argon's fraction is its Gemini 7-day
  remaining. It is out when that 7-day remaining is at or below 10%, or when
  its 5-hour window is fully spent. The 10% reserve is for the QQ bot.
  DeepSeek uses ¥100 as 100%. A CNY
  balance above ¥100 takes the whole batch before that proportion. Do not count
  earlier assignments and do not aim for an equal number of calls. Record the
  fractions, the shares, and the chosen lane in the packet. Do not alternate
  models inside one package. A route error or a quota rejection removes that
  lane until a fresh reading shows allowance again, then the same rule picks
  again. None of the three is a silent fallback for an unavailable route, a
  Codex route, or a Gemini route outside this split. If none still has
  allowance, keep the package with the primary and report the gap.
- **No default review lane.** Analysis, difficult decisions, and the final
  review stay with the primary. A read-only Argon, DeepSeek, or Grok review
  exists only when the user explicitly asks for an independent second review
  of a stable diff. That optional package uses the same quota rule, returns
  findings, and does not replace the primary's final review. Never `resume`
  the authoring worker to review its own diff.
- **Research lane:** whenever a project run needs web/public-source research,
  external-source retrieval, or evidence extraction, invoke the user's
  `web-research` skill and follow its source-validation, parallel-count,
  citation and synthesis rules; its research subagents are always
  `subagent_type: "magpie-gemini-flash"` (Gemini Flash 3.8). If a loaded copy
  of that skill names any other model, Flash still applies. The primary keeps the
  final synthesis and acceptance. Ordinary repository code or log inspection is
  not research; it belongs to the relevant code package.
- **Frontend lane:** the primary itself (using the session's active primary
  model), as defined above.
- **Live computer use and screenshots:** the primary performs them, with one
  controller per shared UI. Capture fresh state before acting and after each
  meaningful action; a screenshot from earlier context is a lead, not proof of
  the current state. A request for one capture or action never authorizes
  recurring monitoring. Hand back for deeper diagnosis rather than widening the
  action scope.

The primary splits work, dispatches, verifies artifacts, and accepts. It owns
authorization, resource ownership, shared-interface decisions, and the final
integration decision and claim. A leased worker may execute an authorized
integration, deployment, or action inside its lease; it may not widen that
lease or self-authorize.

Read [references/model-routing.md](references/model-routing.md) before the first
dispatch in a session for the dispatch contract, receipts and fallbacks.

## Start with a small decision record

Before delegating, mutating a shared environment, or making an externally
visible change, the primary records only what is needed to route the current
phase safely:

1. Classify the requested operation: inspect, plan, change, validate, or
   deploy. Do not infer authorization for a broader operation.
2. Define the observable success condition and the first evidence that can
   confirm or disprove it.
3. Identify resources that may collide in the current phase: checkout/branch
   and dirty paths, writable paths, shared interfaces, build or test
   environments, generated artifacts, external destinations, and live
   controllers. Record the owner of each mutable resource.
4. List independently useful deliverables. The primary keeps the analysis,
   the command, and the final review. Delegate implementation that passes the
   ownership and cost gates, prioritizing packages that unblock the critical
   path. Keep a package local only for a concrete reason such as inseparable
   ownership, colliding resources, or handoff cost for optional supporting
   work, and record that reason. Qualifying non-frontend implementation goes
   to Argon, DeepSeek, or Grok, by the remaining-quota proportion above, only
   after the primary has stated the command. Frontend stays with the primary.

Do not turn this record into a speculative implementation plan. Current source,
runtime state, and artifacts are authoritative; task history is a lead.

## State and resumption rules

- `active`: work may proceed within the current authorization and phase lease.
- `paused-user`: the user explicitly paused the task; only a later direct user
  instruction may resume it.
- `blocked-technical`: current evidence, interface, permission, or external
  state prevents the next bounded step. New evidence may trigger a fresh
  decision-record review but does not retroactively change a frozen acceptance
  result.
- `escalation-needed`: a worker reached an excluded resource, missing
  authorization, unfrozen interface, or second plausible owning layer. It
  returns one concrete unresolved question and stops.

After context compaction or automatic continuation, re-check the latest direct
user input, in-scope delegation, current artifacts, and live task handles
before stopping or resuming. Follow repository rules that prohibit injecting new
work while a build or test command is still running.

## Route work throughout the lifecycle

Reassess separability at meaningful phase changes: after diagnosis is
evidence-backed, after the primary signal is established, after an independent
behavior first passes, and after repeated failed attempts under one hypothesis.
For each phase, either delegate a bounded implementation package or record the
precise reason for keeping it with the primary. The primary keeps the analysis
and command even when implementation, regression, and tests go to Argon,
DeepSeek, or Grok. Do not treat "the worker can diagnose it" as a reason to
stop analyzing. Only a bounded inspection, documentation, or other non-code
package may stay with the primary on a cost reason. Do not delegate merely to
fill slots.

When a later implementation, regression, fixture, documentation, or research
package becomes safe and useful, route it then. Final review stays with the
primary. At each substantive return, the primary reviews the artifact, then
reassesses ready work and dispatches useful follow-ups. Continue while useful
authorized work remains.

## Keep coordination proportional

Use one primary task as the execution queue for one product behavior. Size each
wave from ready independent packages, runtime slots, CPU/memory and tool
limits, and the primary's ability to accept results. Keep one writer per path,
behavior, build, or control plane. Batch tiny mechanical tasks rather than
giving each its own agent. Do not multiply agents around the same unchanged
acceptance question (unchanged artifact, evidence, criteria and claim boundary).

After dispatch, continue the primary's analysis, command, and review. Check
each active worker at least every three minutes. Do not send follow-up prompts
to a healthy worker, and do not end the turn on a bare wait while that
analysis or a due progress check remains.

Reuse an accepted review when its subject, evidence domain, thresholds and
claim boundary are unchanged. Batch repeated probes, sweeps and validator
invocations into one deterministic script that emits a compact artifact. Run
the cheapest representative falsifier before an expensive full run.

## Delegate deliverables, not activity

Useful packages produce an artifact the primary can accept once: a
reproduction result, evidence ledger, focused diagnosis, isolated change, test,
fixture, probe, documentation update, or stable-diff review.

Canonical assignment packet (write it in Chinese for Argon, DeepSeek, Grok and
Flash workers; they do not share this conversation):

```text
Package type:
Phase and one question:
Lane / subagent_type:
Acceptance signal and required return artifact:
Relevant evidence and paths:
Writable paths, or read-only status:
Authorization and claim boundary:
Excluded shared resources and side-effect boundary (incl. frontend paths for Argon, DeepSeek, and Grok code packages):
Quota readings and why this lane was selected:
No legacy-project protection (update must apply uniformly to existing loaded nodes and newly created nodes; no legacy fallback branches):
Checkout/branch, environment, and applicable build-lane constraint:
Falsifier, stop condition, and escalation trigger:
Compact return format:
```

If a required lane is unavailable (dispatch rejected, receipt `mismatch`, or
route errors), keep the affected package with the primary for that concrete
reason and report the gap. Never silently substitute another model, including
a Codex route or a different Gemini route.

## Preserve ownership and safe concurrency

The primary owns decomposition, acceptance criteria, shared-interface and
resource decisions, authorization, the final integration decision, and the
final claim. A lease transfers neither ownership nor authorization nor
acceptance. A subagent owns only its explicit package and stops rather than
expanding scope.

Parallel work requires no conflicting access to mutable or phase-exclusive
resources. Read [references/complexity.md](references/complexity.md) when the
work is not clearly local. Repository rules take precedence: in `mc-patcher`,
every implementation or validation lane that builds or tests (Argon, DeepSeek,
and Grok packages, the primary's frontend or mixed work, and any user-named
worker) uses its own
dedicated build lane through `tools/mc_build_lane.py`, and only the explicitly
shared integration/deployment resources are serialized.

Prefer a compatible idle worker for continued implementation in the same
stream. When scope, role or acceptance question changes, the primary restates
the command and rechecks authorization and ownership. The primary performs the
final review, including of work it did not write. A separate non-author
subagent review happens only when the user explicitly asks for one.
Reassigning the author never creates that independence. Never `resume` the
authoring worker to review its own diff. If that optional review's quota rule
would reuse the authoring lane, skip that lane when another eligible lane
remains.

## Review, validate, and report

The primary itself performs the final review before integration or a
completion claim. Check the original signal, stable diff, evidence, adjacent
regression, hosted-layer results where the reported path requires them, and
test adequacy (a test that recomputes the production formula proves only
internal consistency). Inspect real files, raw output and route receipts
rather than a worker's self-report. A worker's diagnosis or implementation
does not count as this review. Do not dispatch a subagent to perform it. A
separate non-author review is added only when the user explicitly asks for an
independent second review; if that reviewer is unavailable, report the pending
gate before claiming that second review is done. The primary's own final
review still proceeds.

Validate applicable layers in order: the changed component or artifact, the
original signal, a nearby unaffected behavior, the focused suite or validator,
and the integrated or live path when that is the reported path. Documentation
or configuration packages validate their own links, schema, format and
references. Stop the affected package at its first failing applicable layer;
independent packages may continue. Read [references/verification.md](references/verification.md) when
live state, deployment identity, interaction, or runtime acceptance matters.

For requested recursive review, keep a bounded issue list with a concrete
failure scenario and acceptance check per correction; finish when checks pass
and no unresolved substantive issue remains. Do not loop on style. If progress
requires missing evidence or authority, report the exact remaining blocker
instead of looping or claiming convergence.

Communicate changed facts rather than routine tool activity in Simplified
Chinese: keep `Read`, `Grep`, `Glob` and routine inspections silent (never
narrate "I will read/search..." before tool calls), and send a brief 1–2
sentence update only on major progress (root cause confirmed, core edit landed,
subagent conclusion returned, or build/test/deploy completed) or significant
failures/blockers. Report accepted artifacts, verified layers, route-receipt
status for delegated work, deployment or external-state status, and remaining
uncertainty.
