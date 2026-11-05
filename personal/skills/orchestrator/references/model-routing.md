# Execution and model routing

Use this reference before the first dispatch in the current session. Re-read
the live `Agent` (Claude) or `Task` (Cursor) tool schema and the available agent types at call time; this
file records routing policy, not a frozen API.

## Allowed routes

| Lane | `Agent` (Claude) / `Task` (Cursor) call | Configured route |
|---|---|---|
| Argon (execution, review, and judgment) | `subagent_type: "magpie-gemini"` | `antigravity/gemini-4-argon` |
| Research agents (only inside the `web-research` skill) | `subagent_type: "magpie-gemini-flash"` | `antigravity/gemini-3.8-flash` |
| Frontend, mixed tasks, live operation | none: the primary does it | Session primary model (any user-selected model, e.g. Argon or Claude Opus) |

For `magpie-*` agents omit `model` and `effort`; the agent definition fixes the
route. Never `fork` for these lanes. Every packet tells the worker not to call
`Agent` or `Task` itself.

Not proactively used: DeepSeek (`magpie-deepseek`), every ChatGPT/Codex route
(`magpie-codex-sol`, `magpie-codex-astra`, `magpie-codex-terra`,
`magpie-codex-luna`), `magpie-vertex-gemini`, and other Claude subagents (Opus,
Sonnet, Fable, Haiku, `Explore`, `general-purpose`). Use one only when the user
names it in the current request, and only for that request. They are never
fallbacks.

## Frontend exclusion comes first

Apply the [frontend exclusion](../SKILL.md#frontend-and-visual-work-primary-only)
before choosing an Argon execution package. Frontend or mixed frontend/backend
tasks, including their diagnosis, backend parts and tests, stay with the
primary. For an unrelated backend-only Argon package, list frontend paths,
shared files containing frontend code, and scripts or generated outputs that
would change frontend content as excluded from its writable scope. Scope
discovered later stops and returns to the primary before any frontend action.

## Argon execution lane: non-frontend code, docs, and config

- Dispatch qualifying non-frontend code packages to `subagent_type: "magpie-gemini"`
  at the first engineering checkpoint with a complete Chinese packet: paths,
  symptom, acceptance signal, writable scope, excluded resources, build lane,
  stop condition, return format.
- Delegable non-frontend documentation or configuration packages also go to
  Argon (`magpie-gemini`), or stay with the primary on a recorded cost reason;
  never to Flash.
- Keep implementation and tests in one package; continue the same worker with
  `SendMessage` (Claude) or `Task(resume=...)` (Cursor) for repair rounds.
- Builds and tests go through `python3 tools/mc_build_lane.py run --lane <id>
  --build-dir <dir> -- ...` with a dedicated lane per package. Deployment
  through `build-juce` needs the shared lock and stays inside the authorization
  the primary states in the packet.
- Require the worker to report changed files, commands run with raw results,
  and anything not run. The primary inspects the real diff before accepting.

## Argon judgment and review lane

- Send a stable subject to `subagent_type: "magpie-gemini"`: the diff or
  artifact paths, the acceptance criteria, the claim boundary, and one exact
  question or review scope.
- Always read-only when dispatched as a review or judgment package (whereas an
  Argon execution package writes within its assigned non-frontend paths; the
  primary session also retains full write authority when Argon is the primary
  model).
- Return format: findings ranked by severity, each with file/line, concrete
  failure scenario and suggested acceptance check; or a decision with the
  evidence that supports it and the remaining question.
- A fresh `magpie-gemini` subagent instance is the default non-author reviewer
  for work authored by another `magpie-gemini` worker or by the primary session.
  Never `resume` the authoring worker instance to review its own diff.
  Implementation following a judgment package goes to an Argon execution
  package (`magpie-gemini`) for backend-only tasks or stays with the primary for
  frontend or mixed tasks. An implementation-time Argon decision does not count
  as post-change review.

## Research lane: web-research skill with Gemini Flash

Whenever a project run needs web/public-source research, external retrieval or
evidence extraction:

1. Invoke the user's `web-research` skill and follow its rules (parallel count,
   fetch-before-cite, dated sources, gaps, lead synthesis).
2. Every research subagent it dispatches uses
   `subagent_type: "magpie-gemini-flash"` with no `model` or `effort`, as the
   skill itself specifies; if a loaded copy of the skill names another model,
   Flash still applies.
3. The primary performs the final synthesis and acceptance. Flash research
   agents never modify repository files. Never dispatch Flash outside this
   skill.

If Gemini Flash is unavailable, report the gap and do the research with the
primary; do not switch to another route.

## Route receipts

After each `magpie-*` worker finishes, a local hook writes a receipt to
`~/.claude/state/magpie-routing/<session_id>.json` (the prompt hook gives the
absolute path). Read the entry for that worker's agent id. This applies to every
`magpie-*` package, including read-only reviews and research:

- `verified`: the gateway's provider/model/served/status matched the worker's
  response ids; you may state the route actually ran.
- missing or `unverified`: it may be log delay; read again later or run
  `python3 ~/.claude/hooks/magpie-routing/magpie_router.py --audit <session_id>`.
  In Cursor (`Cursor Private Inference`), where subagents are defined in `.cursor/agents/magpie-*.md` / `~/.cursor/agents/magpie-*.md` with direct `provider/model` routes, if no `.claude/state/magpie-routing/<session_id>.json` entry was written for the turn, verify the completed call in `~/.config/magpie/usage.jsonl` (`provider`, `model`, `req`, `served`, `status: 200`). Until verified, report the route as unconfirmed.
- `mismatch`: treat the artifact as not produced by the requested lane; report
  it and do not accept it as that lane's deliverable.

A worker's self-reported identity or a correct answer is never route evidence.
Do not dispatch extra agents just to prove identity.

## Choose the lane

- **Routine backend bug:** one Argon (`magpie-gemini`) package with
  implementation and regression.
- **Frontend or mixed change:** the primary only; a fresh Argon
  (`magpie-gemini`) subagent may review the stable diff read-only.
- **Architecture or conflicting evidence:** bounded Argon (`magpie-gemini`)
  decision, then an Argon execution package (backend-only) or the primary
  (frontend or mixed) implements.
- **Public sources, datasheets, docs, pricing:** `web-research` skill with
  Gemini Flash research agents.
- **Live screen or app operation:** the primary; one controller.
- **Required lane unavailable:** keep the package with the primary for that
  concrete reason and report it; no silent substitution.

## Keep delegation economical

Direct tools are fine for deterministic one- or two-step checks with no
independent deliverable. "Small task", "cost", "handoff cost" or "shared state"
alone are not reasons to keep a qualifying non-frontend code package local.
Bundle related small steps into an existing Argon package. Do not re-delegate an
accepted artifact. Report measured usage or timing when available; never infer
savings from model names or agent counts.

## Escalate without churn

A worker stops and returns immediately at an unfrozen interface, second
plausible owning layer, missing authorization, ownership conflict, external
mutation outside its lease, or scope outside its lease. In backend-only tasks,
in-scope engineering uncertainty may first get a bounded Argon diagnostic
package; in frontend or mixed tasks the primary diagnoses. Difficult decisions
go to Argon with the gathered evidence and one exact question.
