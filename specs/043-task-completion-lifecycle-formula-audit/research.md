# Research: Task Completion Lifecycle and Formula Audit

## Decision 1: Audit-only package, no runtime mutation

- **Decision**: The feature will be implemented as an analysis package that consumes existing runtime outputs and trace metadata without changing environment, policy, reward, timeout, or topology behavior.
- **Rationale**: The feature’s purpose is diagnosis, not repair. Any runtime change would invalidate the audit and create a false explanation.
- **Alternatives considered**: Patching runtime completion behavior directly. Rejected because it would hide the root cause instead of classifying it.

## Decision 2: Fixed paper-default horizon and seeds

- **Decision**: Use `T = 110` and seeds `0, 1, 2` for the audit.
- **Rationale**: Feature 042 already established that the short `T = 20` probe was misleading. Reusing the same seed set keeps comparison stable.
- **Alternatives considered**: Smaller or arbitrary seed sets. Rejected because they would weaken reproducibility and make cross-feature comparison noisy.

## Decision 3: Strategy coverage matches Feature 042

- **Decision**: Audit the same strategy set as Feature 042: environment default, forced local, forced horizontal, forced vertical, and mixed legal round robin.
- **Rationale**: The feature is about lifecycle completion, so the same action-path coverage is needed to separate queue pressure from lifecycle failure.
- **Alternatives considered**: Adding new strategy families. Rejected because they would expand scope without improving the root-cause analysis.

## Decision 4: Hand-calculation model

- **Decision**: Compute expected cycles as `η × ρ`, then derive expected compute slots from host capacities and expected transmission slots from the paper-default horizontal and vertical/cloud rates.
- **Rationale**: The audit needs a paper-faithful formula baseline to compare against observed lifecycle behavior.
- **Alternatives considered**: Relying only on runtime counters. Rejected because counters alone cannot tell whether the formulas are inconsistent.

## Decision 5: Breakpoint classification

- **Decision**: Classify zero-completion behavior into queue pressure, lifecycle counter bug, runtime lifecycle bug, formula/unit mismatch, or inconclusive instrumentation.
- **Rationale**: The next feature depends on whether the runtime is valid but congested, or whether the lifecycle accounting is broken.
- **Alternatives considered**: Collapsing everything into a generic failure. Rejected because it would not tell the team what to do next.

## Decision 6: Passive analysis-side tracing only

- **Decision**: If metadata is insufficient, add passive tracing inside `src/analysis` only.
- **Rationale**: The feature must diagnose the problem without mutating simulator behavior.
- **Alternatives considered**: Instrumenting `src/environment`. Rejected by scope and by the diagnostic-only constraint.

## Decision 7: Reporting contract

- **Decision**: Reports must carry the required no-training, no-drift, no-tuning, and no-reproduction flags, plus a final verdict and recommended next feature.
- **Rationale**: The report is part of the audit evidence; it should fail closed if any anti-fraud signal is missing.
- **Alternatives considered**: Leaving these as narrative text. Rejected because the analysis gate needs schema-level checks.
