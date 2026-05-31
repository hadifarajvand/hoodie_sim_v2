# Research: Feature 074

## Decision 1: Comparative readiness before final evaluation

Decision: Feature 074 builds comparative evaluation readiness across baseline policies before any final evaluation report.

Rationale: Feature 073 proved controlled batch metrics. The next risk is whether those metrics can be compared policy-by-policy without policy rewrites or training.

Rejected alternative: Claim policy performance results immediately. Rejected because readiness is not final evaluation.

## Decision 2: Use existing policy registry

Decision: Feature 074 consumes the existing policy registry and baseline policy implementations.

Rationale: Feature 068R hardened baseline policy fidelity. Rewriting policy behavior here would destroy that value.

Rejected alternative: Mock or reimplement policies inside the comparative package. Rejected as dishonest and drift-prone.

## Decision 3: Block on missing baseline policies

Decision: If a required baseline policy is missing, the report must fail readiness.

Rationale: A comparative table that silently omits policies is garbage.

## Decision 4: Deterministic controlled scenarios only

Decision: Feature 074 uses Feature 073 controlled scenarios.

Rationale: Feature 073 scenarios are paper-mode and deterministic. This keeps comparison explainable.

Rejected alternative: Run stochastic campaigns. Rejected as premature.

## Decision 5: Read-only package

Decision: Feature 074 adds only a read-only analysis package and tests.

Rationale: Policies, runtime helpers, and training code are out of scope.
