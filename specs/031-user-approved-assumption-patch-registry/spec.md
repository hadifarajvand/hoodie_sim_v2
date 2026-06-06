# Feature Specification: User-Approved Assumption Patch Registry

**Feature Branch**: `031-user-approved-assumption-patch-registry`  
**Created**: 2026-05-12  
**Status**: Draft  
**Input**: User description: "Create a controlled assumption patch registry that records user-approved assumptions for unrecoverable paper gaps without misclassifying them as recovered paper values."

## Clarifications

### Session 2026-05-12

- Q: What assumption statuses and runtime-use rules should the registry enforce? → A: Use `proposed`, `approved`, `rejected`, and `blocked_no_assumption`; runtime may use only approved assumptions; proposed assumptions are report-only; rejected and blocked assumptions must never be consumed by runtime.
- Q: How should paper status be preserved? → A: Never rewrite Feature 030 unrecoverable items as recovered; preserve `paper_status` separately from `assumption_status` for every registry entry.
- Q: Which high-risk items need manual user values versus safe proposed defaults? → A: `Figure_7_adjacency` requires a user-supplied/manual topology; `legal_horizontal_destinations` depends on topology and cannot be patched independently; EA CPU capacities may reuse current runtime assumptions only if explicitly approved; `cloud_data_rate` may reuse the vertical data-rate assumption only if explicitly approved; `timeout_value` requires an explicit user-supplied timeout rule/value; `multi_agent_aggregation_reduction_order` can be safely proposed as per-agent episode cumulative reward followed by arithmetic mean across agents.
- Q: Should Feature 031 fold in governance/docs reconciliation as a patch or minor update? → A: MINOR update; keep the approved interpreter/runtime guidance reconciliation, set the constitution and sync report/footer to `1.4.0`, and retain the intentionally added governance principles.
- Q: Is runtime adoption of assumptions part of Feature 031? → A: No; runtime adoption remains out of scope for Feature 031 and must be a later feature if ever approved.

## Governance and Runtime Guidance Reconciliation

Feature 031 intentionally includes governance/runtime-guidance reconciliation because the assumption registry depends on the approved interpreter and reproducibility guidance being internally consistent. This governance work is part of the same feature only to keep the branch diff intentional and to prevent accidental pollution from lingering constitution/docs edits.

The governance correction is a MINOR constitution expansion, not a patch:

- Constitution version: `1.4.0`
- Sync Impact Report version: `1.4.0`
- Constitution footer version: `1.4.0`
- Approved interpreter path: `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`

The MINOR bump is required because principles 21 through 30 were intentionally added. The expanded governance content must remain explicit and internally consistent across the constitution, plan, and supporting docs.

Scope of the governance/docs reconciliation:

1. `.specify/memory/constitution.md` to keep the versioning, version report, and interpreter guidance wording aligned.
2. `AGENTS.md` only if needed to keep the governance entry point aligned with the current Feature 031 workflow and plan reference.
3. `docs/reproducibility.md` only if needed to keep runtime guidance aligned with the approved interpreter path.
4. `.specify/feature.json` only as active Spec Kit metadata pointing to Feature 031, and only for explicit workflow handling before merge.

This reconciliation must not modify runtime behavior, must not change the Feature 031 registry/report outputs, and must not claim any runtime adoption of registry assumptions. Runtime adoption of registry assumptions remains out of scope for Feature 031 and must be handled by a later feature if ever approved.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Review Assumptions (Priority: P1)

As a reviewer, I want every unrecoverable paper gap to appear as an explicit assumption candidate or remain blocked, so later runtime work cannot silently treat missing paper evidence as recovered truth.

**Why this priority**: If this registry is incomplete or ambiguous, downstream simulator and training work can drift into fabricated topology, capacity, timeout, or reward semantics.

**Independent Test**: A reviewer can inspect the registry and confirm that every in-scope unrecoverable item is either blocked or has a clearly labeled proposed or approved assumption.

**Acceptance Scenarios**:

1. **Given** the Feature 030 closure report, **When** the registry is generated, **Then** every in-scope unrecoverable item appears with a paper-status and assumption-status.
2. **Given** an item with no approved assumption, **When** the registry is reviewed, **Then** it remains blocked and is not misclassified as paper-backed.
3. **Given** a candidate with no safe default, **When** the registry is created, **Then** it is marked `blocked_no_assumption` until a user supplies or approves a value.

