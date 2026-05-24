# Research: Selected-Action Outcome Evidence Rerun

## Decision 1: Use Feature 051 readiness as a hard gate

- **Decision**: Feature 052 will not attempt rerun analysis unless Feature 051 reports `evidence_readiness_for_feature_050_rerun = true` and the associated readiness fields are all `available`/`ready`.
- **Rationale**: The rerun is only meaningful if the upstream trace population is complete and behaviorally stable.
- **Alternatives considered**: Running against partially populated trace evidence; rejected because it would reintroduce placeholder inference and stale blockers.

## Decision 2: Consume committed prior-feature artifacts only

- **Decision**: Feature 052 will read the committed Feature 048, 049, 050, and 051 JSON reports as inputs.
- **Rationale**: This keeps the rerun deterministic and prevents dirty-worktree leakage from influencing evidence.
- **Alternatives considered**: Rebuilding prior reports; rejected because it would invalidate the evidence-rerun contract.

## Decision 3: Compute rerun evidence as passive summaries

- **Decision**: The analysis will recompute counts, rates, consistency checks, and blocker lists without changing environment or policy behavior.
- **Rationale**: The feature’s purpose is to prove evidence status, not to repair runtime semantics.
- **Alternatives considered**: Modifying environment emission or policies; rejected as out of scope.

## Decision 4: Keep behavior-equivalence checks unique

- **Decision**: The rerun report will use unique behavior-equivalence check names and preserve them as stable identifiers.
- **Rationale**: Duplicate check names hide drift and reduce auditability.
- **Alternatives considered**: Aggregating checks without named labels; rejected because it obscures review.

## Decision 5: Treat exposure-matrix consistency as an evidence gate

- **Decision**: Exposure-matrix internal consistency will be assessed from rerun evidence and used to route the Feature 049 unblock assessment.
- **Rationale**: Feature 049 should only be considered rerunnable if the recomputed evidence remains internally consistent.
- **Alternatives considered**: Allowing Feature 049 rerun claims on incomplete or partially consistent evidence; rejected.
