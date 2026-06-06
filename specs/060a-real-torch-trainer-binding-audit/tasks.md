# Tasks: Feature 060A — Real Torch Trainer Binding Audit

## A. Prerequisite and environment gates

- [X] T001 Verify branch is `060a-real-torch-trainer-binding-audit` and not `main`.
- [X] T002 Verify branch is based on current Feature 060 branch/head or current main containing Feature 060 if already merged.
- [X] T003 Verify Feature 060 report exists and has `final_verdict = full_paper_default_training_campaign_execution_passed`.
- [X] T004 Capture Python interpreter path using `which python3` and `sys.executable`.
- [X] T005 Capture `torch` and `torchrl` availability using `importlib.util.find_spec`.
- [X] T006 Capture `torch.__version__` and `pip show torch torchrl` evidence.

## B. Model and schema

- [X] T007 Create `src/analysis/real_torch_trainer_binding_audit/config.py`.
- [X] T008 Create `src/analysis/real_torch_trainer_binding_audit/model.py` with required audit report dataclass and verdicts.
- [X] T009 Create `src/analysis/real_torch_trainer_binding_audit/report.py` for JSON and Markdown outputs.
- [X] T010 Create `src/analysis/real_torch_trainer_binding_audit/runner.py`.
- [X] T011 Create `src/analysis/real_torch_trainer_binding_audit/__init__.py` and `__main__.py`.

## C. Binding audit

- [X] T012 Scan Feature 060 runner imports for `torch`, `torchrl`, and real trainer/learner imports.
- [X] T013 Scan Feature 060 runner call sites for real trainer/learner instantiation or execution.
- [X] T014 Detect scalar fallback markers: `random.Random`, manual replay list construction, manual scalar loss, manual optimizer-step counter, and manual target-sync count.
- [X] T015 Scan real trainer candidates under `src/agents/torchrl_hoodie_learner.py`, `src/analysis/full_training_reproduction_campaign/`, and `src/analysis/paper_hoodie_network_implementation/`.
- [X] T016 Compare Feature 060 claim against actual binding evidence.

## D. Verdict routing

- [X] T017 If torch/torchrl are unavailable, verdict must be `torch_environment_blocked`.
- [X] T018 If Feature 060 artifacts/code are missing, verdict must be the corresponding missing-artifact/code verdict.
- [X] T019 If torch/torchrl are available but Feature 060 is not bound to the real trainer, verdict must be `real_torch_trainer_binding_missing_repair_required`.
- [X] T020 If real binding is verified, verdict may be `real_torch_trainer_binding_verified`.
- [X] T021 Report blockers must name exact missing binding evidence.

## E. Tests

- [X] T022 Add `tests/unit/test_real_torch_trainer_binding_audit_schema.py`.
- [X] T023 Add `tests/unit/test_real_torch_trainer_binding_audit_metrics.py`.
- [X] T024 Add `tests/unit/test_real_torch_trainer_binding_audit_behavior_equivalence.py`.
- [X] T025 Add `tests/integration/test_real_torch_trainer_binding_audit.py`.
- [X] T026 Add `tests/integration/test_real_torch_trainer_binding_audit_report.py`.
- [X] T027 Add `tests/integration/test_real_torch_trainer_binding_audit_scope_guard.py`.

## F. Report generation and final gate

- [X] T028 Generate JSON and Markdown reports under `artifacts/analysis/real-torch-trainer-binding-audit/`.
- [X] T029 Ensure verdict is internally consistent with blockers and next-feature routing.
- [X] T030 Ensure audit does not modify Feature 060 execution source or Feature 060 artifacts.

## Validation Handoff and Remote Audit Packet

- [X] T031 Print local test output, Codex validation output, or CI result URL.
- [X] T032 Print generated report proof fields from the JSON artifact.
- [X] T033 Print `git status --short`.
- [X] T034 Print `git diff --name-only main...HEAD` or the correct base ref if branching from Feature 060.
- [X] T035 Print `git diff --stat main...HEAD` or the correct base ref if branching from Feature 060.
- [X] T036 Print `git diff --cached --name-only`.
- [X] T037 If auto-commit is used, print staged path list and verify only approved Feature 060A paths are staged.
- [X] T038 If auto-push is used, print commit SHA, branch name, pushed remote ref, final verdict, recommended next feature, and final `git status --short`.
