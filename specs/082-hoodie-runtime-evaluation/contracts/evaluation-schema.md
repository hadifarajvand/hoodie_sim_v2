# Feature 082 Contract - Evaluation Schema

## Public Functions
- `build_feature_082_report()`
- `generate_hoodie_runtime_evaluation_artifacts()`
- `validate_hoodie_runtime_evaluation_artifacts()`

## Required Report Fields
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

## Required Policies
- `HOODIE_PROPOSED`
- `ORIGINAL_HOODIE_BASELINE`
- `RANDOM_POLICY`
- `LOCAL_ONLY`
- `CLOUD_ONLY`

## Required Scenarios
- `light_load_no_deadline_pressure`
- `tight_deadline_pressure`
- `legal_horizontal_offload`
- `illegal_horizontal_destination_attempt`
- `cloud_vertical_fallback`
- `timeout_drop_case`
- `mixed_local_horizontal_cloud_candidates`

## Required Metrics
- `completion_rate`
- `timeout_drop_rate`
- `unavailable_drop_rate`
- `deadline_violation_rate`
- `average_delay`
- `average_reward`
- `total_reward`
- `throughput`
- `queue_stability_score`
- `illegal_action_rejection_count`

