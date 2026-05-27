# Data Model: Feature 065

## PaperStateActionSpaceBatchReport

Fields:

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

## PaperStateVector

Represents the full structured observation at a decision point.

Required components:

- `source_agent_id`
- `task_features`
- `private_waiting_time_slots`
- `offloading_waiting_time_slots`
- `private_queue_depth`
- `offloading_queue_depth`
- `public_queue_lengths_by_destination`
- `load_history_matrix`
- `legal_destination_mask`
- `flattened_state_vector`
- `state_dim`

## PaperLoadHistoryMatrix

Represents node active queue counts over a fixed lookback window.

Required components:

- `lookback_w`
- `edge_agent_count`
- `node_order`
- `matrix_shape`
- `rows`
- `padding_policy`
- `source`

## PaperLstmForecastInput

Represents the LSTM-facing tensor derived from `PaperLoadHistoryMatrix`.

Required components:

- `forecast_input_shape`
- `forecast_node_order`
- `forecast_source`
- `tensor_rows`
- `deterministic_conversion`

## PaperActionSpace

Represents destination-specific action registry per source Edge Agent.

Required components per action:

- `action_index`
- `action_family`
- `source_node_id`
- `destination_node_id`
- `destination_kind`
- `is_legal`
- `legality_source`

## LegalDestinationMask

Represents a one-to-one mask aligned to `PaperActionSpace` action indices.

Required behavior:

- local/self is legal
- topology-backed horizontal Edge-Agent destinations are legal
- Cloud vertical destination is legal
- non-neighbor Edge-Agent destinations are illegal
- mask index order equals action registry order

## SafetySummary

Must prove no training rerun, no prior artifact rewrite, no reward timing change, no dependency drift, no paper reproduction claim, and no unsupported superiority claim.
