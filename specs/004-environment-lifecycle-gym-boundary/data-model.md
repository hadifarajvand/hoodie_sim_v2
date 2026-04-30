# Data Model: 004-environment-lifecycle-gym-boundary

## Entities

### EnvironmentBoundarySession

- **Fields**: `seed`, `trace_id`, `policy_name`, `current_slot`, `terminated`, `truncated`, `trace_metadata`
- **Relationships**: Owns one episode trace, one active task at a time, and the current queue state snapshot
- **Validation rules**: Seed must be recorded; `terminated` and `truncated` are mutually exclusive in the normal path

### Task

- **Fields**: `task_id`, `source_agent_id`, `arrival_slot`, `size`, `processing_density`, `timeout_length`, `absolute_deadline_slot`, `selected_action`, `resolved_destination`, `queue_state`, `start_slot`, `completion_slot`, `terminal_outcome`, `reward_emitted`, `drop_flag`, `metadata`
- **Relationships**: Moves through private queue, offloading queue, public queue, execution state, and terminal state
- **Validation rules**: Terminal outcome must be `completed` or `dropped` before reward emission; reward is emitted only once

### TraceTaskBlueprint

- **Fields**: `task_id`, `source_agent_id`, `arrival_slot`, `size`, `processing_density`, `timeout_length`, `absolute_deadline_slot`
- **Relationships**: Builds one `Task` instance during reset or trace loading
- **Validation rules**: Blueprints must be deterministic for a given seed/trace source

### QueueState

- **Fields**: private queue heads, offloading queue heads, public queue heads, waiting time, queue entry slot
- **Relationships**: Tasks can reside in at most one queue state at a time
- **Validation rules**: Queue head changes must preserve FIFO ordering

### ObservationSnapshot

- **Fields**: slot, queue load, active task ID, source agent ID, task features, legal-action mask, topology hint, load hints, history length
- **Relationships**: Derived from the current session state and current active task
- **Validation rules**: Observation must be stable across identical seeds and policy choices

### TraceMetrics

- **Fields**: average delay, drop ratio, throughput, completed tasks, dropped tasks, total tasks, raw task records, metadata
- **Relationships**: Built by the shared evaluation path from finalized task records
- **Validation rules**: Metric formulas must remain unchanged

## State transitions

1. Blueprint becomes active task.
2. Active task becomes admitted to private or offloading queue.
3. Queue task progresses through runtime or offloading phases.
4. Task resolves to completed or dropped terminal state.
5. Terminal task emits reward exactly once.
6. Finalized task is recorded in evaluation metrics.

## Same-slot multi-arrival rule

When multiple tasks arrive in the same slot, the session owns a deterministic presentation order and only one task is active at a time. Remaining same-slot arrivals stay pending until the active task is resolved or the next deterministic presentation turn.

