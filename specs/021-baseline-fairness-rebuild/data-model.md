# Data Model: Baseline Fairness Rebuild

## Entities

### Source Gate Artifact
- **Purpose**: Captures the prior credibility evidence required before the rebuild can run.
- **Attributes**:
  - `feature_id`
  - `artifact_path`
  - `status`
  - `key_finding`
  - `relevance_to_rebuild`

### Baseline Policy
- **Purpose**: Represents one existing baseline policy included in the fairness matrix.
- **Attributes**:
  - `policy_name`
  - `policy_source`
  - `scenario_coverage`
  - `run_count`

### Rebuild Scenario
- **Purpose**: Represents one of the smallest existing scenarios/traces selected for fairness checking.
- **Attributes**:
  - `scenario_name`
  - `trace_identifier`
  - `seed`
  - `workload_notes`

### Collapse Indicator
- **Purpose**: Captures the qualitative collapse signature for a baseline run or comparison set.
- **Attributes**:
  - `policy_name`
  - `scenario_name`
  - `completed_tasks`
  - `dropped_tasks`
  - `differentiation_signal`
  - `collapse_status`

### Fairness Rebuild Report
- **Purpose**: The final JSON and Markdown artifacts summarizing the baseline fairness rebuild.
- **Attributes**:
  - `metadata`
  - `source_gate_status`
  - `baseline_policies_included`
  - `scenarios_used`
  - `fairness_controls`
  - `metrics_reused`
  - `collapse_indicators`
  - `anti_collapse_assessment`
  - `unchanged_collapse_explanation`
  - `limitations`
  - `disclaimers`
  - `reproducibility`
  - `overall_status`

## Relationships

- Each `Baseline Policy` is evaluated across the same set of `Rebuild Scenario` entries.
- Each `Collapse Indicator` is derived from the policy/scenario evaluation results.
- The `Fairness Rebuild Report` aggregates all source gates, policies, scenarios, indicators, and conclusions.

## Validation Rules

- The rebuild must use existing baseline policies only.
- The rebuild must use identical workload conditions across all baselines.
- The collapse classification must be qualitative and must not depend on new metric formulas.
- The report must preserve the possibility that collapse is a mechanism property rather than a bug.
