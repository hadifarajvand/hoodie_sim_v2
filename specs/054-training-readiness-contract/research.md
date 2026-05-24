# Research: Training Readiness Contract

## Decision 1: Use committed prior artifacts only

- **Decision**: Feature 054 will consume only the committed JSON report artifacts from Features 048, 049, 050, 051, 052, and 053.
- **Rationale**: The contract is supposed to certify readiness from the existing diagnostic chain, not rebuild that chain or peek at live dirty-worktree state.
- **Alternatives considered**:
  - Reading current worktree state directly. Rejected because it couples readiness to transient local changes.
  - Regenerating prior artifacts. Rejected because it violates the immutability requirement and creates false confidence.

## Decision 2: Gate the contract on Feature 053 readiness

- **Decision**: Feature 053 readiness is a hard prerequisite for evaluating the training-readiness contract.
- **Rationale**: The training contract only makes sense after the paper-mechanism rerun has already proven the evidence chain is ready for a training gate.
- **Alternatives considered**:
  - Skipping the Feature 053 gate and evaluating contract locks directly. Rejected because it would allow training gating on an unverified evidence chain.

## Decision 3: Split the contract into explicit lock fields

- **Decision**: The report will expose independent lock fields for the paper-default config, observation, action, legality, reward, timeout, capacity, transmission, queue, metric, seed, and artifact contracts.
- **Rationale**: A single aggregate boolean would hide the first failing contract family and weaken the audit trail.
- **Alternatives considered**:
  - Using one readiness flag only. Rejected because it obscures the blocker and is harder to test.
  - Collapsing the runtime contract family into one generic field. Rejected because it makes the routing path ambiguous.

## Decision 4: Keep the contract passive and evidence-only

- **Decision**: Feature 054 will not start training, optimizer work, replay, target updates, checkpoints, or campaigns.
- **Rationale**: The feature is a gate, not an execution step.
- **Alternatives considered**:
  - Automatically launching the smoke run when the contract passes. Rejected because it would blur readiness evaluation with execution.

## Decision 5: Preserve behavior-equivalence as a separate audit

- **Decision**: The report will include behavior-equivalence results with unique check names.
- **Rationale**: The readiness gate must show that the contract evaluation itself did not introduce drift.
- **Alternatives considered**:
  - Omitting behavior equivalence because this is only a readiness contract. Rejected because it would weaken confidence in the go/no-go decision.

## Decision 6: Route to Feature 055 only on full pass

- **Decision**: The report will recommend Feature 055 only when the evidence chain is ready, every contract lock is true, and no drift or rewrite condition is present.
- **Rationale**: The next smoke run should only begin when the report can defend that transition explicitly.
- **Alternatives considered**:
  - Routing to Feature 055 whenever Feature 053 passed. Rejected because training readiness is a separate contract.
