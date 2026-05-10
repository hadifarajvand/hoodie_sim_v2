# Data Model: Environment Lifecycle Divergence Repair

## Entities

### Lifecycle Divergence Case
- **Purpose**: A named divergence discovered by the differential environment audit.
- **Key Fields**:
  - `case_id`
  - `classification`
  - `terminal_outcome`
  - `evidence_source`
  - `repair_candidate`
  - `blocked_reason`

### Reference Lifecycle Kernel Event
- **Purpose**: A lifecycle step from `src/reference_model/` that defines the expected order for a task.
- **Key Fields**:
  - `sequence_index`
  - `slot`
  - `event_type`
  - `task_id`
  - `status`

### Repair Decision
- **Purpose**: The evidence-backed decision to apply a repair or stop with a blocker.
- **Key Fields**:
  - `decision`
  - `justification`
  - `evidence_sources`
  - `blocked_constraints`

### Repair Summary
- **Purpose**: The audit artifact documenting what changed and what remained blocked.
- **Key Fields**:
  - `repaired_cases`
  - `remaining_findings`
  - `scope_guard_results`
  - `regenerated_audit_paths`
  - `disclaimers`

## Relationships

- Each `Lifecycle Divergence Case` is compared against one or more `Reference Lifecycle Kernel Event` sequences.
- A `Repair Decision` is derived from the comparison between the current environment and the reference lifecycle kernel.
- The `Repair Summary` records the final decision, the regression tests, and the regenerated audit outputs.

## Validation Rules

- Local-compute and deterministic-ordering cases must not remain classified as `divergence / likely_environment_bug` after a successful repair.
- Delayed reward changes remain blocked unless supported by both paper OCR evidence and lifecycle evidence.
- Any repair requiring policy, metric, baseline, training, or campaign changes is blocked.
