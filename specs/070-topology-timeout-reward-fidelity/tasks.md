# Tasks: Feature 070

**Input**: Spec Kit artifacts for `070-topology-timeout-reward-fidelity`  
**Prerequisites**: Feature 069 merged into `main`  
**Status**: Implementation branch under review; blocker-resolution refinement required

## Phase 1: Setup and Evidence Read

- [X] T001 Verify branch starts from current `origin/main` after Feature 069.

Comment:
This prevents stale-branch contamination.
Acceptance:
- HEAD is based on the current main SHA after Feature 069.
Failure mode:
- Old Feature 069 implementation attempts leak into Feature 070.

- [X] T002 Read Feature 069 report and blocker list.

Comment:
Feature 070 exists to resolve the blockers recorded by Feature 069.
Acceptance:
- Topology, timeout/drop, and reward blockers are listed before implementation.
Failure mode:
- Agent implements random mechanism work instead of blocker resolution.

- [X] T003 Read paper mechanism registry and paper-to-code mapping.

Comment:
The implementation must be grounded in available paper evidence.
Acceptance:
- Evidence sources are listed in the implementation report.
Failure mode:
- Agent invents topology or equations.

## Phase 2: Topology Contract

- [X] T004 Add tests for TopologyEvidenceReport.

Comment:
Structured topology must be explicit before neighbor legality is trusted.
Acceptance:
- Tests verify evidence source, adjacency status, and blocker handling.
Failure mode:
- A complete graph is assumed without paper-backed evidence.

- [X] T005 Add tests for NeighborLegalityEvidence.

Comment:
Horizontal offloading must not allow self-destination or non-neighbor destinations.
Acceptance:
- Tests prove final legality requires topology and legal mask approval.
Failure mode:
- Legal mask alone is treated as enough topology evidence.

- [X] T006R Search for existing topology or adjacency evidence.

Comment:
The current implementation preserves the topology blocker. Before leaving it blocked, the agent must search committed evidence for an adjacency matrix, Figure 7 extraction, action-space topology mapping, or topology helper.
Acceptance:
- Search results are recorded in the Feature 070 handoff.
- If no structured evidence exists, the report says exactly what was searched.
Failure mode:
- Topology remains blocked even though the evidence already exists somewhere in the repo or prior files.

- [X] T007R Add manual topology evidence intake.

Comment:
The user may already have manually extracted adjacency from the paper. The implementation must support that evidence without pretending it is runtime-derived truth.
Acceptance:
- Manual topology evidence can be represented as edge list or labeled adjacency matrix.
- Provenance records extraction method, source reference, confidence, and reviewer note.
- Invalid self-edges and mismatched labels are rejected.
Failure mode:
- User-supplied topology is either ignored or silently treated as verified runtime fact.

- [X] T008R Derive neighbor map from structured evidence.

Comment:
Neighbor legality must come from topology evidence, not from a hard-coded complete graph.
Acceptance:
- Neighbor map is derived from manual or source-backed topology evidence.
- Self-destination is illegal.
- Final legality requires topology legality and legal mask legality.
Failure mode:
- Legal mask alone is treated as enough topology evidence.

## Phase 3: Timeout/Drop Contract

- [X] T009 Add tests for TimeoutDropAccountingEvidence.

Comment:
Timeout/drop fidelity needs per-task terminal evidence.
Acceptance:
- Tests cover completed, dropped, and unresolved task terminal states.
Failure mode:
- Aggregate counters replace task-level accounting.

- [X] T010R Search for timeout/drop paper and runtime evidence.

Comment:
The implementation must try to recover the accounting rule before keeping it blocker-backed.
Acceptance:
- Existing runtime files and paper mechanism registry references are inspected.
- Evidence distinguishes paper rule, runtime compatibility behavior, and unresolved gaps.
Failure mode:
- Runtime behavior is called paper-faithful without source evidence.

- [X] T011R Implement TimeoutDropRuleEvidence.

Comment:
The report needs a separate rule-level object, not only per-task example evidence.
Acceptance:
- Rule text, timeout relation, drop condition, provenance, and paper semantics status are represented.
- Unverified rules remain assumption-backed or blocked.
Failure mode:
- Per-task sample evidence is mistaken for the paper rule.

