# Data Model: Feature 065

## PaperFaithfulStateActionSpaceBatchReport

Fields:

- `feature_id`
- `batch_items_covered`
- `feature_064_verified`
- `paper_state_contract_summary`
- `waiting_time_summary`
- `public_queue_vector_summary`
- `load_history_summary`
- `forecast_input_summary`
- `destination_action_space_summary`
- `legal_mask_summary`
- `compatibility_summary`
- `safety_summary`
- `remaining_blockers`
- `recommended_next_feature`
- `final_verdict`

## PaperStateSnapshot

Must represent the paper-facing observation surface.

Required fields:

- `source_agent_id`
- `task_size_mbits`
- `private_waiting_time_slots`
- `offloading_waiting_time_slots`
- `public_queue_lengths_by_destination`
- `public_queue_destination_order`
- `load_history_matrix`
- `load_history_shape`
- `forecast_input_matrix`
- `forecast_input_shape`
- `active_queue_counts_by_node`
- `legal_destination_ids`
- `paper_state_version`

## WaitingTimeSnapshot

Required fields:

- `private_waiting_time_slots`
- `offloading_waiting_time_slots`
- `waiting_time_source`
- `waiting_time_exactness`

## PublicQueueVectorSnapshot

Required fields:

- `public_queue_lengths_by_destination`
- `public_queue_vector_length`
- `public_queue_destination_order`
- `public_queue_source_scope`

## PaperLoadHistorySnapshot

Required fields:

- `window_w`
- `node_order`
- `load_history_matrix`
- `load_history_shape`
- `active_queue_counts_by_node`

The expected shape is `W × (N+1)`.

## ForecastInputSnapshot

Required fields:

- `forecast_input_matrix`
- `forecast_input_shape`
- `forecast_input_source`
- `forecast_output_status`

## DestinationActionSpace

Required fields:

- `paper_action_count`
- `action_index_to_destination`
- `destination_to_action_index`
- `local_action_index`
- `cloud_action_index`
- `horizontal_action_indices`
- `invalid_action_indices`
- `action_encoding_version`

## DestinationLegalMask

Required fields:

- `source_agent_id`
- `legal_action_mask`
- `legal_action_reasons`
- `illegal_action_reasons`
- `topology_source`
- `mask_encoding_version`

## MigrationReadinessForFeature066

Required fields:

- `legacy_training_behavior_preserved`
- `paper_faithful_contract_available`
- `feature_066_required_to_bind_training`
- `known_non_migrated_components`
- `recommended_next_feature`
