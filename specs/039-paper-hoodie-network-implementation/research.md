# Research: Paper HOODIE Network Implementation

## Decision 1: Dependency status

- **Decision**: Treat torch as dependency-blocked in the approved interpreter because `ModuleNotFoundError` is returned when importing it from `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`.
- **Rationale**: The feature cannot create a compliant architecture implementation without the dependency already being available. Adding or modifying dependency files would violate the feature scope.
- **Alternatives considered**: Add torch to dependency files. Rejected because the feature explicitly forbids dependency changes.

## Decision 2: Input/output shape contract

- **Decision**: Use `batch_size x lookback_w x state_dim` as the input convention and `batch_size x action_count` as the output convention.
- **Rationale**: This preserves the Feature 038 state contract while making the architecture validation explicit and testable.
- **Alternatives considered**: Flatten history into a single vector before the LSTM. Rejected because it obscures the sequence contract.

## Decision 3: Action space

- **Decision**: Keep `action_count = 3` with stable indices `0 local`, `1 horizontal`, and `2 vertical_cloud`.
- **Rationale**: Feature 038 already established the stable action contract and the architecture must not expand it.
- **Alternatives considered**: Per-destination horizontal outputs. Rejected because it violates the generic horizontal-action contract.

## Decision 4: LSTM placement

- **Decision**: Encode the Feature 038 `W=10` history with an LSTM before the shared Q-network body.
- **Rationale**: The sequence encoder should summarize temporal context before the Q-network body builds action scores.
- **Alternatives considered**: Put the LSTM after the Q-network body. Rejected because it inverts the intended contract.

## Decision 5: Dueling architecture

- **Decision**: Use a shared body followed by separate value and advantage heads.
- **Rationale**: This is the standard dueling pattern and cleanly separates state value from action-specific advantage.
- **Alternatives considered**: Single-head Q output only. Rejected because it does not satisfy the requested dueling surface.

## Decision 6: Double-DQN scope

- **Decision**: Limit this feature to online/target network construction and forward APIs.
- **Rationale**: Training logic, loss computation, and target-network updates belong to later implementation features.
- **Alternatives considered**: Add Double-DQN loss and update logic now. Rejected because this feature must not train the model.

## Decision 7: Deterministic initialization

- **Decision**: Use the Feature 038 model-initialization seed for deterministic architecture initialization tests.
- **Rationale**: Deterministic initialization is required to validate architecture stability without touching training behavior.
- **Alternatives considered**: Seed training, replay, and exploration here. Rejected because those domains are outside this feature.

## Decision 8: Report semantics

- **Decision**: Generate architecture report artifacts that explicitly record the dependency status and the no-training constraints.
- **Rationale**: The report must make the dependency blocker and the architecture-only scope obvious to reviewers.
- **Alternatives considered**: Emit only test output. Rejected because the feature requires report artifacts.
