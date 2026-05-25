# Tasks: Feature 059 — Full Paper-Default Training Campaign Gate

## A. Prerequisite gates

- [ ] T001 Verify `main` contains Feature 058 merge evidence.
- [ ] T002 Verify branch is not `main` and is based on current `main`.
- [ ] T003 Verify Feature 058 report is committed and has `final_verdict = evaluation_trace_bank_baseline_harness_ready`.
- [ ] T004 Verify Feature 058 report has `remaining_blockers = []`, deterministic evaluation trace bank, train/eval separation, baseline harness readiness, metric schema completeness, and no training/performance claim.

## B. Model and schema

- [ ] T005 Create `src/analysis/full_paper_default_training_campaign_gate/config.py`.
- [ ] T006 Create `src/analysis/full_paper_default_training_campaign_gate/model.py` with required report dataclass and fields.
- [ ] T007 Create `src/analysis/full_paper_default_training_campaign_gate/report.py` for JSON and Markdown outputs.
- [ ] T008 Create `src/analysis/full_paper_default_training_campaign_gate/runner.py`.
- [ ] T009 Create `src/analysis/full_paper_default_training_campaign_gate/__init__.py` and `__main__.py`.

## C. Campaign gate contracts

- [ ] T010 Define campaign scope summary for next execution feature.
- [ ] T011 Define training execution gate summary without executing training.
- [ ] T012 Define evaluation harness gate summary using Feature 058 evidence.
- [ ] T013 Define next-feature artifact output contract.
- [ ] T014 Define resource-control summary.
- [ ] T015 Define checkpoint contract summary.
- [ ] T016 Define metric collection contract summary.

## D. Safety gates

- [ ] T017 Validate no training execution occurs.
- [ ] T018 Validate no optimizer execution occurs.
- [ ] T019 Validate no replay mutation occurs.
- [ ] T020 Validate no checkpoint binary is written.
- [ ] T021 Validate no full campaign execution happens in Feature 059.
- [ ] T022 Validate no paper reproduction, performance, or baseline superiority claim is made.
- [ ] T023 Validate no policy, dependency, environment semantic, or reward timing drift occurs.
- [ ] T024 Validate no Feature 037–058 artifacts are rewritten.

## E. Tests

- [ ] T025 Add `tests/unit/test_full_paper_default_training_campaign_gate_schema.py`.
- [ ] T026 Add `tests/unit/test_full_paper_default_training_campaign_gate_metrics.py`.
- [ ] T027 Add `tests/unit/test_full_paper_default_training_campaign_gate_behavior_equivalence.py`.
- [ ] T028 Add `tests/integration/test_full_paper_default_training_campaign_gate.py`.
- [ ] T029 Add `tests/integration/test_full_paper_default_training_campaign_gate_report.py`.
- [ ] T030 Add `tests/integration/test_full_paper_default_training_campaign_gate_scope_guard.py`.

## F. Report generation and final gate

- [ ] T031 Generate JSON and Markdown reports under `artifacts/analysis/full-paper-default-training-campaign-gate/`.
- [ ] T032 Final verdict must be `full_paper_default_training_campaign_gate_ready` only when all validation gates pass and blockers are empty.
- [ ] T033 Recommended next feature must be `Feature 060 — Full Paper-Default Training Campaign Execution` only on passing verdict.

## Validation Handoff and Remote Audit Packet

- [ ] T034 Print local test output, Codex validation output, or CI result URL.
- [ ] T035 Print generated report proof fields from the JSON artifact.
- [ ] T036 Print `git status --short`.
- [ ] T037 Print `git diff --name-only main...HEAD`.
- [ ] T038 Print `git diff --stat main...HEAD`.
- [ ] T039 Print `git diff --cached --name-only`.
- [ ] T040 If auto-commit is used, print staged path list and verify only approved Feature 059 paths are staged.
- [ ] T041 If auto-push is used, print commit SHA, branch name, pushed remote ref, final verdict, recommended next feature, and final `git status --short`.
