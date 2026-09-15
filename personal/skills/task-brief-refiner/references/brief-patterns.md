# Conversation and Brief Patterns

Use these as question prompts and synthesis aids, not mandatory forms. Select
only dimensions that can change the result. Never copy illustrative facts into
a real instruction unless the user supplied them.

## Find the highest-value next question

Prefer the uncertainty with the largest downstream effect:

1. What result or decision does the user actually want?
2. Who or what is the result for, and in what context will it be used?
3. Which choices are fixed, preferred, forbidden, or still open?
4. What form should the result take?
5. What would make the user regard it as satisfactory?

Do not ask all five automatically. If the answer is already present, move on.
If several details depend on one strategic choice, ask that choice first.

## Large project or plan

Clarify the intended outcome, planning horizon, current state, stakeholders,
boundaries, priorities, resources, dependencies, decision points, risks, and
what the requested plan itself must contain. Distinguish among a proposal, an
execution roadmap, active implementation, and final completion.

Useful question shapes:

- “Is the immediate deliverable a decision-ready plan, or should the AI also
  begin executing it?”
- “Which matters more here: delivery speed, cost, quality, flexibility, or
  reducing risk?”
- “What is definitely outside this initiative even if it would be useful?”

Do not request milestones, owners, or budgets when the user only wants help
exploring whether a project is worth doing.

## Creative, writing, or communication task

Clarify the audience, intended effect, core message or content, voice, format,
length, references, elements to preserve, and elements to avoid. Ask for an
example only when it would communicate taste better than abstract adjectives.

Useful question shapes:

- “After reading or seeing this, what should the audience understand, feel, or
  do?”
- “Should it sound authoritative, warm, restrained, playful, or like a specific
  reference you can provide?”
- “Which ideas or phrases must remain, and what must not appear?”

Treat aesthetic preferences as preferences unless the user makes them strict
requirements. Do not manufacture an objective score for a subjective result.

## Research, comparison, or decision

Clarify the decision the research supports, viable options, user priorities,
evidence freshness and authority, geographic or time scope, excluded sources,
required comparisons, and acceptable uncertainty.

Useful question shapes:

- “What decision will this research change?”
- “Which tradeoff could reverse your choice?”
- “Do you need a quick directional answer or a source-complete report?”

Do not ask for exhaustive research when a bounded fact can settle the decision.
Keep facts, source statements, calculations, and AI inference distinct when it
matters.

## Technical task or exact change

Clarify the reported behavior, desired behavior, relevant environment or
artifact, scope, compatibility, preserved behavior, authority boundaries, and
the most relevant check. Use engineering details only when the work is
technical.

For a tiny change, the final instruction may be only:

```markdown
Change [exact target] from [current state] to [desired state]. Preserve [nearby
behavior that matters], do not modify [unrelated scope], and confirm the change
with [proportionate check].
```

For diagnosis, do not imply authorization to implement. For implementation, do
not claim the user-visible problem is resolved solely because a lower-level
check passes when the real path is part of the requirement.

## Everyday, personal, or administrative task

Clarify the intended recipient or destination, relevant facts, desired tone,
deadline only if one exists, privacy boundary, and whether the user wants a
draft, options, a recommendation, or an action performed.

Do not turn a simple message, checklist, explanation, or personal decision into
a project-management document.

## Final instruction shapes

Use a compact paragraph when the request is narrow:

```markdown
[Direct action and target]. [Necessary context or desired effect]. [Important
constraint or preference]. Deliver [output form] and [quality/completion cue].
```

For a genuinely multi-part request, use only relevant sections:

```markdown
[Direct objective]

Context:
- ...

Requirements:
- ...

Boundaries and preferences:
- ...

Deliverable:
- ...

Completion or quality standard:
- ...
```

The final instruction must not say “as discussed above” when it will be given
to another AI without the conversation.

## Audit impact

When auditing rather than rewriting, classify only meaningful gaps:

- Blocking: different answers define materially different tasks or authorize a
  risky action.
- Material: work can start, but its direction, scope, or quality may drift.
- Optional: the detail could improve convenience but is not necessary.

Prioritize blocking and material gaps over stylistic polish.
