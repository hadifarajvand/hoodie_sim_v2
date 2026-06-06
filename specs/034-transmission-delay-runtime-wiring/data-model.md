# Data Model: Transmission Delay Runtime Wiring

## Entities

### Task

Existing runtime object that carries lifecycle state and metadata.

Relevant fields:
- `task_id`
- `source_agent_id`
- `arrival_slot`
- `size`
- `processing_density`
- `timeout_length`
- `absolute_deadline_slot`
- `selected_action`
- `resolved_destination`
- `queue_state`
- `start_slot`
- `completion_slot`
- `terminal_outcome`
- `reward_emitted`
- `drop_flag`
- `metadata`

Transmission-delay additions are stored in `metadata` rather than as new core fields.

Validation rules:
- `size` is interpreted as Mbits.
- `metadata["transmission_payload_bits"]` must be the bit conversion of `size`.
- `metadata["transmission_delay_slots"]` must come from `compute_transmission_delay()`.
- `metadata["transmission_started_at"]` and `metadata["transmission_completed_at"]` must be integers when present.

### OffloadingQueue

Queue for tasks waiting to complete transmission before downstream admission.

Relevant fields:
- `owner_node_id`
- `resolved_destination`
- `tasks`
- `current_head_entered_at`

Validation rules:
- The head-entry slot marks when the queue became non-empty.
- Admission cannot occur before the task-specific transmission boundary is satisfied.
- Queue state remains `offloading_queue` while transmission is in progress.

### Transmission Metadata

Deterministic metadata attached to the task during offload admission.

Fields:
- `transmission_started_at`
- `transmission_completed_at`
- `transmission_delay_slots`
- `transmission_delay_seconds`
- `transmission_payload_bits`
- `transmission_data_rate_bps`
- `transmission_rate_source`

Validation rules:
- `transmission_rate_source` is either `horizontal_R_H` or `vertical_R_V`.
- `transmission_delay_slots` is computed from payload bits, rate, slot duration, and rounding policy.
- `transmission_completed_at` must equal the first slot where the admission boundary is satisfied.

### SlotEngine

Helper-only admission component.

Relevant behavior:
- Accepts an offloading queue, a public queue, and the current slot.
- Admits only when the documented transmission boundary has been reached.
- Does not compute transmission delay itself.

### HoodieGymEnvironment

Orchestrator for transmission wiring.

Relevant behavior:
- Computes and stores transmission metadata when a task enters offloading.
- Chooses the correct link rate for horizontal or vertical offload.
- Emits trace events for transmission start and completion.
- Keeps reward emission and execution-capacity behavior unchanged.

## State Transitions

### Offload Transmission

1. Task is selected for horizontal or vertical offload.
2. Environment records transmission start metadata.
3. Task remains in the offloading queue while current slot is before the boundary.
4. When the boundary is reached, `SlotEngine` admits the task to the downstream execution queue.
5. Transmission completion metadata is recorded.
6. Downstream execution follows the existing Feature 033 execution contract.

### Local Execution

1. Task is selected for local execution.
2. No transmission metadata is recorded.
3. Task proceeds directly into execution capacity accounting.

## Constraints

- No separate cloud-specific data rate.
- No change to CPU execution capacity behavior.
- No reward timing change.
- No topology legality change.
- No public/cloud capacity-sharing redesign.
