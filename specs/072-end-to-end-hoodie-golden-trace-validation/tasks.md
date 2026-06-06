# Tasks: Feature 072

**Input**: Feature 071 runtime paper-faithful semantics alignment  
**Prerequisites**: Feature 071 branch accepted for review  
**Status**: Spec Kit created; implementation pending

## Phase 1: Setup and Prior Evidence

- [X] T001 Confirm Feature 071 remote branch status.

Comment:
Feature 072 must start from Feature 071 runtime helper semantics, not stale Feature 070 or main.
Acceptance:
- Feature 071 report is passed and compatibility mode is explicit.

- [X] T002 Create Feature 072 branch from Feature 071 commit.

Comment:
Feature 072 depends on Feature 071 helper behavior.
Acceptance:
- Branch `072-golden-trace-validation` exists from commit `4a3b33388074e60aa4462ce4fb71e282cfccc81c` or newer.

- [X] T003 Read Feature 070 and Feature 071 evidence files.

Comment:
The trace package must consume prior evidence instead of inventing topology or formulas.
Acceptance:
- Figure 7 neighbor map and Feature 071 runtime helper behavior are verified before implementation.

## Phase 2: Tests First

- [X] T004 Add model tests for GoldenTraceScenario and GoldenTraceStep.

- [X] T005 Add scenario tests for local success and local timeout.

- [X] T006 Add topology trace tests for legal neighbor, non-neighbor, and self-destination rejection.

- [X] T007 Add cloud/vertical success trace test.

- [X] T008 Add reward trace tests for success, drop, inactive, and pending states.

- [X] T009 Add compatibility boundary test proving paper mode is default.

- [X] T010 Add report and scope-guard tests.

## Phase 3: Implementation

- [X] T011 Implement Feature 072 analysis package.

Comment:
Create a read-only package under `src/analysis/end_to_end_hoodie_golden_trace_validation/`.
Acceptance:
- Package has config, model, report, runner, CLI entry, and scope validator.

- [X] T012 Implement deterministic scenario builders.

Comment:
Golden traces must be deterministic and use Feature 070/071 helpers.
Acceptance:
- All required scenarios are represented.

- [X] T013 Implement topology legality trace using Figure 7.

Comment:
No complete graph fallback.
Acceptance:
- `1 -> 6` is legal, `1 -> 2` is illegal, and `1 -> 1` is illegal.

- [X] T014 Implement deadline and terminal state traces using Feature 071 helpers.

Comment:
Do not duplicate deadline formulas.
Acceptance:
- Completion at paper deadline drops in paper mode.

- [X] T015 Implement reward traces using Feature 071 helpers.

Comment:
Do not duplicate reward formulas.
Acceptance:
- Success returns `-Phi`, drop returns `-C`, inactive returns no-reward sentinel, pending raises or records blocked emission.

- [X] T016 Implement Feature 072 report.

Comment:
Report must include all scenarios and prior regression statuses.
Acceptance:
- `passed=True` only when all scenarios and regressions pass.

- [X] T017 Implement scope validator.

Comment:
Protect branch from artifacts, training, agents, dependencies, and Feature 073+ paths.
Acceptance:
- Scope validator rejects forbidden paths.

## Phase 4: Validation and Handoff

- [X] T018 Run Feature 068R regression slice.

- [X] T019 Run Feature 069 regression slice.

- [X] T020 Run Feature 070 regression slice.

- [X] T021 Run Feature 071 regression slice.

- [X] T022 Run Feature 072 targeted tests.

- [X] T023 Run `git diff --check` and Feature 072 scope validator.

- [X] T024 Commit and push only.

Comment:
No PR and no merge.
Acceptance:
- Branch is pushed, SHA equality is proven, and clean tree is shown.
