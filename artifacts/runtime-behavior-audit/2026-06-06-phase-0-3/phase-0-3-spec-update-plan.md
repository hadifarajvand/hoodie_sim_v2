# Phase 0.3 Spec Update Plan

## Objective

Define the paper-faithful simulator contract before implementation. Do not modify runtime logic yet.

## Required SpecKit Updates

If the project is going to support the Phase 0.3 rebuild cleanly, the next spec update should add or revise:

1. `specs/090-hoodie-paper-faithful-simulation-rebuild/spec.md`
2. `specs/090-hoodie-paper-faithful-simulation-rebuild/plan.md`
3. `specs/090-hoodie-paper-faithful-simulation-rebuild/tasks.md`
4. `specs/090-hoodie-paper-faithful-simulation-rebuild/data-model.md`
5. `specs/090-hoodie-paper-faithful-simulation-rebuild/contracts/validation-rules.md`

## Exact Change Types Needed

### A. Architecture contract

- Define the runtime as a slot-based episode with separate action and drain phases.
- Define the task lifecycle as an auditable event chain.
- Define queue semantics explicitly for private, offloading, and source-specific public queues.

### B. State contract

- Add explicit state snapshot fields:
  - task size
  - private wait
  - offloading wait
  - public queue footprint
  - historical load matrix
  - forecast mode

### C. Reward contract

- Replace step-aggregated reward semantics with delayed task-level reward events.
- Explicitly distinguish completion reward and timeout penalty.

### D. Topology contract

- Name the topology mode.
- Tie action legality to the paper topology and Figure 7 reference.

### E. Validation contract

- Add checks for:
  - arrivals
  - queue events
  - delayed reward emission
  - drain-phase processing
  - public CPU sharing behavior
  - unresolved task detection

### F. Baseline contract

- Explicitly scope the baseline registry to:
  - HOODIE
  - RO
  - FLC
  - VO
  - HO
  - BCO
  - MLEO

## Proposed Phase 0.3 Work Product

Phase 0.3 should produce a frozen architecture spec that answers:

- What is a task?
- What is a slot?
- What is an action?
- What is a queue?
- What is a reward event?
- What constitutes paper-faithful validation?

That contract should be written before any simulator rewrite is attempted.

