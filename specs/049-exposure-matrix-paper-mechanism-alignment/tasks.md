# Tasks: Exposure Matrix Rerun and Paper Mechanism Alignment

## Phase 1: Setup

- [ ] T001 Verify the current branch is `049-exposure-matrix-paper-mechanism-alignment`, the branch is not `main`, `main` matches `origin/main`, `main` matches `048-legality-evidence-expansion-complete^{}`, and the diff from `048-legality-evidence-expansion-complete^{}` to `main` is empty.
- [ ] T002 Verify SpecKit pointer is set to `specs/049-exposure-matrix-paper-mechanism-alignment` and is local-only by inspecting `git status --short`, `git diff --name-only`, `git diff --cached --name-only`, and `git diff --name-only main...HEAD`; classify a correctly pointed `.specify/feature.json` as allowed local-only, confirm it is not staged, is not in the `main...HEAD` diff, and is not included in any Feature 049 commit, while also confirming `AGENTS.md` is clean before report generation, `AGENTS.md` is not added to `.gitignore`, and there are no unrelated dirty files. If `.specify/feature.json` is staged or points to any feature other than 049, stop implementation; if the pointer must be changed, do not auto-restore it to HEAD during Feature 049 work because HEAD points to Feature 036.
- [ ] T003 Verify the Feature 049 spec, plan, research, data model, contracts, and quickstart artifacts are present under `specs/049-exposure-matrix-paper-mechanism-alignment/`.

## Phase 2: Foundational Gates

- [ ] T004 Verify committed artifacts exist for Feature 043 completion lifecycle audit.
- [ ] T005 Verify committed artifacts exist for Feature 044 passive lifecycle trace instrumentation.
- [ ] T006 Verify committed artifacts exist for Feature 045 completion root-cause diagnosis.
- [ ] T007 Verify committed artifacts exist for Feature 046 load/admission/action exposure review.
- [ ] T008 Verify committed artifacts exist for Feature 047 exposure matrix review.
- [ ] T009 Verify committed artifacts exist for Feature 048 legality evidence expansion.
- [ ] T010 Verify the validation command excludes dirty-worktree-sensitive older report tests and relies on committed-artifact checks for Features 043 through 048.

## Phase 3: User Story 1 - Rerun Exposure Matrix With Legality Evidence

### Story Goal

Rerun the exposure matrix using Feature 048 legality evidence and summarize legal-vs-selected action exposure before training is attempted.

### Independent Test Criteria

This story is independently testable when the report can show a legality-backed exposure rerun, per-strategy/per-seed/per-action summaries, and exposure bias findings without starting training.

