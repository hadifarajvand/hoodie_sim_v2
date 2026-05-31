# Feature 077 Data Model

## CampaignSeedPlan

### Purpose

Define a deterministic seed schedule for future campaign execution.

### Fields

- `seed_ids: tuple[str, ...]`
- `minimum_seed_count: int`
- `reproducibility_rule: str`
- `record_seed_identity_in_results: bool`

### Validation Rules

- `seed_ids` must be non-empty.
- `minimum_seed_count` must be greater than zero.
- `seed_ids` must be unique.
- `reproducibility_rule` must be non-empty.
- `record_seed_identity_in_results` must be `True`.

## CampaignWorkloadLevel

### Purpose

Represent a workload level in the experimental campaign.

### Fields

- `name: str`
- `description: str`

### Validation Rules

- `name` must be one of `low`, `medium`, `high`.
- `description` must be non-empty.

## CampaignDeadlinePressureLevel

### Purpose

Represent a deadline pressure level in the experimental campaign.

### Fields

- `name: str`
- `description: str`

### Validation Rules

- `name` must be one of `relaxed`, `moderate`, `tight`.
- `description` must be non-empty.

## CampaignScenarioGridEntry

### Purpose

Define one future campaign grid cell.

### Fields

- `policy_id: str`
- `scenario_id: str`
- `seed_id: str`
- `workload_level: str`
- `deadline_pressure_level: str`
- `topology_mode: str`
- `runtime_mode: str`
- `compatibility_mode_used: bool`

### Validation Rules

- `policy_id` must be one of the required 7 policy/method IDs.
- `scenario_id` must be one of the required 7 scenario IDs.
- `seed_id` must be non-empty.
- `workload_level` must be one of `low`, `medium`, `high`.
- `deadline_pressure_level` must be one of `relaxed`, `moderate`, `tight`.
- `topology_mode` must equal `paper_figure_7`.
- `runtime_mode` must equal `paper`.
- `compatibility_mode_used` must be `False`.

## CampaignMetricSchema

### Purpose

Define the result metrics expected from future experiments.

### Fields

- `completed_count: int`
- `dropped_timeout_count: int`
- `dropped_unavailable_count: int`
- `deadline_violation_count: int`
- `illegal_action_rejection_count: int`
- `average_delay: float | None`
- `average_reward: float | None`
- `total_reward: float | None`
- `completion_rate: float | None`
- `timeout_drop_rate: float | None`
- `unavailable_drop_rate: float | None`
- `deadline_violation_rate: float | None`
- `compatibility_mode_used: bool`

### Validation Rules

- Count fields must be non-negative integers.
- Rate and average fields must be numeric or `None` when unavailable.
- `compatibility_mode_used` must be `False`.

## CampaignStatisticalSummarySchema

### Purpose

Define the statistical summary schema for campaign-level aggregation.

### Fields

- `mean: float | None`
- `std: float | None`
- `min: float | None`
- `max: float | None`
- `count: int`
- `ci95_low: float | None`
- `ci95_high: float | None`

### Validation Rules

- `count` must be greater than or equal to zero.
- If present, `ci95_low` and `ci95_high` must be numeric.
- Summary fields may be `None` only when no data exists.

## ExperimentalCampaignReadinessReport

### Purpose

Capture readiness for an experimental campaign without executing it.

### Fields

- `feature_id: str`
- `status: str`
- `passed: bool`
- `dependency_feature: str`
- `policy_ids: tuple[str, ...]`
- `scenario_ids: tuple[str, ...]`
- `seed_plan: CampaignSeedPlan`
- `workload_levels: tuple[str, ...]`
- `deadline_pressure_levels: tuple[str, ...]`
- `topology_mode: str`
- `runtime_mode: str`
- `expected_grid_size_formula: str`
- `metric_schema: CampaignMetricSchema`
- `statistical_summary_schema: CampaignStatisticalSummarySchema`
- `no_execution_performed: bool`
- `no_artifacts_generated: bool`
- `claim_boundary: tuple[str, ...]`
- `validation_summary: tuple[str, ...]`

### Validation Rules

- `feature_id` must identify Feature 077.
- `status` must record readiness state.
- `dependency_feature` must equal `076-combined-baseline-proposed-comparative-readiness`.
- `policy_ids` must contain exactly 7 required policy/method IDs.
- `scenario_ids` must contain exactly 7 required scenario IDs.
- `seed_plan` must be deterministic and non-empty.
- `workload_levels` must be exactly `low`, `medium`, `high`.
- `deadline_pressure_levels` must be exactly `relaxed`, `moderate`, `tight`.
- `topology_mode` must equal `paper_figure_7`.
- `runtime_mode` must equal `paper`.
- `expected_grid_size_formula` must match the campaign size definition.
- `metric_schema` must include the required metric fields.
- `statistical_summary_schema` must include the required summary fields.
- `no_execution_performed` must be `True`.
- `no_artifacts_generated` must be `True`.
- `claim_boundary` must explicitly prohibit final, superiority, statistical, reproduction, and training claims.
- `validation_summary` must document the readiness checks performed.
