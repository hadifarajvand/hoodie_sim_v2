# Tasks: Feature 068

**Input**: Design artifacts from `specs/068-paper-baseline-policy-fidelity-batch/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `quickstart.md`
**Branch**: `068-paper-baseline-policy-fidelity-batch`

**Dependency gate**: Start from current `main`. Do not touch environment, training, artifacts, campaign outputs, or dependency files.

## Format: `[ID] [P?] [Story?] Description with file path`

- [P]: safe parallel task.
- [US1]: registry coverage.
- [US2]: action-mask compliance.
- [US3]: MLEO delay ranking.
- [US4]: controlled baseline differentiation.
- Tests must be written before implementation changes that make them pass.

## Phase 1: Setup and Scope Gates

- [X] T001 Verify branch starts from current `main` and no unrelated dirty files exist.
- [X] T002 Read `spec.md`, `plan.md`, `research.md`, `data-model.md`, `quickstart.md`, and `tasks.md`.
- [X] T003 Inspect `src/policies/policy_interface.py`.
- [X] T004 Inspect current baseline modules in `src/policies/`.
- [X] T005 Inspect `src/evaluation/policy_registry.py`.
- [X] T006 Decide whether `docs/paper_notes/paper_to_code_mapping.md` needs a mapping update; do not edit unless implementation changes mapping evidence.

## Phase 2: Foundational Test Contracts

- [X] T007 [P] [US1] Add registry coverage tests in `tests/unit/test_policy_registry.py` for RO, FLC, VO, HO, BCO, and MLEO.
- [X] T008 [P] [US2] Add baseline mask tests in `tests/unit/test_baseline_policy_fidelity.py`.
- [X] T009 [P] [US2] Add fallback tests in `tests/unit/test_baseline_policy_fidelity.py`.
- [X] T010 [P] [US2] Add seeded RO tests in `tests/unit/test_baseline_policy_fidelity.py`.
- [X] T011 [P] [US3] Add MLEO candidate extraction tests in `tests/unit/test_mleo_policy.py`.
- [X] T012 [P] [US3] Add MLEO candidate filtering tests in `tests/unit/test_mleo_policy.py`.
- [X] T013 [P] [US3] Add MLEO total-delay ranking tests in `tests/unit/test_mleo_policy.py`.
- [X] T014 [P] [US3] Add MLEO tie handling tests in `tests/unit/test_mleo_policy.py`.
- [X] T015 [P] [US3] Add MLEO missing-field fallback tests in `tests/unit/test_mleo_policy.py`.
- [X] T016 [P] [US4] Add shared-context integration tests in `tests/integration/test_baseline_policy_fidelity_flow.py`.

## Phase 3: User Story 1 - Registry Coverage

**Goal**: Every required paper baseline resolves from the shared policy registry.

**Independent Test**: Registry coverage tests pass without direct class shortcuts.

- [X] T017 [US1] Update `src/evaluation/policy_registry.py` so all required baselines are exposed under stable names.
- [X] T018 [US1] Preserve existing policy aliases already used by evaluation code.
- [X] T019 [US1] Keep unknown-policy errors explicit and useful.

## Phase 4: User Story 2 - Action-Mask Compliance

**Goal**: No baseline selects an unavailable action.

**Independent Test**: Mask-compliance tests pass for all baselines.

- [X] T020 [US2] Repair FLC in `src/policies/flc.py`.
- [X] T021 [US2] Repair VO in `src/policies/vo.py`.
- [X] T022 [US2] Repair HO in `src/policies/ho.py`.
- [X] T023 [US2] Repair RO in `src/policies/ro.py`.
- [X] T024 [US2] Repair BCO in `src/policies/bco.py`.
- [X] T025 [US2] Add helpers in `src/policies/common.py` only if needed.
- [X] T026 [US2] Ensure fallback paths are documented by tests.

## Phase 5: User Story 3 - MLEO Total-Delay Ranking

**Goal**: MLEO behaves like a minimum-latency estimate baseline.

**Independent Test**: MLEO tests pass for extraction, filtering, ranking, tie handling, and fallback.

- [X] T027 [US3] Define DelayCandidate behavior in `src/policies/mleo.py` or `src/policies/common.py`.
- [X] T028 [US3] Extract local candidate delay.
- [X] T029 [US3] Extract horizontal candidate delay.
- [X] T030 [US3] Extract vertical candidate delay.
- [X] T031 [US3] Remove unavailable candidates before ranking.
- [X] T032 [US3] Rank candidates by total estimated delay.
- [X] T033 [US3] Implement deterministic tie handling.
- [X] T034 [US3] Implement explicit fallback for incomplete candidate data.
- [X] T035 [US3] Expose enough metadata through tests to prove fallback behavior.

## Phase 6: User Story 4 - Controlled Differentiation

**Goal**: Show baseline families do not collapse into the same behavior under controlled inputs.

**Independent Test**: Integration tests show FLC, HO, VO, and MLEO can select different action families.

- [X] T036 [US4] Build shared controlled contexts in `tests/integration/test_baseline_policy_fidelity_flow.py`.
- [X] T037 [US4] Verify FLC, HO, VO, and MLEO can differ on shared contexts.
- [X] T038 [US4] Verify all baselines use the same context shape.
- [X] T039 [US4] Verify seeded behavior remains reproducible where randomness is involved.

## Phase 7: Validation and Scope Audit

- [X] T040 Run targeted unit tests.
- [X] T041 Run targeted integration tests.
- [X] T042 Run `git diff --name-only` and confirm no forbidden paths changed.
- [X] T043 Confirm dependency files are unchanged.
- [X] T044 Confirm generated artifacts and campaign outputs are unchanged.
- [X] T045 Record exact commands, results, changed files, and open risks in the PR body.

## Dependencies and Execution Order

- Setup gates block all other work.
- Test contracts precede behavior repair.
- Registry coverage precedes broad integration testing.
- MLEO ranking depends on candidate extraction.
- Scope audit runs after all implementation work.

## Parallel Opportunities

- T007 through T016 can run in parallel when test files are separate.
- T020 through T024 can run in parallel if each policy file is independent.
- T028 through T030 can run in parallel after candidate helpers are defined.

## MVP First

1. Complete setup gates.
2. Add registry coverage tests.
3. Expose all required baselines through the registry.
4. Validate that every required baseline resolves.

## Final Validation Command

```bash
/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest discover tests/unit
/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest discover tests/integration
```

If unavailable, use the project interpreter and record the exact commands.
