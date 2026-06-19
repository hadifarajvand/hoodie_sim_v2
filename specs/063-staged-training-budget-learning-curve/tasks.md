# Tasks: Feature 063 - Staged Training Budget Learning Curve and Comparison Analysis

## Phase 1: Setup (Shared Infrastructure)

- [ ] T001 [P] Create the feature contract docs in `specs/063-staged-training-budget-learning-curve/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `quickstart.md`)
- [ ] T002 [P] Create the architecture note at `docs/architecture/euls_phase22_staged_training_budget_learning_curve.md`
- [ ] T003 [P] Create the analysis package skeleton in `src/analysis/staged_training_budget_learning_curve/` (`__init__.py`, `config.py`, `model.py`, `report.py`, `figures.py`, `runner.py`)

## Phase 2: Foundational (Blocking Prerequisites)

- [ ] T004 Implement the feature config and artifact path contract in `src/analysis/staged_training_budget_learning_curve/config.py`
- [ ] T005 Implement checkpoint, readiness, figure-manifest, claim-safety, and report dataclasses in `src/analysis/staged_training_budget_learning_curve/model.py`
- [ ] T006 Implement JSON/Markdown writers for the report and findings in `src/analysis/staged_training_budget_learning_curve/report.py`
- [ ] T007 Implement matplotlib-only figure generation in `src/analysis/staged_training_budget_learning_curve/figures.py`

## Phase 3: User Story 1 - Cumulative staged training sweep (Priority: P1)

**Goal**: Continue one trainer instance across the staged budgets and capture checkpoint metrics.

**Independent Test**: A mocked trainer sweep still produces four cumulative checkpoints with budgets `[100, 150, 200, 500]` and no 5000-episode run.

### Tests for User Story 1

- [ ] T008 [P] [US1] Add schema and checkpoint-budget tests in `tests/unit/test_staged_training_budget_learning_curve_schema.py`
- [ ] T009 [P] [US1] Add checkpoint metric accounting tests in `tests/unit/test_staged_training_budget_learning_curve_metrics.py`
- [ ] T010 [P] [US1] Add integration coverage for the staged sweep in `tests/integration/test_staged_training_budget_learning_curve.py`

### Implementation for User Story 1

- [ ] T011 [US1] Implement cumulative staged training orchestration in `src/analysis/staged_training_budget_learning_curve/runner.py`
- [ ] T012 [US1] Implement checkpoint metric extraction and cumulative replay/loss summaries in `src/analysis/staged_training_budget_learning_curve/runner.py`
- [ ] T013 [US1] Materialize `artifacts/analysis/staged-training-budget-learning-curve/checkpoint-metrics.json`
- [ ] T014 [US1] Materialize `artifacts/analysis/staged-training-budget-learning-curve/comparison-readiness.json`

## Phase 4: User Story 2 - Comparison analysis and reporting (Priority: P2)

**Goal**: Reuse the baseline reference once, generate figures, comparison tables, findings, and claim-safety checks.

**Independent Test**: A mocked execution still writes the report, findings, figure manifest, and required PNG figures.

### Tests for User Story 2

- [ ] T015 [P] [US2] Add claim-safety tests in `tests/unit/test_staged_training_budget_learning_curve_claim_safety.py`
- [ ] T016 [P] [US2] Add report generation tests in `tests/integration/test_staged_training_budget_learning_curve_report.py`
- [ ] T017 [P] [US2] Add scope-guard tests in `tests/integration/test_staged_training_budget_learning_curve_scope_guard.py`

### Implementation for User Story 2

- [ ] T018 [US2] Reuse the Feature 060 baseline reference summary and build the staged comparative table in `src/analysis/staged_training_budget_learning_curve/runner.py`
- [ ] T019 [US2] Generate the five required matplotlib figures and write `artifacts/analysis/staged-training-budget-learning-curve/figure-manifest.json`
- [ ] T020 [US2] Generate `artifacts/analysis/staged-training-budget-learning-curve/staged-training-budget-learning-curve-report.json` and `.md`
- [ ] T021 [US2] Generate `artifacts/analysis/staged-training-budget-learning-curve/staged-findings.md`

## Phase 5: Polish & Cross-Cutting Concerns

- [ ] T022 Run `py_compile`, the staged-training-budget-learning-curve feature command, and the focused pytest selection
- [ ] T023 Verify `git diff --name-only 062-unified-campaign-result-analysis-figures-findings...HEAD`, `git diff --stat`, `git diff --check`, and `git status --short --untracked-files=no`
- [ ] T024 Commit and push only approved Feature 063 paths after validation passes

## Dependencies & Execution Order

- Phase 1 and Phase 2 must complete before either user story begins.
- US1 is the prerequisite for the staged comparison artifacts because the figures and findings depend on real checkpoint metrics.
- US2 may reuse the completed US1 checkpoint data and baseline reference summary.

## Implementation Strategy

### MVP First

1. Complete the package skeleton and config/model/report/figure scaffolding.
2. Implement the cumulative staged sweep and verify the four checkpoints.
3. Add the comparison reporting and figure generation.
4. Run the focused tests and verify the scope guard.
