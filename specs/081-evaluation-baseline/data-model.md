# Feature 081 Data Model — HOODIE Evaluation & Baseline Benchmarking

## EvaluationConfig
Fields:
- `policies`: list of policy names
- `scenarios`: list of scenario names
- `workloads`: low, medium, high
- `deadline_pressures`: relaxed, moderate, tight
- `seeds`: deterministic integer seeds
- `topology_mode`: expected `paper_figure_7`
- `runtime_mode`: expected `paper`

## ScenarioContext
Fields:
- `scenario_name`
- `workload`
- `deadline_pressure`
- `seed`
- `vehicle_count`
- `task_type_count`
- `task_count`
- `scenario_duration`
- `local_available`
- `horizontal_destinations`
- `illegal_horizontal_destinations`
- `cloud_available`
- `deadline_slots`
- `network_condition`
- `queue_initial_state`

## PolicyDecision
Fields:
- `policy`
- `task_id`
- `action_type`: local, horizontal, vertical, reject
- `destination`
- `is_legal`
- `decision_trace`

## ExecutionOutcome
Fields:
- `task_id`
- `completed`
- `dropped_timeout`
- `dropped_unavailable`
- `deadline_violation`
- `illegal_action_rejected`
- `arrival_time`
- `completion_time`
- `delay`
- `reward`
- `queue_length_observations`

## MetricRow
Fields:
- `policy`
- `scenario`
- `workload`
- `deadline_pressure`
- `seed`
- `completed_count`
- `dropped_timeout_count`
- `dropped_unavailable_count`
- `deadline_violation_count`
- `illegal_action_rejection_count`
- `average_delay`
- `average_reward`
- `total_reward`
- `completion_rate`
- `timeout_drop_rate`
- `unavailable_drop_rate`
- `deadline_violation_rate`
- `throughput`
- `queue_stability_score`
- `compatibility_mode_used`

## RankingRow
Fields:
- `metric`
- `rank`
- `policy`
- `value`
- `direction`: higher_is_better or lower_is_better
- `tie_break_trace`

## Feature081Report
Fields:
- `status`
- `passed`
- `readiness_level`
- `policy_coverage`
- `scenario_coverage`
- `metric_coverage`
- `ranking_coverage`
- `summary_rows`
- `ranking_tables`
- `claim_boundary`
- `scope_proof`
- `remaining_gaps`
