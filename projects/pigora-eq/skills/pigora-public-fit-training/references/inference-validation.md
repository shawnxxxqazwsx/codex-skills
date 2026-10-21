# Inference engineering validation adapter

This adapter retains the strict `pigora-inference-validation-v1` numeric schema.
The owner-authorized prospective measured-product 0.5 dB fallback is a separate
gate under [measurement-acceptance.md](measurement-acceptance.md); this CLI
cannot adjudicate it at 48 kHz or replace objective smoothness/actual-audio
measurement. Preserve any strict-tier FAIL and use a separately versioned
production-verifier measurement certificate with independent review. Do not
rename a 0.5 dB fallback as this adapter's 0.2 dB baseline PASS.

Use `validate_inference_fit.py` only after an inference target, scope,
exclusions, public-state snapshot, candidate, response path, and per-rate
evaluations have been frozen and independently reviewed. The validator is a
read-only, standard-library-only adapter. It computes magnitude gates from the
rows; it does not trust a producer's PASS summary.

Its successful status means only **inference engineering numeric verification**
against the supplied frozen target. It does not establish public-source fit,
hardware equivalence, product selectability, safety/integration, deployment, or
hosted acceptance.

Existing dataset formats do not need to migrate. Export deterministic UTF-8 CSV
sidecars in the normalized schema below while preserving the original artifacts,
then bind both the sidecars and the producing candidate/response-path artifacts
in the reviewed manifest. The validator never rewrites an input.

## Command

The externally recorded reviewed-manifest hash is mandatory:

```bash
python3 .agents/skills/pigora-public-fit-training/scripts/validate_inference_fit.py \
  --manifest-sha256 <lowercase-sha256-of-reviewed-manifest> \
  /absolute/path/to/inference-validation-manifest.json
```

Paths inside the manifest may be absolute or relative to the manifest. Every
file entry is `{ "path": "...", "sha256": "..." }`. All hashes are lowercase
SHA-256. JSON objects and CSV headers are closed schemas: missing or additional
fields fail validation. Missing trailing CSV cells also fail through the normal
validation error path; intentional empty cells are permitted only for the
prediction/reason combinations defined by evaluation eligibility below.

## Reviewed manifest schema

```json
{
  "schema_version": "pigora-inference-validation-v1",
  "contract_kind": "donor-curve-inference-only",
  "claim_boundary": "inference-derived/source-informed approximation",
  "review": {
    "author_id": "fit-author",
    "reviewer_id": "independent-reviewer",
    "review_status": "reviewed",
    "review_decision_id": "inference-review-2026-09-05"
  },
  "scope": {
    "in_scope_identity_ids": ["identity-a"],
    "excluded_identity_ids": ["identity-b"]
  },
  "candidate": {
    "candidate_id": "candidate-v1",
    "candidate_artifact": {"path": "candidate.bin", "sha256": "..."},
    "response_path_id": "production-response-v1",
    "response_path_artifact": {"path": "response-path.bin", "sha256": "..."}
  },
  "target": {
    "path": "inference-target.csv",
    "sha256": "...",
    "target_grid_hash": "..."
  },
  "exclusions": {"path": "exclusions.csv", "sha256": "..."},
  "public_state_snapshot": {"path": "public-snapshot.csv", "sha256": "..."},
  "public_state_current": {"path": "public-current.csv", "sha256": "..."},
  "rates": [
    {
      "sample_rate_hz": 48000,
      "evaluation": {"path": "evaluation-48000.csv", "sha256": "..."},
      "declared_nyquist_hz": 24000,
      "condition_id": "host-condition-48k",
      "control_state_coverage": "complete-with-explicit-nyquist-ineligibility",
      "engineering_gate_kind": "inference-engineering-0.2",
      "engineering_gate_db": 0.2,
      "engineering_decision_id": "inference-rate-48000-v1",
      "baseline_engineering_decision_id": "not-applicable",
      "target_grid_hash": "...",
      "candidate_id": "candidate-v1",
      "response_path_id": "production-response-v1"
    },
    {
      "sample_rate_hz": 96000,
      "evaluation": {"path": "evaluation-96000.csv", "sha256": "..."},
      "declared_nyquist_hz": 48000,
      "condition_id": "host-condition-96k",
      "control_state_coverage": "complete-with-explicit-nyquist-ineligibility",
      "engineering_gate_kind": "sample-rate-engineering-0.5",
      "engineering_gate_db": 0.5,
      "engineering_decision_id": "inference-rate-96000-v1",
      "baseline_engineering_decision_id": "inference-rate-48000-v1",
      "target_grid_hash": "...",
      "candidate_id": "candidate-v1",
      "response_path_id": "production-response-v1"
    }
  ]
}
```

