# Quickstart: 004-environment-lifecycle-gym-boundary

## Goal

Use the existing Gymnasium-style adapter to run one deterministic HOODIE episode without adding a Gymnasium dependency.

## Intended usage

- Instantiate `src.environment.gym_adapter.HoodieGymEnvironment`
- Call `reset(seed=...)`
- Repeatedly call `step(action)` with the current baseline action
- Read reward, termination flags, and trace/debug information from the returned tuple

## Baseline integration

- Keep policy execution outside the adapter.
- Feed observations and legal-action masks to the baseline policy.
- Pass the chosen action back into `step()`.

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

