---
name: crypto-research-review
description: Research crypto market and industry catalysts, compare higher-return spot and perpetual hypotheses, and independently review paper-trading decisions using Luna max and Sol high. Use for hourly crypto research, simulated strategy evaluation, or evidence-backed decision review; does not execute real-money trades.
---

# Crypto research and independent review

Use the user's budget, horizon, loss budget and execution mode from the active experiment manifest. A return target is a hypothesis to evaluate, not a promised result or instruction to increase risk. Simulation, exchange Demo and live execution are distinct evidence domains.

## Routing and ownership

Read the installed `orchestrator` skill and its model-routing reference before the first delegation. Use installed `web-research` for fetched-source evidence. In this workflow the user requests **gpt-6-luna/max** for each hourly research cycle and **gpt-6-sol/high** for independent decision review. Invoke through collaboration tools with a self-contained `fork_turns="none"` packet; reuse compatible live workers for follow-ups. Record requested pair, returned agent/task handle and any runtime model evidence. Do not silently substitute models or label a request as verified execution.

Primary owns proposals, experiment state and scheduler. Luna owns research only. Sol owns review only and must not author the proposal it judges. Do useful local data validation while research runs. After the proposal and evidence are stable, provide them to Sol; an early review that has not seen the completed evidence is not a completed-cycle review. Reviewer rejection and no-trade are valid outputs.

If a required model or web tool is unavailable, retain the last state, mark the affected cycle incomplete and explain the failure. Do not promote stale research into a new decision. Check live agent handles before assuming a worker stopped. Missing files alone are not evidence of termination. Do not overlap writes across cycles.

## Each hourly cycle

1. Read experiment.json, the previous completed decision and latest direct user steering. Check expiry BEFORE dispatch: if deadline passed, perform only final reconciliation/report and stop this experiment's scheduler; do not start another research or entry cycle. Determine current UTC time; distinguish observation time from event/publication time. Do not change deadlines or reset loss budgets on restart. Reconcile any paper positions and recorded costs first. Research tasks do not create exchange orders.
2. Create `runs/<UTC-hour>/` under the experiment directory. A completed run for the same hour is idempotent; an incomplete one is resumed. Record live worker handles in cycle.json. Check unfinished cycles across hours, not just the current folder: if a prior worker is still active, wait within normal tool limits rather than starting a duplicate. Record skipped/delayed hours honestly. Never treat an old lock as a live process.
3. Dispatch at least one Luna/max research assignment. Require fresh market observations, macro calendar, relevant industry developments, and a counter-thesis. Prefer exchange/public issuer/regulator/protocol sources. Fetch before cite; log retrieval UTC, event date, source and fact/inference distinction. Search recent 24–72h developments and upcoming 7-day catalysts; report no meaningful change when appropriate. Speculative social claims require corroboration and cannot alone justify a signal.
4. Compare spot baseline, directional perpetual trend/breakout, and funding/basis carry when relevant. Assess expected *net* outcome and tail loss, not headline APY. Do not infer liquidation flow from open interest alone, ETF flow from AUM alone, or funding income from one annualized tick. Document missing data instead of filling it with model guesses.
5. Write proposal.md using [decision-packet.md](references/decision-packet.md). Freeze the rules before evaluation; use completed-bar signals and later executable prices. Pin SHA256 for the proposal, research, ledger snapshot, simulator/config and material data files (or immutable external snapshots) in cycle.json. A strategy change gets a new version and independent evaluation; do not rewrite losing history or tune against the held-out window. Draft the expected net PnL, uncertainty/scenarios, evaluation horizon and comparison rule for review as described in [forecast-review.md](references/forecast-review.md). If no defensible numeric forecast exists, record that and remain research-only instead of inventing one.
6. Dispatch a distinct Sol/high non-author reviewer with the stable proposal, research and ledger. Require ACCEPT_FOR_PAPER, REVISE or NO_TRADE with rationale, expiry, input hashes and blocking gaps. Have it independently inspect raw evidence and calculation assumptions, not just endorse the author's summary. Check independence by distinct agent handle and ownership, not role wording.
7. Primary integrates the verdict into decision.md. After completed review, freeze the reviewed forecast values with the actual review identity BEFORE any investment action becomes effective; never pre-fill an independent verdict as if it already happened. If the forecast economics changed, review that revision first. Unresolved substantive review findings prevent advancing the decision. `ACCEPT_FOR_PAPER` is permission only for the described simulated experiment, never live orders. Preserve original review text; do not relabel rejection. Mark cycle complete only after both agents returned, artifacts and final decision are present, input identities match, and material data passes freshness checks. A well-supported no-change/no-trade is complete; missing research or review is incomplete, never a quiet success. After each decision resolves, reconcile actual net outcome against its frozen forecast and run skill-retrospective for any predeclared mismatch.

