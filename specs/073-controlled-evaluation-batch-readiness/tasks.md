# Tasks: Feature 073

**Input**: Feature 072 deterministic golden trace validation  
**Prerequisites**: Feature 072 branch accepted for review  
**Status**: Spec Kit created; implementation pending

## Phase 1: Setup and Prior Evidence

- [X] T001 Confirm Feature 072 remote branch status.

Comment:
Feature 073 must start from the repaired Feature 072 golden trace branch.
Acceptance:
- Feature 072 report has `passed=True`, independent expected/actual traces, and no full paper reproduction claim.

- [X] T002 Create Feature 073 branch from Feature 072 commit.

Comment:
Feature 073 depends on Feature 072 deterministic trace readiness.
Acceptance:
- Branch `073-controlled-evaluation-batch-readiness` exists from commit `66f140c020ddf7f362d331523148782d923f2bdf` or newer.

- [X] T003 Read Feature 070, 071, and 072 evidence files.

Comment:
The batch layer must consume prior validated topology, runtime semantics, and trace validation.
Acceptance:
- Implementation verifies Feature 072 report before building controlled batch metrics.

## Phase 2: Tests First

- [X] T004 Add model tests for scenario, task record, metrics, and report.

- [X] T005 Add tests for all required controlled scenarios.

- [X] T006 Add metric calculation tests.

- [X] T007 Add aggregate metrics tests.

- [X] T008 Add compatibility-mode exclusion tests.

- [X] T009 Add report and scope-guard tests.

## Phase 3: Implementation

- [X] T010 Implement Feature 073 analysis package.

Comment:
Create a read-only package under `src/analysis/controlled_evaluation_batch_readiness/`.
Acceptance:
- Package has config, model, report, runner, CLI entry, and scope validator.

- [X] T011 Implement deterministic scenario fixtures.

Comment:
Scenarios must be deterministic and paper-mode by default.
Acceptance:
- All required scenarios are present.

- [X] T012 Implement per-scenario metrics.

Comment:
Metrics must be derived from task records, not hand-written summary prose.
Acceptance:
- Completed/drop/violation/delay/reward metrics are computed deterministically.

- [X] T013 Implement aggregate batch metrics.

Comment:
The report must include batch-level metrics across scenarios.
Acceptance:
- Aggregate metrics equal the sum/average of scenario-level metrics.

- [X] T014 Implement Feature 073 report.

Comment:
Report must include scenario metrics, aggregate metrics, prior regression evidence, claim boundary, and next feature recommendation.
Acceptance:
- `passed=True` only when all scenarios, metrics, and prior regressions pass.

- [X] T015 Implement scope validator.

Comment:
Protect branch from training, agents, artifacts, dependencies, and Feature 074+ paths.
Acceptance:
- Scope validator rejects forbidden paths.

## Phase 4: Validation and Handoff

- [X] T016 Run Feature 068R regression slice.

- [X] T017 Run Feature 069 regression slice.

- [X] T018 Run Feature 070 regression slice.

- [X] T019 Run Feature 071 regression slice.

- [X] T020 Run Feature 072 regression slice.

- [X] T021 Run Feature 073 targeted tests.

- [X] T022 Run `git diff --check` and Feature 073 scope validator.

- [X] T023 Commit and push only.

Comment:
No PR and no merge.
Acceptance:
- Branch is pushed, SHA equality is proven, and clean tree is shown.
