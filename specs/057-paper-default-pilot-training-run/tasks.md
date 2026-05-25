# Tasks: Feature 057 — Paper-Default Pilot Training Run

## A. Prerequisite gates

- [ ] T001 Verify `main` contains `056-target-update-replay-training-validation-complete`.
- [ ] T002 Verify branch is not `main` and is based on current `main`.
- [ ] T003 Verify Feature 056 report is committed and has `final_verdict = target_update_replay_validation_passed`.
- [ ] T004 Verify Feature 056 report has `remaining_blockers = []`, replay validation passed, optimizer counter validation passed, target update contract validation passed, and checkpoint metadata validation passed.

## B. Model and schema

- [ ] T005 Create `src/analysis/paper_default_pilot_training_run/config.py`.
- [ ] T006 Create `src/analysis/paper_default_pilot_training_run/model.py` with the required report dataclass and fields.
- [ ] T007 Create `src/analysis/paper_default_pilot_training_run/report.py` for JSON and Markdown outputs.
- [ ] T008 Create `src/analysis/paper_default_pilot_training_run/runner.py`.
- [ ] T009 Create `src/analysis/paper_default_pilot_training_run/__init__.py` and `__main__.py`.

## C. Pilot execution and metrics

- [ ] T010 Run controlled paper-default pilot training with more episodes than Feature 055 smoke and less than full-campaign scale.
- [ ] T011 Validate live environment training is used and fixture-only training is not used.
- [ ] T012 Validate replay grows beyond Feature 055 smoke replay size.
- [ ] T013 Validate optimizer steps grow beyond Feature 055 smoke optimizer count.
- [ ] T014 Validate losses are finite across the pilot run.
- [ ] T015 Validate delayed reward contract remains preserved.
- [ ] T016 Validate selected actions are legal.
- [ ] T017 Validate train/eval trace-bank separation is preserved.
- [ ] T018 Validate checkpoint metadata schema is valid and metadata-only unless explicitly scoped otherwise.

## D. Safety gates

- [ ] T019 Validate no full campaign is run.
- [ ] T020 Validate no baseline comparison is run.
- [ ] T021 Validate no paper reproduction or performance claim is made.
- [ ] T022 Validate no policy, dependency, environment semantic, or reward timing drift appears.
- [ ] T023 Validate no Feature 037–056 artifacts are rewritten.

## E. Tests

- [ ] T024 Add `tests/unit/test_paper_default_pilot_training_run_schema.py`.
- [ ] T025 Add `tests/unit/test_paper_default_pilot_training_run_metrics.py`.
- [ ] T026 Add `tests/unit/test_paper_default_pilot_training_run_behavior_equivalence.py`.
- [ ] T027 Add `tests/integration/test_paper_default_pilot_training_run.py`.
- [ ] T028 Add `tests/integration/test_paper_default_pilot_training_run_report.py`.
- [ ] T029 Add `tests/integration/test_paper_default_pilot_training_run_scope_guard.py`.

## F. Report generation and final gate

- [ ] T030 Generate JSON and Markdown reports under `artifacts/analysis/paper-default-pilot-training-run/`.
- [ ] T031 Final verdict must be `paper_default_pilot_training_passed` only when all validation gates pass and blockers are empty.
- [ ] T032 Recommended next feature must be `Feature 058 — Evaluation Trace Bank and Baseline Evaluation Harness` only on passing verdict.

## Validation Handoff and Remote Audit Packet

- [ ] T033 Print local test output, Codex validation output, or CI result URL.
- [ ] T034 Print generated report proof fields from the JSON artifact.
- [ ] T035 Print `git status --short`.
- [ ] T036 Print `git diff --name-only main...HEAD`.
- [ ] T037 Print `git diff --stat main...HEAD`.
- [ ] T038 Print `git diff --cached --name-only`.
- [ ] T039 If auto-commit is used, print staged path list and verify only approved Feature 057 paths are staged.
- [ ] T040 If auto-push is used, print commit SHA, branch name, pushed remote ref, final verdict, recommended next feature, and final `git status --short`.
