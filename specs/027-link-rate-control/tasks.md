# Tasks: Link-Rate Control and Transmission Delay Contract

**Input**: Design documents from `/specs/027-link-rate-control/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: This feature explicitly requests unit and integration tests for unit conversion, transmission-delay math, invalid inputs, environment control hooks, monotonicity, Feature 026 regression, topology fabrication guard, scope guard, and report generation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the approved scope and the source artifacts that gate this feature

### Quality Gate

- [X] T001 Confirm source gates for Feature 020, Feature 025, and Feature 026 in `artifacts/analysis/controlled-mechanistic-sweeps/controlled-mechanistic-sweeps.json`, `artifacts/analysis/structured-paper-topology-linkrate-registry/topology-recovery-report.json`, and `artifacts/analysis/offload-lifecycle-instrumentation/instrumentation-summary.json`
- [X] T002 Verify Feature 020 still classifies `link_rate` as `instrumentation_gap` in `artifacts/analysis/controlled-mechanistic-sweeps/controlled-mechanistic-sweeps.md` and `artifacts/analysis/controlled-mechanistic-sweeps/controlled-mechanistic-sweeps.json`
- [X] T003 Verify Feature 025 registry artifacts preserve horizontal `30 Mbps`, vertical `10 Mbps`, unrecoverable cloud data rate, and unrecoverable Figure 7 adjacency in `artifacts/analysis/structured-paper-topology-linkrate-registry/topology-recovery-report.json` and `resources/papers/hoodie/recovered/topology-g.json`
- [X] T004 Verify Feature 026 lifecycle instrumentation artifacts remain present in `artifacts/analysis/offload-lifecycle-instrumentation/instrumentation-summary.json` and `artifacts/analysis/offload-lifecycle-instrumentation/instrumentation-summary.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the contract boundary before story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Record the pre-feature boundary that `link_rate` was previously an instrumentation gap and that per-edge/offload control remains unsupported without runtime-backed non-paper evidence in `specs/027-link-rate-control/research.md`
- [X] T006 Define the link-rate config fields, conversion entities, and transmission-delay contract in `specs/027-link-rate-control/data-model.md` and `specs/027-link-rate-control/contracts/transmission-delay-contract.md`
- [X] T007 Define the validation/reporting scope for supported defaults, unsupported controls, and monotonic delay evidence in `specs/027-link-rate-control/quickstart.md`

**Checkpoint**: Contract boundary is explicit and testable

---

## Phase 3: User Story 1 - Configure Link Rates (Priority: P1) 🎯 MVP

**Goal**: Expose public, config-backed horizontal and vertical link-rate controls with explicit unsupported handling for per-edge/offload requests

**Independent Test**: Can set horizontal and vertical rates through the public environment/config contract, while per-edge/offload requests are labeled unsupported instead of being fabricated

### Tests for User Story 1

- [X] T008 [P] [US1] Add unit conversion tests for `bits/Mbits`, `bps/Mbps`, and explicit `seconds/slots` handling in `tests/unit/test_link_rate_conversion.py`
- [X] T009 [P] [US1] Add invalid-input tests for zero/negative rates and invalid payload sizes in `tests/unit/test_link_rate_invalid_inputs.py`
- [X] T010 [P] [US1] Add public environment config-hook tests for `horizontal_data_rate` and `vertical_data_rate` in `tests/integration/test_link_rate_control_horizontal.py` and `tests/integration/test_link_rate_control_vertical.py`
- [X] T011 [P] [US1] Add unsupported per-edge/offload control tests that must report blocked/unsupported when topology evidence is missing in `tests/integration/test_link_rate_control_scope_guard.py`

### Implementation for User Story 1

- [X] T012 [P] [US1] Create the public link-rate config entrypoint in `src/environment/link_rate_config.py` exposing `horizontal_data_rate_mbps`, `vertical_data_rate_mbps`, optional `per_edge_link_rates` only when non-fabricated, and `slot_duration_seconds` or an explicit reference to the existing slot-duration config
- [X] T013 [US1] Implement public link-rate config plumbing and validation in `src/environment/gym_adapter.py` and `src/environment/environment.py` using `src/environment/link_rate_config.py`
- [X] T014 [P] [US1] Implement link-rate normalization and conversion helpers in `src/environment/compute_config.py` or a new `src/environment/link_rate.py`
- [X] T015 [P] [US1] Implement unsupported per-edge/offload handling that refuses topology fabrication in `src/environment/topology.py` and `src/environment/gym_adapter.py`

**Checkpoint**: Horizontal/vertical defaults are configurable and unsupported controls are honestly blocked

---

## Phase 4: User Story 2 - Compute Transmission Delay (Priority: P2)

**Goal**: Provide a deterministic transmission-delay contract and validation artifact for controllable link-rate changes

**Independent Test**: Higher controllable rates for the same payload never increase computed delay, and the rounding policy is explicit

### Tests for User Story 2

- [X] T016 [P] [US2] Add transmission-delay formula tests for `payload_bits / data_rate_bps` in `tests/unit/test_link_rate_transmission_delay.py`
- [X] T017 [P] [US2] Add rounding-policy tests for converting delay seconds to simulator slots in `tests/unit/test_link_rate_rounding_policy.py`
- [X] T018 [P] [US2] Add monotonicity validation tests proving increased data rate does not increase delay for fixed payload in `tests/integration/test_link_rate_monotonicity.py`

### Implementation for User Story 2

