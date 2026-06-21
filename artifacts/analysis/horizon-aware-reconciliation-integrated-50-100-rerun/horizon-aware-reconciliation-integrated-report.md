# Horizon-aware reconciliation integrated 50/100 report (Feature 081)

- recovery_strategy: `horizon_aware_recovered_reward_event`
- campaign_level_reward_reconciliation_passed: `True`
- campaign_level_terminal_reconciliation_passed: `True`
- raw_vs_canonical_reward_delta_max: `0.0`
- terminal_event_coverage_ratio_min: `1.0`

| policy | budget | completed | dropped | recovered_horizon_reward_events | delta | reward_recon | term_recon |
|---|---|---|---|---|---|---|---|
| deadline_queue_feasibility_candidate_at_50 | 50 | 1754 | 7767 | 83 | 0.0 | True | True |
| deadline_queue_feasibility_candidate_at_100 | 100 | 2589 | 6961 | 75 | 0.0 | True | True |
| fixed_local_policy | None | 2589 | 6961 | 75 | 0.0 | True | True |
| fixed_horizontal_policy | None | 1743 | 7778 | 83 | 0.0 | True | True |
| fixed_vertical_policy | None | 1413 | 8099 | 85 | 0.0 | True | True |
| random_legal_policy | None | 2551 | 7001 | 78 | 0.0 | True | True |
| legacy_minimal_candidate_at_50 | 50 | 2589 | 6961 | 75 | 0.0 | True | True |
| legacy_minimal_candidate_at_100 | 100 | 1413 | 8099 | 85 | 0.0 | True | True |
