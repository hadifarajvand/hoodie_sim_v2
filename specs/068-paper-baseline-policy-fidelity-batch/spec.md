# Feature Specification: Paper Baseline Policy Fidelity Batch

**Feature Branch**: `068-paper-baseline-policy-fidelity-batch`  
**Created**: 2026-05-29  
**Status**: Ready for implementation handoff  
**Input**: User description: "Define paper baseline policy fidelity for RO, FLC, VO, HO, BCO, and MLEO before implementation."

## Clarifications

### Session 2026-05-30

- This feature is a baseline-policy fidelity feature, not a HOODIE training feature.
- Implementation must stay inside the policy layer, policy registry, and targeted tests unless a documentation-only update is needed.
- The shared policy context and action mask are the contract for all baselines.
- MLEO must use total-delay estimates for candidate selection when required fields are present.
- Missing MLEO estimate inputs must produce an explicit, test-covered fallback path.
- This feature must not change simulator lifecycle, traffic generation, reward timing, generated artifacts, campaign outputs, or dependency files.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registry Coverage for Paper Baselines (Priority: P1)

As a reproduction maintainer, I want RO, FLC, VO, HO, BCO, and MLEO to resolve through one shared policy registry so that evaluation code can request each paper baseline by name without special-case wiring.

**Why this priority**: Without registry coverage, no fair baseline matrix can run. This is the smallest independently testable slice of the feature.

**Independent Test**: Resolve every required baseline name from the policy registry and call the shared action-selection interface with a controlled policy context.

**Acceptance Scenarios**:

1. **Given** the required baseline names, **When** the registry resolves each name, **Then** each returns a policy object.
2. **Given** a resolved policy object, **When** it receives a controlled policy context, **Then** it can choose through the shared interface.
3. **Given** any missing required baseline name, **When** the registry coverage test runs, **Then** the test fails.

---

### User Story 2 - Action-Mask Compliance (Priority: P1)

As a maintainer, I want every baseline to respect the action mask so that policies cannot choose actions unavailable to the source agent or current topology.

**Why this priority**: A baseline that bypasses the mask corrupts every downstream comparison and hides environment or topology drift.

**Independent Test**: Provide controlled masks that disable each baseline preferred action family and verify the selected action is still allowed, or that an explicit no-choice fallback is reported.

**Acceptance Scenarios**:

1. **Given** local compute is unavailable, **When** FLC chooses, **Then** it does not return a local action.
2. **Given** vertical offload is unavailable, **When** VO chooses, **Then** it does not return a vertical action.
3. **Given** horizontal offload is unavailable, **When** HO chooses, **Then** it does not return a horizontal action.
4. **Given** a seeded RO policy, **When** it chooses repeatedly, **Then** every sampled action is allowed and the sequence is reproducible.
5. **Given** BCO or MLEO cannot use its preferred candidate, **When** it chooses, **Then** documented fallback behavior is used.

---

### User Story 3 - MLEO Total-Delay Candidate Ranking (Priority: P1)

As a reproduction maintainer, I want MLEO to compare local, horizontal, and vertical candidates by estimated total delay so that it behaves like a minimum-latency baseline rather than a placeholder preference rule.

**Why this priority**: MLEO is one of the paper-facing baselines; if it is not delay-based, baseline comparison claims are weak.

**Independent Test**: Provide controlled local, horizontal, and vertical candidate delay fields and verify MLEO selects the allowed candidate with the smallest total estimated delay.

**Acceptance Scenarios**:

1. **Given** complete local, horizontal, and vertical candidate estimates, **When** MLEO ranks candidates, **Then** the lowest total-delay candidate is selected.
2. **Given** a lower-delay candidate is unavailable under the action mask, **When** MLEO ranks candidates, **Then** that candidate is skipped.
3. **Given** candidate totals tie, **When** MLEO ranks candidates, **Then** tie handling is deterministic and documented.
4. **Given** required estimate fields are missing, **When** MLEO cannot build comparable candidates, **Then** visible fallback behavior is used and tested.

---

### User Story 4 - Controlled Baseline Differentiation Evidence (Priority: P2)

As a project owner, I want controlled tests showing FLC, HO, VO, and MLEO can produce different action families so that later evaluation reports do not collapse baselines into identical behavior.

**Why this priority**: Prior audit evidence showed weak policy differentiation. This feature must prove that baseline behavior is separable under controlled inputs before larger campaigns rely on it.

**Independent Test**: Run all required baselines on shared contexts designed to separate their intended decisions and compare selected action families.

**Acceptance Scenarios**:

1. **Given** shared contexts, **When** each baseline chooses, **Then** each consumes the same context format.
2. **Given** context values favor different action families, **When** FLC, HO, VO, and MLEO choose, **Then** their selected action families can differ.
3. **Given** seeded randomness, **When** RO is repeated, **Then** the result is reproducible while still sampling only from allowed actions.

---

### Edge Cases

