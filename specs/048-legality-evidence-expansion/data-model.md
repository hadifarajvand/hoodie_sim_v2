# Data Model: Legality Evidence Expansion

## LegalityEvidenceConfig

Represents the fixed paper-default passive instrumentation configuration.

Fields:
- feature_id
- episode_length
- timeout_slots
- node_count
- arrival_probability
- seeds
- strategies
- capture_runtime_mask
- capture_public_legality_helper
- capture_trace_legality_snapshot
- no_runtime_repair
- no_training

Validation rules:
- feature_id must equal `048-legality-evidence-expansion`
- episode_length must equal 110
- timeout_slots must equal 20
- node_count must equal 20
- arrival_probability must equal 0.5
- seeds must equal `[0, 1, 2]`
- strategies must equal the approved five-strategy probe grid
- capture flags must remain passive and behavior-equivalent

## LegalitySnapshot

Represents the per-decision legality evidence for a selected or selectable action opportunity.

Fields:
- strategy
- seed
- slot
- agent_id
- task_id
- selected_action
- action_index
- legal_local
- legal_horizontal
- legal_vertical
- legal_action_mask
- selected_was_legal
- selected_illegal_reason
- legal_horizontal_neighbors
- horizontal_neighbor_count
- vertical_available
- cloud_available
- private_queue_available
- public_queue_available
- legality_evidence_source
- legality_snapshot_schema_version

Relationships:
- Belongs to one strategy/seed run
- Supports legality evidence coverage summaries
- Supports selected-illegal-action derivation for Feature 049

Validation rules:
- Every record must preserve the paper-default runtime contract.
- Missing decision opportunities must be marked unavailable, not invented.
- Legal evidence sources must be trace-backed or explicitly unavailable.

## LegalityEvidenceRecord

Represents one captured legality observation attached to a decision opportunity.

Fields:
- snapshot_id
- strategy
- seed
- slot
- agent_id
- task_id
- selected_action
- action_index
- legal_action_mask
- selected_was_legal
- selected_illegal_reason
- legality_evidence_source
- capture_mode
- evidence_notes

Validation rules:
- Records must not change runtime behavior.
- Records must distinguish between availability and legality.

## BehaviorEquivalenceCheck

Represents one check that compares a legality-capture run against a no-legality-capture baseline.

Fields:
- check_name
- verified
- details
- baseline_run_id
- capture_run_id

Validation rules:
- The same seeds, strategies, and paper-default config must be used for baseline and capture runs.
- A failed equivalence check blocks Feature 049 routing.

## LegalityEvidenceReport

Represents the final JSON/Markdown report.

Fields:
- feature_id
- legal_evidence_coverage_ratio
- prerequisite_tags_verified
- prior_feature_gates_verified
- paper_default_runtime_verified
- legality_evidence_source
- legality_snapshot_schema
- legality_evidence_coverage_summary
- per_strategy_seed_legality_coverage
- action_mask_summary
- selected_illegal_action_summary
- selected_illegal_action_count
- selected_illegal_local_count
- selected_illegal_horizontal_count
- selected_illegal_vertical_count
- selected_illegal_action_rate
- selected_illegal_action_examples
- selected_illegal_action_evidence_status
- behavior_equivalence_summary
- exposure_matrix_unblocked
- recommended_next_feature
- no_runtime_repair_performed
- no_training_started
- no_optimizer_step
- no_replay_training
- no_target_update_execution
- no_dependency_drift
- no_policy_drift
- no_reward_timing_change
- no_timeout_contract_drift
- no_capacity_contract_drift
- no_transmission_contract_drift
- no_action_legality_drift
- no_action_selection_drift
- no_curve_fitting
- no_simulator_output_tuning
- no_paper_reproduction_claim
- final_verdict

Validation rules:
- Legal evidence fields must be null/unavailable when evidence is missing.
- `legal_evidence_coverage_ratio` must equal `legality_snapshot_count / decision_opportunity_count`, must be `0.0` when decision opportunities are known but no legality snapshots exist, and must be `null` when the denominator is zero.
- `selected_illegal_action_count`, `selected_illegal_local_count`, `selected_illegal_horizontal_count`, and `selected_illegal_vertical_count` must be null when legal evidence is unavailable.
- `selected_illegal_action_rate` must use `selected_action_count` as its denominator and must be null when the denominator is unavailable.
- `selected_illegal_action_examples` must remain representative examples only.
- `selected_illegal_action_evidence_status` must report whether illegal-selection evidence is available, unavailable, or partial.
- Behavior equivalence must be explicit and pass before Feature 049 is recommended.
