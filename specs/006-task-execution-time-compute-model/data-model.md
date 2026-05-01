# Data Model: Task Execution Time & Compute Resource Modeling

## Entities

### ComputeConfig

- **Fields**: `cpu_capacity_per_slot_agent`, `cpu_capacity_per_slot_edge`, `cpu_capacity_per_slot_cloud`
- **Relationships**: Parameterizes execution progress for local, edge, and cloud destinations.
- **Validation rules**: Capacities must be positive and deterministic for a fixed configuration.

### TaskExecutionState

- **Fields**: `cycles_required`, `cycles_remaining`, `execution_destination`, `execution_started_at`, `execution_completed_at`
- **Relationships**: Extends the shared task state with compute-budget tracking.
- **Validation rules**: `cycles_required` must be derived from task size and processing density; `cycles_remaining` must never exceed `cycles_required` after initialization.

### ExecutionProgressRecord

- **Fields**: `task_id`, `slot`, `destination_kind`, `cycles_before`, `cycles_consumed`, `cycles_after`, `completed`
- **Relationships**: Represents one slot of compute progression for a task.
- **Validation rules**: `cycles_after = max(0, cycles_before - cycles_consumed)`.

### TerminalOutcome

- **Fields**: `task_id`, `terminal_state`, `completion_slot`, `drop_flag`, `reward_emitted`
- **Relationships**: Captures the final result of execution and reward timing.
- **Validation rules**: Reward emission occurs only after terminal state resolution.

### Shared Task Model

- **Fields**: existing task lifecycle fields plus compute-budget fields and destination metadata
- **Relationships**: Used by traffic, execution, runtime, and evaluation layers.
- **Validation rules**: Existing lifecycle fields remain backward compatible for existing consumers.

## State transitions

1. Task is created with size and processing density.
2. Required cycles are computed.
3. Task enters execution at a destination.
4. Each active slot decrements remaining cycles by the destination capacity.
5. When remaining cycles reach zero or below, the task becomes terminal.
6. Reward emission follows terminal resolution and delayed-reward semantics.

## Compatibility rules

- The compute model does not replace the existing environment lifecycle.
- The compute model does not introduce stochastic allocation.
- Offloaded tasks continue execution at the destination that admitted them.
- The compute helper records terminal readiness, but `HoodieGymEnvironment` still performs the actual terminal resolution and delayed reward emission.
