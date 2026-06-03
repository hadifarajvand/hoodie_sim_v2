# Feature 081 Tasks — HOODIE Evaluation & Baseline Benchmarking

## Task Group A — Specification Completion
- [x] Define policies under evaluation.
- [x] Define scenarios.
- [x] Define workload/deadline dimensions.
- [x] Define metrics and formulas.
- [x] Define ranking rules.
- [x] Define scope gates and claim boundary.

## Task Group B — Models
- [x] Create evaluation config model.
- [x] Create policy enum/name registry.
- [x] Create scenario context model.
- [x] Create action/outcome model.
- [x] Create metric row model.
- [x] Create ranking row model.
- [x] Create report model.

## Task Group C — Policy Adapters
- [x] Implement `LOCAL_ONLY` policy adapter.
- [x] Implement `CLOUD_ONLY` policy adapter.
- [x] Implement `RANDOM_POLICY` with seed control.
- [x] Implement `ORIGINAL_HOODIE_BASELINE` adapter or compatibility-mode adapter.
- [x] Implement `HOODIE_PROPOSED` adapter using Feature 080.
- [x] Reject illegal actions consistently.

## Task Group D — Scenario Generator
- [x] Implement `light_load_no_deadline_pressure`.
- [x] Implement `tight_deadline_pressure`.
- [x] Implement `legal_horizontal_offload`.
- [x] Implement `illegal_horizontal_destination_attempt`.
- [x] Implement `cloud_vertical_fallback`.
- [x] Implement `timeout_drop_case`.
- [x] Implement `mixed_local_horizontal_cloud_candidates`.
- [x] Add low/medium/high workload expansion.
- [x] Add relaxed/moderate/tight deadline-pressure expansion.
- [x] Add deterministic seed handling.

## Task Group E — Metrics
- [x] Implement completion_rate.
- [x] Implement timeout_drop_rate.
- [x] Implement unavailable_drop_rate.
- [x] Implement deadline_violation_rate.
- [x] Implement average_delay.
- [x] Implement average_reward.
- [x] Implement total_reward.
- [x] Implement throughput.
- [x] Implement queue_stability_score.
- [x] Implement illegal_action_rejection_count.

## Task Group F — Aggregation and Ranking
- [x] Aggregate by policy.
- [x] Aggregate by policy + scenario.
- [x] Aggregate by policy + workload.
- [x] Aggregate by policy + deadline pressure.
- [x] Build metric-by-metric ranking tables.
- [x] Implement deterministic tie-breaking.

## Task Group G — Report
- [x] Implement `build_feature_081_report()`.
- [x] Include policy coverage.
- [x] Include scenario coverage.
- [x] Include metric coverage.
- [x] Include ranking coverage.
- [x] Include claim boundary.
- [x] Include scope proof.
- [x] Include remaining gaps.

## Task Group H — Tests
- [x] Unit tests for policies.
- [x] Unit tests for scenarios.
- [x] Unit tests for metrics.
- [x] Unit tests for ranking.
- [x] Integration tests for report.
- [x] Scope guard tests rejecting DCQ/thesis drift.
