# Data Model: HOODIE Training Foundation Readiness Audit

## Entities

### SourceGateBundle
- **Purpose**: Collects the prior feature artifacts that must be present and internally consistent before the audit runs.
- **Key Fields**:
  - `paper_ocr_artifact`
  - `mechanism_registry_artifact`
  - `differential_audit_artifact`
  - `mechanism_repair_summary_artifact`
  - `controlled_sweeps_artifact`
  - `baseline_fairness_rebuild_artifact`
  - `baseline_rebuild_sensitivity_audit_artifact`
  - `passed`

### ReadinessDimension
- **Purpose**: Represents one prerequisite area that must be ready before any future training loop can begin.
- **Key Fields**:
  - `name`
  - `supported`
  - `evidence_source`
  - `blocker_notes`

### MechanismGap
- **Purpose**: Captures a missing paper mechanism or training prerequisite needed for future DRL work.
- **Key Fields**:
  - `family`
  - `gap_type`
  - `severity`
  - `evidence`

### ReadinessAuditReport
- **Purpose**: Summarizes whether the project is blocked for future training work or ready to proceed.
- **Key Fields**:
  - `metadata`
  - `source_gate_status`
  - `readiness_dimensions`
  - `mechanism_gaps`
  - `blockers`
  - `verdict`
  - `limitations`
  - `disclaimers`
  - `reproducibility_details`

## Relationships

- `SourceGateBundle` must be valid before any `ReadinessAuditReport` is produced.
- Each `ReadinessDimension` may produce one or more `MechanismGap` entries.
- `MechanismGap` entries are aggregated into `ReadinessAuditReport` blockers and verdicts.

