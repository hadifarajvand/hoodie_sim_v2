# Research: Task Execution Time & Compute Resource Modeling

## Decision 1: Add an explicit compute configuration module

- **Decision**: Introduce `src/environment/compute_config.py` with configurable per-slot compute capacities for local, edge, and cloud execution contexts.
- **Rationale**: Compute capacity is scenario data, not lifecycle logic. A dedicated config module keeps the execution model testable and avoids hardcoding capacity assumptions inside the environment boundary.
- **Alternatives considered**:
  - Hardcoding capacity values in the execution helper. Rejected because it makes scenario validation brittle.
  - Encoding compute capacity only in docs. Rejected because the feature needs executable, testable capacities.

## Decision 2: Compute required cycles directly from size and processing density

- **Decision**: Derive task compute budget as `cycles_required = size × processing_density` and initialize remaining cycles to the same value.
- **Rationale**: This is the paper-backed relationship described in the feature request and preserves the recovered fractional traffic values from feature 005.
- **Alternatives considered**:
  - Converting sizes into integers first. Rejected because it discards fractional paper values.
  - Inventing a different compute formula. Rejected because it would not be paper-backed.

## Decision 3: Add a narrow execution helper rather than a second lifecycle controller

- **Decision**: Implement compute decrement logic in `src/environment/execution_helper.py` as `step_execution(...)`, which mutates task execution state under `HoodieGymEnvironment` control.
- **Rationale**: The environment lifecycle is already stable. Compute progression should sit beneath it, not replace it.
- **Alternatives considered**:
  - Moving slot progression into the compute helper. Rejected because it would duplicate lifecycle control.
  - Reworking `SlotEngine` into a controller. Rejected because feature 004 already fixed `SlotEngine` as helper-only.

## Decision 4: Keep destination-specific execution rates deterministic

- **Decision**: Use fixed per-slot compute capacities for local, edge, and cloud destinations and apply them deterministically on each active execution slot.
- **Rationale**: The paper-backed model is compute-deterministic. A fixed capacity profile gives reproducible execution timing and supports regression testing.
- **Alternatives considered**:
  - Introducing stochastic CPU allocation. Rejected because the feature explicitly forbids unsupported stochastic compute models.
  - Sharing compute dynamically among tasks. Rejected because that is outside the documented scope.

## Decision 5: Preserve delayed reward semantics

- **Decision**: Reward continues to be emitted only when a task reaches a terminal state, but the terminal state now depends on compute exhaustion rather than an abstract queue placeholder.
- **Rationale**: Feature 004 already established delayed reward timing. This feature makes the terminal event paper-faithful without changing reward semantics.
- **Alternatives considered**:
  - Emitting reward each slot while compute decreases. Rejected because it breaks delayed reward integrity.

## Decision 6: Track compute progression in the shared task state

- **Decision**: Extend task state with `cycles_required` and `cycles_remaining` so execution progression is visible in tests and debug traces.
- **Rationale**: The environment needs observable progress to validate completion timing and offload continuation.
- **Alternatives considered**:
  - Keeping compute state hidden inside the helper only. Rejected because it would make testing and trace reconstruction harder.

## Resulting implementation shape

- `Task` owns compute-budget state.
- `ComputeConfig` owns deterministic capacity settings.
- `execution_helper.step_execution(...)` owns cycle decrement logic under environment control.
- `HoodieGymEnvironment` remains the lifecycle owner.
- `SlotEngine` remains helper-only.
- No new dependency, no lifecycle ownership change, and no training-layer work are required.

## Unresolved gap

- The OCR-backed paper text recovers the compute relationship, but not exact slot-capacity values. The repository therefore uses explicit configuration capacities for local, edge, and cloud execution, and the capacity fixture is documented instead of being presented as a recovered paper constant.
