# Research: Public/Cloud Queue Capacity Sharing Contract

## Decision 1: Group queues by host before applying execution capacity

- **Decision**: In each simulator slot, group public queues by destination EA host and group cloud queues under the cloud host before applying capacity shares.
- **Rationale**: Capacity duplication happens when each queue is treated independently. Grouping by host is the minimal fix that preserves the existing queue model while preventing over-consumption.
- **Alternatives considered**:
  - Per-queue full capacity: rejected because it multiplies host capacity.
  - Redesigning queue structure: rejected because the scope is a runtime contract, not a scheduler rewrite.

## Decision 2: Use deterministic equal-share at slot start

- **Decision**: Split each host's capacity equally across active queue heads at the start of the slot.
- **Rationale**: Equal-share is simple, deterministic, and directly satisfies the no-duplication requirement without introducing policy logic.
- **Alternatives considered**:
  - Priority-based allocation: rejected because it would create a new scheduling policy.
  - Weighted allocation: rejected because no weighting policy is defined and it would increase ambiguity.

## Decision 3: Do not redistribute leftover share within the same slot

- **Decision**: If a task completes early, its unused share remains unused until the next slot.
- **Rationale**: Same-slot redistribution adds complexity and can introduce non-deterministic behavior if multiple heads complete at different times.
- **Alternatives considered**:
  - Work-conserving redistribution: rejected because it increases complexity and can obscure the contract.
  - Dynamic refill within the slot: rejected because the feature is intended to be stable and testable.

## Decision 4: Preserve existing execution and transmission contracts

- **Decision**: Leave local/private execution unchanged, preserve Feature 033 execution behavior, and preserve Feature 034 transmission delay behavior.
- **Rationale**: The feature addresses only host-level sharing for public/cloud queues and must not alter unrelated timing contracts.
- **Alternatives considered**:
  - Fold in execution timing cleanup: rejected as scope creep.
  - Adjust transmission delays: rejected because this feature is not about offload transit.

## Decision 5: Validate with targeted regression tests only

- **Decision**: Add tests for same-host sharing, different-host independence, deterministic ordering, and regression guards for local/private, transmission delay, and reward timing.
- **Rationale**: The contract is runtime-specific and should be proven by narrow regression coverage rather than broad campaign reruns.
- **Alternatives considered**:
  - Baseline campaign reruns: rejected by scope.
  - Policy or training tests: rejected because no policy/training behavior changes are in scope.
