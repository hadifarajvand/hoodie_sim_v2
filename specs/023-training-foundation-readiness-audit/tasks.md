# Tasks: HOODIE Training Foundation Readiness Audit

**Input**: Design documents from `/specs/023-training-foundation-readiness-audit/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md  
**Tests**: Required. This feature is a scientific readiness audit and must be driven by tests before implementation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Lock down branch hygiene and forbidden-path guardrails before any audit code is written.

- [X] T001 Add the branch hygiene and scope-guard integration test in `tests/integration/test_hoodie_training_foundation_readiness_audit_scope_guard.py` to reject changes to `src/environment`, `src/policies`, `src/training`, `src/metrics`, dependency files, lockfiles, existing campaign artifacts, plots, TorchRL, Gymnasium, ns-3, ns-3-gym, and policy behavior

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Prove the source gates, readiness dimensions, and blocked-readiness verdict rules are valid before implementation begins.

- [X] T002 [US1] Add source-gate validation tests in `tests/unit/test_hoodie_training_foundation_readiness_audit.py` for the HOODIE paper OCR at `resources/papers/hoodie/ocr/merged.tex`, mechanism registry, differential audit, mechanism repair summary, controlled sweeps, baseline fairness rebuild, and baseline rebuild sensitivity audit artifacts
- [X] T003 [US1] Add readiness-dimension definition tests in `tests/unit/test_hoodie_training_foundation_readiness_audit.py` for state representation, action-space legality, delayed reward timing, episode protocol, replay/log artifact requirements, and reproducibility requirements
- [X] T004 [US2] Add mechanism-gap tests in `tests/unit/test_hoodie_training_foundation_readiness_audit.py` for DQN, Double-DQN, Dueling-DQN, and LSTM paper mechanism readiness gaps
- [X] T005 [US1] Add verdict-taxonomy tests in `tests/unit/test_hoodie_training_foundation_readiness_audit.py` for blocked readiness and inconclusive evidence handling, with no partial-readiness path
- [X] T006 [US1] Add report-schema tests in `tests/unit/test_hoodie_training_foundation_readiness_audit.py` for metadata, source gate status, readiness dimensions, included source artifacts, mechanism gaps, blockers, verdict, limitations, disclaimers, and reproducibility details
- [X] T007 [US3] Add no-training and no-policy-redesign disclaimer tests in `tests/unit/test_hoodie_training_foundation_readiness_audit.py` to ensure the audit never claims a training loop, policy redesign, metric change, or environment change
- [X] T008 [US1] Add input-loading tests in `tests/unit/test_hoodie_training_foundation_readiness_audit.py` to confirm the audit reads the approved artifact set from the current repository and fails closed on missing or inconsistent inputs
- [X] T009 [US1] Add constitution-required integration coverage in `tests/integration/test_hoodie_training_foundation_readiness_audit_flow.py` that runs the readiness audit through the shared `HoodieGymEnvironment` interface using at least one existing baseline policy path and one test-local learned-policy placeholder/stub, with no real training, no neural network, no TorchRL, no Gymnasium, no ns-3, and no ns-3-gym
- [X] T010 [US1] Add a dedicated readiness-dimension blocker test in `tests/unit/test_hoodie_training_foundation_readiness_audit.py` that asserts training/evaluation separation is a first-class blocker condition, not merely a report-string phrase
- [X] T011 [US1] Add OCR evidence-gate tests in `tests/unit/test_hoodie_training_foundation_readiness_audit.py` and, if needed, `specs/023-training-foundation-readiness-audit/spec.md` / `specs/023-training-foundation-readiness-audit/plan.md` to pin `resources/papers/hoodie/ocr/merged.tex` and require minimum recoverable evidence for distributed DRL agents, state/input features, LSTM/load forecasting, Double/Dueling DQN, single-step offloading, reward/latency/drop objective, and training/evaluation protocol evidence

**Checkpoint**: Gate validation, readiness semantics, verdict taxonomy, constitution-required integration coverage, and no-training boundaries are covered before implementation begins.

---

## Phase 3: User Story 1 - Training Readiness Gap Audit (Priority: P1) 🎯 MVP

**Goal**: Determine whether the project is blocked or ready for future DRL training work based on paper-faithful readiness checks.

**Independent Test**: The audit runs deterministically from the same inputs and produces the same blocked-readiness verdict on repeated runs unless every required readiness dimension is supported.

### Implementation for User Story 1

- [X] T012 [US1] Create the isolated audit package scaffold in `src/analysis/hoodie_training_foundation_readiness_audit/__init__.py`
- [X] T013 [US1] Implement the source-gate loader and hard-fail validation helpers in `src/analysis/hoodie_training_foundation_readiness_audit/gates.py`
- [X] T014 [US1] Implement the readiness-dimension model and blocked-readiness verdict helpers in `src/analysis/hoodie_training_foundation_readiness_audit/readiness.py`
- [X] T015 [US1] Implement the tiny deterministic audit runner in `src/analysis/hoodie_training_foundation_readiness_audit/runner.py`
- [X] T016 [US1] Implement the deterministic JSON and Markdown report writer in `src/analysis/hoodie_training_foundation_readiness_audit/report.py`

### Validation for User Story 1

- [X] T017 [US1] Add the integration test in `tests/integration/test_hoodie_training_foundation_readiness_audit_flow.py` that runs the tiny deterministic readiness audit and writes the JSON and Markdown artifacts to a temporary path
- [X] T018 [US1] Add the final diff and scope audit in `tests/integration/test_hoodie_training_foundation_readiness_audit_final_diff.py` to verify no forbidden source paths, dependency files, campaign artifacts, plots, metric files, simulator changes, or policy changes are introduced

**Checkpoint**: The audit runs deterministically, fails closed on incomplete evidence, and stays within diagnostic-only scope.

---

## Phase 4: User Story 2 - Paper Mechanism Readiness Gaps (Priority: P2)

**Goal**: Ensure the report clearly identifies DQN-family and LSTM mechanism gaps and keeps training/evaluation separation visible.

**Independent Test**: The report contains mechanism-gap sections and preserves the distinction between paper readiness and training implementation.

### Implementation for User Story 2

- [X] T019 [US2] Extend `src/analysis/hoodie_training_foundation_readiness_audit/readiness.py` with explicit mechanism-gap classification for DQN, Double-DQN, Dueling-DQN, and LSTM readiness
- [X] T020 [US2] Extend `src/analysis/hoodie_training_foundation_readiness_audit/report.py` and `tests/unit/test_hoodie_training_foundation_readiness_audit.py` to render and verify mechanism-gap summaries and training/evaluation separation text

**Checkpoint**: The report exposes mechanism readiness gaps without becoming a training plan.

---

## Phase 5: User Story 3 - Preserve No-Training Boundaries (Priority: P3)

**Goal**: Ensure the feature stays diagnostic only and does not drift into training implementation, environment redesign, or metric changes.

**Independent Test**: The report and task graph clearly state that blocked readiness is the correct outcome when any prerequisite remains unsupported.

### Validation for User Story 3

- [X] T021 [US3] Add quick validation guidance in `specs/023-training-foundation-readiness-audit/quickstart.md` with the exact approved interpreter, input artifact list, and output artifact paths
- [X] T022 [US3] Add the scope-framing and limitation language in `specs/023-training-foundation-readiness-audit/research.md` so the feature remains diagnostic-only and does not claim paper-validity or training readiness approval

**Checkpoint**: The report and documentation clearly state the feature is a gate, not a training implementation.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1**: No dependencies. Establish the scope guard first.
- **Phase 2**: Depends on Phase 1. Gate validation, readiness semantics, and no-training boundaries must exist before implementation.
- **Phase 3**: Depends on Phase 2. The audit can start only after the readiness dimensions and verdict rules are in place.
- **Phase 4**: Depends on Phase 3. The mechanism-gap presentation is validated after the audit workflow exists.
- **Phase 5**: Depends on Phase 4. The diagnostic framing is validated after the core audit and report exist.

### Task Dependencies

- `T001` must complete before any implementation work begins.
- `T002`, `T003`, `T004`, `T005`, `T006`, `T007`, `T008`, `T010`, and `T011` must be written before `T012`.
- `T009` must complete before `T012`, `T013`, `T014`, `T015`, `T016`, `T017`, `T018`, `T019`, `T020`, `T021`, and `T022`.
- `T017` must complete before `T018`.
- `T019` and `T020` may be developed after the runner and report scaffold exist.
- `T021` and `T022` must complete before final signoff.

### Within the User Story

- Tests first, then the isolated analysis/audit package implementation.
- Deterministic report writing follows the runner and verdict logic.
- Documentation and final diff audit happen after the core audit workflow exists.

## Parallel Opportunities

- None are marked here to avoid fake parallelism. The task list is intentionally serialized around the single diagnostic workflow.

## Implementation Strategy

### MVP First

1. Complete `T001` to lock the scope guard and branch hygiene.
2. Complete `T002`-`T011` so the source gates, readiness dimensions, verdict rules, constitution-required integration coverage, and no-training boundaries are covered before implementation.
3. Complete `T012`-`T016` to build the isolated audit workflow.
4. Complete `T017`-`T022` to validate output, scope, and diagnostic framing.

### Incremental Delivery

1. Add the gate and verdict tests first.
2. Implement the audit runner and report writer second.
3. Verify the output artifacts third.
4. Tighten the report language and scope guard last.

## Notes

- The feature is diagnostic analysis only.
- No campaign-scale reproduction is allowed.
- No plots are introduced.
- No simulator or environment behavior changes are allowed.
- No policy redesign, new training loops, or metric changes are permitted.
- No paper-level validity claim is permitted.

## Acceptance Mapping

- `Source gate requirement` is satisfied by `T002` and `T011` because they validate the prior credibility artifacts and pin the HOODIE OCR source gate before running the audit.
- `Readiness semantics requirement` is satisfied by `T003`, `T005`, and `T010` because they define the readiness dimensions, blocked-only verdict rules, and first-class training/evaluation separation blocker condition.
- `Mechanism-gap requirement` is satisfied by `T004` and `T019` because they surface DQN-family and LSTM readiness gaps.
- `No-training boundary requirement` is satisfied by `T007`, `T018`, `T021`, and `T022` because they prohibit training claims and require diagnostic-only framing.
- `Output requirement` is satisfied by `T006`, `T016`, and `T017` because they require deterministic JSON and Markdown artifacts and integration validation.
