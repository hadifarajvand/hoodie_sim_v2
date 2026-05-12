# Execution-Time Contract

## Scope

This contract defines how a task advances through execution slots for local/private, public/edge, and cloud destinations.

## Rules

1. Each simulator slot may consume at most the configured per-slot capacity for the selected destination kind.
2. Tasks requiring more cycles than the configured capacity must span multiple slots.
3. Completion is recorded at the end of the slot in which the final cycles are consumed.
4. Timeout/drop evaluation occurs after execution progress and before reward emission.
5. Reward is emitted only when the task reaches a terminal state.

## Destination Capacity Mapping

- local/private/self -> agent capacity
- public/edge/horizontal -> edge capacity
- cloud/vertical -> cloud capacity

