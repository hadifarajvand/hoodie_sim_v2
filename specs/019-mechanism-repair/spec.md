# Feature Specification: Mechanism Repair

**Feature Branch**: `[019-mechanism-repair]`  
**Created**: 2026-05-10  
**Status**: Draft  
**Input**: User description: "Create a tightly scoped mechanism repair feature for the HOODIE reproduction project, gated only on exact divergences identified by Feature 018."

## Clarifications

### Session 2026-05-10

- Q: Which exact Feature 018 finding is eligible for repair? → A: Only `case-timeout-drop` is eligible for repair.
- Q: Which environment module owns timeout/drop terminal accounting? → A: The public environment adapter boundary owns timeout/drop terminal accounting.
- Q: Which regression test will reproduce the timeout/drop divergence? → A: A public `step`-lifecycle regression test that asserts `terminal_outcome == dropped` and reward is emitted only at terminal finalization.
- Q: Whether existing metrics are read-only in this feature? → A: Existing metrics are read-only; no metric formula changes are allowed.
- Q: Whether Feature 018 artifacts should be regenerated after repair? → A: Regenerate the Feature 018 differential audit after the repair.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Repair Confirmed Divergence (Priority: P1)

As a maintainer, I want a surgical repair path for the one confirmed Feature 018 divergence so the current environment can respect timeout/drop terminal behavior without disturbing unrelated behavior.

**Why this priority**: This is the only confirmed repair target in the committed audit artifact. It is the minimal useful scope and the only place where the feature is justified.

**Independent Test**: The timeout/drop regression can be reproduced before repair, then passes after a minimal patch, while the rest of the audited behavior remains unchanged.

**Acceptance Scenarios**:

1. **Given** the committed Feature 018 audit, **When** the timeout/drop case is exercised, **Then** the environment is reported as diverging from the reference terminal outcome until the repair is applied.
2. **Given** the repair is applied, **When** the same timeout/drop regression test runs, **Then** the terminal outcome matches the timeout/drop expectation and delayed reward still emits only at terminal completion or drop.

### User Story 2 - Guard Against Scope Drift (Priority: P2)

As a maintainer, I want the repair scope to stay surgical so that unrelated simulator behavior, metrics, campaigns, and baseline behavior do not change as collateral damage.

**Why this priority**: A narrow repair is only valuable if it stays narrow. Scope drift would turn a mechanism repair into a simulator rewrite.

**Independent Test**: The regression suite proves that only the confirmed timeout/drop divergence is addressed and that other Feature 018 findings remain unrepaired unless a separate concrete divergence is proven.

**Acceptance Scenarios**:

1. **Given** the Feature 018 audit findings, **When** the repair is proposed, **Then** only confirmed divergences are eligible for fixes.
2. **Given** the repair is complete, **When** the regression suite is run, **Then** unrelated behavior still follows the prior observed contract.

### User Story 3 - Protect Existing Contracts (Priority: P3)

As a maintainer, I want the repair feature to preserve the existing environment interface and surrounding repository contracts so the repair does not silently change the reproduction surface.

**Why this priority**: The project’s value depends on reproducibility. The repair must not weaken that by changing interfaces or metrics behind the scenes.

**Independent Test**: The existing public environment behavior and Feature 017 reference kernel tests continue to pass after the repair.

**Acceptance Scenarios**:

1. **Given** the pre-repair test suite, **When** the repair is applied, **Then** the relevant Feature 017 and Feature 018 targeted tests still pass.
2. **Given** the environment public interface, **When** the regression suite runs, **Then** the interface remains stable and no unrelated paths change.

### Edge Cases

