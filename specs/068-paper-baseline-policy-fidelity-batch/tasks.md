# Tasks: Feature 068

Input: `specs/068-paper-baseline-policy-fidelity-batch/`

Tests are required before behavior changes.

## Phase 1: Setup

- [ ] T001 Review `specs/068-paper-baseline-policy-fidelity-batch/spec.md`
- [ ] T002 Review `specs/068-paper-baseline-policy-fidelity-batch/plan.md`
- [ ] T003 Inspect `src/policies/`
- [ ] T004 Inspect `src/evaluation/policy_registry.py`

## Phase 2: Tests

- [ ] T005 Add registry coverage tests in `tests/unit/test_policy_registry.py`
- [ ] T006 Add baseline legality tests in `tests/unit/test_baseline_policy_fidelity.py`
- [ ] T007 Add MLEO ranking tests in `tests/unit/test_mleo_policy.py`
- [ ] T008 Add MLEO fallback tests in `tests/unit/test_mleo_policy.py`
- [ ] T009 Add shared interface tests in `tests/integration/test_baseline_policy_fidelity_flow.py`

## Phase 3: Baseline Policies

- [ ] T010 Complete FLC behavior in `src/policies/flc.py`
- [ ] T011 Complete VO behavior in `src/policies/vo.py`
- [ ] T012 Complete HO behavior in `src/policies/ho.py`
- [ ] T013 Complete RO behavior in `src/policies/ro.py`
- [ ] T014 Complete BCO behavior in `src/policies/bco.py`
- [ ] T015 Complete helpers in `src/policies/common.py`

## Phase 4: MLEO

- [ ] T016 Add delay candidate extraction in `src/policies/mleo.py`
- [ ] T017 Exclude illegal MLEO candidates in `src/policies/mleo.py`
- [ ] T018 Rank MLEO candidates by total delay in `src/policies/mleo.py`
- [ ] T019 Add explicit MLEO fallback behavior in `src/policies/mleo.py`

## Phase 5: Validation

- [ ] T020 Confirm required baselines resolve in `src/evaluation/policy_registry.py`
- [ ] T021 Run targeted unit tests
- [ ] T022 Run targeted integration tests
- [ ] T023 Audit changed files
- [ ] T024 Record commands and open risks in the PR body

## MVP

Registry coverage, legal-action compliance, and MLEO minimum-delay selection under controlled observations.
