# Execution and model routing

Use this reference before the first dispatch in the current session. Re-read
the live `Agent` (Claude) or `Task` (Cursor) tool schema and the available agent types at call time; this
file records routing policy, not a frozen API.

## Allowed routes

| Lane | `Agent` (Claude) / `Task` (Cursor) call | Configured route |
|---|---|---|
| Argon (code execution) | `subagent_type: "magpie-gemini"` | `antigravity/gemini-4-argon` |
| DeepSeek (code execution) | `subagent_type: "magpie-deepseek"` | `deepseek/deepseek-flash` |
| Grok (code execution) | `subagent_type: "generalPurpose"`, `model: "cursor/grok-4.7@500k"` | `cursor/grok-4.7@500k` |
| Research agents (only inside the `web-research` skill) | `subagent_type: "magpie-gemini-flash"` | `antigravity/gemini-3.8-flash` |
| Analysis, command, final review, progress checks, frontend, mixed tasks, live operation | none: the primary does it | Session primary model (any user-selected model) |

For `magpie-*` agents omit `model` and `effort`; the agent definition fixes the
route. Grok is the exception: pass `model: "cursor/grok-4.7@500k"` or the call
inherits the session primary. Never `fork` for these lanes. Every packet tells
the worker not to call `Agent` or `Task` itself.

Not proactively used: every ChatGPT/Codex route (`magpie-codex-sol`,
`magpie-codex-astra`, `magpie-codex-terra`, `magpie-codex-luna`),
`magpie-vertex-gemini`, and other Claude subagents (Opus, Sonnet, Fable, Haiku,
`Explore`). Use one only when the user names it in the current request, and
only for that request. They are never fallbacks. `generalPurpose` is only the
Grok lane. DeepSeek and Grok are active lanes, not excluded routes.

## QQ bot persona

This exception comes before the quota proportion. It applies only when the
package changes the QQ bot's persona or anthropomorphic setting: character,
voice, personality, or the prompt that defines how the bot speaks. Other QQ
bot work, including unrelated code, stays on the quota proportion.

- Every subagent for that persona package is Argon (`subagent_type:
  "magpie-gemini"`). Do not read `magpie quota` for it, and do not send it to
  DeepSeek or Grok. The over-¥100 DeepSeek priority does not apply.
- Web or public-source research inside that work still follows the research
  lane: `web-research` with `subagent_type: "magpie-gemini-flash"`. Flash is
  not part of the quota proportion on this work or on any other work.
- Frontend and visual edits stay with the primary. A read-only Argon review
  happens only when the user explicitly asks for an independent second review.
- QQ bot work may use the Gemini reserve below. Persona packages, other QQ bot
  packages, and Flash research inside QQ bot work stay eligible while the
  governing Gemini 7-day fraction is greater than 0 and the 5-hour window is
  not fully spent, including when the 7-day fraction is at or below 10%.

## Gemini 10% reserve for the QQ bot

Keep a 10% safety reserve in the Gemini pool for the QQ bot. The reserve and
every other Gemini quota judgment use `Gemini · 7 days` only. Do not use the
smaller of the 7-day and 5-hour windows. Across Antigravity accounts, use the
largest 7-day fraction whose `Gemini · 5 hours` remaining is greater than 0.
10% means 7-day remaining 10 on that 0–100 window, so the fraction is 0.10.

- For work that is not QQ bot work, Argon (`magpie-gemini`) and Gemini Flash
  (`magpie-gemini-flash`) are ineligible when that 7-day fraction is less than
  or equal to 0.10. A 5-hour remaining above 0 does not keep them eligible
  below this floor, and a 5-hour remaining below the 7-day remaining does not
  lower the fraction. Do not start a new Argon code package, optional review,
  or Flash research wave. Drop Argon from the proportion and recompute with
  the lanes that remain. For blocked research, the primary does the work and
  reports the reserve. Do not substitute another model.
- `Gemini · 5 hours` is only a spent-window gate. If its remaining is greater
  than 0, dispatch is still allowed under the 7-day rule. If its remaining is
  0, that account is fully spent for this window: do not dispatch Argon or
  Flash on it, including QQ bot work, until it resets.
- QQ bot work is the reserved consumer and is exempt, as stated in the persona
  section. The floor applies again as soon as the work is not for the QQ bot.
- Resuming an Argon or Flash worker already started above the floor may finish.
  Do not start another non-QQ-bot Gemini package once the reading is at or
  below 10%.
