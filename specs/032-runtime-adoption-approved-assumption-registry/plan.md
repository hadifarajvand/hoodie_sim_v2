# Implementation Plan: Runtime Adoption of Approved Assumption Registry

**Branch**: `032-runtime-adoption-approved-assumption-registry` | **Date**: 2026-05-12 | **Spec**: [`spec.md`](spec.md)
**Input**: Feature specification from `/specs/032-runtime-adoption-approved-assumption-registry/spec.md`

## Summary

Adopt the approved Feature 031 assumptions into runtime configuration, topology legality, link-rate behavior, timeout validation, and aggregation semantics without changing training, policy design, dependency sets, or paper-recovery claims. The runtime adoption path consumes the approved assumption registry and report artifacts as the source of truth, while preserving provenance and audit labels.

## Technical Context

**Language/Version**: Python 3.x via `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`  
**Primary Dependencies**: Standard library plus existing runtime, policy, and evaluation modules in `src/environment/`, `src/policies/`, `src/evaluation/`, and `src/analysis/`  
**Storage**: Repository files, Feature 031 registry/report artifacts, and new Feature 032 runtime adoption artifacts under `artifacts/analysis/runtime-adoption-approved-assumption-registry/`  
**Testing**: `unittest` and targeted integration checks run through the approved interpreter  
**Target Platform**: Local repository execution on the approved development environment  
**Project Type**: Runtime adoption / validation pipeline with report generation  
**Performance Goals**: Preserve current step-level behavior and avoid measurable runtime regressions relative to the existing environment path  
**Constraints**: No DRL training; no neural-network work; no dependency changes; no campaign reruns; no paper-recovery claims; approved assumptions stay explicitly labeled as user-approved assumptions  
**Scale/Scope**: Limited to ComputeConfig adoption, topology legality, link-rate adoption, timeout validation, aggregation helper/reporting contract, and scoped runtime adoption report generation

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

### Governance Decision

This feature follows a runtime-adoption design that consumes approved assumptions as runtime inputs while preserving their provenance labels.

- Constitution version: `1.4.0`
- Approved interpreter path: `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`
- Feature 031 registry/report artifacts are treated as authoritative sources for adoption
- No paper-recovery claim is allowed

The constitution gate passes because this feature does not change dependency policy, training policy, or the approved interpreter boundary.
- Branch hygiene must confirm that the current branch is not `main`, that it was created from updated `main`, and that the `031-user-approved-assumption-patch-registry-complete` tag matches `main` before implementation starts.

## Project Structure

### Documentation (this feature)

```text
specs/032-runtime-adoption-approved-assumption-registry/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Repository Files Affected by This Feature

```text
resources/papers/hoodie/recovered/user-approved-assumption-registry.json
artifacts/analysis/user-approved-assumption-patch-registry/assumption-patch-report.json
artifacts/analysis/user-approved-assumption-patch-registry/assumption-patch-report.md

src/environment/compute_config.py
src/environment/topology.py
src/environment/gym_adapter.py
src/policies/action_masking.py
src/environment/link_rate_config.py
src/environment/traffic_config.py
src/evaluation/aggregate_metrics.py
src/evaluation/metrics.py

src/analysis/runtime_adoption_approved_assumption_registry/
├── __init__.py
├── report.py
└── runner.py

tests/unit/
└── test_runtime_adoption_approved_assumption_registry_*.py