- [X] T019 [P] [US2] Implement deterministic transmission-delay calculation and explicit slot conversion in `src/environment/runtime_model.py` or `src/environment/link_rate.py`
- [X] T020 [US2] Add validation/report helpers in `src/analysis/link_rate_transmission_delay_contract/__init__.py`, `src/analysis/link_rate_transmission_delay_contract/report.py`, and `src/analysis/link_rate_transmission_delay_contract/runner.py` that summarize the transmission-delay contract
- [X] T021 [US2] Regenerate the link-rate contract report artifacts in `artifacts/analysis/link-rate-transmission-delay-contract/link-rate-contract-report.json` and `artifacts/analysis/link-rate-transmission-delay-contract/link-rate-contract-report.md`

**Checkpoint**: The contract can prove that controlled rate changes reduce or preserve delay

---

## Phase 5: User Story 3 - Respect Topology Boundaries (Priority: P3)

**Goal**: Preserve Feature 026 observability and reject any topology or policy invention while validating unsupported controls honestly

**Independent Test**: Feature 026 trace observability remains intact, Figure 7 adjacency stays unrecoverable, and no forbidden scope drift occurs

### Tests for User Story 3

- [X] T022 [P] [US3] Add a regression test proving Feature 026 offload lifecycle trace observability is preserved in `tests/integration/test_offload_instrumentation_trace_regression.py`
- [X] T023 [P] [US3] Add a topology-fabrication guard test proving Figure 7 adjacency and legal horizontal destinations remain unrecoverable unless evidence-backed in `tests/integration/test_link_rate_topology_fabrication_guard.py`
- [X] T024 [P] [US3] Add a no-curve-fitting guard test proving no paper plot fitting or artificial output tuning was introduced in `tests/integration/test_link_rate_no_curve_fitting_guard.py`
- [X] T025 [P] [US3] Add a scope-guard test proving no `src/policies`, `src/metrics`, `src/training`, dependency, lockfile, campaign artifact, baseline redesign, training stack, or paper-validity claim changes in `tests/integration/test_link_rate_scope_guard.py`

### Implementation for User Story 3

- [X] T026 Update the link-rate validation/report pipeline in `src/analysis/link_rate_transmission_delay_contract/__init__.py`, `src/analysis/link_rate_transmission_delay_contract/report.py`, and `src/analysis/link_rate_transmission_delay_contract/runner.py` to distinguish recovered defaults, controllable rates, unsupported controls, and remaining blockers
- [X] T027 Preserve Feature 026 observability coverage while integrating link-rate controls in `src/environment/gym_adapter.py`, `src/audits/differential_environment/audit.py`, and `src/environment/offload_trace_ledger.py`
- [X] T028 Reconcile any unsupported topology/legal-destination outcomes with the recovered registry without inventing Figure 7 edges in `resources/papers/hoodie/recovered/topology-g.json`

**Checkpoint**: The feature remains honest about topology limits while preserving lifecycle observability

---

## Phase 6: Final Validation & Reporting

**Purpose**: Finish the feature with deterministic reporting and clear blockers

- [X] T029 Generate the final link-rate contract validation report in `artifacts/analysis/link-rate-transmission-delay-contract/link-rate-contract-report.json` and `artifacts/analysis/link-rate-transmission-delay-contract/link-rate-contract-report.md`
- [X] T030 Write the final validation summary covering recovered defaults, controllable rates, unsupported controls, formula, unit conversions, tests, and remaining blockers in `specs/027-link-rate-control/quickstart.md`
- [X] T031 Confirm all required tests pass and no forbidden paths changed before handoff by reviewing `tests/unit/test_link_rate_*.py`, `tests/integration/test_link_rate_*.py`, and `git diff --name-only origin/main...HEAD`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel if staffed
  - Or sequentially in priority order (P1 → P2 → P3)
- **Final Validation (Phase 6)**: Depends on the selected user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2)
- **User Story 2 (P2)**: Can start after Foundational (Phase 2); benefits from US1 config helpers but remains independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2); depends on registry and observability context but remains independently testable

### Within Each User Story

- Tests MUST be written first and fail before implementation
- Shared contract definitions before integration wiring
- Unsupported controls must remain labeled blocked/unsupported
- No topology fabrication, policy redesign, or metric redesign

### Parallel Opportunities

- Setup gate checks T001-T004 can run independently
- T008-T011 can run in parallel because they touch different test files
- T012-T015 can run in parallel because they touch different implementation files
- T016-T018 can run in parallel because they validate distinct delay behaviors
- T022-T025 can run in parallel because they touch different guard/regression files

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Add unit conversion tests for bits/Mbits, bps/Mbps, and explicit seconds/slots handling in tests/unit/test_link_rate_conversion.py"
Task: "Add invalid-input tests for zero/negative rates and invalid payload sizes in tests/unit/test_link_rate_invalid_inputs.py"
Task: "Add public environment config-hook tests for horizontal_data_rate and vertical_data_rate in tests/integration/test_link_rate_control_horizontal.py and tests/integration/test_link_rate_control_vertical.py"
Task: "Add unsupported per-edge/offload control tests that must report blocked/unsupported when topology evidence is missing in tests/integration/test_link_rate_control_scope_guard.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate that public horizontal/vertical link-rate control exists and unsupported controls are blocked honestly

### Incremental Delivery

1. Setup + Foundational → contract boundary locked
2. User Story 1 → public link-rate control
3. User Story 2 → transmission-delay contract and monotonicity proof
4. User Story 3 → topology boundary guards and observability regression protection
5. Final validation → report artifacts and blocker summary

### Parallel Team Strategy

With multiple developers:

1. One developer handles the gate checks and contract docs
2. One developer implements the rate config and conversion helpers
3. One developer implements the transmission-delay math and report generation
4. One developer builds the topology/guard regression tests and Feature 026 preservation checks

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- This feature must not invent topology or claim paper-validity
- Unsupported controls must stay visibly unsupported
