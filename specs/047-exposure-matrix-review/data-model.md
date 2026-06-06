# Data Model: Exposure-Matrix Review

## ExposureMatrixConfig

Represents the fixed paper-default analysis configuration.

Fields:
- feature_id
- episode_length
- timeout_slots
- node_count
- arrival_probability
- seeds
- strategies
- no_runtime_repair
- no_training

Validation rules:
- feature_id must equal `047-exposure-matrix-review`
- episode_length must equal 110
- timeout_slots must equal 20
- node_count must equal 20
- arrival_probability must equal 0.5
- seeds must equal `[0, 1, 2]`
- strategies must equal the approved five-strategy probe grid

## ExposureDecisionRecord

Represents one decision opportunity in the exposure matrix.

Fields:
- run_id
- strategy
- seed
- decision_opportunity_index
- generated_task_id
- admitted_slot
- selected_action
- legal_actions
- terminal_outcome
- queue_type
- transmission_started_at
- transmission_completed_at
- execution_started_at
- task_completed_at
- task_dropped_at
- pending_at_horizon_at
- wait_time_slots
- execution_progress_slots
- task_age_at_terminal

Relationships:
- Belongs to one strategy/seed run
- Contributes to action exposure, queue, and offload matrices

Validation rules:
- Every record must preserve the paper-default contract.
- Legal actions must be trace-backed when present.
- Missing legal evidence must be recorded as unavailable, not zero.

## ExposureMatrixMetrics

Represents the aggregate per-strategy and per-action summaries.

Fields:
- decision_opportunity_count
- generated_task_count
- admitted_task_count
- selected_action_count
- terminal_task_count
- completed_task_count
- dropped_task_count
- pending_at_horizon_count
- legal_local_count
- legal_horizontal_count
- legal_vertical_count
- selected_local_count
- selected_horizontal_count
- selected_vertical_count
- selected_illegal_local_count
- selected_illegal_horizontal_count
- selected_illegal_vertical_count
- legal_but_unselected_local_count
- legal_but_unselected_horizontal_count
- legal_but_unselected_vertical_count
- selected_illegal_action_count
- selected_illegal_action_examples
- selected_illegal_action_rate
- action_entropy
- per_action_completion_rate
- per_action_drop_rate
- per_action_pending_rate
- per_action_mean_wait_slots
- per_action_mean_execution_progress_slots
- per_action_mean_task_age_at_terminal
- private_queue_admission_count
- public_queue_admission_count
- cloud_queue_admission_count
- offloaded_transmission_started_count
- offloaded_transmission_completed_count
- offloaded_completed_count
- offloaded_dropped_count
- offloaded_pending_count

Validation rules:
- Aggregate metrics must use full-population counts when available.
- Representative sample records may not substitute for aggregate metrics.
- Illegal-selection counts and rates must be null/unavailable when legal evidence is missing.
- Illegal-selection rates must use `selected_action_count` as the denominator.

## ExposureMatrixReport

Represents the final JSON/Markdown report.

Fields:
- feature_id
- prerequisite_tags_verified
- prior_feature_gates_verified
- paper_default_runtime_verified
- exposure_matrix_input_sources
- exposure_matrix_population
- legal_action_evidence_source
- legal_action_evidence_coverage_ratio
- per_strategy_seed_matrix
- aggregate_exposure_matrix
- per_action_outcome_matrix
- per_queue_matrix
- offload_exposure_matrix
- illegal_action_summary
- exposure_bias_summary
- load_vs_exposure_summary
- matrix_completeness_summary
- dominant_exposure_findings
- diagnosis
- recommended_next_feature
- no_runtime_repair_performed
- no_training_started
- no_optimizer_step
- no_replay_training
- no_target_update_execution
- no_dependency_drift
- no_environment_contract_drift
- no_policy_drift
- no_reward_timing_change
- no_timeout_contract_drift
- no_capacity_contract_drift
- no_transmission_contract_drift
- no_action_legality_drift
- no_curve_fitting
- no_simulator_output_tuning
- no_paper_reproduction_claim
- final_verdict

Illegal action summary fields:
- selected_illegal_action_count
- selected_illegal_local_count
- selected_illegal_horizontal_count
- selected_illegal_vertical_count
- selected_illegal_action_examples
- selected_illegal_action_rate
- evidence_status

Validation rules:
- Legal exposure fields must be null/unavailable when legal evidence is missing.
- Final verdict must align with matrix completeness and evidence coverage.
