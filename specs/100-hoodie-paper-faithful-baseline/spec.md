# HOODIE Paper-Faithful Baseline

## Purpose

Define the simulator target for a paper-faithful HOODIE rebuild without claiming the current repository already satisfies it.

## Current Promoted Baseline Behavior

The promoted baseline currently provides:

- per-server task generation
- private/offloading/public queue machinery
- adjacency-based action legality
- per-server DQN agents with replay memory and LSTM input handling
- step-aggregated reward flow
- JSON-driven configuration
- a smoke-runnable entrypoint

The Phase 0.3 audit established that:

- `main.py`, `environment/environment.py`, `utils/__init__.py`, and `hyperparameters/hyperparameters.json` match the promoted baseline snapshot at the file-content level
- public queue CPU sharing is priority-weighted
- reward is step-aggregated, not delayed and task-traceable
- LSTM is embedded in DQN input handling, not an auditable forecasting/history pipeline
- no Figure 8/9/10/11 generation workflows exist
- no 200-episode validation mode exists

## Paper-Faithful Target Behavior

The target simulator must provide:

- explicit time-slotted runtime phases
- explicit arrivals, actions, queue insertion, transmission, processing, completion, timeout, and reward attribution
- source-specific public queues with auditable CPU-sharing semantics
- task-level delayed reward events
- auditable state and historical load traces
- a reproducible training / validation / figure-generation pipeline

## Non-Goals

- Do not reproduce numerical paper curves in this spec package.
- Do not implement simulator runtime changes in the spec phase.
- Do not fabricate training or validation outputs.
- Do not claim the simulator is already paper-faithful.

## Forbidden Claims

- The current simulator is paper-faithful.
- The current branch reproduces Figures 8, 9, 10, or 11.
- The current branch has a validated 200-episode evaluation mode.
- The current branch already uses delayed task-level reward attribution.

## Acceptance Criteria

This spec is acceptable only if it:

- separates current baseline behavior from target behavior
- records the Phase 0.3 gaps explicitly
- defines a paper-faithful contract without modifying runtime code
- provides verifiable, implementation-neutral work items for later phases

