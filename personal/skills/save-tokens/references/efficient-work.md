# Efficient Codex work patterns

Apply these patterns selectively. The goal is lower repeated context cost with
the same or better task quality.

## Discovery

Start with the cheapest query that can narrow the scope:

| Need | Preferred first move |
|---|---|
| Find candidate files | `rg --files` with a path or extension filter |
| Find a symbol or literal | `rg -n` in the narrowest plausible directory |
| Understand a large file | Locate symbols first, then read surrounding ranges |
| Inspect repository state | One scoped status/diff command |
| Compare independent facts | Batch independent read-only queries |

Avoid recursive output from dependency trees, generated sources, caches, build
artifacts, and large binary directories unless the task targets them.

## Reading

- Read enough context to understand control flow, contracts, and nearby tests.
- Prefer a focused range after locating a symbol, but do not assume the first
  range is sufficient when definitions or callers live elsewhere.
- Read user-named files and governing instruction files before making edits.
- Do not repeatedly reopen content already captured accurately in the current
  task.
- Summarize stable findings in working notes rather than carrying raw output
  forward.

## Tool batching

Batch calls when their inputs are already known and the calls are independent.
Keep sequential dependencies sequential: do not run a test that depends on an
edit before the edit exists, and do not batch destructive or state-changing
operations merely to reduce round trips.

For long-running commands, yield or poll the existing process rather than
launching duplicates. Preserve its session identifier and request only new
output.

## Output trimming

- Use tool output limits and narrow command flags.
- For a failure, keep the command, exit status, first actionable error, and
  relevant tail or summary.
- For a passing suite, keep the concise pass summary rather than every test
  name.
- Never trim away a warning or secondary failure that changes the diagnosis.
- Do not place secrets, tokens, credentials, or unrelated environment values in
  command output or the handoff.

## Editing and verification

Prefer one coherent patch after the relevant files and tests are understood.
Avoid speculative edit-run-revert loops; after a failed attempt, use the new
evidence to change the hypothesis before editing again.

Verification depth follows risk:

- Small local text or code change: targeted syntax, unit, or focused check.
- Cross-file behavior change: focused checks plus relevant broader regression.
- Build, release, security, migration, or data change: the full required
  validation and explicit limitations.

Token efficiency never justifies changing tests or acceptance conditions to
make verification easier.

## Parallelism

Good subagent tasks have a clear boundary and independent output, such as:

- auditing separate directories;
- checking tests while the parent inspects implementation;
- comparing independent approaches or specifications;
- running a bounded read-only investigation.

Avoid parallel agents that edit the same files, repeat the same search, or need
the entire conversation. Give each agent paths, constraints, and the expected
return format, then integrate results without replaying their full transcripts.

## Communication

Intermediate updates should state material progress, a changed assumption, or a
real blocker. Final replies should lead with the result and include only the
evidence, files, and limitations the user needs to act.

Do not apply a fixed sentence, file, tool-call, or turn cap. Complexity and risk
determine the minimum sufficient work.