- Record the Gemini readings and whether the reserve blocked the lane.

## Quota proportion for code packages

Skip this section for a QQ-bot persona package and for every web-research
package. Also skip it for the primary's analysis, command, final review, and
progress checks; those are not packages. Before each other new Argon,
DeepSeek, or Grok code package, read live
remaining allowance and assign from those remaining fractions. Do not count
how many packages a lane has already taken, and do not try to make those
counts equal. Model fit does not choose among them. Repair rounds that
`resume` the same worker are not a new assignment and do not need a new reading.

Run `magpie quota antigravity deepseek cursor --json`. Argon and Grok use
`remaining / 100` on the plan window below. DeepSeek uses yuan divided by 100:

- **Argon:** on each Antigravity card, the Gemini pool only. The fraction is
  `Gemini · 7 days` remaining / 100. Ignore `Gemini · 5 hours` except as a
  spent-window gate: remaining greater than 0 still qualifies, and remaining 0
  removes that account. Do not take the smaller window. Ignore per-model rows
  and the Claude & GPT pool. If several accounts qualify, use the largest
  7-day fraction. For non-QQ-bot work, eligible only when that 7-day fraction
  is greater than 0.10 and the 5-hour remaining is greater than 0. At or below
  10% on the 7-day window, the
  [Gemini reserve](#gemini-10-reserve-for-the-qq-bot) removes Argon. QQ bot work
  stays eligible while the 7-day fraction is greater than 0 and the 5-hour
  remaining is greater than 0.
- **DeepSeek:** read the CNY amount in `balance` (the `¥` figure). Ignore the
  `$` figure. ¥100 is 100%, so the fraction is `yuan / 100` and is not capped:
  ¥39.21 is 0.3921, and ¥100 is 1. Eligible when that amount is greater than 0.
  A missing card, or a balance with no CNY amount, is not eligible.
- **Grok:** the Cursor card's included plan window, named `Weekly` (or
  `Monthly` when that is the plan window). Fraction is that window's
  `remaining / 100`. Eligible when it is greater than 0. Do not read
  `Grok Bot`. A spent Grok Bot allowance does not remove this lane. Do not
  treat `On-demand` as plan remaining.

If the DeepSeek CNY balance is greater than ¥100, DeepSeek takes priority:
give every new code package in this batch to DeepSeek and do not
apply the proportion. Record the yuan amount and that the over-¥100 priority
applied. The only exception is an optional second review, requested by the
user, of a diff that this DeepSeek worker
authored: skip it while another eligible lane remains.

Otherwise every eligible lane, including DeepSeek at `yuan / 100`, enters the
proportion below. Ignore how many times any lane was used before.

- The weight of a lane is its fraction divided by the sum of those fractions.
- One package: assign it by those weights. A lane with twice the remaining
  fraction gets twice the weight. Do not give every single package to the
  largest fraction, and do not keep a tally to force the weights afterward.
- Several packages ready at the same time: split this batch by the same
  weights. For each lane, `share = packages × fraction / sum of fractions`.
  Give each lane the integer part, then give each leftover package to the lane
  with the next largest fractional part. Do not look at earlier batches.
- If no lane is eligible, keep the package with the primary and report the
  readings.

Record each fraction, the shares, and the chosen lane. A route error or a
quota rejection drops that lane until the next reading shows allowance again,
then the same proportion is calculated again. If the chosen lane authored the
diff under review, skip it while another eligible lane remains and give the
package to the next lane in the proportion. Do not substitute a Codex route or
another Gemini route.

## Frontend exclusion comes first

