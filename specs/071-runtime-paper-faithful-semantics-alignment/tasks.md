# Tasks: Feature 071

**Input**: Feature 070 runtime divergence evidence  
**Prerequisites**: Feature 070 evidence branch accepted for review  
**Status**: Spec Kit created; implementation pending

## Phase 1: Setup and Prior Evidence

- [X] T001 Confirm Feature 070 remote branch status.

Comment:
Feature 071 must start from Feature 070's recovered evidence and pass semantics, not stale `main`.
Acceptance:
- Feature 070 report has `passed=True`, zero blockers, runtime divergence visible, and no full paper reproduction claim.
Failure mode:
- Feature 071 starts from missing or stale evidence.

- [X] T002 Create Feature 071 branch from Feature 070 commit.

Comment:
Feature 071 depends on Feature 070 evidence recovery.
Acceptance:
- Branch `071-runtime-paper-faithful-semantics-alignment` exists from Feature 070 commit `3851cd3be63de09189d4ed45c038b34c9ca57aee` or newer.
Failure mode:
- Branch starts from `main` and loses Feature 070 recovery.

- [ ] T003 Read runtime helper files and prior evidence files.

Comment:
Implementation must be grounded in current helper behavior and recovered equations.
Acceptance:
- Read `paper_timeout.py`, `deadline_rules.py`, `reward_timing.py`, `runtime_model.py`, Feature 070 report, and paper notes.
Failure mode:
- Runtime behavior is changed blindly.

## Phase 2: Spec Kit Completion

- [X] T004 Create Feature 071 specification.

Comment:
Implementation needs a hard contract before code changes.
Acceptance:
- `spec.md` records deadline, terminal-state, reward, compatibility, and claim boundary contracts.
Failure mode:
- Agent implements vague runtime changes.

- [X] T005 Create Feature 071 plan and research decisions.

Comment:
This prevents training/campaign scope creep.
Acceptance:
- `plan.md` and `research.md` define boundaries, order, and rejected alternatives.
Failure mode:
- Feature expands into unrelated simulator rewrite.

- [X] T006 Create Feature 071 data model.

Comment:
Report and tests need explicit evidence objects.
Acceptance:
- `data-model.md` defines runtime mode, deadline evidence, terminal state evidence, reward evidence, compatibility evidence, and final report.
Failure mode:
- Report becomes unstructured prose.

## Phase 3: Tests First

- [ ] T007 Add paper-mode deadline strictness tests.

Comment:
This is the main divergence identified by Feature 070.
Acceptance:
- Completion before deadline succeeds; completion at deadline fails in paper mode.
Failure mode:
- Equality-at-deadline remains silently paper-compatible.

- [ ] T008 Add explicit compatibility-mode tests.

Comment:
Legacy behavior may remain only if named and tested.
Acceptance:
- Completion at deadline passes only in compatibility mode.
Failure mode:
- Legacy behavior stays default.

- [ ] T009 Add terminal-state consistency tests.

Comment:
Reward must depend on terminal state.
Acceptance:
- Completed tasks cannot carry drop reason; dropped tasks require terminal evidence; pending tasks cannot emit reward.
Failure mode:
- Contradictory terminal records still pass.

- [ ] T010 Add reward Eq. (20)-(23) tests.

Comment:
Runtime reward must use recovered paper equations.
Acceptance:
- Tests cover inactive reward, success reward, drop reward, Phi_priv, and Phi_pub.
Failure mode:
- Old completion-slot approximation remains hidden.

## Phase 4: Runtime Implementation

- [ ] T011 Align `paper_timeout.py` with paper and compatibility modes.

Comment:
Deadline strictness must be executable behavior.
Acceptance:
- Helper exposes deadline computation, strict success, and terminal status in paper mode; compatibility mode is explicit.
Failure mode:
- Different modules continue disagreeing about deadline semantics.

- [ ] T012 Align `deadline_rules.py` with `paper_timeout.py`.

Comment:
Avoid duplicated contradictory deadline rules.
Acceptance:
- `deadline_rules.py` delegates to or matches `paper_timeout.py`.
Failure mode:
- Two deadline implementations diverge.

- [ ] T013 Align `reward_timing.py` with Eq. (20)-(23).

Comment:
Feature 070 recovered the reward equations; Feature 071 must make them executable.
Acceptance:
- Runtime helpers compute Phi_priv, Phi_pub, success reward, drop reward, and inactive behavior.
Failure mode:
- Reward still uses old completion-slot approximation by default.

- [ ] T014 Modify `runtime_model.py` only if required.

Comment:
Broad lifecycle rewrites are risky.
Acceptance:
- If changed, the report justifies why terminal-state integration required it.
Failure mode:
- Unrelated simulator behavior changes sneak into Feature 071.

## Phase 5: Feature 071 Report

- [ ] T015 Implement Feature 071 analysis/report package.

Comment:
The branch needs a clear audit output.
Acceptance:
- Package reports paper mode, compatibility mode, deadline evidence, terminal-state evidence, reward evidence, regressions, claim boundary, and next feature.
Failure mode:
- Reviewer cannot tell what changed.

- [ ] T016 Add scope validator.

Comment:
Protect the branch from artifact/training/dependency pollution.
Acceptance:
- Scope validator accepts only approved Feature 071 paths.
Failure mode:
- Generated artifacts or unrelated runtime files leak in.

## Phase 6: Validation and Handoff

- [ ] T017 Run Feature 068R regression slice.

- [ ] T018 Run Feature 069 regression slice.

- [ ] T019 Run Feature 070 regression slice.

- [ ] T020 Run Feature 071 targeted tests.

- [ ] T021 Run `git diff --check` and scope validator.

- [ ] T022 Commit and push only.

Comment:
No PR and no merge.
Acceptance:
- Branch is pushed, SHA equality is proven, clean tree is shown, and no PR/merge occurred.
Failure mode:
- Agent opens PR or merges without review.
