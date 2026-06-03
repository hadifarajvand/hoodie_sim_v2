# Feature 081 Requirements Checklist

## Policies
- [x] HOODIE_PROPOSED adapter represented.
- [x] ORIGINAL_HOODIE_BASELINE adapter represented.
- [x] RANDOM_POLICY adapter represented.
- [x] LOCAL_ONLY adapter represented.
- [x] CLOUD_ONLY adapter represented.

## Scenarios
- [x] light_load_no_deadline_pressure represented.
- [x] tight_deadline_pressure represented.
- [x] legal_horizontal_offload represented.
- [x] illegal_horizontal_destination_attempt represented.
- [x] cloud_vertical_fallback represented.
- [x] timeout_drop_case represented.
- [x] mixed_local_horizontal_cloud_candidates represented.

## Metrics
- [x] completion_rate implemented.
- [x] timeout_drop_rate implemented.
- [x] unavailable_drop_rate implemented.
- [x] deadline_violation_rate implemented.
- [x] average_delay implemented.
- [x] average_reward implemented.
- [x] total_reward implemented.
- [x] throughput implemented.
- [x] queue_stability_score implemented.
- [x] illegal_action_rejection_count implemented.

## Ranking and Reporting
- [x] metric-by-metric ranking implemented.
- [x] deterministic tie-breaking implemented.
- [x] `build_feature_081_report()` implemented.
- [x] claim boundary included.
- [x] scope proof included.
