# Research: Differential Environment Audit

## Decision 1: Use a dedicated audit package under `src/audits/differential_environment/`

- **Decision**: Implement the audit as an isolated analysis package rather than inside the simulator or the reference kernel.
- **Rationale**: The feature is diagnostic only and must not be conflated with environment repair or lifecycle behavior.
- **Alternatives considered**:
  - Putting the logic in `src/environment/` was rejected because it would entangle analysis with simulator behavior.
  - Extending `src/reference_model/` was rejected because the audit compares two systems and should remain distinct from either one.

## Decision 2: Compare deterministic toy-case fixtures through a stable case schema

- **Decision**: Define each toy case as a small declarative record with stable fields for case identity, task/action description, timeout boundary, and expected comparison context.
- **Rationale**: Deterministic fixtures make the audit reproducible and keep the report schema stable.
- **Alternatives considered**:
  - Free-form scenario strings were rejected because they make comparison inputs ambiguous.
  - External fixture loading was rejected because the feature does not need another file format layer.

## Decision 3: Use public `reset`/`step` interface access only

- **Decision**: Drive the current environment through its public `reset`/`step` lifecycle interface only.
- **Rationale**: This preserves the diagnostic boundary and ensures missing trace injection is reported as an instrumentation gap rather than patched away.
- **Alternatives considered**:
  - Direct private-method access was rejected because it would violate interface stability and audit purity.
  - Adding new environment hooks was rejected because the feature must not modify HoodieGymEnvironment.

## Decision 4: Preserve divergence and gap categories explicitly

- **Decision**: Classify outputs using the explicit comparison and finding taxonomy from the spec without normalization.
- **Rationale**: The feature’s purpose is to surface mismatches, not hide them.
- **Alternatives considered**:
  - Collapsing everything into a single pass/fail verdict was rejected because it destroys audit value.
  - Converting all unsupported cases to generic failures was rejected because it obscures instrumentation gaps and assumptions.

## Decision 5: Write deterministic JSON and Markdown artifacts under a feature-specific analysis directory

- **Decision**: Emit both artifacts under `artifacts/analysis/differential-environment-audit/` with deterministic filenames and ordering.
- **Rationale**: The spec requires reproducible outputs and explicit paths.
- **Alternatives considered**:
  - Writing into the main artifacts tree without a feature namespace was rejected because it would blur provenance.
  - Generating only one report format was rejected because the feature requires both machine-readable and human-readable outputs.

