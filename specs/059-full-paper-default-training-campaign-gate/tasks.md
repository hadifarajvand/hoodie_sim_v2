# Tasks: Feature 059 — Full Paper-Default Training Campaign Gate

## A. Prerequisite gates

- [X] T001 Verify `main` contains Feature 058 merge evidence.
- [X] T002 Verify branch is not `main` and is based on current `main`.
- [X] T003 Verify Feature 058 report is committed and has `final_verdict = evaluation_trace_bank_baseline_harness_ready`.
- [X] T004 Verify Feature 058 report has `remaining_blockers = []`, deterministic evaluation trace bank, train/eval separation, baseline harness readiness, metric schema completeness, and no training/performance claim.

## B. Model and schema

- [X] T005 Create `src/analysis/full_paper_default_training_campaign_gate/config.py`.
- [X] T006 Create `src/analysis/full_paper_default_training_campaign_gate/model.py` with required report dataclass and fields.
- [X] T007 Create `src/analysis/full_paper_default_training_campaign_gate/report.py` for JSON and Markdown outputs.
- [X] T008 Create `src/analysis/full_paper_default_training_campaign_gate/runner.py`.
- [X] T009 Create `src/analysis/full_paper_default_training_campaign_gate/__init__.py` and `__main__.py`.

## C. Campaign gate contracts

- [X] T010 Define campaign scope summary for next execution feature.
- [X] T011 Define training execution gate summary without executing training.
- [X] T012 Define evaluation harness gate summary using Feature 058 evidence.
- [X] T013 Define next-feature artifact output contract.
- [X] T014 Define resource-control summary.
- [X] T015 Define checkpoint contract summary.
- [X] T016 Define metric collection contract summary.

## D. Safety gates

- [X] T017 Validate no training execution occurs.
- [X] T018 Validate no optimizer execution occurs.
- [X] T019 Validate no replay mutation occurs.
- [X] T020 Validate no checkpoint binary is written.
- [X] T021 Validate no full campaign execution happens in Feature 059.
- [X] T022 Validate no paper reproduction, performance, or baseline superiority claim is made.
- [X] T023 Validate no policy, dependency, environment semantic, or reward timing drift occurs.
- [X] T024 Validate no Feature 037–058 artifacts are rewritten.

## E. Tests

- [X] T025 Add `tests/unit/test_full_paper_default_training_campaign_gate_schema.py`.
- [X] T026 Add `tests/unit/test_full_paper_default_training_campaign_gate_metrics.py`.
- [X] T027 Add `tests/unit/test_full_paper_default_training_campaign_gate_behavior_equivalence.py`.
- [X] T028 Add `tests/integration/test_full_paper_default_training_campaign_gate.py`.
- [X] T029 Add `tests/integration/test_full_paper_default_training_campaign_gate_report.py`.
- [X] T030 Add `tests/integration/test_full_paper_default_training_campaign_gate_scope_guard.py`.

## F. Report generation and final gate

- [X] T031 Generate JSON and Markdown reports under `artifacts/analysis/full-paper-default-training-campaign-gate/`.
- [X] T032 Final verdict must be `full_paper_default_training_campaign_gate_ready` only when all validation gates pass and blockers are empty.
- [X] T033 Recommended next feature must be `Feature 060 — Full Paper-Default Training Campaign Execution` only on passing verdict.

## Validation Handoff and Remote Audit Packet

- [X] T034 Print local test output, Codex validation output, or CI result URL.
- [X] T035 Print generated report proof fields from the JSON artifact.
- [X] T036 Print `git status --short`.
- [X] T037 Print `git diff --name-only main...HEAD`.
- [X] T038 Print `git diff --stat main...HEAD`.
- [X] T039 Print `git diff --cached --name-only`.
- [X] T040 If auto-commit is used, print staged path list and verify only approved Feature 059 paths are staged.
- [X] T041 If auto-push is used, print commit SHA, branch name, pushed remote ref, final verdict, recommended next feature, and final `git status --short`.
