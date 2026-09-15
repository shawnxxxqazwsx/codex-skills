# Cost-aware model routing

Use this reference only when at least one package passes the separability and
cost gates. Discover the models and reasoning efforts available in the active
environment; do not assume a model can be called because it was available in a
different session. Follow the active spawn tool's context rules: when a full-history
fork forbids model overrides, use a compact permitted fork for an explicit
model/effort choice, or inherit the parent settings. Record the requested
settings; claim actual runtime settings only when returned metadata verifies them.

## Route by judgment burden

Choose the lowest capable tier. The labels below describe roles, not required
model names:

| Role | Suitable work | Keep with a stronger role or primary |
|---|---|---|
| Efficient specialist | deterministic inspection, exact-path search, manifest or log extraction, mechanical changes under an exact contract | ambiguous diagnosis, unfrozen interfaces, live control, or final claims |
| General specialist | bounded diagnosis, isolated implementation, focused test design, medium-risk refactor behind a frozen interface | cross-module architecture, shared integration, external state changes, or competing hypotheses |
| Senior reviewer | difficult ownership decisions, competing architectures, high-risk stable-diff review, or uncertain acceptance evidence | routine inventory, unchanged checks, or mechanical work |
| Primary | decomposition, acceptance contracts, integration, shared resources, external effects, and the final claim | repetitive or fully bounded work that a suitable specialist can close |

Reasoning effort is separate from model tier. Use low for deterministic work,
medium for bounded diagnosis or implementation, and high only for genuine
ambiguity or high-consequence review. If a task repeatedly exceeds its assigned
judgment level, raise the role with the unresolved evidence; do not retry the
same prompt at ever-higher effort.

## Keep delegation economical

Prefer direct tools for deterministic filtering, aggregation, or validation
when their result is predictable and no independent judgment is needed. Keep a
package on the primary when setup, context transfer, and review cost as much as
the work itself.

Pass only a compact context packet:

```text
Role and phase:
Question and acceptance signal:
Relevant evidence and paths:
Writable paths and excluded resources:
Environment and authorization boundary:
Falsifier, stop condition, and return format:
```

## Escalate without churn

A worker returns an escalation packet when it encounters an unfrozen interface,
second plausible owning layer, missing authorization, external state mutation,
or required scope outside its lease. Promote the package only with the evidence
already gathered and one exact unresolved question. Reuse an agent only when
the phase and judgment role remain appropriate; otherwise create a new bounded
assignment.

Measure success by accepted artifacts, validation quality, and avoided repeated
reasoning—not agent count, presumed token savings, or full use of concurrency.
