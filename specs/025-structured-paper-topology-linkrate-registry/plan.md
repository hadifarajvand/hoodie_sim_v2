# Implementation Plan: Structured Paper Topology and Link-Rate Registry

**Branch**: `[025-structured-paper-topology-linkrate-registry]` | **Date**: 2026-05-10 | **Spec**: [`spec.md`](./spec.md)
**Input**: Feature specification from `/specs/025-structured-paper-topology-linkrate-registry/spec.md`

## Summary

Produce frozen, deterministic registry artifacts for paper-backed HOODIE topology and parameters. The feature is read-only: it recovers evidence, records provenance, and marks unrecoverable items honestly. It must not infer missing Figure 7 edges or reuse simulator defaults as paper truth.

## Technical Context

**Language/Version**: Python 3.x in the approved project interpreter  
**Primary Dependencies**: Existing project modules, standard library, paper/OCR/PDF artifacts  
**Storage**: JSON/Markdown files under `resources/papers/hoodie/recovered/` and `artifacts/analysis/structured-paper-topology-linkrate-registry/`  
**Testing**: `unittest`-based schema, determinism, no-fabrication, and scope-guard tests  
**Target Platform**: Local project workspace / developer machine  
**Project Type**: Internal paper-recovery and registry feature  
**Performance Goals**: Keep recovery deterministic and reviewable; produce artifacts quickly enough for manual audit  
**Constraints**: No simulator behavior changes, no policy changes, no metric changes, no training, no neural-network code, no TorchRL, no Gymnasium, no ns-3, no ns-3-gym, no baseline redesign, no campaign reruns, no paper-validity claim  
**Scale/Scope**: A single HOODIE paper recovery pass covering Figure 7 topology and paper parameter registry values

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

The plan remains valid only if it preserves a strict no-fabrication stance. Figure 7 topology edges may be marked unrecoverable; they may not be derived from simulator defaults, node counts, or trace counts.

## Project Structure

### Documentation (this feature)

```text
specs/025-structured-paper-topology-linkrate-registry/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
└── quickstart.md
```

### Source / Artifacts (repository root)

```text
resources/papers/hoodie/recovered/
├── topology-g.json
└── paper-parameter-registry.json

src/analysis/structured_paper_topology_linkrate_registry/
├── __init__.py
├── recovery.py
├── registry.py
├── report.py
└── runner.py

tests/unit/
└── test_structured_paper_topology_linkrate_registry.py

tests/integration/
├── test_structured_paper_topology_linkrate_registry_schema.py
├── test_structured_paper_topology_linkrate_registry_determinism.py
├── test_structured_paper_topology_linkrate_registry_no_fabrication.py
└── test_structured_paper_topology_linkrate_registry_scope_guard.py

artifacts/analysis/structured-paper-topology-linkrate-registry/
├── topology-recovery-report.json
└── topology-recovery-report.md
```

**Structure Decision**: Keep the recovery logic isolated to a new analysis package. Store frozen paper-derived registries under `resources/papers/hoodie/recovered/` and the audit summary under `artifacts/analysis/structured-paper-topology-linkrate-registry/`.

## Phase 0: Outline & Research

1. Confirm what the OCR/PDF/registry sources can support for Figure 7, topology adjacency, link rates, CPU capacities, and scenario parameters.
2. Record unrecoverable items explicitly where the paper does not expose enough evidence.
3. Define canonical JSON schemas for topology and parameter registries, including provenance and recovery status fields.
4. Verify that no simulator defaults are treated as source truth for the paper registry.

## Phase 1: Design & Contracts

1. Define registry entities and recovery statuses in `data-model.md`.
2. Define validation and determinism checks in `quickstart.md`.
3. Define report fields and provenance rules in `quickstart.md`.
4. Update `AGENTS.md` to point at this plan file for Feature 025.
5. Re-check constitution alignment after the design artifacts are written.

## Implementation Approach

1. Read paper OCR and supporting registries first.
2. Recover only values that are directly supported by source evidence.
3. Mark unsupported topology edges or values unrecoverable instead of guessing.
4. Emit deterministic JSON and a matching Markdown audit summary.
5. Keep the feature read-only and archival.

## Validation Strategy

1. Schema tests validate both recovered JSON artifacts.
2. Determinism tests verify stable output ordering and stable conclusions.
3. No-fabrication tests confirm every recovered item has evidence or a documented unrecoverable status.
4. Scope-guard tests reject simulator, policy, metric, training, dependency, and lockfile changes.
5. Integration tests confirm Figure 7 recovery does not silently fall back to simulator defaults.

## Risks and Constraints

- Figure 7 may be only partially legible or not fully recoverable; the topology registry must then be unrecoverable rather than inferred.
- Link-rate and CPU values may be present only in prose or table fragments; each recovered value must cite its source evidence.
- Existing simulator structures may resemble the paper but are not authoritative and must not be treated as paper truth.

## Deliverables

- `resources/papers/hoodie/recovered/topology-g.json`
- `resources/papers/hoodie/recovered/paper-parameter-registry.json`
- `artifacts/analysis/structured-paper-topology-linkrate-registry/topology-recovery-report.json`
- `artifacts/analysis/structured-paper-topology-linkrate-registry/topology-recovery-report.md`