### User Story 2 - Approve Runtime Assumptions (Priority: P2)

As an approver, I want proposed runtime assumptions to be recorded with rationale, risk, and affected components, so I can make an informed approval decision without changing paper evidence.

**Why this priority**: The project needs explicit runtime decisions for gaps such as topology legality, CPU capacity, timeout handling, cloud data-rate assumptions, and reward aggregation order.

**Independent Test**: A reviewer can approve or reject a proposed assumption and see that the registry records the decision without altering the paper recovery status.

**Acceptance Scenarios**:

1. **Given** a proposed assumption for an unrecoverable item, **When** it is approved, **Then** the registry records the approval source, runtime-use permission, and rationale.
2. **Given** a proposed assumption for an unrecoverable item, **When** it is rejected, **Then** the registry records the rejection and the item remains blocked for runtime use.
3. **Given** a runtime-approved assumption, **When** downstream consumers inspect the registry, **Then** they can see the exact approved value and the affected runtime components without any paper-recovery claim.

### User Story 3 - Audit Downstream Use (Priority: P3)

As an auditor, I want a report that shows which values may be used at runtime and which remain blocked, so future implementation work can rely on the registry without inventing values.

**Why this priority**: The registry is only useful if downstream users can tell the difference between approved assumptions, rejected assumptions, and unresolved paper gaps.

**Independent Test**: An auditor can regenerate the report from the same inputs and confirm that runtime-use eligibility matches the registry decisions.

**Acceptance Scenarios**:

1. **Given** the same closure report input, **When** the patch registry report is regenerated, **Then** the output is deterministic and preserves the same approvals and blocks.
2. **Given** an item with `runtime_use_allowed = false`, **When** the report is read, **Then** it is clearly listed as blocked.
3. **Given** a `proposed` item, **When** the report is read, **Then** it is labeled report-only and not eligible for runtime consumption.

### Edge Cases

- What happens when the same item appears in both a proposed assumption list and a blocked-items list?
- How does the registry handle an approved assumption that later becomes contradicted by a future paper recovery attempt?
- What happens when a user review records no decision yet?
- What happens when multiple runtime assumptions are possible for the same unresolved item?
- How should the registry surface a proposed value that is safe for runtime only after a user approval?
- What happens if the constitution sync report and footer disagree on the version number?
- How should Feature 031 treat governance/docs cleanup when the approved interpreter path changes but runtime behavior must remain untouched?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST ingest the Feature 030 assumption-closure report as the source gate for all candidate items.
- **FR-002**: The system MUST create a registry entry for each in-scope item from the Feature 030 closure report.
- **FR-003**: The system MUST record `paper_status` separately from `assumption_status` so paper gaps are never reclassified as recovered paper values.
- **FR-004**: The system MUST support `proposed`, `approved`, `rejected`, and `blocked_no_assumption` assumption states for each candidate item.
- **FR-005**: The system MUST record whether runtime use is allowed for each item.
- **FR-006**: The system MUST record whether user approval is required before any runtime use.
- **FR-007**: The system MUST preserve a rationale, scientific risk note, affected runtime components, and validation plan for every item.
- **FR-008**: The system MUST include a flag stating that no entry is a paper recovery claim.
- **FR-009**: The system MUST list unresolved blocked items separately from approved assumptions.
- **FR-010**: The system MUST prevent any approved assumption from being written back as a recovered paper fact.
- **FR-011**: The system MUST generate a machine-readable registry and a human-readable report.
- **FR-012**: The system MUST remain analysis-only unless a later approved plan explicitly applies a runtime config or contract patch.
- **FR-013**: The system MUST mark `Figure_7_adjacency` as requiring a user-supplied/manual topology and MUST NOT auto-generate topology.
- **FR-014**: The system MUST mark `legal_horizontal_destinations` as blocked unless topology is explicitly provided.
- **FR-015**: The system MUST allow `EA_private_cpu_capacity`, `EA_public_cpu_capacity`, and `cloud_cpu_capacity` to reuse current runtime assumptions only after explicit user approval.
- **FR-016**: The system MUST allow `cloud_data_rate` to reuse the current vertical data-rate assumption only after explicit user approval.
- **FR-017**: The system MUST require an explicit timeout rule/value for `timeout_value` and MUST NOT invent a timeout.
- **FR-018**: The system MUST allow `multi_agent_aggregation_reduction_order` to be proposed as per-agent episode cumulative reward followed by arithmetic mean across agents, with runtime use only after approval.
- **FR-019**: The feature MUST keep the governance/docs reconciliation scoped to the approved interpreter/runtime guidance correction and intentionally retained governance principles 21 through 30.
- **FR-020**: The feature MUST keep the constitution sync report version, constitution footer version, and reproducibility guidance aligned at `1.4.0`.
- **FR-021**: The feature MUST record the approved interpreter path `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python` consistently in governance/runtime guidance documents that reference the execution environment.
- **FR-022**: The feature MUST ensure Feature 031 registry/report artifacts remain unchanged by the governance/docs reconciliation.