- Preferred action family is masked out.
- Only one action is available.
- No action is available and the policy must report a documented no-choice path.
- MLEO receives partial delay fields.
- MLEO receives tied total-delay candidates.
- MLEO receives mixed action aliases such as `local`, `compute_local`, `vertical`, and `offload_vertical`.
- RO receives a fixed seed and a single available action.
- BCO reaches the end of its balancing cycle.
- Horizontal offload is allowed by action family but no concrete destination is available.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose RO, FLC, VO, HO, BCO, and MLEO through the shared policy registry.
- **FR-002**: System MUST keep all required baselines on the shared PolicyContext action-selection interface.
- **FR-003**: System MUST ensure every baseline respects the supplied action mask.
- **FR-004**: FLC MUST prefer local compute when local compute is available.
- **FR-005**: VO MUST prefer vertical offload when vertical offload is available.
- **FR-006**: HO MUST prefer horizontal offload when horizontal offload is available.
- **FR-007**: RO MUST sample only from available actions and MUST support controlled seeding.
- **FR-008**: BCO MUST use documented balancing behavior and deterministic rollover behavior.
- **FR-009**: MLEO MUST build candidate estimates from available observation fields.
- **FR-010**: MLEO MUST remove unavailable candidates before ranking.
- **FR-011**: MLEO MUST rank comparable candidates by total estimated delay.
- **FR-012**: MLEO MUST use deterministic tie handling.
- **FR-013**: MLEO MUST expose documented fallback behavior when candidate estimates cannot be compared.
- **FR-014**: Tests MUST cover registry coverage, mask behavior, deterministic baselines, RO seeding, BCO balancing, MLEO ranking, MLEO tie handling, MLEO fallback, and controlled differentiation.
- **FR-015**: This feature MUST NOT change environment lifecycle, task execution, traffic generation, reward timing, training, generated artifacts, campaign outputs, or dependency files.

### Key Entities *(include if feature involves data)*

- **BaselinePolicy**: A policy implementation for one paper baseline; key attributes are baseline name, preference rule, fallback rule, and deterministic or seeded behavior.
- **PolicyContext**: Shared policy input containing observation data, legal-action mask, optional trace history, and optional seed or RNG source.
- **DelayCandidate**: MLEO candidate containing action family, action id or alias, queue delay, transmission delay, compute delay, total delay, availability, tie-break key, and fallback notes.
- **BaselineFidelityEvidence**: Test evidence proving registry coverage, mask behavior, delay ranking, fallback behavior, and controlled differentiation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All six required baselines resolve from the registry in targeted tests.
- **SC-002**: Targeted tests prove every baseline returns an available action or documented no-choice result.
- **SC-003**: MLEO selects the available minimum-delay candidate in controlled tests.
- **SC-004**: MLEO tie handling is deterministic in targeted tests.
- **SC-005**: Missing MLEO estimate fields produce visible fallback behavior covered by tests.
- **SC-006**: Controlled contexts demonstrate distinct behavior for FLC, HO, VO, and MLEO.
- **SC-007**: Scope audit confirms no environment, training, artifact, campaign-output, or dependency files changed.

## Assumptions

Any assumption that materially changes code, workflow, or repository state MUST be recorded and presented for approval before implementation depends on it.

- Full paper experiment reproduction is out of scope for this feature.
- This feature may use current observation fields and documented fallback behavior until a later feature expands simulator observations.
- Baseline fairness requires shared policy context, shared action masks, and shared evaluation wiring.
- Paper-to-code mapping is updated only if implementation changes the mapping between baseline concepts and code paths.

## Production Constraints

- [x] Performance budgets identified: no campaign-scale execution belongs to this feature.
- [x] Artifact handling rules identified: no generated artifacts are refreshed by this feature.
- [x] Security and secret-hygiene constraints identified: no secrets, tokens, or remote service calls are required.
- [x] CI quality gate impact identified: targeted unit and integration tests are required.

## Public Interfaces Affected

- [ ] Environment reset/step
- [x] Policy interface
- [ ] Task model
- [ ] Topology interface
- [ ] Runtime model interface
- [ ] Evaluation metric interface
- [x] Config schema
- [ ] Artifact schema

## Config / Schema Impact

- [x] Required config fields identified: no new global config is expected.
- [x] Validation rules identified: mask behavior, seed behavior, candidate ranking, fallback behavior.
- [x] Backward-compatibility impact identified: existing baseline names must remain resolvable.

## Artifact Impact

- [ ] Raw metrics
- [ ] Plots
- [ ] Reports
- [ ] Checkpoints
- [ ] Debug traces
- [x] Validation summaries

## Security Considerations

- [x] Secrets / tokens / credentials reviewed: not used.
- [x] Remote code execution reviewed: not introduced.
- [x] External references documented: no runtime external reference is required.

## Definition of Done

- [x] Spec matched by plan.
- [x] Tests identified.
- [x] Assumptions documented.
- [x] Configs validated or updated.
- [x] Paper-to-code mapping update rule documented.
- [x] Artifacts handled per lifecycle rules.
- [x] Review and merge gate satisfied before implementation begins.
