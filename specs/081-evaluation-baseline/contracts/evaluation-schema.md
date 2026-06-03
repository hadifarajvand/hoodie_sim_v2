# Feature 081 Contract — Evaluation Schema

## Required Public Function
The implementation must expose:

```python
build_feature_081_report()
```

## Report Contract
The returned report must include:
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

## Ranking Contract
Ranking must be metric-by-metric. No hidden overall score is allowed in Feature 081 unless a later spec explicitly defines it.
