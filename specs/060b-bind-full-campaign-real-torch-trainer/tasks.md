# Tasks: Feature 060B — Bind Full Campaign Execution to Real Torch Trainer

## A. Prerequisite gates

- [ ] T001 Verify branch is `060b-bind-full-campaign-real-torch-trainer` and not `main`.
- [ ] T002 Verify branch is based on `060-full-paper-default-training-campaign-execution` after Feature 060A audit merge.
- [ ] T003 Verify Feature 060A report exists and has `final_verdict = real_torch_trainer_binding_missing_repair_required`.
- [ ] T004 Verify repo venv has `torch` and `torchrl` available.

## B. Repair model and package

- [ ] T005 Create `src/analysis/bind_full_campaign_real_torch_trainer/config.py`.
- [ ] T006 Create `src/analysis/bind_full_campaign_real_torch_trainer/model.py`.
- [ ] T007 Create `src/analysis/bind_full_campaign_real_torch_trainer/report.py`.
- [ ] T008 Create `src/analysis/bind_full_campaign_real_torch_trainer/runner.py`.
- [ ] T009 Create `src/analysis/bind_full_campaign_real_torch_trainer/__init__.py` and `__main__.py`.

## C. Feature 060 real binding repair

- [ ] T010 Update Feature 060 execution package to import real trainer, learner, or network code.
- [ ] T011 Replace scalar-only campaign claim with real trainer-bound execution evidence.
- [ ] T012 Keep configured and actual execution budgets explicit.
- [ ] T013 Regenerate Feature 060 report and support artifacts.
- [ ] T014 Ensure Feature 060 report proves real trainer binding and no unsupported scalar fallback claim.

## D. Feature 060B report

- [ ] T015 Generate Feature 060B JSON and Markdown repair report.
- [ ] T016 Report torch and torchrl availability through repo venv.
- [ ] T017 Report real trainer import, instantiation, and update/train call evidence.
- [ ] T018 Report regenerated Feature 060 artifact consistency.
- [ ] T019 Final verdict must be `real_torch_trainer_binding_repair_passed` only if blockers are empty.
- [ ] T020 Recommended next feature must be `Feature 061 — Campaign Result Integrity and Comparison Readiness Audit` only on passing verdict.

## E. Tests

- [ ] T021 Add `tests/unit/test_bind_full_campaign_real_torch_trainer_schema.py`.
- [ ] T022 Add `tests/unit/test_bind_full_campaign_real_torch_trainer_metrics.py`.
- [ ] T023 Add `tests/unit/test_bind_full_campaign_real_torch_trainer_behavior_equivalence.py`.
- [ ] T024 Add `tests/integration/test_bind_full_campaign_real_torch_trainer.py`.
- [ ] T025 Add `tests/integration/test_bind_full_campaign_real_torch_trainer_report.py`.
- [ ] T026 Add `tests/integration/test_bind_full_campaign_real_torch_trainer_scope_guard.py`.
- [ ] T027 Run Feature 060 regression tests after repair.

## Validation Handoff and Remote Audit Packet

- [ ] T028 Print local test output, Codex validation output, or CI result URL.
- [ ] T029 Print Feature 060B report proof fields.
- [ ] T030 Print regenerated Feature 060 report proof fields.
- [ ] T031 Print `git status --short`.
- [ ] T032 Print `git diff --name-only 060-full-paper-default-training-campaign-execution...HEAD`.
- [ ] T033 Print `git diff --stat 060-full-paper-default-training-campaign-execution...HEAD`.
- [ ] T034 Print `git diff --cached --name-only`.
- [ ] T035 If auto-commit is used, print staged path list and verify only approved Feature 060B paths are staged.
- [ ] T036 If auto-push is used, print commit SHA, branch name, pushed remote ref, final verdict, recommended next feature, and final `git status --short`.