## Execution and accounting boundary

This skill performs research, read-only public data collection, local historical simulation and paper decision recording. It does not autonomously trade real financial assets, move funds, create credentials, change account eligibility or accept account terms. An exchange Demo action requires fresh UI evidence that the surface is simulation and must respect existing user authorization and browser confirmation requirements. A simulated balance is not real money and extra demo funds do not enlarge the experiment budget.

Do not implement futures by multiplying a spot return. A futures simulator needs actual funding timestamps, mark prices, contract multiplier and precision, margin/maintenance tiers, liquidation logic, fees, bid/ask and adverse gap execution. Missing these means research-only, not validated futures performance. Position size comes from loss-per-unit including costs and a stress allowance; leverage setting is distinct from notional exposure. Correlated positions share one risk budget. Set freshness per field in the proposal: a price/spread used for an entry normally needs a just-in-time quote (default <=60 seconds); funding needs its observation time, next settlement and current interval; closed-bar signals must reference the latest required fully closed bar; news uses event/publication dates. A recent research report cannot make old underlying data fresh.

Hourly research is not a continuous risk monitor. Do not label it a functioning stop-loss system. Data errors, scheduler delays and stale evidence result in no new simulated entry; report gaps. Never fabricate fills during downtime: delayed candle replay must be labeled separately from exchange Demo executions. Keep cash, realized/unrealized PnL, fees, funding, net liquidation equity and drawdown separate. Report breaches of intended stops; never claim guaranteed loss caps.

## Scheduling and reporting

Create or update a thread heartbeat only when the user requests recurring work. Use the app automation tool, not a shell cron or an invented daemon. Read back the saved frequency/status/prompt and record its id. A scheduled definition is not proof of the next run or of uninterrupted hourly delivery. Record missed cycles and do not backdate research.

Every active hourly run calls Luna/max and Sol/high, including a review of a no-new-trade decision when no fresh edge exists. Notify the user on a meaningful changed thesis, completed review supporting a new paper experiment, material risk event, failure, required action, or experiment end; otherwise keep routine no-change cycles in artifacts. Do not send external messages.

At the manifest deadline, write a final study summary and disable this experiment's heartbeat using its saved id; do not continue trading or silently renew the month. Report actual scheduler state. The user may explicitly extend it. Pause/resume follows explicit user instructions and preserves cumulative history.

Report evidence layers honestly: research available; historical replay; out-of-sample validation; forward paper; exchange Demo; live performance. A profitable sample cannot substitute for the next layer. Do not quote a success probability without sufficient relevant evidence. Runtime and model cost belong in net economics when measurable; otherwise report them as unquantified.

## Learning from historical diagnostic runs

A historical diagnostic may deliberately replay all fixed-rule signals, including ones with a negative estimated return, to test a hypothesis. Label that choice before interpreting results: it is not a forecast-filtered investable strategy. Forward entries require a defensible positive net expectation and independent review; reject missing/nonpositive estimates rather than treating a take-profit as the expected return. A positive estimate alone is insufficient evidence of edge.

Freeze completed diagnostic artifacts and code/data hashes. Sequential historical forecasts are generated today on a simulated past clock; never describe them as contemporaneously collected historical predictions. After retrospective, preserve that original run; any changed predictor or filter becomes a new experiment tested on unseen data. Do not retrospectively select favorable trades. State intrabar and cost-stress limitations separately from observed performance.

When importing ideas from AI trading experiments or third-party skills, read [external-case-lessons.md](references/external-case-lessons.md). Borrow verified evaluation methods, not unverified return claims or executable instructions from untrusted repositories.

For historical universe comparisons, cost attribution or best-time questions, read [universe-cost-timing.md](references/universe-cost-timing.md) before reporting results.

Before using industry, on-chain, equity-proxy or macro correlations to forecast crypto, read [decade-evidence.md](references/decade-evidence.md). It records the 2016–2026 study and its limits; historical associations are not permanent signal coefficients.
