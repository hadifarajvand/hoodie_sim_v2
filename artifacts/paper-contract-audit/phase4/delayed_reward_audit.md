# Delayed Reward Audit

## What was fixed
- Pending transitions are now recorded explicitly at decision time.
- Final task outcomes now produce delayed reward events instead of only being inferred post-hoc from `task_lifecycle.csv`.
- Replay insertion for DRL agents uses the original state/action context from the pending transition.

## Where pending transitions are registered
- `main.py` calls `TraceRecorder.note_pending_transition()` after action selection and after the environment step provides the immediate successor state.

## Where reward events are resolved
- `TraceRecorder.resolve_delayed_reward_candidates()` identifies final task outcomes and pairs them with pending transitions when available.
- `delayed_reward_runtime.process_delayed_reward_events()` writes the delayed reward trace row and inserts replay only for agents that support it.

## Replay insertion
- Active for DRL agents.
- Inactive for baseline policies.

## Reward timing convention
- `completion_minus_arrival`
- Completed tasks use `reward = -(completion_time - arrival_time)`.
- Dropped or timed-out tasks use `reward = -drop_penalty`.

## Why this phase matters
- The previous reward path was post-hoc reconstruction from lifecycle rows.
- That is not sufficient for paper-grade delayed reward replay pairing.
- This phase makes the reward pipeline traceable and auditable.

## Unresolved limitations
- Figure 8 / 9 / 10 / 11 generation is still out of scope.
- This phase does not guarantee paper-grade performance.
- The broader training pipeline still depends on the rest of the runtime contract.
