# Tasks: Feature 060 — Full Paper-Default Training Campaign Execution

## A. Prerequisite gates

- [ ] T001 Verify `main` contains Feature 059 merge evidence.
- [ ] T002 Verify branch is not `main` and is based on current `main`.
- [ ] T003 Verify Feature 059 report is committed and has `final_verdict = full_paper_default_training_campaign_gate_ready`.
- [ ] T004 Verify Feature 059 report has `remaining_blockers = []`, campaign scope complete, resource controls complete, checkpoint contract complete, metric collection contract complete, and no execution occurred in Feature 059.

## B. Model and schema

- [ ] T005 Create `src/analysis/full_paper_default_training_campaign_execution/config.py`.
- [ ] T006 Create `src/analysis/full_paper_default_training_campaign_execution/model.py` with required report dataclass and fields.
- [ ] T007 Create `src/analysis/full_paper_default_training_campaign_execution/report.py` for JSON and Markdown outputs.
- [ ] T008 Create `src/analysis/full_paper_default_training_campaign_execution/runner.py`.
- [ ] T009 Create `src/analysis/full_paper_default_training_campaign_execution/__init__.py` and `__main__.py`.

## C. Campaign execution and artifacts

- [ ] T010 Execute controlled paper-default training campaign within Feature 059 resource controls.
- [ ] T011 Generate training metrics artifact.
- [ ] T012 Generate evaluation metrics artifact using Feature 058 evaluation trace bank.
- [ ] T013 Generate baseline evaluation metrics artifact using Feature 058 baseline registry/harness contract.
- [ ] T014 Generate checkpoint metadata artifact.
- [ ] T015 Generate run manifest artifact listing all required outputs.
- [ ] T016 Validate all required artifacts exist and are internally consistent.

## D. Safety gates

- [ ] T017 Validate no paper reproduction claim is made.
- [ ] T018 Validate no performance superiority or baseline superiority claim is made.
- [ ] T019 Validate no uncontrolled campaign loop exists.
- [ ] T020 Validate no policy, dependency, environment semantic, or reward timing drift occurs.
- [ ] T021 Validate no Feature 037–059 artifacts are rewritten.

## E. Tests

- [ ] T022 Add `tests/unit/test_full_paper_default_training_campaign_execution_schema.py`.
- [ ] T023 Add `tests/unit/test_full_paper_default_training_campaign_execution_metrics.py`.
- [ ] T024 Add `tests/unit/test_full_paper_default_training_campaign_execution_behavior_equivalence.py`.
- [ ] T025 Add `tests/integration/test_full_paper_default_training_campaign_execution.py`.
- [ ] T026 Add `tests/integration/test_full_paper_default_training_campaign_execution_report.py`.
- [ ] T027 Add `tests/integration/test_full_paper_default_training_campaign_execution_scope_guard.py`.

## F. Report generation and final gate

- [ ] T028 Generate JSON and Markdown reports under `artifacts/analysis/full-paper-default-training-campaign-execution/`.
- [ ] T029 Final verdict must be `full_paper_default_training_campaign_execution_passed` only when all validation gates pass and blockers are empty.
- [ ] T030 Recommended next feature must be `Feature 061 — Campaign Result Integrity and Comparison Readiness Audit` only on passing verdict.

## Validation Handoff and Remote Audit Packet

- [ ] T031 Print local test output, Codex validation output, or CI result URL.
- [ ] T032 Print generated report proof fields from the JSON artifact.
- [ ] T033 Print `git status --short`.
- [ ] T034 Print `git diff --name-only main...HEAD`.
- [ ] T035 Print `git diff --stat main...HEAD`.
- [ ] T036 Print `git diff --cached --name-only`.
- [ ] T037 If auto-commit is used, print staged path list and verify only approved Feature 060 paths are staged.
- [ ] T038 If auto-push is used, print commit SHA, branch name, pushed remote ref, final verdict, recommended next feature, and final `git status --short`.
