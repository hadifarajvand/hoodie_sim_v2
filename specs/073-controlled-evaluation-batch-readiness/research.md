# Research: Feature 073

## Decision 1: Controlled batch before comparative evaluation

Decision: Feature 073 builds controlled evaluation batch readiness before baseline comparison reports.

Rationale: Feature 072 validated deterministic traces. The next risk is whether several controlled scenarios can produce consistent metrics. Baseline comparison is premature until this layer exists.

Rejected alternative: Jump directly to baseline comparison. Rejected because that would make tables before proving batch metrics are stable.

## Decision 2: Deterministic scenarios only

Decision: Feature 073 uses deterministic scenario fixtures.

Rationale: Random or large campaigns make debugging impossible at this stage.

Rejected alternative: Full stochastic simulation. Rejected as too broad for readiness.

## Decision 3: Paper mode only by default

Decision: Controlled evaluation uses Feature 071 paper mode by default.

Rationale: Compatibility mode exists only as explicit legacy behavior. Evaluation metrics must not accidentally include it.

Rejected alternative: Allow compatibility mode silently. Rejected because it corrupts paper-semantic metrics.

## Decision 4: Metrics are readiness metrics, not final results

Decision: Feature 073 reports completed/drop/violation/delay/reward metrics as readiness evidence.

Rationale: These metrics prove the evaluation harness can compute defensible values. They do not prove performance superiority.

Rejected alternative: Claim final evaluation results. Rejected as overclaiming.

## Decision 5: Read-only analysis package

Decision: Feature 073 adds a read-only analysis package.

Rationale: Runtime semantics were handled by Feature 071 and golden traces by Feature 072. Feature 073 should not rewrite runtime, policies, or agents.
