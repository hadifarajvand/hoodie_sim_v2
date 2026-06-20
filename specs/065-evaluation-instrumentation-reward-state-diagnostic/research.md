# Research: Feature 065 - Evaluation Instrumentation and Reward/State Diagnostic Repair

## Decision 1: Reuse the real staged campaign but add instrumentation outside the trainer

- **Decision**: Use the existing trainer, environment, and policy code, and add diagnostic wrappers in the new feature package.
- **Rationale**: The user explicitly forbids semantic changes and the blind spots can be diagnosed by logging more evidence.

## Decision 2: Keep replay-window and cumulative history separate

- **Decision**: Record replay-buffer counts as a rolling window and separately track all training actions from the staged run.
- **Rationale**: The earlier report conflated the buffer window with the full campaign history.

## Decision 3: Compare candidate and fixed policies on the same trace bank

- **Decision**: Evaluate candidate checkpoints and fixed baseline policies against the same staged evaluation traces.
- **Rationale**: This isolates policy effect from trace-bank drift.

## Decision 4: Matplotlib-only figures

- **Decision**: Use matplotlib only for the summary figures.
- **Rationale**: The prompt requires it and the diagnostic does not need seaborn.
