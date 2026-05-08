# Data Model: Baseline Sensitivity Analysis

## Entities

### CampaignArtifactRoot

- `root_dir`: committed campaign artifact root
- `campaign_dir`: campaign summary directory
- `matrix_dir`: matrix result directory
- `trace_dir`: trace JSON directory
- `bundle_dir`: bundle output directory
- `audit_dir`: optional audit output directory

### TraceSensitivityRecord

- `scenario_name`: scenario identifier
- `seed`: shared seed identifier
- `trace_id`: trace identifier
- `task_count`: number of tasks in the trace
- `arrival_distribution`: counts by arrival slot
- `task_size_distribution`: distribution by task size when present
- `processing_density_distribution`: distribution by processing density when present

### PolicySensitivityRecord

- `policy_name`: policy identifier
- `action_distribution`: counts by selected action
- `terminal_outcome_distribution`: counts by terminal outcome
- `completed_tasks`: completed total
- `dropped_tasks`: dropped total
- `average_delay`: summarized delay

### ScenarioSensitivityRecord

- `scenario_name`: scenario identifier
- `throughput`: completed task throughput
- `drop_ratio`: fraction dropped
- `average_delay`: summarized delay
- `completed_tasks`: completed total
- `dropped_tasks`: dropped total

### SensitivityReport

- `trace_classification`: trace collapse findings
- `policy_classification`: policy collapse findings
- `scenario_classification`: scenario collapse findings
- `saturation_diagnosis`: saturation and masking findings
- `accounting_check`: reconciliation state
- `passed`: whether any blocking missing-data condition exists

## Relationships

- `CampaignArtifactRoot` is the source input to the analysis.
- `TraceSensitivityRecord` is grouped by scenario and seed.
- `PolicySensitivityRecord` is grouped by policy.
- `ScenarioSensitivityRecord` is grouped by scenario.
- `SensitivityReport` references all three record families and any optional audit report input.

## Validation Rules

- Inputs must be treated as read-only.
- Report ordering must be deterministic for the same artifact set.
- Missing or incomplete artifacts must be reported explicitly.
- Identical traces, identical policy signatures, and scenario collapse must be detected from the committed artifacts only.

