# Data Model

## EdgeAgent

- `agent_id`
- `origin_task_queue`
- `private_queue`
- `offloading_queue`
- `public_queue_view`
- `policy_state`

## Cloud

- `cloud_id`
- `public_queue_manager`
- `available_cpu`

## Task

- `task_id`
- `source_agent_id`
- `arrival_slot`
- `deadline_slot`
- `size_mbits`
- `processing_density_gcycles_per_mbit`
- `selected_action`
- `current_status`

## PrivateQueue

- `queue_id`
- `waiting_workload`
- `current_task`

## OffloadingQueue

- `queue_id`
- `waiting_workload`
- `destination_id`
- `current_task`

## PublicQueue

- `queue_id`
- `source_agent_id`
- `destination_id`
- `remaining_workload`
- `active_flag`

## PublicQueueManager

- `destination_id`
- `public_queues`
- `active_queue_count`
- `allocated_cpu_map`

## Action

- `action_id`
- `source_agent_id`
- `kind`
- `destination_id`
- `validity`

## RewardEvent

- `task_id`
- `source_agent_id`
- `selected_action`
- `collection_slot`
- `outcome`
- `delay_slots`
- `reward_value`

## TaskLifecycleTrace

- `task_id`
- `arrival_slot`
- `action_slot`
- `queue_transition_slots`
- `completion_or_timeout_slot`

## ValidationEpisode

- `episode_id`
- `seed`
- `policy_name`
- `episode_length`
- `artifact_paths`

## FigureDataset

- `figure_id`
- `source_episodes`
- `aggregation_method`
- `output_path`

