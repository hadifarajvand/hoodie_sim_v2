# Contract: Environment Boundary

## Purpose

Define the stable adapter contract for the HOODIE simulator boundary.

## Interface

### `reset(seed: int | None = None) -> tuple[observation, info]`

- Initializes deterministic episode state.
- Seeds trace generation or trace loading.
- Clears queues, metrics, and task history.
- Returns the first observation and reset metadata.

### `step(action) -> tuple[observation, reward, terminated, truncated, info]`

- Advances exactly one simulator slot.
- Accepts one action for the current active task only.
- Returns a scalar reward for terminal completions/drops collected in that slot.
- Returns `terminated` when the episode is semantically finished.
- Returns `truncated` when the configured slot horizon ends the episode.

## Observation contract

- Observation is a slot-scoped mapping keyed by edge-agent ID.
- Each value contains task features, legal-action mask, queue/load context, and lifecycle/debug metadata.
- Only one active task is exposed to `step()` at a time.

## Same-slot arrival contract

- If multiple tasks arrive in the same slot, the adapter uses deterministic presentation order.
- Only one task is active at a time.
- Remaining arrivals stay pending for later presentation.

## Illegal action behavior

- Illegal actions are rejected by the shared legality check.
- The adapter does not silently remap illegal actions.

## Empty-slot behavior

- If no active task exists for the current slot, the adapter advances the slot and returns a no-op update.
- Queue progression and delayed reward collection still proceed.

## Baseline integration

- `HoodieGymEnvironment` owns the episode and slot lifecycle orchestration.
- `SlotEngine` provides helper methods only and does not own lifecycle control.
- Baselines call `reset()` and `step()` externally.
- Any helper episode runner must be a thin wrapper, not a separate contract.
