# Tasks: Structured Paper Topology and Link-Rate Registry

**Input**: Design documents from `/specs/025-structured-paper-topology-linkrate-registry/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md  
**Tests**: Required. This feature is read-only paper recovery and must prove no fabricated topology or parameter values are introduced.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Lock down the allowed paper sources, output locations, and schema boundaries before any registry recovery is written.

- [ ] T001 Add the source-gate validation test in `tests/unit/test_structured_paper_topology_linkrate_registry.py` to confirm the OCR/PDF inputs, the paper-mechanism-registry input, and the paper-figure-extraction input all exist, are readable, and can be loaded before any recovery begins
- [ ] T002 Add the schema definition task in `src/analysis/structured_paper_topology_linkrate_registry/registry.py` to define the frozen topology-g.json and paper-parameter-registry.json structures, including schema_version, recovery_status, source_evidence, unrecoverable_items, and no_fabrication_disclaimer fields

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Prove what can and cannot be recovered before writing any frozen registry artifacts.

- [ ] T003 [US1] Add the Figure 7 evidence extraction task in `src/analysis/structured_paper_topology_linkrate_registry/recovery.py` to recover the paper Figure 7 topology graph / matrix G only from paper/OCR/PDF evidence and to record unresolved topology gaps explicitly
- [ ] T004 [US1] Add the N=20 EA structure extraction task in `src/analysis/structured_paper_topology_linkrate_registry/recovery.py` to capture the edge-agent count and any recoverable node identifiers without inferring missing graph edges
- [ ] T005 [US1] Add the adjacency and horizontal-destination extraction task in `src/analysis/structured_paper_topology_linkrate_registry/recovery.py` to recover the adjacency matrix and legal horizontal offload destinations only when paper evidence supports them
- [ ] T006 [US1] Add the edge/cloud connectivity extraction task in `src/analysis/structured_paper_topology_linkrate_registry/recovery.py` to recover cloud connectivity facts only from paper-backed evidence
- [ ] T007 [US2] Add the link-rate and data-rate extraction task in `src/analysis/structured_paper_topology_linkrate_registry/recovery.py` to recover horizontal, vertical, and cloud-facing data-rate values only when the paper/OCR/PDF evidence supports them
- [ ] T008 [US2] Add the CPU-capacity and processing-parameter extraction task in `src/analysis/structured_paper_topology_linkrate_registry/recovery.py` to recover EA private/public/cloud CPU capacities and related processing parameters only when explicitly paper-backed
- [ ] T009 [US2] Add the scenario-parameter extraction task in `src/analysis/structured_paper_topology_linkrate_registry/recovery.py` to recover paper-level experiment parameters such as arrival, size, timeout, and workload settings only when supported by source evidence
- [ ] T010 [US1] Add the unrecoverable-item classification task in `src/analysis/structured_paper_topology_linkrate_registry/recovery.py` to reject fabricated edges or values and mark unsupported items as unrecoverable or partially recovered only when allowed by the spec

**Checkpoint**: The paper-backed recovery boundary is established before any artifact writing begins.

---

## Phase 3: User Story 1 - Topology Registry Recovery (Priority: P1)

**Goal**: Recover the Figure 7 topology registry as a frozen artifact without inventing any edges or connectivity.

**Independent Test**: The topology artifact either fully recovers Figure 7 with evidence for every edge or is explicitly marked unrecoverable; it never silently uses simulator defaults.

### Tests for User Story 1

- [ ] T011 [US1] Add the schema validation test in `tests/unit/test_structured_paper_topology_linkrate_registry.py` for `resources/papers/hoodie/recovered/topology-g.json` to verify required fields, schema_version, recovery_status, and evidence metadata
- [ ] T012 [P] [US1] Add the deterministic output test in `tests/integration/test_structured_paper_topology_linkrate_registry_determinism.py` to verify stable ordering and stable conclusions for topology recovery
- [ ] T013 [US1] Add the topology no-fabrication integration test in `tests/integration/test_structured_paper_topology_linkrate_registry_no_fabrication.py` to verify every recovered topology edge or connectivity value has evidence or is explicitly unrecoverable
- [ ] T014 [US1] Add the simulator-defaults integration test in `tests/integration/test_structured_paper_topology_linkrate_registry_schema.py` to prove Figure 7 recovery does not silently use simulator topology defaults as paper evidence

### Implementation for User Story 1

- [ ] T015 [US1] Build the topology registry writer in `src/analysis/structured_paper_topology_linkrate_registry/recovery.py` and `src/analysis/structured_paper_topology_linkrate_registry/runner.py` to produce deterministic `resources/papers/hoodie/recovered/topology-g.json`

### Validation for User Story 1

- [ ] T016 [US1] Add the final topology validation in `tests/unit/test_structured_paper_topology_linkrate_registry.py` to confirm the recovered topology registry either contains paper-backed Figure 7 facts or is marked unrecoverable without fabricated edges

---

## Phase 4: User Story 2 - Parameter Registry Recovery (Priority: P2)

**Goal**: Recover the paper-backed parameter registry with provenance for each recovered value.

**Independent Test**: The parameter registry contains only paper-backed values, each with a recovery status and source evidence, and any unsupported value is explicitly unrecoverable.

### Tests for User Story 2

- [ ] T017 [P] [US2] Add the schema validation test in `tests/unit/test_structured_paper_topology_linkrate_registry.py` for `resources/papers/hoodie/recovered/paper-parameter-registry.json` to verify required fields, schema_version, recovery_status, and evidence metadata
- [ ] T018 [US2] Add the parameter no-fabrication integration test in `tests/integration/test_structured_paper_topology_linkrate_registry_no_fabrication.py` to verify every recovered parameter value has evidence or is explicitly unrecoverable

### Implementation for User Story 2

- [ ] T019 [US2] Build the parameter registry writer in `src/analysis/structured_paper_topology_linkrate_registry/recovery.py` and `src/analysis/structured_paper_topology_linkrate_registry/runner.py` to produce deterministic `resources/papers/hoodie/recovered/paper-parameter-registry.json`

### Validation for User Story 2

- [ ] T020 [US2] Add the final parameter validation in `tests/unit/test_structured_paper_topology_linkrate_registry.py` to confirm all recovered parameter values are evidence-backed and unsupported values remain unrecoverable

---

## Phase 5: User Story 3 - Recovery Report and Scope Guards (Priority: P3)

**Goal**: Produce deterministic report artifacts and prove the recovery feature stays read-only and paper-bound.

**Independent Test**: The report artifacts summarize recovered, partially recovered, and unrecoverable items, and the feature leaves simulator, policy, metric, training, dependency, and campaign artifacts untouched.

### Tests for User Story 3

- [ ] T021 [US3] Add the report schema validation test in `tests/unit/test_structured_paper_topology_linkrate_registry.py` to verify `artifacts/analysis/structured-paper-topology-linkrate-registry/topology-recovery-report.json` contains the expected schema_version, counts, evidence fields, and disclaimers
- [ ] T022 [P] [US3] Add the report determinism test in `tests/integration/test_structured_paper_topology_linkrate_registry_determinism.py` to verify the recovery report output is stable across repeated runs with the same evidence
- [ ] T023 [US3] Add the analysis report writer in `src/analysis/structured_paper_topology_linkrate_registry/report.py` and `src/analysis/structured_paper_topology_linkrate_registry/runner.py` to produce deterministic JSON and Markdown reports under `artifacts/analysis/structured-paper-topology-linkrate-registry/`
- [ ] T024 [US3] Add the scope guard test in `tests/integration/test_structured_paper_topology_linkrate_registry_scope_guard.py` to reject any changes to `src/environment`, `src/policies`, `src/metrics`, `src/training`, dependency files, lockfiles, baseline campaign artifacts, or existing campaign artifacts
- [ ] T025 [US3] Add the final validation task in `tests/integration/test_structured_paper_topology_linkrate_registry_schema.py` and `tests/integration/test_structured_paper_topology_linkrate_registry_no_fabrication.py` to summarize recovered, partially recovered, and unrecoverable items without claiming paper-validity or reproduction readiness

**Checkpoint**: The frozen registry artifacts and their audit report prove the feature stayed read-only and evidence-bound.

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1**: No dependencies. Establish gates, schema boundaries, and source validation first.
- **Phase 2**: Depends on Phase 1. Evidence extraction and unrecoverable classification must be established before any registry writer runs.
- **Phase 3**: Depends on Phase 2. Topology registry writing can begin only after Figure 7 recovery evidence is understood.
- **Phase 4**: Depends on Phase 2. Parameter registry writing can proceed once parameter evidence extraction is complete.
- **Phase 5**: Depends on Phases 3 and 4. Reporting and scope guards finalize the feature after the registries exist.

### Task Dependencies

- `T001` must complete before any recovery work begins.
- `T002` must complete before `T015`, `T019`, and `T023`.
- `T003`, `T004`, `T005`, `T006`, `T007`, `T008`, `T009`, and `T010` must complete before `T015`, `T019`, and `T023`.
- `T011` must complete before `T015` and `T016`.
- `T012` must complete before `T016`.
- `T017` must complete before `T019` and `T020`.
- `T021` must complete before `T023` and `T025`.
- `T023` must complete before `T025`.

## Parallel Opportunities

- `T003` and `T004` can run in parallel after `T001`.
- `T005` and `T006` can run in parallel after `T001`.
- `T007`, `T008`, and `T009` can run in parallel after `T001`.
- `T012` and `T017` can run in parallel after the foundational evidence extraction is in place.
- `T022` can run in parallel with `T021`.

## Implementation Strategy

### MVP First

1. Complete `T001`-`T010` to lock down the paper evidence boundary and unrecoverable rules.
2. Complete `T011`-`T016` to recover or reject the topology artifact.
3. Complete `T017`-`T020` to recover or reject the parameter registry.
4. Complete `T021`-`T025` to write the report and prove the feature remains read-only and deterministic.

### Incremental Delivery

1. Start with source-gate and schema definitions.
2. Recover topology evidence next, because Figure 7 has the strictest no-fabrication rule.
3. Recover parameter values only when the paper supports them.
4. Emit deterministic artifacts and validate them before declaring completion.

## Notes

- The feature is diagnostic and archival only.
- No campaign reruns are allowed.
- No paper-validity claim is permitted.
- The topology registry is all-or-nothing for Figure 7: if the topology is not fully recoverable, the artifact is unrecoverable rather than partially recovered.

## Acceptance Mapping

- `Source gate requirement` is satisfied by `T001`.
- `Schema definition requirement` is satisfied by `T002`.
- `Figure 7 topology recovery requirement` is satisfied by `T003`, `T011`, `T012`, `T013`, `T014`, `T015`, and `T016`.
- `Parameter recovery requirement` is satisfied by `T004`, `T005`, `T006`, `T007`, `T008`, `T009`, `T017`, `T018`, `T019`, and `T020`.
- `Unrecoverable classification requirement` is satisfied by `T010`.
- `Registry writing requirement` is satisfied by `T015` and `T019`.
- `Report writing requirement` is satisfied by `T021`, `T022`, `T023`, and `T025`.
- `Scope guard requirement` is satisfied by `T024`.
