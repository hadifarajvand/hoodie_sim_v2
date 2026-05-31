# Tasks: Feature 074

**Input**: Feature 073 controlled evaluation batch readiness  
**Prerequisites**: Feature 073 branch accepted for review  
**Status**: Spec Kit created; implementation pending

## Phase 1: Setup and Prior Evidence

- [X] T001 Confirm Feature 073 remote branch status.
- [X] T002 Create Feature 074 branch from Feature 073 commit.
- [ ] T003 Read Feature 068R through Feature 073 evidence files.

## Phase 2: Tests First

- [ ] T004 Add model tests for policy descriptors, scenario comparisons, aggregate metrics, and report.
- [ ] T005 Add policy registry coverage tests.
- [ ] T006 Add per-policy scenario comparison tests.
- [ ] T007 Add aggregate per-policy metric tests.
- [ ] T008 Add compatibility-mode exclusion tests.
- [ ] T009 Add report and scope-guard tests.

## Phase 3: Implementation

- [ ] T010 Implement Feature 074 analysis package.
- [ ] T011 Implement required baseline policy registry verification.
- [ ] T012 Implement per-policy scenario comparison.
- [ ] T013 Implement per-policy aggregate metrics.
- [ ] T014 Implement Feature 074 report.
- [ ] T015 Implement scope validator.

## Phase 4: Validation and Handoff

- [ ] T016 Run Feature 068R regression slice.
- [ ] T017 Run Feature 069 regression slice.
- [ ] T018 Run Feature 070 regression slice.
- [ ] T019 Run Feature 071 regression slice.
- [ ] T020 Run Feature 072 regression slice.
- [ ] T021 Run Feature 073 regression slice.
- [ ] T022 Run Feature 074 targeted tests.
- [ ] T023 Run git diff check and Feature 074 scope validator.
- [ ] T024 Commit and push only.

## Notes

Feature 074 must stay read-only. It must not open a PR, merge, change policy code, start training, generate campaign artifacts, or claim final evaluation results.
