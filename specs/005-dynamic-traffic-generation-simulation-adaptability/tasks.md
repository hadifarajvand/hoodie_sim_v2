# Tasks: Dynamic Traffic Generation & Simulation Adaptability

**Input**: Design documents from `/specs/005-dynamic-traffic-generation-simulation-adaptability/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Organization**: Tasks are grouped by user story or cross-cutting phase so the traffic feature can be implemented and validated without touching lifecycle ownership, training, agents, TorchRL, neural networks, ns-3, or dependency files.

## Phase 1: Setup (Shared Documentation and Traceability)

**Purpose**: Align the paper-backed feature docs with the planned traffic boundary before code changes begin.

- [X] T001 [P] Review and align `specs/005-dynamic-traffic-generation-simulation-adaptability/spec.md` so the paper-backed Bernoulli traffic scope, scenario presets, observability, and out-of-scope items match the approved feature plan.
- [X] T002 [P] Review and align `specs/005-dynamic-traffic-generation-simulation-adaptability/plan.md` so the constitution gate, architecture, affected modules, and no-dependency policy match the approved traffic feature boundary.
- [X] T003 [P] Review and align `specs/005-dynamic-traffic-generation-simulation-adaptability/research.md` so it records only OCR-backed traffic decisions and explicitly documents unresolved gaps instead of inventing behavior.
- [X] T004 [P] Review and align `specs/005-dynamic-traffic-generation-simulation-adaptability/data-model.md` so `TrafficConfig`, `TrafficSummary`, `TrafficTrace`, and `EvaluationTrace` compatibility are described consistently.
- [X] T005 [P] Review and align `specs/005-dynamic-traffic-generation-simulation-adaptability/contracts/traffic-generation.md` so the generator API and summary API match the planned traffic boundary.
- [X] T006 [P] Review and align `specs/005-dynamic-traffic-generation-simulation-adaptability/quickstart.md` so it shows traffic generation, `HoodieGymEnvironment.reset(seed)` / `step(action)` usage, and the no-dependency-change note.

**Checkpoint**: Traffic docs are aligned to the paper-backed boundary and ready for implementation.

## Phase 2: Foundational Traffic Configuration

**Purpose**: Establish the paper-backed traffic presets that all generators and summaries depend on.

- [X] T007 Add `src/environment/traffic_config.py` with `TrafficConfig` and paper-backed preset constructors for `paper_default`, `moderate`, `heavy`, and `extreme`.
- [X] T008 [P] Add `tests/unit/test_traffic_config.py` verifying `paper_default` values (`P=0.5`, `N=20`, `T=110`, `Δ=0.1`, `timeout=20`, size range `2-5` by `0.1`, density `0.297`) plus the `moderate`, `heavy`, `extreme`, and invalid-scenario cases.

**Checkpoint**: Paper-backed traffic presets are executable and validated.

## Phase 3: User Story 1 - Deterministic Bernoulli Traffic Traces (Priority: P1)

**Goal**: Generate seeded Bernoulli traffic traces that are reproducible and ordered deterministically.

**Independent Test**: Generate the same configuration and seed twice and confirm identical traffic records, task blueprints, ordering, and summary metadata.

- [X] T009 [US1] Add `src/environment/traffic_generator.py` implementing seeded per-agent, per-slot Bernoulli generation using `rand < P` and emitting compatibility `EvaluationTrace` / `TraceTaskBlueprint` objects.
- [X] T010 [P] [US1] Add `tests/unit/test_traffic_generator.py` verifying same-seed determinism, deterministic task IDs, sorted order by `arrival_slot` / `source_agent_id` / `task_id`, slot bounds, agent bounds, one task per agent per slot, and required task fields.
- [X] T011 [US1] Add a deterministic RNG injection path or equivalent test hook in `src/environment/traffic_generator.py` only if needed to prove exact `rand < P` threshold behavior, and cover it in `tests/unit/test_traffic_generator.py`.

**Checkpoint**: Traffic generation is deterministic, paper-backed, and reproducible by seed.

## Phase 4: User Story 2 - Traffic Summary and Observability (Priority: P2)

**Goal**: Report configured and observed load metrics over generated traces without adding traffic-model switching.

**Independent Test**: Generate a known trace and verify configured arrival probability, observed arrival probability, total arrivals, arrivals per slot, arrivals per agent, scenario name, and seed.

- [X] T012 [US2] Add `src/environment/traffic_observer.py` with `TrafficSummary` computation over the full trace and optional rolling-window summaries.
- [X] T013 [P] [US2] Add `tests/unit/test_traffic_observer.py` verifying observed arrival probability and per-slot / per-agent counts from a known small trace, including clipped rolling-window behavior.

**Checkpoint**: Traffic observability reports the load metrics needed for future adaptability features.

## Phase 5: User Story 3 - Environment Compatibility (Priority: P2)

**Goal**: Feed generated traffic through the existing environment boundary without changing lifecycle ownership.

**Independent Test**: Run a generated traffic trace through `HoodieGymEnvironment` using the external `reset(seed)` / `step(action)` loop and confirm same-slot arrivals remain deterministically serialized.

- [X] T014 [P] [US3] Update `src/evaluation/trace_protocol.py` only if needed so generated traffic traces serialize into the existing `EvaluationTrace` / `TraceTaskBlueprint` shape without breaking current callers.
- [X] T015 [US3] Add `tests/integration/test_dynamic_traffic_environment_flow.py` proving a generated traffic trace runs through `HoodieGymEnvironment` using the external policy loop and `reset(seed)` / `step(action)` only.
- [X] T016 [P] [US3] Extend `tests/integration/test_dynamic_traffic_environment_flow.py` or `tests/integration/test_flc_episode.py` to verify same-slot multi-agent arrivals from generated traffic are preserved and serialized by the existing deterministic environment ordering.

**Checkpoint**: Generated traffic flows through the existing environment boundary unchanged.

## Phase 6: Documentation and Mapping

**Purpose**: Record the paper-to-code mapping, assumptions, and no-dependency note for the feature.

- [X] T017 [P] Update `docs/paper_notes/paper_to_code_mapping.md` with mappings for Algorithm 1 arrivals, Table 4 defaults, traffic scenarios, and traffic observability helpers.
- [X] T018 [P] Update `docs/assumptions/hoodie_assumptions.md` only for unresolved paper gaps, and record unit-conversion blockers explicitly if they remain unresolved.
- [X] T019 [P] Add the no-dependency-change verification note to `specs/005-dynamic-traffic-generation-simulation-adaptability/quickstart.md`.

**Checkpoint**: The feature is traceable and its paper-backed boundaries are documented.

## Phase 7: Guardrails and Validation

**Purpose**: Lock the traffic feature down with rejection tests and repository-level verification.

- [X] T020 [P] Add regression coverage in `tests/unit/test_traffic_config.py` or `tests/unit/test_traffic_generator.py` ensuring unsupported traffic scenario or model names are rejected and never silently accepted.
- [X] T021 Verify no dependency files changed by checking `pyproject.toml`, `requirements.txt`, `setup.cfg`, and `setup.py` remain untouched for this feature.
- [X] T022 Run relevant unit tests: `tests/unit/test_traffic_config.py`, `tests/unit/test_traffic_generator.py`, `tests/unit/test_traffic_observer.py`, and the existing environment boundary tests that cover `HoodieGymEnvironment` and `SlotEngine`.
- [X] T023 Run relevant integration tests: `tests/integration/test_dynamic_traffic_environment_flow.py`, `tests/integration/test_flc_episode.py`, and `tests/integration/test_evaluation_runner.py`.
- [X] T024 Update `specs/005-dynamic-traffic-generation-simulation-adaptability/tasks.md` checkboxes only after the code, docs, and tests are complete.

**Checkpoint**: Traffic generation is verified, traceable, and still dependency-clean.

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1**: No dependencies, can start immediately.
- **Phase 2**: Depends on Phase 1 completion.
- **Phase 3**: Depends on Phase 2 completion.
- **Phase 4**: Depends on Phase 3 completion.
- **Phase 5**: Depends on Phase 3 and Phase 4 completion.
- **Phase 6**: Depends on Phases 3 through 5 being stable.
- **Phase 7**: Depends on all implementation, documentation, and compatibility work being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 2. No dependency on observability or environment compatibility.
- **User Story 2 (P2)**: Depends on the generated trace shape from User Story 1.
- **User Story 3 (P2)**: Depends on User Story 1 and User Story 2 so it can validate generated traces through the stable environment boundary.

### Within Each Story

- Tests or validation tasks must exist for every implementation task.
- Configuration before generator.
- Generator before observer and environment compatibility.
- Environment compatibility before integration validation of same-slot serialization.
- Documentation and traceability updates after behavior is stable.

## Parallel Execution Examples

```bash
# Phase 1 documentation alignment can be split across files
Task: "Review and align specs/005-dynamic-traffic-generation-simulation-adaptability/spec.md"
Task: "Review and align specs/005-dynamic-traffic-generation-simulation-adaptability/plan.md"
Task: "Review and align specs/005-dynamic-traffic-generation-simulation-adaptability/research.md"

