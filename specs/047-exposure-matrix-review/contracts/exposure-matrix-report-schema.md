# Contract: Exposure Matrix Report Schema

## Purpose

Define the required JSON/Markdown report shape for Feature 047.

## Required Fields

- `feature_id`
- `prerequisite_tags_verified`
- `prior_feature_gates_verified`
- `paper_default_runtime_verified`
- `exposure_matrix_input_sources`
- `exposure_matrix_population`
- `legal_action_evidence_source`
- `legal_action_evidence_coverage_ratio`
- `per_strategy_seed_matrix`
- `aggregate_exposure_matrix`
- `per_action_outcome_matrix`
- `per_queue_matrix`
- `offload_exposure_matrix`
- `illegal_action_summary`
- `exposure_bias_summary`
- `load_vs_exposure_summary`
- `matrix_completeness_summary`
- `dominant_exposure_findings`
- `diagnosis`
- `recommended_next_feature`
- `no_runtime_repair_performed`
- `no_training_started`
- `no_optimizer_step`
- `no_replay_training`
- `no_target_update_execution`
- `no_dependency_drift`
- `no_environment_contract_drift`
- `no_policy_drift`
- `no_reward_timing_change`
- `no_timeout_contract_drift`
- `no_capacity_contract_drift`
- `no_transmission_contract_drift`
- `no_action_legality_drift`
- `no_curve_fitting`
- `no_simulator_output_tuning`
- `no_paper_reproduction_claim`
- `final_verdict`

## Field Semantics

- `exposure_matrix_population` must identify the population supporting aggregate counts.
- `legal_action_evidence_source` must identify the trace-backed legality source, or report `unavailable`.
- `legal_action_evidence_coverage_ratio` must expose the fraction of decision opportunities backed by legal evidence.
- `aggregate_exposure_matrix` must not be derived from representative samples.
- `matrix_completeness_summary` must state whether the matrix is complete, partial, or incomplete.
- `illegal_action_summary` must include `selected_illegal_action_count`, `selected_illegal_local_count`, `selected_illegal_horizontal_count`, `selected_illegal_vertical_count`, `selected_illegal_action_examples`, `selected_illegal_action_rate`, and `evidence_status`.
- `illegal_action_summary.selected_illegal_action_count`, `illegal_action_summary.selected_illegal_local_count`, `illegal_action_summary.selected_illegal_horizontal_count`, `illegal_action_summary.selected_illegal_vertical_count`, `illegal_action_summary.selected_illegal_action_examples`, and `illegal_action_summary.selected_illegal_action_rate` must be present and explicit when legal evidence exists.
- `illegal_action_summary.selected_illegal_action_rate` must use `selected_action_count` as its denominator.
- `aggregate_exposure_matrix.selected_illegal_action_count` must reflect full-population illegal selections when legal evidence exists.
- `per_strategy_seed_matrix[].selected_illegal_action_count` must reflect illegal selections per strategy and seed when legal evidence exists.
- When legal evidence is unavailable, illegal-selection counts and rates must be null/unavailable rather than zero.

## Verdict Values

- `exposure_matrix_complete_ready_for_observation_vector`
- `exposure_matrix_identifies_action_exposure_bias`
- `exposure_matrix_identifies_load_dominance`
- `exposure_matrix_identifies_offload_underexposure`
- `exposure_matrix_incomplete_requires_legality_evidence`
- `exposure_matrix_incomplete_requires_full_trace_collection`
- `prerequisite_blocked`
