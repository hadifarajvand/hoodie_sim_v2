# Plan

## Phase 0.4: Specification Restoration

- Restore the paper-faithful architecture contract after repository flattening and branch promotion.
- Capture the current baseline gaps as normative spec text.
- Freeze the target behavior before any runtime implementation.

## Phase 1: Runtime Instrumentation Only

- Add traceability and audit hooks.
- Do not change queue math, reward math, or topology legality.
- Emit task, queue, and reward traces for inspection.

## Phase 2: Queue / Reward / Topology Correction

- Correct queue semantics to the paper contract.
- Replace step-aggregated reward with task-level delayed reward events.
- Make topology legality explicit and auditable.

## Phase 3: Training Pipeline

- Align the DQN / DDQN / Dueling DQN training contract with the paper target.
- Formalize replay memory, checkpointing, and training traces.

## Phase 4: 200-Episode Validation

- Add a first-class 200-validation-episode execution path.
- Record validation outputs as auditable artifacts.

## Phase 5: Figure 8 / 9 / 10 / 11 Generation

- Build figure-data workflows from validated simulation and training outputs.
- Export all figure datasets and artifacts required for paper review.