# Phase 2 config and validation can be worked separately once the file exists
Task: "Add src/environment/traffic_config.py with TrafficConfig and presets"
Task: "Add tests/unit/test_traffic_config.py verifying preset values"

# Phase 3 generator implementation and test drafting can proceed in parallel if the API is stable
Task: "Add src/environment/traffic_generator.py implementing seeded Bernoulli generation"
Task: "Add tests/unit/test_traffic_generator.py verifying deterministic trace generation"

# Phase 5 integration work can be split across compatibility and replay checks
Task: "Add tests/integration/test_dynamic_traffic_environment_flow.py"
Task: "Extend tests/integration/test_flc_episode.py for same-slot serialization"
```

## Implementation Strategy

### MVP First

1. Complete Phase 1 documentation alignment.
2. Complete Phase 2 traffic presets and validation.
3. Complete Phase 3 deterministic Bernoulli generation.
4. Validate one generated trace through `HoodieGymEnvironment` using the existing external loop.
5. Stop and confirm the seedable traffic source is reproducible before expanding observability.

### Incremental Delivery

1. Add paper-backed presets.
2. Add deterministic traffic generation.
3. Add traffic summary metrics.
4. Wire generated traces into the existing environment boundary.
5. Add paper-to-code mapping, assumptions, and no-dependency verification.
6. Finish with regression tests and repository validation.

### Suggested MVP Scope

- User Story 1 only, with a minimal environment compatibility smoke path from User Story 3 if needed to prove the generated trace can actually be consumed.
