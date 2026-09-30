# Cost-aware model routing

Use this reference only when at least one package passes the separability and
cost gates. Discover the models and reasoning efforts available in the active
environment; do not assume a model can be called because it was available in a
different session. Follow the active spawn tool's context rules: when a full-history
fork forbids model overrides, use a compact permitted fork for an explicit
model/effort choice. Prefer `fork_turns="none"` with a self-contained assignment
or a small permitted turn count over inheriting a large Astra conversation.
If overrides are unavailable, record that limitation and keep the package with
the primary unless the user explicitly changes the model choice. Validate the
exact model/effort pair against current tool metadata. On a capability
rejection, refresh availability before choosing another supported pair from
the table below; do not repeat the rejected pair without new evidence that it
is supported. If none is available, keep the package with the primary and
report the limitation. For an explicit user choice, report an unsupported
combination instead of silently substituting. Record requested settings; claim
actual runtime settings only when returned metadata verifies them.

## Route by task difficulty and judgment burden

Explicit user model/effort choices override the defaults below. Otherwise,
select only one of these three exact model/effort pairs instead of silently
inheriting the primary. Use a pair only when advertised by the active tool;
these are routing preferences, not a verified price ranking:

| Package | Model | Reasoning effort |
|---|---|---|
| Exact-path inspection, log extraction, bounded documentation or mechanical edits | `gpt-6-luna` | max |
| Isolated coding, focused regression design, bounded diagnosis | `gpt-6.1-sol` | medium |
| Demanding bounded reasoning or independent review | `gpt-6.1-sol` | high |

Prefer GPT-6 Luna for clearly bounded, low-complexity work and GPT-6.1 Sol
as implementation difficulty, ambiguity, or review judgment increases. Route
each package by its own difficulty rather than the size of the overall task.
Start directly with the pair that fits the package; do not require an
unsuccessful Luna attempt before assigning complex work. Do not substitute
Astra or an older model under these defaults. If a package exceeds all three
pairs, keep it with the primary or ask the user to change the model choice.
Missing inputs, tools, authorization, or ownership isolation are not solved by
model escalation. Keep successful workers at their current pair rather than
upgrading the entire wave.

Choose the least demanding capable pair from the table above. The roles below
guide that judgment:

| Role | Suitable work | Keep with a stronger role or primary |
|---|---|---|
| Efficient specialist | deterministic inspection, exact-path search, manifest or log extraction, mechanical changes under an exact contract | ambiguous diagnosis, unfrozen interfaces, live control, or final claims |
| General specialist | bounded diagnosis, isolated implementation, focused test design, medium-risk refactor behind a frozen interface | cross-module architecture, shared integration, external state changes, or competing hypotheses |
| Senior reviewer | difficult ownership decisions, competing architectures, high-risk stable-diff review, or uncertain acceptance evidence | routine inventory, unchanged checks, or mechanical work |
| Primary | decomposition, acceptance contracts, integration, shared resources, external effects, and the final claim | repetitive or fully bounded work that a suitable specialist can close |

Use the effort fixed by the selected pair, including Luna at max for bounded
mechanical work. If a task exceeds its assigned judgment level, return the
unresolved evidence for a routing decision. Distinguish a reasoning gap from a
missing input or a product defect; change pairs only when that addresses the
diagnosed gap. Do not sample models or raise effort repeatedly on the same
unchanged question.

## Keep delegation economical

Prefer direct tools for deterministic filtering, aggregation, or validation
when their result is predictable and no independent judgment is needed. Keep a
package on the primary when setup, context transfer, and review cost as much as
the work itself.

Use the [canonical assignment packet](../SKILL.md#delegate-deliverables-not-activity).
For compact or no-history forks, include the applicable user constraints and
exact source paths; the worker must not need omitted conversation history to
recover its scope, ownership, acceptance signal, or stop condition.

## Escalate without churn

A worker returns an escalation packet when it encounters an unfrozen interface,
second plausible owning layer, missing authorization, external state mutation,
or required scope outside its lease. Promote the package only with the evidence
already gathered and one exact unresolved question. Apply the
[assignment and worker reuse rules](../SKILL.md#preserve-ownership-and-safe-concurrency):
a fresh assignment can reuse a compatible idle worker after the primary
rechecks its lease, capability, and independence. A changed phase alone does not
require a new agent or a model upgrade.

Aim to lower total cost and elapsed time through compact contexts, capable
workers, and useful parallel waves. Check accepted artifacts, rework,
review burden, and critical-path delay; more simultaneous agents can increase
total tokens. Report measured usage or timing when available, and never infer
a savings percentage from model names or agent counts alone.
