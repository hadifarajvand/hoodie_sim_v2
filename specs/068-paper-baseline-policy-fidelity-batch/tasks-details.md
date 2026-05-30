# Task Details: Feature 068

## Phase 1 Setup

- T001 Read `spec.md`, `spec-details.md`, `plan.md`, `plan-details.md`, `research.md`, `data-model.md`, `quickstart.md`, and `tasks.md`.
- T002 Inspect `src/policies/policy_interface.py` and identify the PolicyContext contract.
- T003 Inspect current baseline policy files.
- T004 Inspect `src/evaluation/policy_registry.py`.

## Phase 2 Tests first

- T005 Add registry coverage tests for RO, FLC, VO, HO, BCO, and MLEO.
- T006 Add action-mask tests for every baseline.
- T007 Add deterministic behavior tests for FLC, VO, HO, BCO, and MLEO fallback cases.
- T008 Add seeded RO tests.
- T009 Add MLEO candidate ranking tests.
- T010 Add MLEO missing-field fallback tests.
- T011 Add integration flow tests with shared contexts.

## Phase 3 Baseline repair

- T012 Repair FLC preference and fallback behavior.
- T013 Repair VO preference and fallback behavior.
- T014 Repair HO preference and fallback behavior.
- T015 Repair RO seeded sampling from allowed actions.
- T016 Repair BCO balancing behavior.
- T017 Add common helpers only when they reduce duplication without changing public interfaces.

## Phase 4 MLEO repair

- T018 Define candidate extraction from observation fields.
- T019 Compute local candidate delay.
- T020 Compute horizontal candidate delay.
- T021 Compute vertical candidate delay.
- T022 Remove unavailable candidates before ranking.
- T023 Rank by total delay.
- T024 Handle ties deterministically.
- T025 Record or expose fallback behavior for incomplete fields.

## Phase 5 Validation

- T026 Run targeted unit tests.
- T027 Run targeted integration tests.
- T028 Audit changed files.
- T029 Confirm no forbidden paths changed.
- T030 Report commands, results, and risks.

## MVP

Registry coverage, mask compliance, and MLEO minimum-delay selection under controlled inputs.
