# Research: Training Foundation Contract

## Decision 1: State vector scope

- **Decision**: Use only paper/runtime-supported observable variables in the training state.
- **Rationale**: Diagnostics belong in reports, traces, and audit artifacts. Putting debug fields into the policy input pollutes the contract and makes later results harder to defend.
- **Alternatives considered**: Include runtime diagnostics in the model input. Rejected because it leaks control-plane information into the learning contract.

## Decision 2: Action indexing contract

- **Decision**: Preserve one generic helper-resolved horizontal action, plus local/private and vertical/cloud actions.
- **Rationale**: This matches current runtime semantics and avoids inflating the action space with topology-specific destination actions that the environment does not currently expose.
- **Alternatives considered**: One action per destination node. Rejected because it bakes Figure 7 topology into the policy contract and creates a larger, less stable action space.

## Decision 3: Replay transition handling

- **Decision**: Store non-terminal transitions separately with `reward_available=false`. Reward becomes available only on completion or drop.
- **Rationale**: Delayed reward is a core simulator property. Flattening it into decision-time reward would be trash contract design.
- **Alternatives considered**: Emit reward immediately at decision time. Rejected because it violates the runtime reward contract.

## Decision 4: Pending-at-horizon treatment

- **Decision**: Define schema and readiness gate only. Do not add drain-phase behavior.
- **Rationale**: Drain phases can change the paper-default episode contract and would blur the distinction between runtime behavior and training readiness.
- **Alternatives considered**: Carry pending tasks into a drain phase. Rejected because it changes episode semantics.

## Decision 5: Target update frequency meaning

- **Decision**: Treat one environment step as one iteration for the contract draft.
- **Rationale**: The simulator is slot-based, so environment steps are the least arbitrary and most auditable unit for a contract-only training foundation.
- **Alternatives considered**:
  - Optimization step
  - Replay insertion
  - Gradient update
  These were rejected as implementation-specific and not yet approved.

## Decision 6: Seed protocol

- **Decision**: Separate seed domains for training trace generation, evaluation trace generation, replay sampling, neural-network initialization, and action exploration.
- **Rationale**: The training foundation must be reproducible and auditable across all stochastic surfaces.
- **Alternatives considered**: Single global seed. Rejected because it makes audits and replay analysis less defensible.

## Decision 7: Train/eval split protocol

- **Decision**: Use fixed trace banks derived from separate seed sets and record explicit trace IDs.
- **Rationale**: This prevents evaluation leakage and keeps baseline/future training comparisons fair.
- **Alternatives considered**: Generate evaluation traces on the fly from training seeds. Rejected because it risks unfair trace overlap.

## Decision 8: Checkpoint schema

- **Decision**: Metadata-only checkpoint schema.
- **Rationale**: This feature is contract-only; actual model checkpoints belong to a later implementation feature.
- **Alternatives considered**: Create empty checkpoint files now. Rejected because they would imply training implementation without actual model semantics.

## Decision 9: Terminal-outcome exposure gate

- **Decision**: Block training unless terminal/reward-bearing exposure is explicitly sufficient and approved.
- **Rationale**: Feature 037 showed sparse terminal outcomes under `paper_default`; that is a readiness blocker, not a result to hide.
- **Alternatives considered**: Automatically declare training-ready based on raw arrival counts. Rejected because arrivals are not terminal samples.

## Decision 10: Threshold policy

- **Decision**: Do not invent a paper threshold. Treat any numeric threshold as an engineering readiness threshold pending explicit approval.
- **Rationale**: The paper does not provide a validated terminal-exposure threshold for training readiness.
- **Alternatives considered**: Hardcode a percentage threshold. Rejected because it would be an invented paper fact.

