# Implementation Plan: Transmission Delay Runtime Wiring

**Branch**: `034-transmission-delay-runtime-wiring` | **Date**: 2026-05-12 | **Spec**: [/Users/hadi/Documents/GitHub/hoodie_sim_v2/specs/034-transmission-delay-runtime-wiring/spec.md](/Users/hadi/Documents/GitHub/hoodie_sim_v2/specs/034-transmission-delay-runtime-wiring/spec.md)
**Input**: Feature specification from `/specs/034-transmission-delay-runtime-wiring/spec.md`

## Summary

Wire the approved Feature 032 link-rate configuration into runtime transmission admission so horizontal and vertical offloads spend deterministic delay slots in transit before entering execution queues. Keep transmission-delay ownership in the environment/orchestration layer, reuse the existing `compute_transmission_delay()` helper, and do not change Feature 033 execution-capacity behavior, topology legality, reward timing, or capacity sharing.

## Technical Context

**Language/Version**: Python 3.x via `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`  
**Primary Dependencies**: Standard library only for this feature; existing project modules in `src/environment/`  
**Storage**: N/A; runtime metadata is stored on `Task.metadata` and in trace artifacts  
**Testing**: `unittest` via the approved interpreter  
**Target Platform**: Local repository execution on the approved dev environment  
**Project Type**: Simulator / environment runtime  
**Performance Goals**: Keep per-slot admission logic deterministic and O(1) per queued task; no new sweeps or training overhead  
**Constraints**: No dependency changes, no training, no neural-network work, no Gymnasium/ns-3/ns-3-gym/TorchRL work, no campaign reruns, no capacity-sharing redesign, no execution-time contract changes  
**Scale/Scope**: Narrow runtime wiring in the environment and queue boundary only

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

No constitution violations require justification. The scope is confined to runtime transmission delay wiring.

## Project Structure

### Documentation (this feature)

```text
specs/034-transmission-delay-runtime-wiring/
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
├── analysis/transmission_delay_runtime_wiring/
├── environment/
│   ├── gym_adapter.py
│   ├── slot_engine.py
│   ├── offloading_queue.py
│   └── link_rate_config.py
└── ...

tests/
├── unit/
└── integration/
```

**Structure Decision**: The feature stays inside the existing simulator stack. `gym_adapter.py` owns orchestration and metadata recording, `slot_engine.py` owns helper-only queue admission, `offloading_queue.py` carries queue state, and `link_rate_config.py` remains the shared delay helper source of truth.

## Complexity Tracking

No constitution violations require a complexity justification.

## Phase 0: Research

### Research Questions

1. Which runtime layer should compute and persist transmission delay metadata without moving admission ownership out of the environment?
2. What exact slot boundary should be used for deterministic offload admission when `delay_slots = 0` and when `delay_slots > 0`?
3. Which existing helper fields already cover payload, rate, delay, and rounding policy so the feature can reuse them instead of introducing a second timing model?
4. Which runtime and regression tests already cover offload timing and timeout behavior, and which new tests are needed?

### Research Outcome

See [`research.md`](./research.md) for the decisions, rationale, and alternatives.

## Phase 1: Design & Contracts

**Prerequisite:** `research.md` complete

1. Extract transmission metadata and queue-admission entities into [`data-model.md`](./data-model.md).
2. Define the runtime transmission contract under [`contracts/`](./contracts/) for slot-bound admission and metadata recording.
3. Write [`quickstart.md`](./quickstart.md) with the approved interpreter, targeted validation command, and report generation expectations.
4. Update `AGENTS.md` to point the spec-kit reference at this feature plan.

## Constitution Re-check

Re-check after Phase 1 design:

- No dependency impact
- No environment drift
- No assumptions beyond clarified feature scope
- No fidelity drift from Feature 032 or Feature 033
- No reward timing change
- No baseline fairness drift
- No artifact or config schema drift beyond runtime metadata tracking

## Definition of Done

- [x] Spec matched by plan
- [ ] Research resolved
- [ ] Data model documented
- [ ] Transmission contract documented
- [ ] Quickstart documented
- [ ] Agent context updated
- [ ] Scope guard preserved
- [ ] No runtime contract drift from Feature 033
