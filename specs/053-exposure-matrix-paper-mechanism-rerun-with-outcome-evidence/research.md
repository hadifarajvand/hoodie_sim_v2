# Research: Exposure Matrix Paper Mechanism Rerun with Outcome Evidence

## Decision 1: Use committed prior artifacts only

- **Decision**: Feature 053 will consume only the committed JSON report artifacts from Features 048, 049, 050, 051, and 052.
- **Rationale**: The feature is a rerun of paper-mechanism alignment, not a runtime repair. Committed artifacts provide stable inputs and avoid dirty-worktree dependence.
- **Alternatives considered**:
  - Reading current worktree state directly. Rejected because it would couple the report to transient local changes.
  - Regenerating prior artifacts. Rejected because the user explicitly prohibits prior-feature artifact rewrites.

## Decision 2: Gate the rerun on Feature 052 readiness

- **Decision**: Feature 052 readiness is a hard prerequisite, and the rerun must fail closed if the Feature 052 report is not fully ready.
- **Rationale**: Feature 053 exists to answer whether the project can advance after the selected-action evidence chain is complete.
- **Alternatives considered**:
  - Inferring readiness from partial evidence. Rejected because it would create false positives.
  - Running the alignment regardless of Feature 052 status. Rejected because the report would be built on an unsupported foundation.

## Decision 3: Separate alignment layers into independent top-level statuses

- **Decision**: The report will expose independent statuses for observation-vector, formula/unit, exposure-matrix, selected-action-outcome, and training-readiness contract alignment.
- **Rationale**: A single verdict without layer-specific evidence would obscure the actual blocker and weaken diagnostic value.
- **Alternatives considered**:
  - Using one aggregate readiness flag only. Rejected because it does not identify the failing layer.
  - Folding all failures into a single blocker string. Rejected because it reduces traceability and testability.

## Decision 4: Keep the rerun passive and evidence-only

- **Decision**: Feature 053 will not modify runtime semantics, policy behavior, or training logic.
- **Rationale**: The feature is a diagnostic rerun. Its job is to assess readiness, not repair the simulator.
- **Alternatives considered**:
  - Making runtime adjustments to force readiness. Rejected because it violates scope and would invalidate the rerun.

## Decision 5: Preserve behavior-equivalence as a separate audit

- **Decision**: The report will include behavior-equivalence results with unique check names.
- **Rationale**: The rerun must prove that the diagnostic path does not introduce drift while still allowing the paper-mechanism decision to be made.
- **Alternatives considered**:
  - Omitting behavior equivalence because the feature is diagnostic. Rejected because the report would then be unable to prove the rerun did not change outcomes.
