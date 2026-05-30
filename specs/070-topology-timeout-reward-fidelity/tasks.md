# Tasks: Feature 070

**Input**: Spec Kit artifacts for `070-topology-timeout-reward-fidelity`  
**Prerequisites**: Feature 069 merged into `main`  
**Status**: Implementation not started

## Phase 1: Setup and Evidence Read

- [ ] T001 Verify branch starts from current `origin/main` after Feature 069.

Comment:
This prevents stale-branch contamination.
Acceptance:
- HEAD is based on the current main SHA after Feature 069.
Failure mode:
- Old Feature 069 implementation attempts leak into Feature 070.

- [ ] T002 Read Feature 069 report and blocker list.

Comment:
Feature 070 exists to resolve the blockers recorded by Feature 069.
Acceptance:
- Topology, timeout/drop, and reward blockers are listed before implementation.
Failure mode:
- Agent implements random mechanism work instead of blocker resolution.

- [ ] T003 Read paper mechanism registry and paper-to-code mapping.

Comment:
The implementation must be grounded in available paper evidence.
Acceptance:
- Evidence sources are listed in the implementation report.
Failure mode:
- Agent invents topology or equations.

## Phase 2: Topology Contract

- [ ] T004 Add tests for TopologyEvidenceReport.

Comment:
Structured topology must be explicit before neighbor legality is trusted.
Acceptance:
- Tests verify evidence source, adjacency status, and blocker handling.
Failure mode:
- A complete graph is assumed without paper-backed evidence.

- [ ] T005 Add tests for NeighborLegalityEvidence.

Comment:
Horizontal offloading must not allow self-destination or non-neighbor destinations.
Acceptance:
- Tests prove final legality requires topology and legal mask approval.
Failure mode:
- Legal mask alone is treated as enough topology evidence.

- [ ] T006 Implement topology evidence model and report section.

Comment:
The report must expose structured or blocked topology evidence.
Acceptance:
- Missing adjacency becomes an explicit blocker.
Failure mode:
- Missing evidence is hidden behind defaults.

## Phase 3: Timeout/Drop Contract

- [ ] T007 Add tests for TimeoutDropAccountingEvidence.

Comment:
Timeout/drop fidelity needs per-task terminal evidence.
Acceptance:
- Tests cover completed, dropped, and unresolved task terminal states.
Failure mode:
- Aggregate counters replace task-level accounting.

- [ ] T008 Implement timeout/drop accounting evidence.

Comment:
The report must show deadline, completion, terminal status, and drop reason.
Acceptance:
- Paper semantics status is explicit.
Failure mode:
- Runtime accounting is called paper-faithful without proof.

## Phase 4: Reward Contract

- [ ] T009 Add tests for RewardEquationEvidence.

Comment:
Recovered equation terms must be separated from assumptions.
Acceptance:
- Tests prove equation evidence can be recovered, assumption-backed, or blocked.
Failure mode:
- Reward timing is confused with reward equation fidelity.

- [ ] T010 Add tests for TerminalRewardEvidence.

Comment:
Terminal reward must be emitted after terminal outcome evidence.
Acceptance:
- Tests prove reward slot is at or after terminal slot.
Failure mode:
- Reward is emitted at decision time without terminal evidence.

- [ ] T011 Implement reward equation and terminal reward evidence.

Comment:
Reward fidelity needs both equation status and terminal timing status.
Acceptance:
- Report separates equation recovery from reward emission timing.
Failure mode:
- The implementation overclaims reward fidelity.

## Phase 5: Integrated Report

- [ ] T012 Implement Feature070FidelityReport.

Comment:
The final report must show all three blocker categories separately.
Acceptance:
- Report contains topology, timeout/drop, reward, regressions, blockers, and claim boundary.
Failure mode:
- Report collapses all blockers into one vague status.

- [ ] T013 Preserve Feature 068R and Feature 069 regression gates.

Comment:
Feature 070 must not break earlier fidelity layers.
Acceptance:
- Targeted Feature 068R and Feature 069 tests remain green.
Failure mode:
- Blocker resolution breaks already-merged readiness.

- [ ] T014 Run targeted validation.

Comment:
The merge gate must use relevant tests, not unrelated full-suite noise.
Acceptance:
- Feature 068R, Feature 069, and Feature 070 targeted tests pass.
Failure mode:
- Full-suite noise is misreported as Feature 070 status.

- [ ] T015 Run scope audit.

Comment:
Feature scope must stay clean.
Acceptance:
- Diff contains only approved Feature 070 paths.
Failure mode:
- Campaign artifacts, resources, or dependencies leak into the PR.

## Phase 6: PR Evidence

- [ ] T016 Record changed files, validation results, blocker status, claim boundary, and open risks in the PR.

Comment:
Reviewers need proof, not status theater.
Acceptance:
- PR body contains scope proof, validation proof, and unresolved blocker list.
Failure mode:
- PR claims success without enough audit evidence.
