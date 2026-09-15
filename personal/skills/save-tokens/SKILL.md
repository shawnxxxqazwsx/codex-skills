---
name: save-tokens
description: >-
  Reduce context and tool-token cost in Codex while preserving correctness and
  required verification. Use when the user explicitly asks to minimize tokens,
  cost, context growth, tool output, or repeated exploration on a coding,
  research, review, or migration task.
---

# Save Tokens

Optimize how the task is executed, not how much necessary work is omitted.
Correctness, safety, user instructions, applicable skills, and proportionate
verification always take precedence over token savings.

## Lean workflow

1. Define the requested outcome and the smallest plausible scope.
2. Search before broad reading. Prefer `rg` or `rg --files`, then read only the
   relevant regions. Fully read any selected skill or instruction file when its
   rules require that.
3. Batch independent searches, reads, and checks when doing so keeps output
   understandable.
4. Reuse facts already established in the task. Do not rerun unchanged commands
   unless fresh evidence is required.
5. Make a cohesive edit after the relevant context is known, then verify in
   proportion to risk.
6. Report the outcome, evidence, and remaining limitation concisely.

## Context and output discipline

- Exclude generated, dependency, cache, and build-output directories from broad
  searches unless they are explicitly in scope.
- Use targeted line ranges for large files, but expand the read when behavior
  crosses the initial range. Do not impose a fixed file or tool-call limit.
- Cap noisy command output at the source when possible. Preserve the error,
  failing test, summary, and enough surrounding context to diagnose it.
- Avoid pasting large source blocks or logs into conversation when a precise
  path, line, or short excerpt is enough.
- Keep required commentary updates short and useful. Do not suppress updates
  required by the active Codex instructions.

## Parallel work

When a domain orchestration skill applies, it owns delegation, resource leases,
and integration. This skill only trims each context packet and returned output.
Otherwise delegate only a bounded independent package whose saved context or
parallel value exceeds its setup and review cost; avoid overlapping writers.

## Never save tokens by

- skipping a required safety check, relevant test, or requested artifact;
- guessing about unread code, current external state, or unstable facts;
- hiding blockers, uncertainty, or test failures;
- asking the user to repeat information already available locally;
- creating a new task without the user's explicit request.

Read [references/efficient-work.md](references/efficient-work.md) for search,
batching, output-trimming, and long-task patterns. If the user explicitly wants
to continue in a fresh Codex task, use `$session-handoff` to preserve only the
context the next task needs.
