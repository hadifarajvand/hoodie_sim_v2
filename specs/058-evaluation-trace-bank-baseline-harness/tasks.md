# Tasks: Feature 058 — Evaluation Trace Bank and Baseline Evaluation Harness

## A. Prerequisite gates

- [X] T001 Verify `main` contains Feature 057 merge evidence.
- [X] T002 Verify branch is not `main` and is based on current `main`.
- [X] T003 Verify Feature 057 report is committed and has `final_verdict = paper_default_pilot_training_passed`.
- [X] T004 Verify Feature 057 report has `remaining_blockers = []`, live environment training used, replay growth validated, optimizer progress validated, and no campaign/reproduction claim.

## B. Model and schema

- [X] T005 Create `src/analysis/evaluation_trace_bank_baseline_harness/config.py`.
- [X] T006 Create `src/analysis/evaluation_trace_bank_baseline_harness/model.py` with required report dataclass and fields.
- [X] T007 Create `src/analysis/evaluation_trace_bank_baseline_harness/report.py` for JSON and Markdown outputs.
- [X] T008 Create `src/analysis/evaluation_trace_bank_baseline_harness/runner.py`.
- [X] T009 Create `src/analysis/evaluation_trace_bank_baseline_harness/__init__.py` and `__main__.py`.

## C. Evaluation trace bank and baseline harness

- [X] T010 Build deterministic evaluation trace bank metadata.
- [X] T011 Validate evaluation trace bank is disjoint from training trace bank.
- [X] T012 Create baseline policy registry summary.
- [X] T013 Validate baseline harness can evaluate registered baseline policies against evaluation traces.
- [X] T014 Validate metric schema includes delay, drop, timeout, reward, action distribution, local/horizontal/vertical action counts, and per-episode summaries.
- [X] T015 Validate repeatability/determinism for trace bank and baseline harness outputs.

## D. Safety gates

- [X] T016 Validate no training execution occurs.
- [X] T017 Validate no optimizer steps execute.
- [X] T018 Validate no replay mutation occurs.
- [X] T019 Validate no checkpoint binary is written.
- [X] T020 Validate no full campaign, paper reproduction claim, performance claim, policy drift, dependency drift, environment semantic drift, or reward timing drift occurs.
- [X] T021 Validate no Feature 037–057 artifacts are rewritten.

## E. Tests

- [X] T022 Add `tests/unit/test_evaluation_trace_bank_baseline_harness_schema.py`.
- [X] T023 Add `tests/unit/test_evaluation_trace_bank_baseline_harness_metrics.py`.
- [X] T024 Add `tests/unit/test_evaluation_trace_bank_baseline_harness_behavior_equivalence.py`.
- [X] T025 Add `tests/integration/test_evaluation_trace_bank_baseline_harness.py`.
- [X] T026 Add `tests/integration/test_evaluation_trace_bank_baseline_harness_report.py`.
- [X] T027 Add `tests/integration/test_evaluation_trace_bank_baseline_harness_scope_guard.py`.

## F. Report generation and final gate

- [X] T028 Generate JSON and Markdown reports under `artifacts/analysis/evaluation-trace-bank-baseline-harness/`.
- [X] T029 Final verdict must be `evaluation_trace_bank_baseline_harness_ready` only when all validation gates pass and blockers are empty.
- [X] T030 Recommended next feature must be `Feature 059 — Full Paper-Default Training Campaign Gate` only on passing verdict.

## Validation Handoff and Remote Audit Packet

- [X] T031 Print local test output, Codex validation output, or CI result URL.
- [X] T032 Print generated report proof fields from the JSON artifact.
- [X] T033 Print `git status --short`.
- [X] T034 Print `git diff --name-only main...HEAD`.
- [X] T035 Print `git diff --stat main...HEAD`.
- [X] T036 Print `git diff --cached --name-only`.
- [X] T037 If auto-commit is used, print staged path list and verify only approved Feature 058 paths are staged.
- [X] T038 If auto-push is used, print commit SHA, branch name, pushed remote ref, final verdict, recommended next feature, and final `git status --short`.
