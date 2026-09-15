---
name: skill-retrospective
description: >-
  Automatically review Codex task history when the user says a skill, workflow,
  verification step, or agent failed to activate or behaved incorrectly; when
  the user re-reports a problem that the active workflow previously claimed
  fixed or verified; when an active user-owned workflow reaches an evidence-
  backed learning gate; or when the user asks to audit or improve skills. Also
  recover durable lessons after visible compaction. Update the narrowest user-
  owned skill, or create one only when no existing skill fits. Do not trigger
  for a first ordinary bug, a one-off correction, task length alone, or a mere
  milestone, and never modify system- or plugin-owned skills.
---

# Skill Retrospective

Turn demonstrated task experience into durable guidance without turning every
conversation detail into a rule.

## Trigger at the earliest safe point

Run automatically, without waiting for the user to say “improve the skill,”
when any of these becomes observable:

- the user reports that a skill, agent, review, verification, or workflow did
  not activate, ran at the wrong stage, or made a misleading completion claim;
- the user re-reports the same product failure after the active workflow said
  that path was fixed or verified;
- two edits under one hypothesis failed, an acceptance threshold was relaxed,
  or independent-review counts no longer match the recorded reviewer turns;
- another active user-owned skill explicitly reaches its learning gate.

Do not wait for deployment, handoff, or the end of the turn. The earliest safe
point is the first moment when the current command has completed and writer,
build, agent, deployment, and live-runtime ownership needed by the review is
released. If a candidate remains pending, resolve the learning gate before the
final answer. Run one consolidated pass per evidence class; do not recursively
review the retrospective itself merely because it made an eligible update.

## Compaction boundary

Do not assume the host exposes an “about to compact” hook. Without one, run only
when visible context pressure and an already-qualified lesson coincide at a safe
checkpoint. If compaction has already occurred, reconstruct only task-relevant,
verified facts from completed history, the retained summary, current artifacts,
and runtime state; do not parse opaque compaction internals. When a continuation
brief is requested, `$session-handoff` owns its selection and output format.

## When a checkpoint is warranted

Run after one of these conditions:

- the user corrected the same class of behavior more than once;
- a measurable workflow inefficiency caused repeated commands, unnecessary
  agents, build contention, wrong binaries, or avoidable user intervention;
- a verified new invariant changed diagnosis, implementation, or validation;
- a high-risk safety or permission gap was demonstrated once;
- the user requests a skill audit, retrospective, handoff learning pass, or
  durable workflow improvement.

Do not interrupt a healthy build, test, deployment, subagent, or live manual
verification. Consolidate candidates at the next safe milestone.

## Diagnose before adding rules

Reconstruct the relevant decision timeline from completed turns, current
artifacts, tool outcomes, and the full active skill text. Classify the failure:

1. **Execution lapse:** the existing skill already required the skipped action.
   Apply that rule to the current task. Do not duplicate it unless repeated
   evidence shows the wording or timing is ambiguous.
2. **Instruction gap:** the skill omitted, weakened, or mistimed a decision that
   would have prevented the observed failure. Patch the narrowest owner.
3. **Product-only failure:** the evidence is specific to product code, data, or
   a test and does not justify reusable workflow guidance. Fix or report it in
   the original task without mutating a skill.

The retrospective is not a substitute for the original request. After any
skill update, validate it, re-read the changed `SKILL.md`, apply the corrected
rule immediately when safe, and continue the original authorized task.

## Select durable lessons

Inspect user corrections, failed hypotheses, repeated exploration, actual tool
outcomes, runtime evidence, and final verification. A candidate must be:

- reusable across future tasks rather than tied to one temporary version, path,
  or session;
- supported by repeated evidence, a measured failure, or one serious verified
  safety invariant;
- specific enough to change an agent decision;
- absent from higher-priority instructions and existing skills.

Reject unverified guesses, generic advice, secrets, personal data, temporary
workarounds, wording preferences with no observed benefit, and product facts
that belong in source documentation or tests.

## Route to the narrowest owner

Before editing, read `$skill-creator` completely. Then read the full target
`SKILL.md` and only the supporting references it routes to for the proposed
change. Use `skill-creator` for every mutation.

1. Put repository-wide operational invariants in the repository `AGENTS.md`
   only when the active task already authorizes repository writes.
2. Put domain workflow guidance in the existing user- or repository-owned skill
   that already owns the trigger.
3. Put conditional detail in that skill's reference file rather than expanding
   its entrypoint.
4. Create a new personal skill only when the capability has a distinct trigger,
   does not fit an existing owner, and at least two realistic future requests
   justify loading it.

Never modify a skill under `$CODEX_HOME/skills/.system/`,
`$CODEX_HOME/plugins/cache/`, their `~/.codex` equivalents, or any other
plugin-managed or cache directory, even when filesystem permissions allow it.
Treat those skills as vendor-owned. Report the issue and recommended upstream
correction; do not copy a vendor skill into a personal fork merely to override
it.

This user-authorized workflow may update only personal, non-`.system`,
non-plugin-managed skills under `$CODEX_HOME/skills` or its `~/.codex/skills`
equivalent at eligible checkpoints. Repository-owned skills or `AGENTS.md`
remain limited to the active task's repository-write scope. No skill text may
grant new authority for external, destructive, costly, or scope-expanding
actions.

## Apply one reviewable change

- Prefer one consolidated update to repeated micro-edits.
- Preserve unrelated user changes and invocation policies.
- Remove or narrow obsolete and duplicate instructions before adding more.
- Validate every changed or new skill with the skill validator.
- Forward-test changed routing or behavior with representative requests when it
  materially affects autonomy, permissions, tools, or agent delegation.
- If no candidate passes the evidence and ownership gates, make no mutation and
  do not create a placeholder skill.

Report only material skill changes, the evidence that justified them, validation
results, and any vendor-owned conflict that could not be changed.
