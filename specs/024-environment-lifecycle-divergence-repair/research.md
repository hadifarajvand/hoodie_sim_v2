# Research: Environment Lifecycle Divergence Repair

## Decisions

### 1. Repair Scope
- **Decision**: Repair only local-compute lifecycle behavior, deterministic ordering behavior, and delayed reward timing when paper/OCR plus lifecycle evidence support the change.
- **Rationale**: These are the remaining lifecycle divergences explicitly named in the feature and they can be fixed without touching policy or training behavior.
- **Alternatives considered**: Broad simulator cleanup was rejected because it would drift into unrelated instrumentation and model changes.

### 2. Reference of Truth
- **Decision**: Use `src/reference_model/` as the lifecycle oracle for event ordering and terminal status expectations.
- **Rationale**: Feature 019 already established the reference lifecycle kernel as the authoritative comparator for lifecycle correctness.
- **Alternatives considered**: Inferring lifecycle correctness from the current environment alone was rejected because it would preserve the existing divergence.

### 3. Delayed Reward Handling
- **Decision**: Keep delayed reward timing paper-backed. If the HOODIE OCR and the lifecycle evidence do not support a tighter rule, classify the issue as an assumption gap rather than changing behavior.
- **Rationale**: Reward timing is a paper-faithful behavior constraint, not a place for invention.
- **Alternatives considered**: Automatic reward-timing repair from the reference kernel was rejected because the user explicitly restricted reward changes to paper-backed cases.

### 4. Regenerated Audit
- **Decision**: Regenerate the differential environment audit after repair and treat that regenerated audit as the success check.
- **Rationale**: The repair is only meaningful if the diagnostic result changes; otherwise the feature should stop and report the blocker.
- **Alternatives considered**: Claiming success from code changes alone was rejected because it would not prove lifecycle convergence.

### 5. Scope Guarding
- **Decision**: Add regression and scope-guard tests that reject policy, metric, baseline, training, dependency, lockfile, and campaign changes.
- **Rationale**: The repair must remain surgical and must not become a back door into broader simulator refactoring.
- **Alternatives considered**: Manual review alone was rejected because the constitution requires testable gates.

## Assumptions

- Feature 018 and Feature 019 artifacts remain available and are trustworthy inputs.
- The current differential audit still reports `case-local-compute` and `case-deterministic-ordering` as divergences until repaired.
- If the evidence is insufficient for delayed reward changes, the issue remains an assumption gap.
- The repair should not touch horizontal or vertical offload instrumentation unless it is strictly necessary for local-compute or deterministic-ordering correctness.
