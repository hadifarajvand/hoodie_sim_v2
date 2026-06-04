# Validation Rules — Feature 085

## Baseline Validation Rules

- Active policy coverage must be exactly: `HOODIE, RO, FLC, VO, HO, BCO, MLEO`.
- `MQO` must not appear in active policy coverage, policy tables, rankings, or report headers.
- The baseline mapping matrix must show `MLEO` as canonical and `MQO` as retired legacy labeling.
- `HOODIE` must continue to point to the Feature 080 proposed-method runtime path.

## Formula Validation Rules

- The formula mapping matrix must include rows for:
  - `task_completion_delay`
  - `task_drop_ratio`
  - reward calculation
  - vertical offload delay
  - horizontal offload delay
  - DQN interface
  - DDQN interface
  - Dueling interface
  - LSTM interface
- Each row must have a code location, audit status, and required-fix field.
- Reported metric tables must use the canonical metric names defined in the audit spec.

## Artifact Validation Rules

- The regenerated audit bundle must include raw rows, aggregate tables, ranking tables, report files, and execution manifest files.
- The report must include claim boundary, scope proof, baseline mapping, and formula mapping summary.
- The validation gate must fail if `MQO` is present as an active policy or if any required formula mapping row is missing.

## Merge Gate Rule

- PR #24 must not be merged before the baseline correction and formula audit validations pass.
