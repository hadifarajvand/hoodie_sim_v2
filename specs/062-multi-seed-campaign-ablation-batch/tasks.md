# Tasks: Feature 062 — Multi-Seed Campaign and Ablation Batch

## A. Prerequisite gates

- [ ] T001 Verify `main` contains Feature 061 merge evidence.
- [ ] T002 Verify Feature 061 report has `final_verdict = campaign_integrity_evaluation_comparison_batch_passed`.
- [ ] T003 Verify Feature 061 report has `remaining_blockers = []`.
- [ ] T004 Verify Feature 061 comparison, baseline evaluation, and trained-policy evaluation artifacts exist.

## B. Model and package

- [ ] T005 Create `src/analysis/multi_seed_campaign_ablation_batch/config.py`.
- [ ] T006 Create `src/analysis/multi_seed_campaign_ablation_batch/model.py`.
- [ ] T007 Create `src/analysis/multi_seed_campaign_ablation_batch/report.py`.
- [ ] T008 Create `src/analysis/multi_seed_campaign_ablation_batch/runner.py`.
- [ ] T009 Create `src/analysis/multi_seed_campaign_ablation_batch/__init__.py` and `__main__.py`.

## C. Batch item 1 — multi-seed campaign gate

- [ ] T010 Define deterministic seed set with at least three seeds.
- [ ] T011 Define bounded execution budget per seed.
- [ ] T012 Validate trace-bank IDs, metric schema, and real-trainer binding evidence are available before multi-seed execution.
- [ ] T013 Generate `multi-seed-campaign-gate.json`.

## D. Batch item 2 — multi-seed campaign execution

- [ ] T014 Execute or controlled-materialize multi-seed trained-policy results under the same metric schema.
- [ ] T015 Execute or controlled-materialize multi-seed baseline results under the same metric schema.
- [ ] T016 Preserve configured budget and actual executed budget separately.
- [ ] T017 Generate `multi-seed-campaign-results.json`.

## E. Batch item 3 — multi-seed result aggregation

- [ ] T018 Aggregate seed-level results.
- [ ] T019 Include sample count, mean, min, max, and available variance/std fields for supported metrics.
- [ ] T020 Mark unsupported schema-only metrics as not-claimed, not missing.
- [ ] T021 Generate `multi-seed-aggregation.json`.

## F. Batch item 4 — mechanism ablation gate

- [ ] T022 Define ablation variants: `full_mechanism`, `no_deadline_awareness`, `no_queue_awareness`, `no_selected_action_outcome_evidence`, `no_real_trainer_binding_control`.
- [ ] T023 Validate each variant has an explicit execution/materialization plan or exact blocker.
- [ ] T024 Generate `ablation-gate.json`.

## G. Batch item 5 — mechanism ablation execution

- [ ] T025 Execute or controlled-materialize each unblocked ablation variant.
- [ ] T026 Use the same seed set, trace-bank constraints, and metric schema.
- [ ] T027 Generate `ablation-results.json`.

## H. Safety gates

- [ ] T028 Validate no dependency, policy, environment, or reward-timing drift.
- [ ] T029 Validate no prior Feature 037–061 artifacts are rewritten.
- [ ] T030 Validate no paper reproduction claim or unsupported superiority claim is made.
- [ ] T031 Validate no uncontrolled campaign loop or checkpoint binary is created.

## I. Tests

- [ ] T032 Add `tests/unit/test_multi_seed_campaign_ablation_batch_schema.py`.
- [ ] T033 Add `tests/unit/test_multi_seed_campaign_ablation_batch_metrics.py`.
- [ ] T034 Add `tests/unit/test_multi_seed_campaign_ablation_batch_behavior_equivalence.py`.
- [ ] T035 Add `tests/integration/test_multi_seed_campaign_ablation_batch.py`.
- [ ] T036 Add `tests/integration/test_multi_seed_campaign_ablation_batch_report.py`.
- [ ] T037 Add `tests/integration/test_multi_seed_campaign_ablation_batch_scope_guard.py`.

## J. Report generation and final gate

- [ ] T038 Generate all Feature 062 batch artifacts.
- [ ] T039 Final verdict must be `multi_seed_campaign_ablation_batch_passed` only when all batch gates pass and blockers are empty.
- [ ] T040 Recommended next feature must be `Feature 063 — Results Export, Reproducibility, and Final Documentation Batch` only on passing verdict.

## Validation Handoff and Remote Audit Packet

- [ ] T041 Print exact test output or CI result URL.
- [ ] T042 Print report proof fields.
- [ ] T043 Print `git status --short`.
- [ ] T044 Print `git diff --name-only main...HEAD`.
- [ ] T045 Print `git diff --stat main...HEAD`.
- [ ] T046 Print `git diff --cached --name-only`.
- [ ] T047 If auto-push is used, print commit SHA, branch name, pushed remote ref, final verdict, recommended next feature, and final `git status --short`.
