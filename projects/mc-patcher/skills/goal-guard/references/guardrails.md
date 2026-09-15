# Goal Guard reference

Use these rules to choose evidence and prevent repeated or misleading goal
turns.

## Contents

- [Evidence by goal type](#evidence-by-goal-type)
- [What counts as progress](#what-counts-as-progress)
- [Per-turn guard](#per-turn-guard)
- [Blocked audit](#blocked-audit)
- [Completion audit](#completion-audit)

## Evidence by goal type

### Implementation, migration, and bug fixing

- Inspect the working tree before editing so pre-existing user changes remain
  distinguishable from goal work.
- For a reported bug, establish a symptom-specific baseline when practical: a
  failing test, reproducible command, log signature, state probe, or precise
  manual reproduction.
- Require at least one primary acceptance check that would not certify the
  known-broken behavior. Supplemental checks such as build, lint, typecheck, or
  a broad test suite may already pass and are still valid regression guards.
- Inspect both tracked and untracked goal artifacts. `git diff --stat` alone
  does not show untracked files; use scoped `git status --short` and diffs where
  Git is available.
- Do not claim ownership of unrelated dirty changes. Report only changes that
  can be tied to the current goal.

### Investigation and reporting

- Do not demand a code diff.
- Prove coverage with the relevant sources, paths, queries, or experiments.
- Put the decision or conclusion before the evidence appendix.
- Separate observed facts, inferences, unresolved questions, and work that was
  deliberately not performed.
- Verify that the requested report or decision artifact is readable and saved
  where promised.

### External or operational work

- Use the resulting external state, receipt, identifier, or read-back as proof.
- Do not perform an external mutation that the user did not authorize.
- When a change cannot be read back, state the uncertainty instead of treating
  the tool call itself as proof.

## What counts as progress

A goal turn can make meaningful progress without producing a diff. Valid
progress includes:

- reproducing the failure or eliminating a concrete hypothesis;
- locating and explaining the root cause with evidence;
- producing a relevant code, test, configuration, document, or external-state
  change;
- completing a long-running build, test, render, or data query;
- resolving a prerequisite that unlocks the next acceptance outcome.

Merely rerunning an unchanged passing check, restating the objective, or
starting duplicate work is not progress.

## Per-turn guard

1. Re-read the native goal state when status, budget, or continuation context is
   uncertain.
2. Choose one unmet outcome.
3. Check whether a command, task, or subagent is already advancing it.
4. Perform the smallest useful work or wait for the existing work.
5. Validate the result with evidence relevant to that outcome.
6. State what changed in the evidence, not a play-by-play of tool calls.

For parallel work, split only bounded independent subtasks. Keep one writer per
file or tightly coupled artifact, and do not interrupt a healthy long-running
task merely to restart it elsewhere.

## Blocked audit

A genuine blocker is an external condition that prevents meaningful progress,
such as a missing credential, unavailable dependency, required human decision,
permission boundary, or persistent external outage.

The following are not blockers by themselves:

- another acceptance outcome is still pending;
- the work is difficult or the first approach failed;
- a build or delegated task is still running;
- more investigation would be useful;
- the token budget is low or exhausted.

On the first and second consecutive goal turns with the same blocker, exhaust
safe in-scope alternatives, preserve evidence, and state the minimum input or
state change required. Only on the third consecutive turn with that unchanged
condition, when no meaningful progress remains, call `update_goal` with
`blocked`. New information or a materially different blocker resets the count.

## Completion audit

Before calling `update_goal` with `complete`:

1. Confirm outcome-specific checks cover the final state; reuse a passing
   receipt when its inputs and relevant environment are unchanged.
2. Run proportionate regression checks.
3. Inspect the scoped diff, artifacts, or external state.
4. Confirm that no required acceptance outcome, requested artifact, or follow-up
   remains.
5. Report limitations and deliberately omitted work.

Do not mark complete simply because a command exited zero if that command does
not prove the user's requested outcome.