### Key Entities *(include if feature involves data)*

- **Assumption Patch Registry Entry**: One item-level decision record containing paper status, assumption status, proposed value, runtime eligibility, approval source, rationale, and validation plan.
- **Patch Registry Report**: The generated audit report listing the entries, unresolved blocked items, and approval state summary.
- **Governance Reconciliation Record**: The governance/docs update that aligns constitution versioning, interpreter guidance, and reproducibility notes without changing runtime behavior.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of in-scope unrecoverable paper-gap items appear in the registry with exactly one assumption-status.
- **SC-002**: 0 approved entries are labeled as paper-backed recoveries.
- **SC-003**: 100% of registry entries include rationale, scientific risk, affected components, and validation plan.
- **SC-004**: Reviewers can distinguish blocked items from runtime-eligible assumptions in a single pass without needing to inspect raw paper OCR.
- **SC-005**: Regenerating the report from unchanged inputs produces identical item ordering and identical status counts.
- **SC-006**: Any item with `runtime_use_allowed = true` must also have `assumption_status = approved`.
- **SC-007**: Any item with `assumption_status = proposed` must remain report-only and excluded from runtime consumption.
- **SC-008**: The constitution sync report and footer show the same version number on every review, and that version is `1.4.0`.
- **SC-009**: Reviewers can verify the approved interpreter path is consistent across the constitution and reproducibility guidance in under 2 minutes.
- **SC-010**: 0 Feature 031 registry/report artifacts are modified by the governance/docs reconciliation portion of Feature 031.

## Assumptions

- Only items classified by Feature 030 as `unrecoverable_after_evidence_exhaustion` or `partially_recovered` are eligible for this registry.
- User approval is required before any assumption marked `proposed` can be used at runtime.
- Approved assumptions remain assumptions, not paper-backed facts.
- Rejected assumptions remain documented for audit history but are not runtime-usable.
- No runtime behavior changes are implied by this feature unless a later approved implementation feature consumes the registry.
- `blocked_no_assumption` means the registry could not safely propose a default and requires a manual user value before any runtime use can be considered.
- Governance/docs reconciliation is a PATCH-level correction only; no new governance principles are introduced by this feature.
- The approved interpreter/runtime guidance must remain consistent across constitution, reproducibility docs, and feature metadata.
- The constitution intentionally retains principles 21 through 30 as part of the MINOR governance expansion.

## Production Constraints

- [x] Performance budgets identified
- [x] Artifact handling rules identified
- [x] Security and secret-hygiene constraints identified
- [x] CI quality gate impact identified

## Public Interfaces Affected

- [ ] Environment reset/step
- [ ] Policy interface
- [ ] Task model
- [ ] Topology interface
- [ ] Runtime model interface
- [ ] Evaluation metric interface
- [x] Config schema
- [x] Artifact schema
- [x] Governance documentation

## Config / Schema Impact

- [x] Required config fields identified
- [x] Validation rules identified
- [x] Backward-compatibility impact identified

## Artifact Impact

- [ ] Raw metrics
- [ ] Plots
- [x] Reports
- [ ] Checkpoints
- [ ] Debug traces
- [x] Validation summaries
- [x] Governance docs

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
- [x] Governance/version consistency gate satisfied
