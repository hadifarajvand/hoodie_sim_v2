# Implementation Plan: Feature 069

**Feature**: Full HOODIE Mechanism Fidelity Batch  
**Status**: Spec Kit handoff; implementation blocked until this Spec Kit is merged  
**Depends On**: Feature 068R merged into `main`

## Summary

Feature 069 defines the mechanism-level fidelity layer around HOODIE. It must validate how topology evidence, synchronization, action application, queue pressure, delayed reward, timeout/drop accounting, and mechanism reporting work together.

## Implementation Boundary

Allowed future implementation areas must be explicitly justified by this plan. Expected future paths may include:

- `src/environment/` mechanism helpers only when directly tied to a contract in this Spec Kit.
- `src/analysis/full_hoodie_mechanism_fidelity_batch/` report generation and read-only audits.
- Targeted unit and integration tests for mechanism contracts.

Forbidden unless a later Spec Kit update approves them:

- Baseline-policy semantic rewrites not needed for Feature 068R regression protection.
- Campaign artifact regeneration.
- Dependency or lock-file changes.
- Feature 070 or later work.

## Repair Execution Order

1. Confirm local `main` includes Feature 068R.
2. Read Feature 068R Spec Kit and tests.
3. Read the paper mechanism registry and paper-to-code mapping.
4. Write tests/contracts for the mechanism layer before implementation.
5. Implement the smallest mechanism helpers needed to satisfy the contracts.
6. Preserve Feature 068R targeted tests.
7. Produce a mechanism fidelity report that separates verified behavior, assumptions, compatibility fallback, and blockers.
8. Run targeted validation and scope audit.

## Validation Gates

- Feature 068R regression gate.
- Coordination graph contract gate.
- Synchronization contract gate.
- Delayed reward contract gate.
- Congestion and queue-pressure contract gate.
- Timeout/drop evidence gate.
- Reward pipeline evidence gate.
- Report schema gate.
- Scope audit gate.

## Do Not Proceed Gates

Do not start implementation if:

- Feature 068R is not present in `main`.
- The branch is not created from current `origin/main`.
- The paper mechanism registry is not read.
- The intended implementation would require inventing topology, reward, timeout/drop, or delay-equation behavior without explicit blocker evidence.
- The intended implementation would regenerate campaign artifacts.

## Complexity Tracking

Any expansion beyond targeted mechanism contracts must be stopped and reported. This feature is not a full paper reproduction campaign and must not become one.

## Claim Boundary

The strongest allowed claim after implementation is mechanism-fidelity readiness for the audited contracts. Full paper reproduction remains out of scope.
