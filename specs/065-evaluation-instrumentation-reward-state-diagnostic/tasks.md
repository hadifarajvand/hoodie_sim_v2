# Tasks: Feature 065 - Evaluation Instrumentation and Reward/State Diagnostic Repair

## Phase 1: Setup

- [ ] T001 Create the feature contract docs in `specs/065-evaluation-instrumentation-reward-state-diagnostic/`
- [ ] T002 Create the architecture note at `docs/architecture/euls_phase24_evaluation_instrumentation_reward_state_diagnostic.md`
- [ ] T003 Create the analysis package skeleton in `src/analysis/evaluation_instrumentation_reward_state_diagnostic/`

## Phase 2: Instrumentation Core

- [ ] T004 Implement the feature config and artifact-path contract in `src/analysis/evaluation_instrumentation_reward_state_diagnostic/config.py`
- [ ] T005 Implement the report and diagnostic dataclasses in `src/analysis/evaluation_instrumentation_reward_state_diagnostic/model.py`
- [ ] T006 Implement instrumented evaluation and training helpers in `src/analysis/evaluation_instrumentation_reward_state_diagnostic/instrumented_evaluator.py`
- [ ] T007 Implement diagnostic synthesis in `src/analysis/evaluation_instrumentation_reward_state_diagnostic/diagnostics.py`
- [ ] T008 Implement matplotlib-only diagnostic figures in `src/analysis/evaluation_instrumentation_reward_state_diagnostic/figures.py`
- [ ] T009 Implement the staged runner in `src/analysis/evaluation_instrumentation_reward_state_diagnostic/runner.py`
- [ ] T010 Implement JSON/Markdown writers in `src/analysis/evaluation_instrumentation_reward_state_diagnostic/report.py`

## Phase 3: Tests

- [ ] T011 Add schema and action-logging tests in `tests/unit/test_evaluation_instrumentation_reward_state_diagnostic_schema.py`
- [ ] T012 Add reward decomposition and state coverage tests in `tests/unit/test_evaluation_instrumentation_reward_state_diagnostic_reward_decomposition.py`
- [ ] T013 Add policy-effect and claim-safety tests in `tests/unit/test_evaluation_instrumentation_reward_state_diagnostic_claim_safety.py`
- [ ] T014 Add integration coverage for the instrumented rerun in `tests/integration/test_evaluation_instrumentation_reward_state_diagnostic.py`
- [ ] T015 Add report and scope-guard coverage in the remaining integration tests

## Phase 4: Validation

- [ ] T016 Run `py_compile`, the diagnostic runner, and the focused pytest selection
- [ ] T017 Verify `git diff --name-only 064-final-review-release-gate-batch...HEAD`, `git diff --stat`, `git diff --check`, and `git status --short --untracked-files=no`
