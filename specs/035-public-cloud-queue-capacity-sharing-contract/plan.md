# Implementation Plan: Public/Cloud Queue Capacity Sharing Contract

**Branch**: `036-public-cloud-queue-capacity-sharing` | **Date**: 2026-05-12 | **Spec**: [/Users/hadi/Documents/GitHub/hoodie_sim_v2/specs/035-public-cloud-queue-capacity-sharing-contract/spec.md](/Users/hadi/Documents/GitHub/hoodie_sim_v2/specs/035-public-cloud-queue-capacity-sharing-contract/spec.md)
**Input**: Feature specification from `/specs/035-public-cloud-queue-capacity-sharing-contract/spec.md`

## Summary

Enforce a deterministic equal-share capacity-sharing contract for public/edge and cloud queues so that multiple active queue heads targeting the same host share that host's fixed CPU capacity per slot instead of each receiving the full host capacity. Keep local/private execution unchanged, preserve the Feature 033 execution formula, and preserve the Feature 034 transmission delay contract.

## Technical Context

**Language/Version**: Python 3.x via `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`  
**Primary Dependencies**: Standard library only for this feature; existing project modules in `src/environment/`  
**Storage**: N/A; sharing state is derived from existing queue/task state during slot progression  
**Testing**: `unittest` via the approved interpreter  
**Target Platform**: Local repository execution on the approved dev environment  
**Project Type**: Simulator / environment runtime  
**Performance Goals**: Keep host-group selection and per-slot allocation deterministic and O(n) over active public/cloud heads for the slot  
**Constraints**: No dependency changes, no training, no neural-network work, no Gymnasium/ns-3/ns-3-gym/TorchRL work, no campaign reruns, no capacity-sharing redesign beyond equal-share host grouping, no execution-time formula changes, no transmission-delay changes  
**Scale/Scope**: Narrow runtime wiring in the environment slot progression path only

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

No constitution violations require justification. The feature is confined to runtime host-level capacity sharing.

## Project Structure

### Documentation (this feature)

```text
specs/035-public-cloud-queue-capacity-sharing-contract/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
src/
├── analysis/public_cloud_queue_capacity_sharing/
├── environment/
│   ├── gym_adapter.py
│   ├── public_queue.py
│   ├── compute_config.py
│   └── slot_engine.py
└── ...

tests/
├── unit/
└── integration/
```

**Structure Decision**: The feature stays inside the existing simulator stack. `gym_adapter.py` owns slot progression and queue grouping, `public_queue.py` may receive helper methods if necessary for host-group selection, `compute_config.py` provides the fixed host capacities, and `slot_engine.py` remains unchanged unless a test proves a boundary helper is needed.

## Complexity Tracking

No constitution violations require a complexity justification.

## Phase 0: Research

### Research Questions

1. Where in the environment slot loop should public and cloud queue heads be grouped by host before execution capacity is applied?
2. What stable ordering should be used for host groups and active heads so equal-share allocation is deterministic?
3. Which runtime metadata or queue state already identifies a queue head as active at slot start without introducing a new scheduler?
4. Which existing tests cover local/private execution, transmission delay, and reward timing so the new capacity-sharing tests can guard against drift?

### Research Outcome

See [`research.md`](./research.md) for the decisions, rationale, and alternatives.

## Phase 1: Design & Contracts

**Prerequisite:** `research.md` complete

1. Extract host-group and active-head entities into [`data-model.md`](./data-model.md).
2. Define the runtime capacity-sharing contract under [`contracts/`](./contracts/) for public EA and cloud host pools.
3. Write [`quickstart.md`](./quickstart.md) with the approved interpreter, targeted validation command, and report expectations.
4. Update `AGENTS.md` to point the spec-kit reference at this feature plan.

## Constitution Re-check

Re-check after Phase 1 design:

- No dependency impact
- No environment drift
- No assumptions beyond clarified feature scope
- No fidelity drift from Feature 033 or Feature 034
- No reward timing change
- No baseline fairness drift
- No artifact or config schema drift beyond runtime sharing metadata

## Definition of Done

- [x] Spec matched by plan
- [ ] Research resolved
- [ ] Data model documented
- [ ] Runtime sharing contract documented
- [ ] Quickstart documented
- [ ] Agent context updated
- [ ] Scope guard preserved
- [ ] No runtime contract drift from Feature 033 or Feature 034
