# Efficient fitting without weaker evidence

Use these checkpoints for new model families, control laws, and fitting/runtime
rewrites. They refine the exploration loop, not the frozen evidence contract.
Reuse existing compatible receipts; do not restart completed stages merely to
adopt this workflow. No checkpoint authorizes opening protected holdouts,
changing targets, interrupting another task, or deploying a candidate.

## 1. Fail fast on the actual optimizer input

Before numerical optimization, run a preflight against the loaded input, not
just the configuration's declared hash. Bind the reviewed target artifact/grid
hash and verify identity, controls, frequencies, values, provenance, and row
coverage. For a training-only projection, verify its own hash and exact permitted
membership through the reviewed split manifest or guarded evaluator; do not
expose held-out values to the fitter. Reject missing, duplicate, extra, or
mismatched rows before spending optimizer time. Matching row IDs or counts alone
does not establish that two targets are the same.

## 2. Buy information with a bounded representative run

Choose representative training or authorized full-domain routes before fitting:
each distinct topology and boost/cut family, neutral and gain extremes,
frequency/control boundaries, and the declared near-Nyquist region. Include
interior gain/control states when available; endpoints alone cannot establish
the control law. This subset is a falsifier, never reduced acceptance coverage.

Measure residual/Jacobian cost on this subset. Prefer vectorized evaluation,
cached invariant terms, stable bounded parameterizations, and a small local
solve or justified warm start. Record solver, seed, evaluation count, wall time,
worst error, and reason for stopping. Choose a finite time/evaluation budget from
this pilot, rather than assuming a universal duration fits every model.

Escalate to larger multistart, differential evolution, Powell, or another costly
search only when a bounded comparison supports the hypothesis that initialization
or local minima own the failure. Record the expected benefit and next budget;
do not automatically chain several expensive solvers or increase iterations
while a target, capacity, conditioning, or control-law failure is unresolved.
Budget exhaustion ends that attempt, not the task: retain its result and select
the next evidence-backed diagnostic or hypothesis without relaxing thresholds.
When repeated bounded corrections and diagnosis establish practical inability
to meet 0.2 dB, follow [measurement-acceptance.md](measurement-acceptance.md)
for the owner's separately reviewed 0.5 dB fallback, prioritizing a defensible
pass rather than endless stricter-tier attempts. This changes neither target
nor objective smoothness limits; one poor run or elapsed time is insufficient.

## 3. Validate the control law before expensive runtime integration

After representative capacity is demonstrated, evaluate the frozen mathematical
candidate over the complete permitted domain and declared continuous-control
probes: intermediate gains, anchor crossings, neutral/baseline behavior, dense
inter-anchor shape, and intended direction or turning points. Distinguish source
error gates from separately declared engineering shape/continuity guards; do
not introduce a new numeric guard retroactively to judge a frozen candidate.
Use [curve-coverage.md](curve-coverage.md) for pole-aware probes, bounded local
extremum refinement, and effective-state accounting. Record frequency coverage
and control coverage independently; neither row count nor smooth coefficients
establish a smooth response. A demonstrated model-family shape defect triggers
one cheap scan of other bands using that structure before the repair is closed.
Do not automatically refit passing unrelated bands.

When a genuine protected holdout exists, first use safe training/synthetic
diagnostics. Prefer a separately frozen, authorized mathematical-prediction
evaluation before costly integration, if the owning contract permits it. If the
contract requires actual C++ predictions or exactly-once access, obey it; do not
open the holdout early for speed. Revealed values are no longer blind and may
not be silently reused for tuning. Mathematical passes are diagnostic and never
replace final production-path evaluation.

Separate target-to-control-law error from control-law-to-runtime error. If the
former already fails, replacing convolution, serialization, or UI cannot fix it.
Localize the failing layer before investing in downstream implementation.

## 4. Screen realtime feasibility before committing to an architecture

Bind the rate-dependent runtime scope from
[training-contract §1C](training-contract.md#1c-realtime-deployment-support-matrix)
during inventory, before committing to an architecture. Estimate order/taps,
memory, latency and operations at each required rate's corresponding channel
and buffer boundary, for one complete admitted native EQ per instance with all
sections available together in each tested mode and native control transitions.
Do not multiply independent rate/channel/slot maxima or turn rack size into the
first guaranteed workload. Expanded workloads are separately declared
extensions; frozen response, safety and authorization gates remain unchanged.
If feasibility
is uncertain, build only the bounded kernel/capacity probe needed to decide;
this may precede full fitting. A long FIR may remain an offline reference while
a different production realization is evaluated against the same frozen target.
Do not reduce target coverage or silently increase the runtime order ceiling.

Check representative serialized coefficients and actual intended arithmetic
precision early, including low-frequency conditioning and control transitions.
Stable poles and double-precision fits do not prove float runtime accuracy.
Likewise, one rate's passing coefficient bank does not validate a rate transform
or frequencies newly visible at higher rates. Final production validation still
requires the complete declared domain, each rate's applicable gate, realtime
safety, and the required hosted path.

## 5. Report where time went

Reuse the existing attempt receipt for stage start/end times, wall durations,
evaluation counts, cache/checkpoint reuse, failure owner, and next falsifier.
Separate source/target preparation, optimization, evaluation, runtime engineering,
build/host checks, and operational waiting. Do not sum overlapping parallel
durations as total elapsed time, or present inference evaluation time as fitting
time. When records are incomplete, report the measured stages and the unknown
remainder rather than inventing a total or a speedup.
