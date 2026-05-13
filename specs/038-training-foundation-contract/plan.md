# Implementation Plan: Training Foundation Contract

**Branch**: `[039-training-foundation-contract]` | **Date**: 2026-05-13 | **Spec**: [`spec.md`](spec.md)
**Input**: Feature specification from `/specs/038-training-foundation-contract/spec.md`

**Note**: This plan is contract-only. It defines the training foundation artifacts needed before any DRL implementation is approved.

## Summary

Define the training foundation contract for HOODIE so future DRL work can only start against explicit, versioned, auditable schemas. The feature captures the state-vector contract, action-index contract, replay transition schema, seed protocol, train/eval split protocol, checkpoint metadata schema, and a terminal-outcome exposure gate that blocks training when terminal rewards remain too sparse.

## Technical Context

**Language/Version**: Python 3.11, documentation-only feature with schema-bearing Markdown artifacts  
**Primary Dependencies**: Existing HOODIE project code; no new dependencies  
**Storage**: Repository Markdown specs plus JSON/Markdown analysis artifacts  
**Testing**: `unittest` for contract and report validation, plus repository-scoped integration checks  
**Target Platform**: Local development environment and repository CI  
**Project Type**: Single-project simulator/research codebase  
**Performance Goals**: No runtime performance change; readiness audits must be lightweight enough to run on existing trace banks  
**Constraints**: No DRL training, no neural-network code, no optimizer or replay execution, no dependency drift, no runtime behavior changes, no reward timing changes, no topology changes  
**Scale/Scope**: Contract definition only; future training must remain blocked until terminal-outcome exposure is explicitly sufficient

**Target Update Contract Assumption**: `2000 iterations` is documented in the plan as one environment step per iteration. This is a contract assumption only; the paper wording remains ambiguous and must stay traceable in research notes rather than being silently converted into implementation behavior.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Constitution Gate

- [x] Dependency impact checked
- [x] Environment impact checked
- [x] Assumption impact checked
- [x] Fidelity impact checked
- [x] Test impact checked
- [x] Reproducibility impact checked
- [x] Config/schema impact checked
- [x] Public interface impact checked
- [x] Artifact impact checked
- [x] Security/secret impact checked
- [x] Performance budget impact checked
- [x] Baseline fairness impact checked
- [x] Paper-to-code mapping impact checked
- [x] Definition-of-done impact checked

Constitution summary:
- The approved interpreter remains `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`.
- The feature does not add or modify runtime semantics.
- The feature does not add training code or dependencies.
- The feature preserves baseline fairness by keeping the same `HoodieGymEnvironment` interface for future training and evaluation.

## Project Structure

### Documentation (this feature)

```text
specs/038-training-foundation-contract/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Optional; only if a separate schema note materially improves traceability
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
src/
├── analysis/
│   └── training_foundation_contract/
├── environment/
├── policies/
└── ...

tests/
├── integration/
└── unit/
```

**Structure Decision**: This feature is documentation- and audit-first. The only expected source-code surface is the new analysis package for contract/report generation under `src/analysis/training_foundation_contract/`. No training, policy, or environment runtime modules should be changed.

## Complexity Tracking

> No constitution violations require a complexity justification at this stage. The feature is deliberately scoped to schema and readiness contracts.

## Phase 0: Outline & Research

### Research Questions

1. What is the safest contract-only interpretation of the paper’s `2000 iterations` target-update wording?
2. What existing trace evidence from Feature 037 is sufficient to characterize terminal-outcome sparsity without changing runtime behavior?
3. What seed split, checkpoint metadata, and replay schema fields must be versioned so future DRL work can be audited without re-litigating assumptions?

### Research Deliverable

- `research.md` must record decisions, rationale, and alternatives considered for:
  - state vector scope
  - action indexing semantics
  - delayed-reward replay handling
  - target-update frequency contract
  - seed protocol
  - train/eval split protocol
  - checkpoint schema
  - terminal-outcome exposure gate

## Phase 1: Design & Contracts

### Deliverables

- `data-model.md` defining the contract entities and their relationships
- `quickstart.md` showing how to validate the readiness report and contract docs with the approved interpreter
- updated agent context reference in `AGENTS.md`

### Design Constraints

- The state contract uses only paper/runtime-supported observable variables.
- The action contract uses one generic helper-resolved horizontal action and one vertical/cloud action independent of Figure 7 adjacency.
- Replay transitions distinguish non-terminal, terminal, and pending-at-horizon cases.
- Target update frequency is documented as a contract assumption, not implemented behavior.
- Seeds are separated by purpose: trace generation, evaluation, replay sampling, initialization, and exploration.
- Checkpoints remain metadata-only.
- The readiness gate blocks training when reward-bearing terminal exposure is insufficient or its threshold is not approved.

## Constitution Re-check After Design

- [x] Dependency impact checked
- [x] Environment impact checked
- [x] Assumption impact checked
- [x] Fidelity impact checked
- [x] Test impact checked
- [x] Reproducibility impact checked
- [x] Config/schema impact checked
- [x] Public interface impact checked
- [x] Artifact impact checked
- [x] Security/secret impact checked
- [x] Performance budget impact checked
- [x] Baseline fairness impact checked
- [x] Paper-to-code mapping impact checked
- [x] Definition-of-done impact checked

No runtime or dependency changes are authorized by this plan.

