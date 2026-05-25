# Tasks: Feature 060A — Real Torch Trainer Binding Audit

## A. Prerequisite and environment gates

- [ ] T001 Verify branch is `060a-real-torch-trainer-binding-audit` and not `main`.
- [ ] T002 Verify branch is based on current Feature 060 branch/head or current main containing Feature 060 if already merged.
- [ ] T003 Verify Feature 060 report exists and has `final_verdict = full_paper_default_training_campaign_execution_passed`.
- [ ] T004 Capture Python interpreter path using `which python3` and `sys.executable`.
- [ ] T005 Capture `torch` and `torchrl` availability using `importlib.util.find_spec`.
- [ ] T006 Capture `torch.__version__` and `pip show torch torchrl` evidence.

## B. Model and schema

- [ ] T007 Create `src/analysis/real_torch_trainer_binding_audit/config.py`.
- [ ] T008 Create `src/analysis/real_torch_trainer_binding_audit/model.py` with required audit report dataclass and verdicts.
- [ ] T009 Create `src/analysis/real_torch_trainer_binding_audit/report.py` for JSON and Markdown outputs.
- [ ] T010 Create `src/analysis/real_torch_trainer_binding_audit/runner.py`.
- [ ] T011 Create `src/analysis/real_torch_trainer_binding_audit/__init__.py` and `__main__.py`.

## C. Binding audit

- [ ] T012 Scan Feature 060 runner imports for `torch`, `torchrl`, and real trainer/learner imports.
- [ ] T013 Scan Feature 060 runner call sites for real trainer/learner instantiation or execution.
- [ ] T014 Detect scalar fallback markers: `random.Random`, manual replay list construction, manual scalar loss, manual optimizer-step counter, and manual target-sync count.
- [ ] T015 Scan real trainer candidates under `src/agents/torchrl_hoodie_learner.py`, `src/analysis/full_training_reproduction_campaign/`, and `src/analysis/paper_hoodie_network_implementation/`.
- [ ] T016 Compare Feature 060 claim against actual binding evidence.

## D. Verdict routing

- [ ] T017 If torch/torchrl are unavailable, verdict must be `torch_environment_blocked`.
- [ ] T018 If Feature 060 artifacts/code are missing, verdict must be the corresponding missing-artifact/code verdict.
- [ ] T019 If torch/torchrl are available but Feature 060 is not bound to the real trainer, verdict must be `real_torch_trainer_binding_missing_repair_required`.
- [ ] T020 If real binding is verified, verdict may be `real_torch_trainer_binding_verified`.
- [ ] T021 Report blockers must name exact missing binding evidence.

## E. Tests

- [ ] T022 Add `tests/unit/test_real_torch_trainer_binding_audit_schema.py`.
- [ ] T023 Add `tests/unit/test_real_torch_trainer_binding_audit_metrics.py`.
- [ ] T024 Add `tests/unit/test_real_torch_trainer_binding_audit_behavior_equivalence.py`.
- [ ] T025 Add `tests/integration/test_real_torch_trainer_binding_audit.py`.
- [ ] T026 Add `tests/integration/test_real_torch_trainer_binding_audit_report.py`.
- [ ] T027 Add `tests/integration/test_real_torch_trainer_binding_audit_scope_guard.py`.

## F. Report generation and final gate

- [ ] T028 Generate JSON and Markdown reports under `artifacts/analysis/real-torch-trainer-binding-audit/`.
- [ ] T029 Ensure verdict is internally consistent with blockers and next-feature routing.
- [ ] T030 Ensure audit does not modify Feature 060 execution source or Feature 060 artifacts.

## Validation Handoff and Remote Audit Packet

- [ ] T031 Print local test output, Codex validation output, or CI result URL.
- [ ] T032 Print generated report proof fields from the JSON artifact.
- [ ] T033 Print `git status --short`.
- [ ] T034 Print `git diff --name-only main...HEAD` or the correct base ref if branching from Feature 060.
- [ ] T035 Print `git diff --stat main...HEAD` or the correct base ref if branching from Feature 060.
- [ ] T036 Print `git diff --cached --name-only`.
- [ ] T037 If auto-commit is used, print staged path list and verify only approved Feature 060A paths are staged.
- [ ] T038 If auto-push is used, print commit SHA, branch name, pushed remote ref, final verdict, recommended next feature, and final `git status --short`.
