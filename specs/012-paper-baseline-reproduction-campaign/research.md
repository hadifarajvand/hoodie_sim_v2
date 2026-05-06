# Research: Paper Baseline Reproduction Campaign

## Decisions

### 1. Campaign orchestration boundary
- **Decision**: Implement the campaign as an orchestration layer that calls `EvaluationMatrixRunner` and `ReproducibilityBundleBuilder`.
- **Rationale**: This avoids duplicating environment stepping and keeps campaign logic separate from simulator behavior.
- **Alternatives considered**: Direct environment stepping was rejected because it would duplicate matrix runner logic and weaken traceability.

### 2. Artifact layout
- **Decision**: Emit campaign artifacts alongside the existing `matrix/` and `bundle/` outputs in a dedicated `campaign/` directory.
- **Rationale**: This makes the reproduction workflow auditable without overwriting matrix or bundle outputs.
- **Alternatives considered**: Writing campaign outputs in place was rejected because it would blur artifact boundaries.

### 3. Aggregation strategy
- **Decision**: Aggregate only the final metrics already produced by the evaluation matrix.
- **Rationale**: The campaign is a reproduction workflow, not a new analysis layer; changing formulas would violate scope.
- **Alternatives considered**: Recomputing metrics from traces was rejected because it duplicates existing validated logic and risks formula drift.

### 4. Determinism
- **Decision**: Use deterministic ordering and optional timestamp override for all campaign outputs.
- **Rationale**: Campaign artifacts must be comparable across repeated runs.
- **Alternatives considered**: Embedding live timestamps only was rejected because it would make validation noisy and non-reproducible.

### 5. Bundle integration
- **Decision**: Reference the reproducibility bundle after matrix outputs exist and include that reference in campaign artifacts.
- **Rationale**: The campaign should surface the audit package, not replace it.
- **Alternatives considered**: Duplicating bundle contents was rejected because it would create redundant artifacts and maintenance burden.

## Unresolved Items

None. The feature scope is bounded and the required behavior is explicit in the spec.