`contract_kind` is `sparse-grid-completion` or
`donor-curve-inference-only`. Reviewer and author must differ. Scope lists are
sorted, unique, disjoint, and non-empty on the in-scope side. Target identities
must exactly cover the in-scope list; excluded identities must have zero target
rows. The public snapshot and current-state files must exactly cover the union
of both lists and match row-for-row.

Each rate binds the same grid, candidate, and response path. Adapter review,
rate, and exclusion decision IDs use the `inference-` prefix and may not contain
`public` or `fallback` anywhere; rate IDs and exclusion IDs are unique within
their respective ledgers. A high-rate baseline reference must equal the actual
48 kHz inference decision ID. `declared_nyquist_hz` must
equal half the rate. A complete 48,000 Hz evaluation is mandatory in every
manifest, even if the only other declared rates are below 48 kHz. At and below
48,000 Hz, only the inclusive 0.2 dB `inference-engineering-0.2` gate is
accepted. A rate above 48,000 Hz may retain that same stricter 0.2 dB gate, or
may use the inclusive 0.5 dB `sample-rate-engineering-0.5` gate. Both high-rate
forms require the passing 48 kHz evaluation and bind its engineering decision
ID; the schema never forces a passing high-rate candidate onto the relaxed
tier. A high-rate result cannot rescue a failing baseline. Rates below 48 kHz
never receive the relaxed gate. Every rate is judged independently.

## Frozen target CSV

Exact header:

```text
row_id,identity_id,control_state_id,control_state_json,point_id,frequency_hz,target_magnitude_db,target_provenance
```

- `row_id` is unique across the file. The tuple `identity_id`,
  `control_state_id`, `point_id` is also unique.
- `control_state_json` is a canonical JSON object: UTF-8, keys sorted, no
  insignificant whitespace, such as `{"frequency_hz":1000,"gain_db":2}`.
  JSON constants `NaN`, `Infinity`, and `-Infinity` are rejected. Numeric
  literals that overflow the runtime JSON number domain, such as `1e999`, are
  also rejected at any nesting depth. Serialization uses `allow_nan=False`.
- Within one identity, every occurrence of a given `control_state_id` must map
  to the identical canonical `control_state_json`; a state ID cannot change
  meaning between frequency points.
- Frequency is finite and positive; target magnitude is finite.
- Provenance is `measured`, `image-digitized`, `inference-donor`,
  `human-supplemented-gain`, `human-supplemented-frequency`, or
  `human-supplemented-curve`.
- File order is frozen and is also the required evaluation order.

Provenance is further restricted by `contract_kind`:

- `donor-curve-inference-only` accepts only `inference-donor` and the three
  `human-supplemented-*` values. It cannot admit `measured` or
  `image-digitized` rows into this engineering-only target.
- `sparse-grid-completion` forbids `inference-donor` and requires at least one
  `measured` or `image-digitized` accepted anchor from the same frozen public
  subset, alongside any supplemented rows. The anchor is an engineering
  reference in this adapter and does not create or upgrade a public-fit pass.

If an older sparse-grid engineering format contains only generated rows, export
a normalized sidecar that carries the unchanged accepted anchor rows from the
same frozen subset, preserve their source traceability, and bind the complete
sidecar hash/grid in the manifest. This is an adapter requirement, not authority
to modify the old target, invent an anchor, or change a public/evidence state.