tests/integration/
└── test_runtime_adoption_approved_assumption_registry_*.py
```

**Structure Decision**: Runtime adoption is implemented as a focused runtime/config/adoption-report feature that reads from the approved Feature 031 registry/report artifacts and exposes a small analysis package for report generation. No training or dependency layer changes are introduced.

### Runtime Adoption Targets

- `src/environment/compute_config.py`: adopt the approved CPU capacities because it owns the runtime CPU capacity values.
- `src/environment/topology.py`: hold adjacency legality because it is the canonical topology graph container.
- `src/environment/gym_adapter.py`: enforce topology legality and expose the runtime action mask because it owns the environment boundary.
- `src/policies/action_masking.py`: reject illegal horizontal destinations because it centralizes action validation.
- `src/environment/link_rate_config.py`: adopt `R_V = 10 Mbps` and preserve horizontal rate behavior because it owns link-rate configuration.
- `src/environment/traffic_config.py`: validate the timeout contract because it owns scenario presets and timeout slots.
- `src/evaluation/aggregate_metrics.py` and `src/evaluation/metrics.py`: provide the shared helper/contract for reward aggregation because they own evaluation aggregation semantics.
- `src/analysis/runtime_adoption_approved_assumption_registry/report.py`: generate the runtime adoption report because it must prove provenance, validations, and no paper-recovery claim.

## Phase Plan

### Phase 0: Research

- Verify branch hygiene against `main` and the `031-user-approved-assumption-patch-registry-complete` tag before any implementation work begins.
- Confirm the exact runtime config entrypoints that currently source CPU capacity, topology legality, link-rate, timeout, and aggregation behavior.
- Confirm the approved assumption artifacts can be consumed directly without a copy that would weaken provenance.
- Confirm the runtime adoption report schema and file locations for proof tracking.
- Confirm no training, policy, dependency, campaign, or reward-timing changes are required.
- Confirm the runtime adoption feature will not touch unrelated docs outside the files required for runtime/config/contract adoption and report generation.

### Phase 1: Design & Contracts

- Define the runtime-adoption data model for approved assumptions, runtime contracts, and the adoption report.
- Define a small contracts folder for runtime adoption semantics, including config inputs, legality invariants, timeout contract, and aggregation helper semantics.
- Update `AGENTS.md` to point at this plan file for Feature 032 guidance.
- Re-check the constitution gate after design to confirm no scope drift.

### Phase 2: Implementation Readiness

- Prepare the task graph for the runtime-adoption modules and their tests.
- Keep the Feature 031 registry/report artifacts unchanged except as consumed by this feature.

## Dependencies & Execution Order

- The approved Feature 031 registry/report artifacts must remain the source of truth before any runtime adoption code is written.
- ComputeConfig adoption depends on the approved capacity values from the Feature 031 registry.
- Topology legality adoption depends on the approved Figure 7 adjacency and neighbor-only rule.
- Link-rate adoption depends on the approved `R_V = 10 Mbps` and preserved horizontal rate contract.
- Timeout adoption depends on the approved `timeout_slots = 20`, `slot_duration_seconds = 0.1`, and `timeout_seconds = 2.0`.
- Aggregation adoption depends on a shared helper/contract used by both runtime and reporting code.
- The runtime adoption report depends on all adoption checks and validations being available.
- Runtime adoption must preserve assumption labels and provenance from Feature 031 and must not relabel approved assumptions as paper-recovered facts.

## Validation Strategy

- Confirm `ComputeConfig` adopts `0.5 / 0.5 / 3.0` gcycles/slot for agent/private, edge/public, and cloud.
- Confirm topology legality loads Figure 7 adjacency directly from the approved assumption registry and enforces neighbor-only horizontal offloading.
- Confirm vertical/cloud actions remain legal independently of horizontal adjacency.
- Confirm link-rate behavior uses `R_V = 10 Mbps` without creating a separate cloud-specific rate.
- Confirm timeout validation consumes the approved `20` slots and `0.1` second slot duration end-to-end and results in `2.0` seconds.
- Confirm aggregation uses per-agent episode terminal-reward sum first, then arithmetic mean across agents, excluding no-task/NaN/omitted slots.
- Confirm the final report lists consumed assumptions, runtime components, proof tests, and no-paper-recovery status.
- Confirm no training, policy, dependency, campaign, or reward-timing drift occurs.
- Confirm the final diff contains only the runtime-adoption files named in this plan and no polluted changes.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
