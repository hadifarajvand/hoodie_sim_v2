# Feature 065 Report Contract

## Required artifacts

- `artifacts/analysis/paper-state-action-space-batch/paper-state-action-space-batch-report.json`
- `artifacts/analysis/paper-state-action-space-batch/paper-state-action-space-batch-report.md`
- `artifacts/analysis/paper-state-action-space-batch/paper-state-vector-contract.json`
- `artifacts/analysis/paper-state-action-space-batch/paper-action-space-contract.json`
- `artifacts/analysis/paper-state-action-space-batch/paper-load-history-contract.json`
- `artifacts/analysis/paper-state-action-space-batch/paper-lstm-forecast-input-contract.json`
- `artifacts/analysis/paper-state-action-space-batch/legal-destination-mask-contract.json`

## Required top-level report fields

- `feature_id`
- `batch_items_covered`
- `prerequisite_tags_verified`
- `feature_064_verified`
- `paper_state_vector_summary`
- `waiting_time_summary`
- `public_queue_vector_summary`
- `load_history_matrix_summary`
- `lstm_forecast_input_summary`
- `destination_action_space_summary`
- `legal_destination_mask_summary`
- `compatibility_summary`
- `safety_summary`
- `remaining_blockers`
- `recommended_next_feature`
- `final_verdict`

## Passing verdict

- `feature_id = 065-paper-state-action-space-batch`
- `feature_064_verified = true`
- `remaining_blockers = []`
- `recommended_next_feature = Feature 066 — Distributed Multi-Agent HOODIE Training Batch`
- `final_verdict = paper_state_action_space_batch_passed`

## Required summary fields

### paper_state_vector_summary

- `structured_state_enabled`
- `task_features_present`
- `private_waiting_time_present`
- `offloading_waiting_time_present`
- `public_queue_vector_present`
- `load_history_matrix_present`
- `legal_destination_mask_present`
- `state_dim`

### waiting_time_summary

- `private_waiting_time_slots_source`
- `offloading_waiting_time_slots_source`
- `zero_empty_queue_behavior`
- `not_global_history_length_guess`

### public_queue_vector_summary

- `destination_node_order`
- `vector_length`
- `edge_agent_count`
- `cloud_included`

### load_history_matrix_summary

- `lookback_w`
- `edge_agent_count`
- `matrix_shape`
- `node_order`
- `source`
- `padding_policy`

### destination_action_space_summary

- `destination_specific_actions_enabled`
- `generic_horizontal_only_removed_or_fenced`
- `action_registry_size_by_source`
- `cloud_action_present`

### legal_destination_mask_summary

- `local_allowed`
- `only_topology_neighbors_allowed`
- `cloud_allowed`
- `illegal_non_neighbors_rejected`
- `mask_aligned_to_action_registry`

## Required safety fields

- `no_training_rerun`
- `no_prior_feature_artifact_rewrite`
- `no_reward_timing_change`
- `no_dependency_drift`
- `no_paper_reproduction_claim`
- `no_unsupported_superiority_claim`
