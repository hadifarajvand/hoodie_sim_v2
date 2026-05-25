# Tasks: Feature 061 — Campaign Integrity, Evaluation Execution, and Comparison Batch

## A. Prerequisite gates

- [ ] T001 Verify `main` contains Feature 060 merge evidence.
- [ ] T002 Verify Feature 060 report has `final_verdict = full_paper_default_training_campaign_execution_passed`.
- [ ] T003 Verify Feature 060B repair report has `final_verdict = real_torch_trainer_binding_repair_passed`.
- [ ] T004 Verify Feature 060 artifacts exist: campaign report, training metrics, evaluation metrics, checkpoint metadata, run manifest.

## B. Model and package

- [ ] T005 Create `src/analysis/campaign_integrity_evaluation_comparison_batch/config.py`.
- [ ] T006 Create `src/analysis/campaign_integrity_evaluation_comparison_batch/model.py`.
- [ ] T007 Create `src/analysis/campaign_integrity_evaluation_comparison_batch/report.py`.
- [ ] T008 Create `src/analysis/campaign_integrity_evaluation_comparison_batch/runner.py`.
- [ ] T009 Create `src/analysis/campaign_integrity_evaluation_comparison_batch/__init__.py` and `__main__.py`.

## C. Batch item 1 — campaign integrity audit

- [ ] T010 Validate Feature 060 artifact manifest consistency.
- [ ] T011 Validate training metrics, evaluation metrics, checkpoint metadata, and run manifest agree on trace-bank IDs, seed bundle, and resource controls.
- [ ] T012 Validate real trainer binding evidence is present in campaign metrics.

## D. Batch item 2 — baseline evaluation execution

- [ ] T013 Execute or materialize baseline evaluation results on the Feature 058 evaluation trace bank.
- [ ] T014 Validate baseline policies use the shared metric schema.

## E. Batch item 3 — trained policy evaluation execution

- [ ] T015 Execute or materialize trained-policy evaluation results on the same Feature 058 evaluation trace bank.
- [ ] T016 Validate trained-policy metrics use the shared metric schema.

## F. Batch item 4 — comparison readiness audit

- [ ] T017 Validate baseline and trained-policy results use the same trace bank.
- [ ] T018 Validate train/eval separation is preserved.
- [ ] T019 Validate comparison schema covers delay, drop, timeout, reward, action distribution, local/horizontal/vertical counts, and per-episode summaries.

## G. Batch item 5 — comparison report

- [ ] T020 Generate baseline-vs-trained-policy comparison JSON.
- [ ] T021 Generate baseline-vs-trained-policy comparison Markdown.
- [ ] T022 Mark comparison values as controlled experiment data, not paper reproduction or superiority claims.

## H. Safety gates

- [ ] T023 Validate no dependency, policy, environment, or reward-timing drift.
- [ ] T024 Validate no prior Feature 037–060B artifacts are rewritten.
- [ ] T025 Validate no paper reproduction or unsupported superiority claim is made.

## I. Tests

- [ ] T026 Add `tests/unit/test_campaign_integrity_evaluation_comparison_batch_schema.py`.
- [ ] T027 Add `tests/unit/test_campaign_integrity_evaluation_comparison_batch_metrics.py`.
- [ ] T028 Add `tests/unit/test_campaign_integrity_evaluation_comparison_batch_behavior_equivalence.py`.
- [ ] T029 Add `tests/integration/test_campaign_integrity_evaluation_comparison_batch.py`.
- [ ] T030 Add `tests/integration/test_campaign_integrity_evaluation_comparison_batch_report.py`.
- [ ] T031 Add `tests/integration/test_campaign_integrity_evaluation_comparison_batch_scope_guard.py`.

## J. Report generation and final gate

- [ ] T032 Generate all Feature 061 batch artifacts.
- [ ] T033 Final verdict must be `campaign_integrity_evaluation_comparison_batch_passed` only when all batch gates pass and blockers are empty.
- [ ] T034 Recommended next feature must be `Feature 062 — Multi-Seed Campaign and Ablation Batch` only on passing verdict.

## Validation Handoff and Remote Audit Packet

- [ ] T035 Print exact test output or CI result URL.
- [ ] T036 Print report proof fields.
- [ ] T037 Print `git status --short`.
- [ ] T038 Print `git diff --name-only main...HEAD`.
- [ ] T039 Print `git diff --stat main...HEAD`.
- [ ] T040 Print `git diff --cached --name-only`.
- [ ] T041 If auto-push is used, print commit SHA, branch name, pushed remote ref, final verdict, recommended next feature, and final `git status --short`.
