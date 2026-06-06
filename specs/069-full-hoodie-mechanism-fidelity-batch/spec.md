# Feature Specification: Full HOODIE Mechanism Fidelity Batch

**Feature Branch**: `069-full-hoodie-mechanism-fidelity-batch`  
**Spec Branch**: `069-full-hoodie-mechanism-fidelity-spec-kit`  
**Created**: 2026-05-31  
**Status**: Spec Kit handoff only; implementation not started  
**Input**: Feature 069 defines the mechanism-fidelity contract after Feature 068R baseline placement fidelity.

## Dependency

Feature 069 depends on Feature 068R being merged into `main`. Feature 068R provides placement-aware baseline policy behavior and compatibility fallback. Feature 069 must treat that work as an input contract, not as a new target for baseline-policy repair.

## Goal

Define the full HOODIE mechanism-fidelity batch around the decision loop: coordination graph, time-slot synchronization, delayed reward, queue pressure, timeout/drop accounting, and mechanism evidence reporting.

## User Stories

### US1 - Coordination fidelity
As a researcher, I need the implementation to expose what coordination or neighbor graph evidence exists, what is assumption-backed, and what remains blocked by missing structured topology evidence.

### US2 - Synchronization fidelity
As a researcher, I need time-slot sequencing, action application, queue updates, and terminal accounting to be validated as a coherent mechanism, not as isolated helpers.

### US3 - Delayed reward and outcome fidelity
As a researcher, I need delayed reward and terminal outcome handling to be audited without inventing paper equations that are not structurally recovered.

### US4 - Congestion and queue-pressure fidelity
As a researcher, I need private, public, and cloud queue pressure to be represented as evidence that is compatible with Feature 068R placement-aware policies.

### US5 - Mechanism report readiness
As a reviewer, I need a report that separates verified behavior, compatibility fallback, assumption-backed behavior, and unresolved blockers.

## Acceptance Criteria

- Feature 068R regression evidence remains present and green in the targeted policy slice.
- Mechanism contracts exist for coordination graph, synchronization, delayed reward, congestion, queue pressure, timeout/drop, and reward pipeline evidence.
- Any topology, reward, timeout/drop, or delay-equation ambiguity is recorded as a blocker or assumption, not hidden in implementation.
- The implementation may claim mechanism-fidelity readiness only after targeted tests pass.
- The implementation may not claim full paper reproduction.

## Out of Scope

- New baseline-policy semantics beyond Feature 068R regression protection.
- Campaign artifact regeneration.
- Full-suite cleanup for unrelated historical failures.
- Paper reproduction claims.
- New dependencies.

## Regression Guard

Feature 069 must not weaken Feature 068R. If a future implementation changes policy behavior, it must prove that Feature 068R registry coverage, legal-mask authority, fallback behavior, seeded RO behavior, BCO balance-hint behavior, and MLEO candidate metadata remain valid.

## Paper-Claim Boundary

This feature can produce mechanism-fidelity readiness evidence. It cannot claim complete HOODIE reproduction unless topology, reward, timeout/drop, delay equations, training details, and evaluation campaigns are separately validated.
