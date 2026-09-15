---
name: session-handoff
description: >-
  Create or resume a continuation brief for moving work to a new Codex task or
  continuing later. Use when the user asks for a handoff, 交接, continuation
  summary, saved state, fresh-task context, a new task that preserves current
  progress, or resuming work from a saved handoff.
---

# Session Handoff

Write for the next Codex task: preserve decisions, evidence, local state, and
the exact next action or completed terminal state without replaying the full
conversation.

## Choose the operation

| User intent | Action |
|---|---|
| Wants a handoff or continuation summary | Produce one copyable brief |
| Explicitly wants a fresh Codex task | Create a new task with the brief as its initial context |
| Explicitly wants copied completed history | Fork the current task, then send any missing current-turn brief |
| Wants the brief saved | Also write it under `.codex/handoffs/` |
| Wants to resume a brief | Read it fully, verify current state, then continue from its first valid next step |

Do not create or fork a task unless the user explicitly asks. Do not use
`handoff_thread` for a continuation summary: that operation relocates another
task's Git checkout/worktree and cannot move the calling task.

## Select the template

- Use the Unity template only when the carried work actually concerns a Unity
  project: the task touched Unity scripts, scenes, prefabs, assets, packages, or
  project settings, or the user explicitly requests a Unity handoff.
- Use the generic template for all other work. The mere presence of a directory
  named `Assets/` is not enough to classify the task as Unity work.

Read the matching section of [references/templates.md](references/templates.md).
Read [references/example.md](references/example.md) only when a detailed Unity
example will materially help.

## CREATE

If `$skill-retrospective` identifies a qualified learning candidate, invoke it
at that skill's safe checkpoint. It alone owns the trigger decision and must not
delay this handoff when no candidate qualifies.

Collect the strongest available facts from the current task and workspace:

- objective, scope, milestone, and exact stopping point;
- completed outcomes and remaining work;
- decisions, rationale, and rejected approaches worth avoiding;
- relevant files or external objects and what changed in each;
- verification performed, exact failures, and tests not run;
- blockers, assumptions, and the next ordered actions;
- repository path, branch/worktree, and scoped dirty-state summary when relevant.

If this work used a native Codex Goal, call `get_goal` and include its objective,
status, evidence summary, and remaining concern. Goal state is task-scoped: do
not claim it automatically transfers, and do not create a goal in the new task
unless the user explicitly requests one.

Distinguish verified facts from assumptions. Do not attribute pre-existing user
changes to this task. Do not include secrets, full logs, tool-call narration, or
large code blocks. Prefer project-relative paths inside the brief so it remains
portable across worktrees.

### Save only when requested

Persist the same brief at:

`.codex/handoffs/YYYY-MM-DD-HHMM-[slug].md`

Create the directory if needed. For a chained handoff, add
`Continues from: [previous filename]` near the top. This is a normal project
artifact, not hidden Codex task state; tell the user where it was written.

### Start a new task only when requested

Use Codex task-management tools according to the requested behavior:

- Create a fresh task when the user wants a compact new context. Put the handoff
  brief in the initial prompt and follow the current project/worktree rules.
- Fork when the user wants completed history copied. A fork excludes the active
  unfinished turn, so send the finished brief to the fork if it contains facts
  not present in completed history.

If only a brief was requested, return it without creating a task. If a task was
created, do not also instruct the user to copy and paste the same text.

## RESUME

1. Read the supplied or saved handoff completely. If it chains to an older file,
   read the predecessor only for decisions or context still needed.
2. Verify the project, branch/worktree, referenced paths, Git state, and relevant
   external state. Treat the handoff as potentially stale.
3. Report material deltas before editing. Do not re-ask facts that still verify.
4. Confirm the objective and first valid next action briefly, then execute that
   action if the user's request authorizes continuation.
5. Re-run verification appropriate to any changed state; do not inherit old
   passing evidence as fresh proof.

## Delivery

Return one handoff, not separate short and long versions. If information is
unknown, label it `未确认` rather than inventing it. If required work remains,
end with the ordered first action for the next task. If the task is complete,
say `已完成，无需继续执行` and omit the new-task instruction; do not invent
follow-up work to fill the template.
