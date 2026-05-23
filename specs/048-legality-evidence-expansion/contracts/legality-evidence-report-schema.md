# Contract: Legality Evidence Report Schema

## Purpose

Define the required JSON/Markdown report shape for Feature 048.

## Required Fields

- `feature_id`
- `prerequisite_tags_verified`
- `prior_feature_gates_verified`
- `paper_default_runtime_verified`
- `legal_evidence_coverage_ratio`
- `legality_evidence_source`
- `legality_snapshot_schema`
- `legality_evidence_coverage_summary`
- `per_strategy_seed_legality_coverage`
- `action_mask_summary`
- `selected_illegal_action_summary`
- `selected_illegal_action_count`
- `selected_illegal_local_count`
- `selected_illegal_horizontal_count`
- `selected_illegal_vertical_count`
- `selected_illegal_action_rate`
- `selected_illegal_action_examples`
- `selected_illegal_action_evidence_status`
- `behavior_equivalence_summary`
- `exposure_matrix_unblocked`
- `recommended_next_feature`
- `no_runtime_repair_performed`
- `no_training_started`
- `no_optimizer_step`
- `no_replay_training`
- `no_target_update_execution`
- `no_dependency_drift`
- `no_policy_drift`
- `no_reward_timing_change`
- `no_timeout_contract_drift`
- `no_capacity_contract_drift`
- `no_transmission_contract_drift`
- `no_action_legality_drift`
- `no_action_selection_drift`
- `no_curve_fitting`
- `no_simulator_output_tuning`
- `no_paper_reproduction_claim`
- `final_verdict`

## Field Semantics

- `legal_evidence_coverage_ratio` must equal `legality_snapshot_count / decision_opportunity_count`, must be `0.0` when decision opportunities are known but no legality snapshots exist, and must be `null` when the denominator is zero.
- `legality_evidence_source` must identify the trace-backed source, runtime mask source, public helper source, or report `unavailable`.
- `legality_snapshot_schema` must describe the passive legality snapshot shape and version.
- `legality_evidence_coverage_summary` must state whether coverage is full, partial, or unavailable and must include `legal_evidence_coverage_ratio`.
- `per_strategy_seed_legality_coverage` must report coverage per strategy and seed.
- `selected_illegal_action_summary` must report whether illegal selections are observable and how they were derived.
- `behavior_equivalence_summary` must state whether the capture run matched the no-legality-capture baseline.
- `exposure_matrix_unblocked` must explicitly state whether Feature 049 can rerun the exposure matrix.

## Required Summary Fields

- `legality_evidence_coverage_summary.legal_evidence_coverage_ratio`
- `selected_illegal_action_count`
- `selected_illegal_local_count`
- `selected_illegal_horizontal_count`
- `selected_illegal_vertical_count`
- `selected_illegal_action_rate`
- `selected_illegal_action_examples`
- `selected_illegal_action_evidence_status`
- `selected_illegal_action_summary.selected_illegal_action_count`
- `selected_illegal_action_summary.selected_illegal_local_count`
- `selected_illegal_action_summary.selected_illegal_horizontal_count`
- `selected_illegal_action_summary.selected_illegal_vertical_count`
- `selected_illegal_action_summary.selected_illegal_action_rate`
- `selected_illegal_action_summary.selected_illegal_action_examples`
- `selected_illegal_action_summary.selected_illegal_action_evidence_status`
- `selected_illegal_action_summary.selected_illegal_action_evidence_status`

## Verdict Values

- `legality_evidence_ready_for_exposure_matrix_rerun`
- `legality_evidence_partial_requires_trace_depth_expansion`
- `legality_evidence_unavailable_requires_runtime_public_helper`
- `behavior_drift_detected`
- `prerequisite_blocked`
