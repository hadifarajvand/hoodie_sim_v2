# Research: Paper-Backed Evaluation Matrix

## Decision 1: Serial execution is the default and only supported mode

- **Decision**: Implement the matrix runner as a deterministic serial loop over policy, scenario, and seed combinations.
- **Rationale**: The clarified scope explicitly rejects parallel execution. Serial execution is simpler to audit and preserves ordering determinism.
- **Alternatives considered**:
  - Parallel fan-out
  - Distributed execution
  - Seed sharding
  - Rejected because they add coordination complexity and were out of scope.

## Decision 2: Registries must reject unknown names

- **Decision**: Implement explicit policy and scenario registries that accept only approved names.
- **Rationale**: The clarified scope says unsupported names are not aliases and must fail fast.
- **Alternatives considered**:
  - Fuzzy matching
  - Alias mapping
  - Auto-discovery from filesystem
  - Rejected because they silently widen scope and make validation weaker.

## Decision 3: Matrix artifacts are stdlib-only

- **Decision**: Emit per-run records and summaries using standard library formats only.
- **Rationale**: The spec rejects pandas, matplotlib, and external experiment trackers.
- **Alternatives considered**:
  - Dataframe-based summaries
  - Plot output
  - External tracking services
  - Rejected because they violate the no-dependency and no-plotting constraints.

## Decision 4: Reproducibility metadata must be explicit but not invented

- **Decision**: Record policy, scenario, seed, trace identifier, config values, and a dependency-change note. Include commit/ref only when available locally.
- **Rationale**: The matrix must be auditable without fabricating unavailable provenance.
- **Alternatives considered**:
  - Inventing a commit hash
  - Omitting run metadata
  - Rejected because they would weaken traceability or create false provenance.

## Decision 5: Existing evaluation metrics remain unchanged

- **Decision**: Reuse the existing evaluation metrics and finalize them through the current environment boundary.
- **Rationale**: The clarified scope forbids metric formula changes.
- **Alternatives considered**:
  - New matrix-specific metrics
  - Different formulas per policy
  - Rejected because they break comparability.

## Decision 6: Matrix orchestration belongs in evaluation, not policy or environment layers

- **Decision**: Place the matrix runner under `src/evaluation/` and drive policies externally through `PolicyContext`.
- **Rationale**: This keeps lifecycle ownership unchanged and preserves baseline fairness.
- **Alternatives considered**:
  - A policy-specific runner
  - Embedding orchestration in the environment
  - Rejected because they create special paths and violate the architecture boundary.
