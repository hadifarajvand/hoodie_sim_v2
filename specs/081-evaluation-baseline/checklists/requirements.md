# Feature 081 Requirements Checklist

## Policies
- [ ] HOODIE_PROPOSED adapter represented.
- [ ] ORIGINAL_HOODIE_BASELINE adapter represented.
- [ ] RANDOM_POLICY adapter represented.
- [ ] LOCAL_ONLY adapter represented.
- [ ] CLOUD_ONLY adapter represented.

## Scenarios
- [ ] light_load_no_deadline_pressure represented.
- [ ] tight_deadline_pressure represented.
- [ ] legal_horizontal_offload represented.
- [ ] illegal_horizontal_destination_attempt represented.
- [ ] cloud_vertical_fallback represented.
- [ ] timeout_drop_case represented.
- [ ] mixed_local_horizontal_cloud_candidates represented.

## Metrics
- [ ] completion_rate implemented.
- [ ] timeout_drop_rate implemented.
- [ ] unavailable_drop_rate implemented.
- [ ] deadline_violation_rate implemented.
- [ ] average_delay implemented.
- [ ] average_reward implemented.
- [ ] total_reward implemented.
- [ ] throughput implemented.
- [ ] queue_stability_score implemented.
- [ ] illegal_action_rejection_count implemented.

## Ranking and Reporting
- [ ] metric-by-metric ranking implemented.
- [ ] deterministic tie-breaking implemented.
- [ ] `build_feature_081_report()` implemented.
- [ ] claim boundary included.
- [ ] scope proof included.
