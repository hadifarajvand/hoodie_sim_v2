# Feature 081 Tasks — HOODIE Evaluation & Baseline Benchmarking

## Task Group A — Specification Completion
- [x] Define policies under evaluation.
- [x] Define scenarios.
- [x] Define workload/deadline dimensions.
- [x] Define metrics and formulas.
- [x] Define ranking rules.
- [x] Define scope gates and claim boundary.

## Task Group B — Models
- [ ] Create evaluation config model.
- [ ] Create policy enum/name registry.
- [ ] Create scenario context model.
- [ ] Create action/outcome model.
- [ ] Create metric row model.
- [ ] Create ranking row model.
- [ ] Create report model.

## Task Group C — Policy Adapters
- [ ] Implement `LOCAL_ONLY` policy adapter.
- [ ] Implement `CLOUD_ONLY` policy adapter.
- [ ] Implement `RANDOM_POLICY` with seed control.
- [ ] Implement `ORIGINAL_HOODIE_BASELINE` adapter or compatibility-mode adapter.
- [ ] Implement `HOODIE_PROPOSED` adapter using Feature 080.
- [ ] Reject illegal actions consistently.

## Task Group D — Scenario Generator
- [ ] Implement `light_load_no_deadline_pressure`.
- [ ] Implement `tight_deadline_pressure`.
- [ ] Implement `legal_horizontal_offload`.
- [ ] Implement `illegal_horizontal_destination_attempt`.
- [ ] Implement `cloud_vertical_fallback`.
- [ ] Implement `timeout_drop_case`.
- [ ] Implement `mixed_local_horizontal_cloud_candidates`.
- [ ] Add low/medium/high workload expansion.
- [ ] Add relaxed/moderate/tight deadline-pressure expansion.
- [ ] Add deterministic seed handling.

## Task Group E — Metrics
- [ ] Implement completion_rate.
- [ ] Implement timeout_drop_rate.
- [ ] Implement unavailable_drop_rate.
- [ ] Implement deadline_violation_rate.
- [ ] Implement average_delay.
- [ ] Implement average_reward.
- [ ] Implement total_reward.
- [ ] Implement throughput.
- [ ] Implement queue_stability_score.
- [ ] Implement illegal_action_rejection_count.

## Task Group F — Aggregation and Ranking
- [ ] Aggregate by policy.
- [ ] Aggregate by policy + scenario.
- [ ] Aggregate by policy + workload.
- [ ] Aggregate by policy + deadline pressure.
- [ ] Build metric-by-metric ranking tables.
- [ ] Implement deterministic tie-breaking.

## Task Group G — Report
- [ ] Implement `build_feature_081_report()`.
- [ ] Include policy coverage.
- [ ] Include scenario coverage.
- [ ] Include metric coverage.
- [ ] Include ranking coverage.
- [ ] Include claim boundary.
- [ ] Include scope proof.
- [ ] Include remaining gaps.

## Task Group H — Tests
- [ ] Unit tests for policies.
- [ ] Unit tests for scenarios.
- [ ] Unit tests for metrics.
- [ ] Unit tests for ranking.
- [ ] Integration tests for report.
- [ ] Scope guard tests rejecting DCQ/thesis drift.
