# HOODIE Paper Simulation Contract

This directory is the canonical contract for rebuilding the simulator to match the mechanisms of the HOODIE paper. It is not a summary and it is not a plotting guide. It defines what the simulator must do before any Figure 8/9/10/11 output can be treated as paper-faithful.

Primary sources:

- `resources/papers/hoodie/original/HOODIE_paper.pdf`
- `resources/papers/hoodie/ocr/merged.txt`

## Required Reading Order

1. `01_system_topology_and_runtime.md`
2. `02_task_arrival_and_action_model.md`
3. `03_private_offloading_public_queue_equations.md`
4. `04_state_reward_and_delayed_collection.md`
5. `05_training_inference_and_validation.md`
6. `06_baselines.md`
7. `07_figure_8_9_10_11_contract.md`
8. `08_table_4_parameters.md`
9. `09_paper_faithful_acceptance_checklist.md`

## Non-Negotiable Rule

Do not tune simulator outputs to match the paper curves. Implement the same mechanisms and let the simulator outputs emerge from the implemented process.

Correct implementation target:

```text
paper system model -> slot runtime -> queues -> delayed reward -> trained/inference policies -> validation episodes -> metrics -> figures
```

Wrong implementation target:

```text
current aggregates -> paper-shaped CSV -> paper-shaped plot
```

## Contract Format

Each mechanism must be read as:

- Paper says
- Formula / parameter
- Meaning
- Implementation requirement
- Validation evidence
- Failure symptom if missing

Codex, future reviewers, and implementation tasks must cite these files when changing simulator behavior.

## Current Project Implication

The current project has produced paper-style output artifacts, but Feature 089 concluded that the simulator is not yet paper-faithful. Feature 090 must rebuild the mechanism layer first: runtime, queues, delayed rewards, policy/baseline execution, training boundary, validation episodes, and metrics denominators.
