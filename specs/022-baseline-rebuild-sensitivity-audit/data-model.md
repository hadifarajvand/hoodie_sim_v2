# Data Model: Baseline Rebuild Sensitivity Audit

## Entities

### SourceGateBundle
- **Purpose**: Collects the prior feature artifacts that must be present and internally consistent before the audit runs.
- **Key Fields**:
  - `feature_018_artifact`
  - `feature_019_artifact`
  - `feature_020_artifact`
  - `feature_021_artifact`
  - `passed`

### SensitivityDimension
- **Purpose**: Represents one controlled perturbation in the audit.
- **Key Fields**:
  - `name`
  - `values`
  - `supported`
  - `control_notes`

### BaselineSignature
- **Purpose**: Captures the observed baseline behavior for a particular setting.
- **Key Fields**:
  - `policy_name`
  - `scenario_name`
  - `seed`
  - `episode_length`
  - `completed_tasks`
  - `dropped_tasks`
  - `throughput`
  - `average_delay`
  - `signature`

### SensitivityAuditReport
- **Purpose**: Summarizes the audit outcome for reviewer and machine consumption.
- **Key Fields**:
  - `metadata`
  - `source_gate_status`
  - `sensitivity_dimensions`
  - `fairness_controls`
  - `included_baselines`
  - `reused_metrics`
  - `per_setting_signatures`
  - `collapse_stability_indicators`
  - `sensitivity_classification`
  - `limitations`
  - `disclaimers`
  - `reproducibility_details`

## Relationships

- `SourceGateBundle` must be valid before any `SensitivityAuditReport` is produced.
- Each `SensitivityDimension` yields one or more `BaselineSignature` entries.
- `BaselineSignature` entries are grouped into `SensitivityAuditReport` comparisons to determine whether the Feature 021 result is robust, fragile, worsened, or inconclusive.