- [ ] T011 [US1] Define `ExposureMatrixRerunSummary` and `LegalVsSelectedActionMatrix` in `src/analysis/exposure_matrix_paper_mechanism_alignment/model.py` to capture exposure completeness, legal availability, selected actions, and outcome summaries.
- [ ] T012 [P] [US1] Define `ExposureMatrixPaperMechanismConfig` and rerun inputs in `src/analysis/exposure_matrix_paper_mechanism_alignment/config.py` so the rerun consumes Feature 048 legality evidence and committed Feature 047 baseline artifacts.
- [ ] T013 [US1] Implement the exposure-matrix rerun analysis path in `src/analysis/exposure_matrix_paper_mechanism_alignment/runner.py` to compute decision-opportunity counts, legal counts, selected counts, illegal counts, legal-but-unselected counts, and per-action outcome rates.
- [ ] T014 [US1] Implement exposure bias summarization in `src/analysis/exposure_matrix_paper_mechanism_alignment/runner.py` so the report can distinguish readiness from exposure-dominant blocking conditions.
- [ ] T015 [US1] Add schema tests in `tests/unit/test_exposure_matrix_paper_mechanism_schema.py` for the rerun summary, legal-vs-selected matrix, per-strategy/per-seed matrix, and per-action outcome matrix fields.
- [ ] T016 [US1] Add metrics tests in `tests/unit/test_exposure_matrix_paper_mechanism_metrics.py` that verify `selected_illegal_action_count` is derived from legality evidence, fake zero legal counts are rejected, and exposure bias is reported without using representative samples as aggregate proof.
- [ ] T017 [US1] Add exposure-count consistency tests in `tests/unit/test_exposure_matrix_paper_mechanism_metrics.py` that fail unless `selected_action_count = selected_local_count + selected_horizontal_count + selected_vertical_count`, `selected_illegal_action_count <= selected_action_count`, `legal_but_unselected_by_action` is consistent with legal and selected counts, and no legal-but-unselected count is negative.
- [ ] T018 [US1] Add selected-action family evidence handling in `src/analysis/exposure_matrix_paper_mechanism_alignment/runner.py` so unavailable selected action family counts set `selected_action_family_evidence_status = unavailable`, `final_verdict = insufficient_legality_or_trace_evidence`, and `recommended_next_feature = selected-action family evidence expansion before training` without inventing action-family counts.
- [ ] T019 [US1] Add per-action outcome evidence handling in `src/analysis/exposure_matrix_paper_mechanism_alignment/runner.py` so completion/drop/pending rates are derived only from joinable selected action family outcomes, otherwise `per_action_outcome_evidence_status = unavailable` and `final_verdict = insufficient_legality_or_trace_evidence`.
- [ ] T020 [US1] Add hardcoded-placeholder rejection tests in `tests/unit/test_exposure_matrix_paper_mechanism_metrics.py` that fail if the runner hardcodes `selected_local_count = 0`, `selected_horizontal_count = 0`, `selected_vertical_count = 0`, all-zero `legal_but_unselected_by_action`, or all-zero per-action completion/drop/pending rates without evidence status explaining availability.

## Phase 4: User Story 2 - Audit Paper HOODIE Mechanism

### Story Goal

Audit the current simulator/network interface against the paper HOODIE mechanism and identify observation-vector or formula/unit gaps before training is attempted.

### Independent Test Criteria

This story is independently testable when the report can explain which observation components are present or missing and whether the paper timing/state formulas pass or fail, without requiring a training run.

- [ ] T021 [P] [US2] Define `ObservationVectorAudit` and `PaperFormulaUnitAudit` in `src/analysis/exposure_matrix_paper_mechanism_alignment/model.py` with fields for required state components, timing checks, terminal-state checks, and contradiction notes.
- [ ] T022 [US2] Implement the observation vector audit in `src/analysis/exposure_matrix_paper_mechanism_alignment/runner.py` to compare the current simulator/network interface against the paper HOODIE mechanism for state visibility and action context.
- [ ] T023 [US2] Implement the formula/unit audit in `src/analysis/exposure_matrix_paper_mechanism_alignment/runner.py` to verify local compute time, transmission delays, queue wait, task age, deadline expiry, delayed reward timing, and terminal/pending semantics.
- [ ] T024 [US2] Add schema tests in `tests/unit/test_exposure_matrix_paper_mechanism_schema.py` for the observation vector audit and paper formula/unit audit report sections.
- [ ] T025 [US2] Add integration tests in `tests/integration/test_exposure_matrix_paper_mechanism_alignment.py` that validate the observation audit and formula audit against the committed Feature 043 through 048 artifacts.
- [ ] T026 [US2] Add scope-guard tests in `tests/integration/test_exposure_matrix_paper_mechanism_scope_guard.py` that reject runtime semantic changes, `src/policies/` changes, dependency changes, training, optimizer, replay training, target update, checkpoints, fake evidence, curve fitting, and paper reproduction claims.

## Phase 5: User Story 3 - Decide Training Readiness

### Story Goal

Produce a final readiness decision that routes to the next training-contract bundle only when the exposure rerun and paper-mechanism audits are clean enough.

