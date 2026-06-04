# Data Model — Feature 085 HOODIE Baseline Fidelity Audit and Formula Mapping

## Core Entities

### BaselinePolicy
- `policy_id`: canonical audit label, for example `HOODIE`, `RO`, `FLC`, `VO`, `HO`, `BCO`, `MLEO`
- `legacy_labels`: optional aliases that must not appear in active audit outputs
- `behavior_summary`: paper-aligned description of the policy
- `code_location`: canonical module or adapter that implements the policy
- `status`: `implemented`, `legacy`, or `blocked`

### FormulaMappingRow
- `paper_reference`: equation, figure, or algorithm identifier
- `meaning`: plain-language meaning of the paper construct
- `expected_simulation`: what the repository should simulate
- `code_location`: file or module responsible for the behavior
- `status`: `verified`, `needs_audit`, or `needs_fix`
- `required_fix`: a short description of the repair needed if status is not verified

### ArtifactBundle
- `raw_rows.json` / `raw_rows.csv`
- `aggregate_by_policy.json` / `aggregate_by_policy.csv`
- `ranking_by_metric.json` / `ranking_by_metric.csv`
- `feature_085_audit_report.json` / `feature_085_audit_report.md`
- `execution_manifest.json`
- `baseline-mapping-matrix.md`
- `formula-mapping-matrix.md`

### MetricRow
- `task_completion_delay`
- `task_drop_ratio`
- `completion_rate`
- `timeout_drop_rate`
- `unavailable_drop_rate`
- `deadline_violation_rate`
- `average_reward`
- `total_reward`
- `throughput`
- `queue_stability_score`
- `illegal_action_rejection_count`

## Relationships

- One `ArtifactBundle` contains many `MetricRow` records and many `FormulaMappingRow` records.
- Each `BaselinePolicy` should map to at least one code location and one validation rule.
- Each `FormulaMappingRow` should link to at least one code location and one report or metric definition.

## Canonical Policy Set

- `HOODIE`
- `RO`
- `FLC`
- `VO`
- `HO`
- `BCO`
- `MLEO`

## Legacy Label Policy

- `MQO` is a legacy label only.
- It may be referenced in historical notes, but it must not appear in active policy coverage or ranked outputs.

## Formula Coverage Targets

- `task_completion_delay`
- `task_drop_ratio`
- reward calculation
- vertical offload delay
- horizontal offload delay
- DQN interface
- DDQN interface
- Dueling interface
- LSTM interface
