# Decision packet and review contract

Use a compact Markdown packet plus cycle.json, not an invented confidence score.

## proposal.md

- Cycle UTC, experiment id/version, mode, budget, fixed end time, current net equity and positions.
- Decision: research-only/no-new-position/hold/exit/proposed-paper-entry. Any existing position comes from a reconciled ledger, not memory.
- Instrument, direction and strategy version; why it might outperform the baseline; strongest counter-thesis.
- Source URLs, retrieved UTC, observation timestamp, event/publication timestamp, provenance; record unavailable fields.
- Entry trigger, expiration/invalidation, exit rules, units/notional, margin mode, liquidation distance, intended loss, aggregate correlated exposure, costs/funding and stress scenario. If no entry is proposed these fields may be N/A with a reason.
- Fees and funding must identify actual verified rates or clearly labeled assumptions. Do not assert 1 USDT equals one redeemable dollar or ignore fiat conversion.
- Historical windows, held-out window, benchmark, sample size, fee/slippage stress; distinguish measured facts from untested hypotheses. Disclose all variants tested and selection bias.
- Check whether +200 is plausible within the risk budget; failure to meet it is an allowed result. Do not loosen loss limits to force a positive answer.
- List blockers and information that would change the decision. Attach immutable forecast.json before any investment decision; specify net PnL expectation, scenarios, time horizon, comparison basis and tolerance using forecast-review.md. Do not fabricate an expected gain simply to complete the template.

## review.md

Reviewer handle/requested model-effort; exact proposal/research/ledger/simulator/config/material-data SHA256 or immutable snapshot identities; independent recalculation or source spot-check performed; verdict ACCEPT_FOR_PAPER / REVISE / NO_TRADE; material findings and required fixes; decision expiry; whether real-time execution/account eligibility remains unverified. Review forecast basis and cost/evaluation comparability. Changes to any material input invalidate approval for the changed decision.

The same model instance that wrote the proposal cannot serve as its independent reviewer. A review without the final proposal hashes is preliminary. Missing required market evidence blocks entry even if prose is persuasive. A no-trade decision does not require a fabricated entry price.

## cycle.json

Required fields: cycle_utc, started_at_utc, completed_at_utc (null until complete), status, experiment_version, researcher_handle, researcher_requested_model, researcher_requested_effort, reviewer_handle, reviewer_requested_model, reviewer_requested_effort, proposal_sha256, research_sha256, review_sha256, decision_sha256, material_input_hashes, forecast_path, verdict, observed_runtime_model_metadata (null when unavailable), missing_evidence. Explain N/A inputs for research-only decisions.

Allowed status: in_progress, complete, incomplete, skipped_duplicate. `complete` proves the research/review cycle only, not strategy profitability or real order execution. Save atomically after checking all referenced files and hashes. Final decisions and reviews are append-only by cycle/version; corrections get a new revision with an explanation.