- What happens when the timeout/drop case remains unchanged after a proposed patch? The feature must reject the patch as incomplete.
- What happens when a proposed change affects offload or ordering behavior? The feature must treat it as out of scope unless the committed audit proves a separate concrete divergence.
- What happens when the repair would require a metric formula change? The feature must block that change unless the audit proves the metric is wrong, which it does not for this feature.
- What happens when a proposed change is a speculative refactor rather than a confirmed divergence fix? The feature must reject it as out of scope.
- What happens to non-repaired Feature 018 findings? They must remain documented as unrepaired in the regenerated audit and in any repair summary.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repair feature MUST be explicitly gated on the exact divergences identified in the committed Feature 018 audit artifacts.
- **FR-002**: The repair scope MUST treat `case-timeout-drop` as the only confirmed repair target unless another exact divergence is proven in the committed audit artifact.
- **FR-003**: Environment changes MUST be surgical and MUST not alter unrelated behavior, including offload behavior, ordering behavior, campaign behavior, baseline behavior, or public interface contracts.
- **FR-004**: Metric formula changes MUST be forbidden unless the differential audit proves a metric is wrong; this feature does not grant that proof.
- **FR-005**: Every repair MUST be paired with a regression test, and the regression test requirement MUST be treated as a first-class rule.
- **FR-006**: The feature MUST separate confirmed divergence fixes from speculative refactors so scope cannot drift.
- **FR-007**: The repair MUST preserve the delayed reward rule: reward is emitted only on task completion or drop.
- **FR-008**: The repair MUST preserve one-slot simulator step semantics and same-slot deterministic ordering.
- **FR-009**: The repair MUST preserve the existing environment public interface and baseline execution path.
- **FR-010**: The feature MUST not include offload instrumentation repair, topology repair, or any speculative cleanup unless a separate concrete divergence is proven.
- **FR-011**: Existing metrics MUST be treated as read-only in this feature unless a differential audit proves a metric bug, which this feature does not assert.
- **FR-012**: The regenerated Feature 018 differential audit MUST be used to verify whether `case-timeout-drop` remains a divergence after the repair.
- **FR-013**: All non-repaired Feature 018 findings MUST remain documented as unrepaired and MUST not be normalized away.

### Key Entities *(include if feature involves data)*

- **Confirmed Divergence**: A discrepancy recorded in the committed Feature 018 audit artifact with a specific classification and evidence trail.
- **Repair Target**: The exact environment behavior allowed to change under this feature, currently limited to timeout/drop terminal accounting.
- **Regression Test**: A test that reproduces the divergence before repair and confirms the repaired behavior after the change.
- **Non-Repair Finding**: An audit finding that remains outside scope unless later proven to be a concrete environment bug.
- **Speculative Refactor**: Any proposed change that does not directly address the confirmed timeout/drop divergence, including offload, ordering, topology, or metric changes without proof of a bug.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The timeout/drop regression is reproducible before the repair and passes after the repair in 100% of targeted runs.
- **SC-002**: At least 1 regression test is added for every repaired divergence, and 100% of repaired divergences are covered.
- **SC-003**: All previously passing Feature 017 targeted tests remain passing after the repair.
- **SC-004**: The regenerated Feature 018 audit no longer reports the repaired timeout/drop case as a divergence unless the behavior still genuinely differs from the reference contract.
- **SC-005**: All non-repaired Feature 018 findings remain classified as unrepaired, with no silent normalization of their status.
- **SC-006**: No speculative refactor is accepted as a repair, and any such proposal is rejected before implementation.

## Assumptions

- The only confirmed repair target is the timeout/drop terminal behavior shown in the committed Feature 018 audit.
- Feature 018 findings classified as instrumentation gaps or assumption gaps remain out of scope unless new evidence proves a concrete environment bug.
- The repair should favor the smallest local change that corrects the confirmed divergence.
- The existing environment public interface is preserved unless the regression test proves a local timeout/drop fix requires an internal adjustment.
- Feature 018 findings that are not confirmed divergences remain unrepaired and are preserved as documented evidence.

## Production Constraints

- [x] Performance budgets identified
- [x] Artifact handling rules identified
- [x] Security and secret-hygiene constraints identified
- [x] CI quality gate impact identified

## Public Interfaces Affected

- [x] Environment reset/step
- [ ] Policy interface
- [x] Task model
- [ ] Topology interface
- [ ] Runtime model interface
- [x] Evaluation metric interface
- [ ] Config schema
- [ ] Artifact schema

## Config / Schema Impact

- [x] Required config fields identified
- [x] Validation rules identified
- [x] Backward-compatibility impact identified

## Artifact Impact

- [ ] Raw metrics
- [ ] Plots
- [x] Reports
- [ ] Checkpoints
- [x] Debug traces
- [x] Validation summaries

## Security Considerations

- [x] Secrets / tokens / credentials reviewed
- [x] Remote code execution reviewed
- [x] External references documented

## Definition of Done

- [x] Spec matched by plan
- [x] Tests identified
- [x] Assumptions documented
- [x] Configs validated or updated
- [x] Paper-to-code mapping updated
- [x] Artifacts handled per lifecycle rules
- [x] Review and merge gate satisfied
