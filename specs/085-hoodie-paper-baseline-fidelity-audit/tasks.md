# Tasks — Feature 085 HOODIE Baseline Fidelity Audit and Formula Mapping

## Phase 1: Setup
- [ ] T001 Audit the current runtime evaluation outputs for stale `MQO` labels and document the required `MLEO` replacements.
- [ ] T002 Create the audit feature metadata pointer for the new feature directory.
- [ ] T003 Add the baseline-mapping matrix and formula-mapping matrix documents.

## Phase 2: Tests
- [ ] T004 Add unit tests proving the active policy set is exactly `HOODIE, RO, FLC, VO, HO, BCO, MLEO`.
- [ ] T005 Add unit tests proving `MQO` is rejected from active output coverage.
- [ ] T006 Add unit tests proving the formula mapping matrix includes the required formula rows.
- [ ] T007 Add integration tests proving the report and artifact bundle render `MLEO` in aggregate tables and rankings.

## Phase 3: Core
- [ ] T008 Update `src/analysis/hoodie_runtime_evaluation_runner/policies.py` to use `MLEO` as the canonical active baseline label.
- [ ] T009 Update `src/analysis/hoodie_runtime_evaluation_runner/config.py` to require the `MLEO` policy set and remove `MQO` from active coverage.
- [ ] T010 Update `src/analysis/hoodie_runtime_evaluation_runner/report.py` to render `MLEO` in policy coverage, baseline mapping, and metric tables.
- [ ] T011 Update `src/analysis/hoodie_runtime_evaluation_runner/runner.py` to validate the new policy set and block stale `MQO` outputs.
- [ ] T012 Update runtime model and metric coverage so the audit bundle records the correct policy names and formula references.

## Phase 4: Integration
- [ ] T013 Regenerate the audit artifact bundle under `artifacts/feature_085_full_audit/`.
- [ ] T014 Validate the audit bundle and report against the updated validation rules.

## Phase 5: Polish
- [ ] T015 Mark the spec checklist complete only after the audit bundle, report, and validation rules all pass.
- [ ] T016 Verify PR #24 remains blocked until the audit is complete.
