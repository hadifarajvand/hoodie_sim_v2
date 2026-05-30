# Tasks: Feature 069

**Input**: Spec Kit artifacts for `069-full-hoodie-mechanism-fidelity-batch`  
**Prerequisites**: Feature 068R merged into `main`  
**Status**: Implementation not started

## Phase 1: Setup and Scope Gate

- [ ] T001 Verify branch starts from current `origin/main` after Feature 068R.

Comment:
This task prevents stale-branch contamination.
Acceptance:
- `HEAD` is based on the current `origin/main`.
Failure mode:
- Work starts from an old branch and drags unrelated files into scope.

- [ ] T002 Read Feature 068R Spec Kit and targeted tests.

Comment:
Feature 069 must protect the baseline placement repair.
Acceptance:
- Feature 068R dependency is explicitly acknowledged in implementation notes.
Failure mode:
- Mechanism work silently breaks policy behavior.

- [ ] T003 Read the paper mechanism registry and paper-to-code mapping.

Comment:
Feature 069 must be grounded in existing paper evidence.
Acceptance:
- Known blockers and high-risk assumptions are listed before implementation.
Failure mode:
- Agent invents topology, reward, timeout, or delay semantics.

## Phase 2: Contract Test Design

- [ ] T004 Add Feature 068R regression tests to the Feature 069 validation slice.

Comment:
Mechanism fidelity is invalid if it damages baseline policy fidelity.
Acceptance:
- Registry, mask authority, seeded RO, BCO balance hint, and MLEO metadata tests run in the validation slice.
Failure mode:
- The implementation passes mechanism tests while breaking Feature 068R.

- [ ] T005 Define coordination graph contract tests.

Comment:
Neighbor/coordination evidence must be explicit and auditable.
Acceptance:
- Tests distinguish structured evidence, assumption-backed evidence, and blockers.
Failure mode:
- Hard-coded topology is treated as paper fact.

- [ ] T006 Define synchronization contract tests.

Comment:
Mechanism correctness depends on ordering across the slot lifecycle.
Acceptance:
- Tests verify decision, action application, queue update, terminal accounting, and reward emission ordering.
Failure mode:
- Isolated helper tests miss lifecycle drift.

- [ ] T007 Define delayed reward contract tests.

Comment:
Delayed reward must be connected to terminal task outcomes.
Acceptance:
- Tests prove reward is emitted after terminal outcome evidence.
Failure mode:
- Reward is emitted too early or without outcome linkage.

- [ ] T008 Define congestion and queue-pressure tests.

Comment:
Private, public, and cloud queue pressure drive mechanism fidelity.
Acceptance:
- Tests cover local/private, horizontal/public, and cloud paths.
Failure mode:
- Queue evidence collapses back to family-only behavior.

## Phase 3: Mechanism Modeling

- [ ] T009 Implement CoordinationGraphContract only if evidence is available.

Comment:
Topology must not be invented.
Acceptance:
- Missing evidence becomes a blocker, not a fake implementation.
Failure mode:
- Agent encodes unsupported adjacency assumptions.

- [ ] T010 Implement SynchronizationContract evidence.

Comment:
The report must show the slot lifecycle order.
Acceptance:
- Evidence includes the expected ordered phases.
Failure mode:
- Report contains unordered snapshots.

- [ ] T011 Implement DelayedRewardContract evidence.

Comment:
Delayed reward is a central HOODIE mechanism.
Acceptance:
- Evidence links decision, terminal outcome, and reward emission.
Failure mode:
- Reward evidence is detached from task outcome.

- [ ] T012 Implement CongestionControlContract evidence.

Comment:
Queue pressure must be visible for placement decisions.
Acceptance:
- Evidence distinguishes private/public/cloud queues.
Failure mode:
- Congestion evidence is too generic to support placement fidelity.

## Phase 4: Report and Validation

- [ ] T013 Produce a MechanismFidelityReport.

Comment:
The final output must be reviewable and claim-safe.
Acceptance:
- Report separates verified behavior, assumptions, fallback, and blockers.
Failure mode:
- Report overclaims paper reproduction.

- [ ] T014 Validate report schema.

Comment:
Structured report evidence prevents vague handoff claims.
Acceptance:
- Required schema fields are present.
Failure mode:
- Report cannot support future thesis or paper writing.

- [ ] T015 Run targeted validation.

Comment:
Only relevant tests should be used as the merge gate.
Acceptance:
- Feature 068R regression tests and Feature 069 contract tests pass.
Failure mode:
- Full-suite noise is misrepresented as Feature 069 failure or success.

- [ ] T016 Run scope audit.

Comment:
Scope contamination previously caused invalid branches.
Acceptance:
- Diff contains only approved files.
Failure mode:
- Feature 069 accidentally includes artifacts, campaign outputs, or unrelated runtime files.

## Phase 5: PR Evidence

- [ ] T017 Record changed files, validation commands, blockers, claim boundary, and open risks in the PR.

Comment:
Reviewers need operational proof, not vague status.
Acceptance:
- PR body includes scope proof, validation proof, and claim boundary.
Failure mode:
- PR claims success without enough audit evidence.
