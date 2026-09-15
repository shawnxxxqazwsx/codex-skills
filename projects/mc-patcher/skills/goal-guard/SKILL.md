---
name: goal-guard
description: >-
  Apply evidence and progress guards to an active Codex Goal without replacing
  its lifecycle. Use when the user explicitly asks to guard a goal, prevent
  false-green checks or empty goal turns, audit completion evidence, coordinate
  parallel goal work, or diagnose repeated goal turns and blockers.
---

# Goal Guard

Keep a Codex Goal moving toward its actual outcome. Use Codex's native Goal
state; do not install hooks, create project-local goal files, or invoke a
separate goal driver.

## Enter the workflow

1. If native Goal tools are available and the repository permits this workflow,
   call `get_goal` to inspect the current objective, status, and budget. Otherwise
   report that limitation and apply evidence checks to the ordinary task without
   inventing a Goal driver or changing lifecycle state.
2. If there is no active goal, do not create one merely because this skill was
   invoked. `create_goal` is allowed only when the user explicitly requested a
   goal.
3. Classify the work as implementation/debugging, investigation/reporting, or
   external/operational work. Apply evidence appropriate to that class.
4. Identify the next unmet outcome and advance that outcome only. Do not repeat
   work already running in a tool, task, or subagent.

## Native Goal lifecycle

Apply this section only when native Goal tools and an active Goal are available.
Evidence remains current when the tested subject, inputs, acceptance rule, and
relevant environment still match; recheck time-sensitive state when needed.

- Treat `get_goal` as the source of truth for goal state and usage.
- Call `update_goal` with `complete` only after every required outcome has current,
  relevant evidence and no required work remains.
- Call `update_goal` with `blocked` only when the same blocking condition has
  persisted for at least three consecutive goal turns and no safe, meaningful
  progress remains. A resumed blocked goal starts a new three-turn audit.
- Never mark a goal complete or blocked merely because its token budget is low
  or exhausted. Budget pauses and resumptions are controlled by the user or
  system.
- Do not invent pause, resume, clear, turn-budget, or deadline commands. Codex
  does not expose those transitions through `update_goal`.
- For a budgeted goal completed successfully, report the final token usage
  returned by `update_goal`.

## Evidence discipline

- For a bug fix, require at least one primary check that distinguishes the
  broken behavior from the fixed behavior. Existing build, lint, and regression
  suites may remain useful supplemental checks even if they were green before.
- Prefer a safe pre-fix reproduction. If it is unsafe, unavailable, or too
  expensive, record the reason and use the strongest available symptom-specific
  evidence.
- Do not require a code diff for investigation or read-only goals. Match proof
  to the requested artifact or state change.
- Do not weaken tests, acceptance conditions, CI, or product behavior to obtain
  a green result.
- Before completion, confirm that relevant checks cover the final state and
  inspect the scoped artifacts or diff. Reuse unchanged passing receipts; rerun
  checks when their inputs or relevant environment changed.

Read [references/guardrails.md](references/guardrails.md) when selecting proof,
coordinating parallel work, deciding whether a turn made progress, or auditing
a blocker.

## End each goal turn

Give a compact update containing:

- the outcome advanced and the evidence obtained;
- the next unmet outcome or the exact blocker;
- any material test, environment, or scope limitation.

When native Goal tools and an active Goal are available, perform the
corresponding `update_goal` transition in the same turn if completion or the
native blocked threshold is met. Otherwise report ordinary-task evidence
without claiming a Goal state transition.