The target file SHA binds its exact bytes. `target_grid_hash` additionally binds
the normalized row semantics. It is SHA-256 of one compact, key-sorted JSON
object per target row, in file order, joined with `\n` and terminated by `\n`.
Numbers use non-exponent decimal form with trailing fractional zeroes removed;
negative zero is `0`. The implementation's `_load_target` routine computes this
hash for sidecar producers or focused tooling, but the reviewed manifest must
record it before formal evaluation.

## Per-rate evaluation CSV

Exact header:

```text
row_id,identity_id,control_state_id,control_state_json,point_id,frequency_hz,target_magnitude_db,target_provenance,sample_rate_hz,predicted_magnitude_db,eligibility,ineligibility_reason
```

Every file repeats every frozen target row, in the same order. Target identity,
state, point, frequency, magnitude, and provenance must match semantically and
exactly; missing, duplicate, additional, reordered, or changed rows fail.

For `frequency_hz < declared_nyquist_hz`, use `eligibility=eligible`, an empty
`ineligibility_reason`, and a finite prediction. The validator computes
`abs(predicted_magnitude_db - target_magnitude_db)` and applies the rate's gate
inclusively.

For a point at or above declared Nyquist, use `eligibility=ineligible`, leave
`predicted_magnitude_db` empty, and give a non-empty reason such as
`at-or-above-declared-nyquist`. Such a row remains in the evaluation so the same
target/domain is visible at every rate. A below-Nyquist exclusion or an omitted
above-Nyquist row is a silent hole and fails validation.

## Exclusion and public-state CSVs

Exclusion exact header:

```text
identity_id,exclusion_scope,exclusion_reason,product_use_state,public_fit_state,evidence_policy_state,engineering_decision_id
```

There is exactly one row per manifest-excluded identity. All fields are
non-empty. `product_use_state` must be
`not-product-selectable-inference`. Its public/evidence fields must equal the
frozen public snapshot. An excluded identity appearing in the target, or absent
from this ledger, fails. `engineering_decision_id` uses the same `inference-`
namespace and public/fallback keyword prohibition as the manifest review and
rate decisions.

Both public-state files have this exact header:

```text
identity_id,public_fit_state,evidence_policy_state
```

They contain one unique row for every in-scope and excluded identity. The
current file must exactly equal the snapshot. `public_fit_state` is one of
`public-fit passed`, `public-fit partial`, `public-fit failed/withheld`, or
`not publicly specified`; the validator preserves it but never upgrades or
re-adjudicates it. `evidence_policy_state` is a non-empty frozen project value
and must also remain unchanged.

## Output and limits

Success writes one deterministic JSON object and exits 0. The top-level status
is `inference-engineering-numeric-verification-passed`; per-rate results contain
computed eligible/ineligible counts, worst error, worst row, and gate. It
explicitly reports public fit, deployment, and product selectability as
unchanged/not adjudicated or not evaluated. Any schema, hash, coverage,
provenance, state-preservation, non-finite-number, or numeric-gate failure writes
`INFERENCE_ENGINEERING_NUMERIC_VERIFICATION FAIL` to stderr and exits 1.

Before emitting success, the validator re-hashes the reviewed manifest and
every bound target, exclusion, public-state, candidate, response-path, and
evaluation artifact. Any file changed between initial binding/parse and final
receipt causes a failure instead of a stale success receipt.

This validator does not prove that predictions really came from the named
response path; the reviewed manifest and bound response-path artifact establish
that chain of custody. It does not validate donor selection/transforms,
uncertainty, runtime safety, serialization, integration, deployment, or hosted
behavior. Those remain separate reviewed artifacts and gates under the Pigora
training contract.

Run the adapter regression suite after changing its implementation or schema:

```bash
python3 .agents/skills/pigora-public-fit-training/scripts/test_validate_inference_fit.py
```
