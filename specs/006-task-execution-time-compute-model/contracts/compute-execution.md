# Contract: Task Execution Time & Compute Resource Modeling

## Purpose

Define the compute-execution boundary that extends task progression without changing the existing environment lifecycle contract.

## Interface

### `ComputeConfig`

- Holds deterministic capacity values for local, edge, and cloud execution contexts.
- Must validate positive per-slot capacities.

### `execution_helper.step_execution(task, compute_capacity, slot, destination_kind) -> ExecutionProgressRecord`

- Decrements a task’s remaining compute budget by the configured destination capacity.
- Returns the updated progress state for the current slot.
- Marks the task as execution-complete when remaining compute budget reaches zero or below, leaving final terminal resolution to the environment boundary.

### Task compute state

- Task records must expose required and remaining compute budgets.
- Task records must preserve existing lifecycle fields and reward timing fields.

## Environment compatibility contract

- `HoodieGymEnvironment` remains the lifecycle owner.
- `SlotEngine` remains helper-only.
- Compute progression is an execution concern, not a second controller.
- Reward emission still occurs only when tasks complete or are dropped.

## Non-goals

- No stochastic compute allocation.
- No GPU or heterogeneous-core modeling.
- No training or policy changes.
- No new lifecycle controller.
