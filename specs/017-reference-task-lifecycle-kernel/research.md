# Research: Reference Task Lifecycle Kernel

## Decision 1: Use a new isolated Python package under `src/reference_model/`

- **Decision**: Implement the reference kernel in a standalone package under `src/reference_model/`.
- **Rationale**: The feature must be isolated from the simulator, policies, training, metrics, campaigns, and environment lifecycle code. A separate package is the clearest way to keep the boundary enforceable.
- **Alternatives considered**:
  - Extending `src/environment/` was rejected because it would blur the line between reference behavior and simulator behavior.
  - Putting the code under `src/analysis/` was rejected because this feature is executable reference logic, not analysis.

## Decision 2: Use standard-library-only dataclasses and enums

- **Decision**: Model tasks, actions, ledger entries, and terminal state with immutable dataclasses and enums from the Python standard library.
- **Rationale**: The plan explicitly prohibits dependency drift and does not need any third-party abstraction. Immutable data makes deterministic traces easier to test.
- **Alternatives considered**:
  - External libraries for validation or state machines were rejected because they add unnecessary dependency risk.
  - Mutable ad hoc dictionaries were rejected because they make ledger ordering and state transitions harder to reason about.

## Decision 3: Make transition logic explicit and path-based

- **Decision**: Implement a small deterministic transition API that accepts a hand-fed action and emits a path-specific ledger for local compute, horizontal offload, vertical offload, or timeout/drop.
- **Rationale**: The feature is a reference kernel, not a policy engine. Explicit transitions keep the behavior transparent and testable.
- **Alternatives considered**:
  - Reusing simulator control flow was rejected because it would couple the reference model to behavior we are not allowed to repair.
  - Inferring action selection from state was rejected because the feature must not contain policy logic.

## Decision 4: Treat delayed reward as a terminal-only event

- **Decision**: Reward emission occurs only when the task reaches a terminal completion or drop state.
- **Rationale**: This matches the clarified spec and the constitution reward integrity rule. It preserves deterministic reference behavior and avoids decision-time reward leakage.
- **Alternatives considered**:
  - Emitting reward at action selection was rejected because it violates delayed reward semantics.
  - Emitting reward in both decision and terminal slots was rejected because it creates double counting.

## Decision 5: Encode same-slot ties with a documented stable sort key

- **Decision**: Use a deterministic, documented ordering rule for same-slot or tie conditions in the ledger.
- **Rationale**: The spec requires repeated runs with identical inputs to produce identical ledger order, even when events land in the same slot.
- **Alternatives considered**:
  - Leaving tie order to incidental execution order was rejected because it makes the reference model non-reproducible.
  - Adding randomization was rejected because it contradicts the feature goal.

## Decision 6: Keep the feature internal; no external contracts

- **Decision**: Do not create `/contracts/` artifacts for external APIs.
- **Rationale**: This is an internal reference model used for audits and tests, not a public service or API surface.
- **Alternatives considered**:
  - Public HTTP or CLI contracts were rejected because they would add fake surface area and distract from the isolated kernel.

