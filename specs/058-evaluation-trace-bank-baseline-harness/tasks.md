# Tasks: Feature 058 — Evaluation Trace Bank and Baseline Evaluation Harness

## A. Prerequisite gates

- [ ] T001 Verify `main` contains Feature 057 merge evidence.
- [ ] T002 Verify branch is not `main` and is based on current `main`.
- [ ] T003 Verify Feature 057 report is committed and has `final_verdict = paper_default_pilot_training_passed`.
- [ ] T004 Verify Feature 057 report has `remaining_blockers = []`, live environment training used, replay growth validated, optimizer progress validated, and no campaign/reproduction claim.

## B. Model and schema

- [ ] T005 Create `src/analysis/evaluation_trace_bank_baseline_harness/config.py`.
- [ ] T006 Create `src/analysis/evaluation_trace_bank_baseline_harness/model.py` with required report dataclass and fields.
- [ ] T007 Create `src/analysis/evaluation_trace_bank_baseline_harness/report.py` for JSON and Markdown outputs.
- [ ] T008 Create `src/analysis/evaluation_trace_bank_baseline_harness/runner.py`.
- [ ] T009 Create `src/analysis/evaluation_trace_bank_baseline_harness/__init__.py` and `__main__.py`.

## C. Evaluation trace bank and baseline harness

- [ ] T010 Build deterministic evaluation trace bank metadata.
- [ ] T011 Validate evaluation trace bank is disjoint from training trace bank.
- [ ] T012 Create baseline policy registry summary.
- [ ] T013 Validate baseline harness can evaluate registered baseline policies against evaluation traces.
- [ ] T014 Validate metric schema includes delay, drop, timeout, reward, action distribution, local/horizontal/vertical action counts, and per-episode summaries.
- [ ] T015 Validate repeatability/determinism for trace bank and baseline harness outputs.

## D. Safety gates

- [ ] T016 Validate no training execution occurs.
- [ ] T017 Validate no optimizer steps execute.
- [ ] T018 Validate no replay mutation occurs.
- [ ] T019 Validate no checkpoint binary is written.
- [ ] T020 Validate no full campaign, paper reproduction claim, performance claim, policy drift, dependency drift, environment semantic drift, or reward timing drift occurs.
- [ ] T021 Validate no Feature 037–057 artifacts are rewritten.

## E. Tests

- [ ] T022 Add `tests/unit/test_evaluation_trace_bank_baseline_harness_schema.py`.
- [ ] T023 Add `tests/unit/test_evaluation_trace_bank_baseline_harness_metrics.py`.
- [ ] T024 Add `tests/unit/test_evaluation_trace_bank_baseline_harness_behavior_equivalence.py`.
- [ ] T025 Add `tests/integration/test_evaluation_trace_bank_baseline_harness.py`.
- [ ] T026 Add `tests/integration/test_evaluation_trace_bank_baseline_harness_report.py`.
- [ ] T027 Add `tests/integration/test_evaluation_trace_bank_baseline_harness_scope_guard.py`.

## F. Report generation and final gate

- [ ] T028 Generate JSON and Markdown reports under `artifacts/analysis/evaluation-trace-bank-baseline-harness/`.
- [ ] T029 Final verdict must be `evaluation_trace_bank_baseline_harness_ready` only when all validation gates pass and blockers are empty.
- [ ] T030 Recommended next feature must be `Feature 059 — Full Paper-Default Training Campaign Gate` only on passing verdict.

## Validation Handoff and Remote Audit Packet

- [ ] T031 Print local test output, Codex validation output, or CI result URL.
- [ ] T032 Print generated report proof fields from the JSON artifact.
- [ ] T033 Print `git status --short`.
- [ ] T034 Print `git diff --name-only main...HEAD`.
- [ ] T035 Print `git diff --stat main...HEAD`.
- [ ] T036 Print `git diff --cached --name-only`.
- [ ] T037 If auto-commit is used, print staged path list and verify only approved Feature 058 paths are staged.
- [ ] T038 If auto-push is used, print commit SHA, branch name, pushed remote ref, final verdict, recommended next feature, and final `git status --short`.
