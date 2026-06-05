# Data Model: Feature 090 HOODIE Paper-Faithful Simulation Rebuild

This data model exists to force the implementation to model the paper runtime, not only figure artifacts.

## EpisodeConfig

Fields:

- `episode_id`
- `num_edge_agents`
- `cloud_node_id`
- `topology_mode`
- `adjacency_matrix`
- `slot_count`
- `action_slot_count`
- `drain_slot_count`
- `slot_duration_sec`
- `task_arrival_probability`
- `task_size_range_mbits`
- `task_size_values_mbits`
- `processing_density_gcycles_per_mbit`
- `timeout_slots`
- `timeout_sec`
- `private_cpu_ghz`
- `public_cpu_ghz`
- `cloud_cpu_ghz`
- `horizontal_rate_mbps`
- `vertical_rate_mbps`
- `random_seed`
- `paper_faithful_mode`
- `test_mode_reason`

## TaskRecord

Fields:

- `task_id`
- `source_ea_id`
- `arrival_slot`
- `size_mbits`
- `processing_density_gcycles_per_mbit`
- `timeout_slots`
- `deadline_slot`
- `policy`
- `decision_level_1`
- `destination_node_id`
- `path_type`: `local`, `horizontal`, `vertical`
- `status`: `pending`, `transmitting`, `in_public_queue`, `completed`, `dropped_timeout`, `unresolved`
- `private_queue_enter_slot`
- `offloading_queue_enter_slot`
- `public_queue_enter_slot`
- `queue_exit_slot`
- `final_completion_slot`
- `drop_slot`
- `reward_collection_slot`
- `reward`
- `delay_slots`
- `delay_sec`

## QueueState

Fields:

- `episode_id`
- `slot`
- `node_id`
- `queue_type`: `private`, `offloading`, `public`
- `source_ea_id`
- `queue_length_workload`
- `queue_length_unit`: `mbits` or `gcycles`
- `active`
- `allocated_cpu_ghz`
- `arrived_task_ids`
- `completed_task_ids`
- `dropped_task_ids`
- `remaining_task_ids`

## PublicQueueActiveSet

Fields:

- `episode_id`
- `slot`
- `node_id`
- `active_public_queue_source_ids`
- `active_public_queue_count`
- `total_public_cpu_ghz`
- `cpu_share_per_active_queue_ghz`

## StateSnapshot

Fields:

- `episode_id`
- `slot`
- `ea_id`
- `task_id`
- `task_size_mbits`
- `private_wait_slots`
- `offloading_wait_slots`
- `public_queue_footprint`
- `load_history_matrix_shape`
- `load_history_matrix_values`
- `forecast_mode`
- `forecast_values`

## PolicyDecision

Fields:

- `episode_id`
- `slot`
- `ea_id`
- `task_id`
- `policy`
- `state_snapshot_id`
- `decision_level_1`
- `destination_node_id`
- `path_type`
- `legal_action`
- `illegal_reason`
- `candidate_latency_table_id`
- `selected_estimated_latency_slots`

## MleoCandidateLatency

Fields:

- `episode_id`
- `slot`
- `task_id`
- `source_ea_id`
- `candidate_destination`
- `candidate_path_type`
- `private_wait_slots`
- `local_service_slots`
- `offloading_wait_slots`
- `transmission_slots`
- `public_wait_estimate_slots`
- `public_service_estimate_slots`
- `total_estimated_latency_slots`
- `selected`

## RewardEvent

Fields:

- `episode_id`
- `reward_collection_slot`
- `task_id`
- `source_ea_id`
- `policy`
- `original_action_slot`
- `completed_or_dropped`
- `delay_slots`
- `reward`
- `drop_penalty_applied`

## MetricAggregate

Fields:

- `figure_id`
- `sweep_name`
- `sweep_value`
- `policy`
- `episode_count`
- `arrived_tasks`
- `completed_tasks`
- `dropped_tasks`
- `unresolved_tasks`
- `average_delay_sec`
- `paper_style_negative_delay_sec`
- `drop_ratio`
- `drop_ratio_percent`
- `average_reward`
- `total_reward`
- `throughput`

## DegeneracyDiagnostic

Fields:

- `figure_id`
- `sweep_name`
- `sweep_value`
- `policy`
- `zero_completion_detected`
- `single_task_trace_detected`
- `drop_saturation_detected`
- `all_policy_tie_detected`
- `missing_sweep_injection_detected`
- `severity`
- `message`
