# Tasks: Feature 074

**Input**: Feature 073 controlled evaluation batch readiness  
**Prerequisites**: Feature 073 branch accepted for review  
**Status**: Spec Kit created; implementation pending

## Phase 1: Setup and Prior Evidence

- [X] T001 Confirm Feature 073 remote branch status.
- [X] T002 Create Feature 074 branch from Feature 073 commit.
- [X] T003 Read Feature 068R through Feature 073 evidence files.

## Phase 2: Tests First

- [X] T004 Add model tests for policy descriptors, scenario comparisons, aggregate metrics, and report.
- [X] T005 Add policy registry coverage tests.
- [X] T006 Add per-policy scenario comparison tests.
- [X] T007 Add aggregate per-policy metric tests.
- [X] T008 Add compatibility-mode exclusion tests.
- [X] T009 Add report and scope-guard tests.

## Phase 3: Implementation

- [X] T010 Implement Feature 074 analysis package.
- [X] T011 Implement required baseline policy registry verification.
- [X] T012 Implement per-policy scenario comparison.
- [X] T013 Implement per-policy aggregate metrics.
- [X] T014 Implement Feature 074 report.
- [X] T015 Implement scope validator.

## Phase 4: Validation and Handoff

- [X] T016 Run Feature 068R regression slice.
- [X] T017 Run Feature 069 regression slice.
- [X] T018 Run Feature 070 regression slice.
- [X] T019 Run Feature 071 regression slice.
- [X] T020 Run Feature 072 regression slice.
- [X] T021 Run Feature 073 regression slice.
- [X] T022 Run Feature 074 targeted tests.
- [X] T023 Run git diff check and Feature 074 scope validator.
- [X] T024 Commit and push only.

## Notes

Feature 074 must stay read-only. It must not open a PR, merge, change policy code, start training, generate campaign artifacts, or claim final evaluation results.
