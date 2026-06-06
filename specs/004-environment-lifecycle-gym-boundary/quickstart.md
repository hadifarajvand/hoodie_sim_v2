# Quickstart: 004-environment-lifecycle-gym-boundary

## Goal

Use the existing local Gymnasium-style adapter to run one deterministic HOODIE episode without adding a Gymnasium dependency or any new simulator package.

## Intended usage

- Instantiate `src.environment.gym_adapter.HoodieGymEnvironment`
- Call `reset(seed=...)`
- Repeatedly call `step(action)` with the current baseline action
- Read reward, termination flags, and trace/debug information from the returned tuple
- Use `observe_flat()` only when migrating an existing caller that still expects the older flat compatibility shape

## Baseline integration

- Keep policy execution outside the adapter.
- Feed observations and legal-action masks to the baseline policy.
- Pass the chosen action back into `step()`.
- No official command or new entry point is required for this feature.

## Determinism check

Run the same seed twice with the same baseline policy and confirm:

- identical trace identifier
- identical observation sequence
- identical finalized task records
- identical reward sequence

## Test focus

Run the unit and integration tests that cover:

- reset determinism
- one-slot step behavior
- queue admission
- offload progression
- delayed reward timing
- metric consistency

## Dependency note

This feature does not require installing, upgrading, or removing dependencies. It does not require Gymnasium, ns-3, or ns-3-gym.