Apply the [frontend exclusion](../SKILL.md#frontend-and-visual-work-primary-only)
before choosing an Argon, DeepSeek, or Grok execution package. Frontend or mixed
frontend/backend tasks, including their diagnosis, backend parts and tests,
stay with the primary. For an unrelated backend-only package, list frontend paths,
shared files containing frontend code, and scripts or generated outputs that
would change frontend content as excluded from its writable scope. Scope
discovered later stops and returns to the primary before any frontend action.

## Backend execution lane: Argon, DeepSeek, or Grok

The primary has already stated the analysis and command. Dispatch only the
implementation.

- Dispatch qualifying non-frontend code packages with a complete Chinese
  packet: the primary's hypothesis, paths, symptom, acceptance signal,
  writable scope, excluded resources, build lane, stop condition, return
  format. Tell the worker to return evidence rather than replace the
  primary's analysis. Choose the worker with the
  [quota proportion](#quota-proportion-for-code-packages) and record the fractions.
  - Argon: `subagent_type: "magpie-gemini"`.
  - DeepSeek: `subagent_type: "magpie-deepseek"`.
  - Grok: `subagent_type: "generalPurpose"` and `model: "cursor/grok-4.7@500k"`.
- Do not alternate models inside one package. A failed route or a spent
  allowance is reassigned by a fresh quota reading, not by model fit. None of
  the three silently substitutes for an unavailable route outside this split.
- Delegable non-frontend documentation or configuration packages also go to
  Argon, DeepSeek, or Grok by the same rule, or stay with the primary on a
  recorded cost reason; never to Flash.
- Keep implementation and tests in one package; continue the same worker with
  `SendMessage` (Claude) or `Task(resume=...)` (Cursor) for repair rounds.
- Builds and tests go through `python3 tools/mc_build_lane.py run --lane <id>
  --build-dir <dir> -- ...` with a dedicated lane per package. Deployment
  through `build-juce` needs the shared lock and stays inside the authorization
  the primary states in the packet.
- Require the worker to report changed files, commands run with raw results,
  and anything not run. The primary inspects the real diff before accepting.

## Optional second review

The primary performs the final review. Do not dispatch a reviewer for it.

Only when the user explicitly asks for an independent second review:

- Send a stable subject to the lane the quota rule selects: the diff or
  artifact paths, the acceptance criteria, the claim boundary, and one exact
  question or review scope. The package is read-only.
- Return format: findings ranked by severity, each with file/line, concrete
  failure scenario and suggested acceptance check.
- Never `resume` the authoring worker to review its own diff. If the quota
  rule selects the author's lane and another eligible lane remains, use that
  other lane. This review does not replace the primary's final review.

## Research lane: web-research skill with Gemini Flash

Whenever a project run needs web/public-source research, external retrieval or
evidence extraction:

1. Invoke the user's `web-research` skill and follow its rules (parallel count,
   fetch-before-cite, dated sources, gaps, lead synthesis).
2. Before dispatch, apply the
   [Gemini reserve](#gemini-10-reserve-for-the-qq-bot). For non-QQ-bot work,
   do not dispatch Flash when the Gemini 7-day fraction is at or below
   0.10, or when the 5-hour window is fully spent. Otherwise every research subagent uses
   `subagent_type: "magpie-gemini-flash"` with no `model` or `effort`, as the
   skill itself specifies; if a loaded copy of the skill names another model,
   Flash still applies. Flash is not part of the DeepSeek/Grok proportion.
3. The primary performs the final synthesis and acceptance. Flash research
   agents never modify repository files. Never dispatch Flash outside this
   skill.

If Gemini Flash is unavailable, or the reserve blocks it, report the gap and do
the research with the primary; do not switch to another route.

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

- **Routine backend bug:** the primary states the hypothesis and acceptance
  signal, then one backend package implements and regresses, assigned by the
  remaining-quota proportion. The primary reviews the result and checks the
  worker at least every three minutes while it runs.
- **Frontend or mixed change:** the primary only, including analysis and final
  review.
- **Architecture or conflicting evidence:** the primary decides. An execution
  package then implements the backend-only part of that decision, or the
  primary implements frontend or mixed work.
- **Public sources, datasheets, docs, pricing:** `web-research` skill with
  Gemini Flash research agents. The primary keeps synthesis.
- **Live screen or app operation:** the primary; one controller.
- **User-requested second review:** one read-only package by the
  remaining-quota proportion. It does not replace the primary's final review.
- **Required lane unavailable:** keep the package with the primary for that
  concrete reason and report it; no silent substitution.

## Keep delegation economical

Direct tools are fine for deterministic one- or two-step checks with no
independent deliverable. "Small task", "cost", "handoff cost" or "shared state"
alone are not reasons to keep a qualifying non-frontend code package local.
Bundle related small steps into the existing Argon, DeepSeek, or Grok package. Do not re-delegate an
accepted artifact. Report measured usage or timing when available; never infer
savings from model names or agent counts.

## Escalate without churn

A worker stops and returns immediately at an unfrozen interface, second
plausible owning layer, missing authorization, ownership conflict, external
mutation outside its lease, or scope outside its lease. The primary keeps the
diagnosis. A worker may run one already-commanded check; it does not take over
the analysis. Difficult decisions stay with the primary.