### Independent Test Criteria

This story is independently testable when the report emits a final verdict and next-feature recommendation that matches the exposure rerun and audit results, without starting any training work.

- [ ] T027 [P] [US3] Define `TrainingReadinessDecision` and the final report schema in `src/analysis/exposure_matrix_paper_mechanism_alignment/model.py` so verdict routing and next-feature recommendations are explicit and machine-readable.
- [ ] T028 [US3] Implement report writers in `src/analysis/exposure_matrix_paper_mechanism_alignment/report.py` for `artifacts/analysis/exposure-matrix-paper-mechanism-alignment/exposure-matrix-paper-mechanism-report.json` and `.md`.
- [ ] T029 [US3] Implement readiness routing in `src/analysis/exposure_matrix_paper_mechanism_alignment/runner.py` so the final verdict resolves to readiness, observation-vector gap, formula/unit gap, exposure bias, runtime semantic contradiction, insufficient evidence, or prerequisite blocked.
- [ ] T030 [US3] Add integration tests in `tests/integration/test_exposure_matrix_paper_mechanism_report.py` that validate the committed-artifact Feature 047 and Feature 048 prerequisites, the final verdict, the recommended next feature, and the no-training/no-drift flags.
- [ ] T031 [US3] Add metrics tests in `tests/unit/test_exposure_matrix_paper_mechanism_metrics.py` that verify readiness routing consistency across exposure completeness, observation audit results, formula audit results, exposure bias outcomes, selected action family evidence status, per-action outcome evidence status, and exposure matrix internal consistency.
- [ ] T032 [US3] Add end-to-end tests in `tests/integration/test_exposure_matrix_paper_mechanism_alignment.py` that ensure the report recommends `Feature 050 — DDQN Training Contract Bundle` only when `exposure_matrix_internal_consistency_verified = true`, `selected_action_family_evidence_status = available`, `per_action_outcome_evidence_status = available`, the observation vector audit passes, and the formula/unit audit passes.

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T033 [P] Update `specs/049-exposure-matrix-paper-mechanism-alignment/quickstart.md` with the corrected Feature 049 validation command that excludes dirty-worktree-sensitive older report tests and uses committed-artifact checks for Features 043 through 048.
- [ ] T034 [P] Update `specs/049-exposure-matrix-paper-mechanism-alignment/spec.md` or `plan.md` only if any report field names, verdict names, or validation rules need alignment after implementation.
- [ ] T035 Run the approved Feature 049 validation command and confirm the Feature 049 tests pass without modifying any forbidden paths or runtime semantics.
- [ ] T036 Mark the Feature 049 tasks complete only after the report artifacts are regenerated, the tests pass, the scope guard confirms no unrelated files changed, `.specify/feature.json` remains local-only and unstaged, the readiness decision is consistent with the audits, and Feature 050 is not recommended unless all exposure consistency and evidence-status gates pass.

## Dependencies

- T001-T003 must complete before any implementation work.
- T004-T010 must complete before the user-story work starts.
- T011-T020 support User Story 1.
- T021-T026 support User Story 2.
- T027-T032 support User Story 3.
- T033-T036 are final validation and cleanup after implementation.

## Parallel Execution Examples

- User Story 1: T012 can run in parallel with T011; T015, T016, T017, and T020 can run in parallel after T011/T013 are available.
- User Story 2: T021 can run in parallel with T022/T023; T024, T025, and T026 can proceed independently once the model/runner shape is settled.
- User Story 3: T027 can run in parallel with T028; T030, T031, and T032 can proceed after the runner/report contract is defined.

## Implementation Strategy

### MVP First

Deliver User Story 1 first: legality-evidence rerun plus exposure summaries. This establishes the evidence base for the rest of the feature.

### Incremental Delivery

Add the paper mechanism audits second, then add the readiness decision and report writers, and finish with validation and quickstart cleanup.