- [ ] T012R Strengthen timeout/drop validation.

Comment:
Task-level accounting must enforce terminal-state consistency.
Acceptance:
- Completed task with drop reason is rejected.
- Dropped task without terminal slot is rejected.
- Absolute deadline must equal arrival slot plus timeout length when that rule is claimed.
Failure mode:
- Contradictory terminal evidence still passes.

## Phase 4: Reward Contract

- [X] T013 Add tests for RewardEquationEvidence.

Comment:
Recovered equation terms must be separated from assumptions.
Acceptance:
- Tests prove equation evidence can be recovered, assumption-backed, or blocked.
Failure mode:
- Reward timing is confused with reward equation fidelity.

- [X] T014 Add tests for TerminalRewardEvidence.

Comment:
Terminal reward must be emitted after terminal outcome evidence.
Acceptance:
- Tests prove reward slot is at or after terminal slot.
Failure mode:
- Reward is emitted at decision time without terminal evidence.

- [X] T015R Search for exact reward equation evidence.

Comment:
The current implementation correctly avoids overclaiming reward fidelity. Next it must search for the equation before keeping it blocked.
Acceptance:
- Search includes paper mechanism registry, paper-to-code mapping, reward timing code, reward equation analysis contracts, and environment reward files.
- If exact equation is missing, the report states what was searched.
Failure mode:
- Reward equation remains blocked without evidence recovery attempt.

- [X] T016R Implement reward equation provenance and term validation.

Comment:
Equation text and inferred terms must be separated.
Acceptance:
- Verified equation text requires source reference.
- Inferred terms are marked assumption-backed.
- Terminal reward can be timing-valid while equation recovery remains blocked.
Failure mode:
- Timing validity is falsely treated as reward equation recovery.

## Phase 5: Integrated Report

- [X] T017 Implement Feature070FidelityReport.

Comment:
The final report must show all three blocker categories separately.
Acceptance:
- Report contains topology, timeout/drop, reward, regressions, blockers, and claim boundary.
Failure mode:
- Report collapses all blockers into one vague status.

- [X] T018 Preserve Feature 068R and Feature 069 regression gates.

Comment:
Feature 070 must not break earlier fidelity layers.
Acceptance:
- Targeted Feature 068R and Feature 069 tests remain green.
Failure mode:
- Blocker resolution breaks already-merged readiness.

- [X] T019 Enforce terminal reward pass gate.

Comment:
A passed report must not be possible with invalid terminal reward timing or reward slot before terminal slot.
Acceptance:
- `passed=True` is rejected when `timing_valid=False`.
- `passed=True` is rejected when `reward_slot < terminal_slot`.
Failure mode:
- A boolean can lie about reward timing and still produce a green report.

- [X] T020R Update report to include recovery search results.

Comment:
The reviewer must see whether blockers remained because evidence was unavailable or because the agent failed to search.
Acceptance:
- Report lists searched sources for topology, timeout/drop, and reward.
- Report marks each category as verified, manual-paper-evidence, assumption-backed, or blocked.
Failure mode:
- Blockers remain without actionable recovery trail.

- [X] T021R Run targeted validation after blocker-recovery refinement.

Comment:
The merge gate must use relevant tests, not unrelated full-suite noise.
Acceptance:
- Feature 068R, Feature 069, and Feature 070 targeted tests pass.
Failure mode:
- Full-suite noise is misreported as Feature 070 status.

- [X] T022R Run scope audit.

Comment:
Feature scope must stay clean.
Acceptance:
- Diff contains only approved Feature 070 paths.
Failure mode:
- Campaign artifacts, resources, or dependencies leak into the branch.

## Phase 6: Handoff Evidence

- [X] T023R Record changed files, validation results, blocker status, claim boundary, open risks, and any user-input needs.

Comment:
Reviewers need proof, not status theater.
Acceptance:
- Handoff includes scope proof, validation proof, unresolved blocker list, and exactly what user evidence is still needed.
Failure mode:
- Handoff claims progress without saying what remains missing.
