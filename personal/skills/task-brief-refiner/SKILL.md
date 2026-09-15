---
name: task-brief-refiner
description: >-
  Clarify what the user wants through a focused conversation, then synthesize
  the settled requirements into an accurate, self-contained instruction for an
  AI. Use when the user asks to work out their requirements, refine or audit a
  vague idea or prompt, be interviewed about a task, or summarize a discussion
  into a final instruction across planning, creative, research, administrative,
  and technical work. Do not trigger merely because an ordinary request could
  be more detailed, and do not execute the resulting instruction unless the
  user also asks for execution.
---

# Brief Refiner

Use conversation as the primary workflow, not merely as a fallback before
writing a template. Help the user discover and articulate the requirement while
keeping ownership of preferences and consequential choices with the user.

## Choose the interaction mode

- **Clarify together:** Default when the user asks to work out the requirement,
  the intent is still forming, or several plausible interpretations would lead
  to different instructions.
- **Refine directly:** Use when the supplied requirement is already sufficiently
  settled or the user asks for an immediate rewrite. Make reasonable defaults
  explicit instead of starting an unnecessary interview.
- **Audit only:** Preserve the original prompt and identify ambiguities,
  contradictions, missing decisions, and likely misinterpretations by impact.

The user may switch modes at any time by asking to continue questioning, accept
reasonable defaults, or output the instruction now.

## Clarify through dialogue

1. Briefly reflect the current understanding in plain language so the user can
   correct the direction early.
2. Identify the unknown that would most change the result. Ask one natural
   question or one tightly related decision cluster, not a long intake form.
3. When useful, offer a few genuine alternatives and explain how each changes
   the outcome. Do not force multiple-choice answers when the user's own words
   are more appropriate.
4. Incorporate each answer into the working understanding. Do not ask again for
   settled information or expose an internal checklist after every turn.
5. Continue until the remaining unknowns can safely be left to the executing AI
   or the user asks to stop and summarize.

Ask about only the dimensions relevant to this request: desired result, purpose,
audience, object or context, content or behavior, boundaries, references,
format, tone, language, level of detail, tools or environment, permissions,
timing, and the standard for a satisfactory result. A creative task may need a
desired effect or reference rather than a test. A personal or administrative
task may need audience and tone rather than technical scope. A tiny change may
need only the exact target, desired difference, and what must remain unchanged.

Read [references/brief-patterns.md](references/brief-patterns.md) when the user
needs help discovering requirements across a large project, a creative or
communication task, a research decision, or a precise technical change.

## Preserve facts, choices, and flexibility

Treat the user's statements and supplied artifacts as facts within the
conversation. Keep confirmed requirements, tentative preferences, assistant
inferences, and unresolved choices distinct. Never invent references, paths,
versions, budgets, deadlines, technical constraints, evidence, or authority.

Translate vague words such as "better," "professional," "complete," or "like
before" only when the user has supplied a concrete effect, reference, boundary,
or comparison. Otherwise ask what the term means in this case. Do not turn a
preference into a hard constraint, and do not prescribe a method when the user
cares only about the result.

Match precision to scale. For a large initiative, settle the objective,
boundaries, decision criteria, and intended planning horizon before expanding
phases or milestones. For a micro-change, keep the final instruction short and
exclude unrelated cleanup. Do not make every request look like software
development or require tests, deployment, paths, and engineering terminology
when they are irrelevant.

## Synthesize the final instruction

When the requirements are sufficiently clear or the user asks for a summary,
produce one copyable, self-contained instruction in the user's language. It
must stand on its own for an AI that cannot see the clarification conversation.

Include only information that changes the work. Depending on the request, this
may cover the objective, essential context, required content or behavior,
boundaries, preferences, deliverable format, and the appropriate quality or
completion standard. Use headings only when they improve a longer instruction;
a small request should remain a compact paragraph.

Distinguish requirements from optional suggestions. Resolve pronouns and
relative references to named targets when possible. If the user deliberately
ends clarification with an important choice unresolved, mark it plainly in the
instruction rather than silently selecting an answer.

Return the final instruction first. Add a short note only when it must disclose
a material assumption, unresolved conflict, or alternative that would change
the task. For an audit-only request, report the gaps without rewriting unless
the user then asks for a revised version.

## Honor execution boundaries

Clarifying or summarizing an instruction is not permission to execute it, edit
files, contact people, purchase, publish, deploy, delete, or mutate an external
system. Perform the resulting task only when the user explicitly asks for both
clarification and execution. All normal domain, safety, and authorization rules
still apply.

Do not replace specialist skills. This skill owns task-expression quality;
domain skills own technical workflow and evidence, `orchestrator` owns complex
execution coordination, and `session-handoff` owns continuation state.

## Final quality check

Before returning the instruction, verify at the smallest useful level of detail:

- It reflects the user's settled choices and intended emphasis.
- Its target, requested result, boundaries, and deliverable are clear enough
  for this kind of work.
- Its quality or completion standard fits the domain instead of assuming every
  task has an engineering test.
- It contains no unsupported assumptions, contradictions, hidden expansion of
  authority, or dependence on unseen conversation context.

Precision is successful when the next AI has the right freedom and no important
reason to guess; maximal detail is not the goal.
