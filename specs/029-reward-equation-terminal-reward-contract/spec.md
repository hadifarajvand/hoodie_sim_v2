# Feature Specification: Reward Equation and Terminal Reward Contract

**Feature Branch**: `[029-reward-equation-terminal-reward-contract]`  
**Created**: 2026-05-11  
**Status**: Draft  
**Input**: User description: "Feature 029 — Reward Equation and Terminal Reward Contract.

The HOODIE reproduction is still blocked before DRL because reward semantics are high-risk. Earlier work preserved references/conventions, but the exact reward equation behavior, terminal timing, delay term, drop penalty, per-task/per-slot/per-episode semantics, and multi-agent aggregation contract have not yet been encoded as an auditable runtime contract.

Scientific risk:
If the reward contract is wrong, any future learned HOODIE agent will optimize the wrong objective. That would make later DRL results scientifically invalid even if training appears stable.

Primary goal:
Recover, encode, and validate the paper-backed reward contract without starting DRL training.

Required paper-backed recovery targets:
1. Equation (20):
   - no-task behavior
   - reward on successful completion
   - penalty on thrown/dropped task
   - delay-cost term Phi_n(t)
   - relationship between private/local and public/offloaded delay cost
2. Equations (21), (22), and (23), if recoverable:
   - Phi_n(t)
   - Phi_n^priv(t)
   - Phi_n^pub(t)
3. Equation (24):
   - accumulated discounted objective
   - per-agent policy objective
   - whether objective is per task, per slot, or per episode
4. Table 4 / recovered registry:
   - drop penalty C
   - C = 40 only if paper-backed by recovered artifact/OCR
5. Experimental text:
   - cumulative reward across episodes
   - averaging across distributed HOODIE agents
   - negative reward convention
   - distinction between reward curves and interpretable metrics like average delay/drop ratio

Runtime validation targets:
1. Completion reward must be emitted only at terminal completion/drop event timing, not at action-selection time.
2. Successful task completion reward must be negative delay cost, not a positive bonus, unless paper evidence proves otherwise.
3. Dropped/thrown task reward must be negative drop penalty.
4. No task arrival must not create a numeric reward if the paper says NaN/omitted reward.
5. Reward emission must be traceable to a task lifecycle event.
6. Multi-agent reward aggregation must be explicitly classified:
   - paper-backed
   - assumption-backed
   - unrecoverable
7. If runtime behavior currently differs from paper-backed reward behavior, produce an audit report and tests showing the divergence.
8. If a missing value/equation cannot be reliably recovered, classify it as unrecoverable or assumption-backed. Do not fabricate.

Out of scope:
- No DRL training.
- No neural network implementation.
- No TorchRL.
- No Gymnasium.
- No ns-3 or ns-3-gym.
- No campaign reruns.
- No baseline metric redesign.
- No policy redesign.
- No reward shaping.
- No curve fitting.
- No topology fabrication.
- No dependency changes.
- No environment rewrite.
- No opportunistic refactors.

Required source inputs:
- resources/papers/hoodie/ocr/merged.tex
- resources/papers/hoodie/recovered/paper-parameter-registry.json
- resources/papers/hoodie/recovered/topology-g.json only as topology status context, not as reward source
- artifacts/analysis/paper-mechanism-registry/paper-mechanism-registry.json
- artifacts/analysis/offload-lifecycle-instrumentation/instrumentation-summary.json
- artifacts/analysis/computation-delay-cpu-unit-validation/unit-validation-report.json
- current environment reward code and trace ledger code

Expected artifacts:
- artifacts/analysis/reward-equation-terminal-reward-contract/reward-contract-report.json
- artifacts/analysis/reward-equation-terminal-reward-contract/reward-contract-report.md
- any structured reward contract module only if needed and scoped
- tests proving terminal reward behavior and report correctness

Definition of done:
- The feature produces an auditable paper-to-runtime reward contract.
- Tests verify reward timing and sign semantics.
- The report explicitly states whether the runtime is:
  `paper_matched`, `assumption_backed`, `divergent`, or `blocked`.
- The report lists all unrecoverable reward details.
- No training code is added.
- No dependency files change."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Recover Reward Contract (Priority: P1)

As a HOODIE reproduction maintainer, I want the paper reward equation and terminal timing recovered so that later DRL work does not optimize the wrong objective.

**Why this priority**: If the reward contract is wrong, every learned-policy result is scientifically suspect.

**Independent Test**: The recovered reward report clearly labels the equation terms, delay-cost terms, and unresolved pieces without inventing missing values.

**Acceptance Scenarios**:

1. **Given** the recovered paper evidence, **When** the reward audit runs, **Then** the report identifies the reward equation terms and their meanings.
2. **Given** missing or unrecoverable reward evidence, **When** the audit runs, **Then** the report labels the gaps explicitly rather than fabricating values.

---

### User Story 2 - Validate Terminal Reward Timing and Sign (Priority: P2)

As a HOODIE reproduction maintainer, I want reward emission to happen only at terminal completion or drop events so that action-selection timing is not mistaken for reward timing.

**Why this priority**: Reward timing determines the learning signal; getting it wrong invalidates downstream optimization.

**Independent Test**: The runtime trace proves completion and drop rewards are terminal, negative-delay completion rewards stay negative, and no-task arrivals do not create spurious numeric rewards.

**Acceptance Scenarios**:

1. **Given** a completed task, **When** the lifecycle reaches terminal completion, **Then** the reward is emitted at that event and reflects the paper-backed sign convention.
2. **Given** a dropped task, **When** the lifecycle reaches terminal drop, **Then** the reward is emitted at that event and reflects the drop penalty convention.

---

### User Story 3 - Preserve Honest Reward Boundaries (Priority: P3)

As a researcher, I want multi-agent reward aggregation and unresolved reward semantics labeled honestly so that the reproduction does not overstate what is paper-backed.

**Why this priority**: Aggregation and reward semantics are easy to get wrong and hard to diagnose later.

**Independent Test**: The report distinguishes paper-backed, assumption-backed, divergent, and blocked reward semantics, and the runtime tests preserve the boundary cases.

**Acceptance Scenarios**:

1. **Given** a multi-agent reward view, **When** validation runs, **Then** the aggregation contract is classified explicitly.
2. **Given** a reward term that cannot be recovered reliably, **When** validation runs, **Then** it is marked unrecoverable or assumption-backed instead of invented.

### Edge Cases

- What happens when a task arrives but no reward should be emitted yet?
- How is a reward reported when the paper describes an omitted or NaN value?
- What happens if runtime reward timing differs from the terminal event timing in the paper?
- How should aggregate reward be labeled when only per-agent signals are paper-backed?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST recover and report the paper-backed reward equation terms relevant to terminal completion, delay cost, and drop penalty.
- **FR-002**: The system MUST classify reward timing semantics explicitly as terminal or non-terminal and MUST reject action-selection reward emission.
- **FR-003**: The system MUST preserve a negative-delay completion reward convention unless paper evidence proves a different sign convention.
- **FR-004**: The system MUST preserve a negative drop-penalty convention unless paper evidence proves otherwise.
- **FR-005**: The system MUST report no-task behavior explicitly, including omitted or NaN reward cases when supported by the paper.
- **FR-006**: The system MUST classify multi-agent reward aggregation as paper-backed, assumption-backed, unrecoverable, or divergent.
- **FR-007**: The system MUST distinguish per-task, per-slot, and per-episode objective semantics when recoverable.
- **FR-008**: The system MUST produce an auditable runtime contract that traces reward emission to task lifecycle events.
- **FR-009**: The system MUST produce a deterministic validation report summarizing recovered, assumption-backed, unrecoverable, and divergent reward semantics.
- **FR-010**: The system MUST not start DRL training, neural-network code, TorchRL, Gymnasium, ns-3, ns-3-gym, policy redesign, reward shaping, campaign reruns, topology fabrication, or dependency changes.
- **FR-011**: The system MUST clearly state whether drop penalty C is paper-backed, and MUST only treat C = 40 as recovered when evidence supports it.
- **FR-012**: The system MUST use existing trace and reward ledger information to validate terminal emission timing and sign semantics.

### Key Entities *(include if feature involves data)*

- **Reward Term**: A named component of the paper reward equation, including delay-cost and drop-penalty terms.
- **Terminal Reward Event**: The lifecycle event that triggers reward emission at completion or drop.
- **Reward Aggregation Contract**: The rule describing whether rewards are per agent, per task, per slot, or per episode.
- **Reward Evidence Record**: A paper-backed, runtime-backed, assumption-backed, or unrecoverable statement about reward semantics.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The validation report clearly labels each reward term as recovered, assumption-backed, unrecoverable, or divergent.
- **SC-002**: 100% of terminal reward emissions in the tests occur at lifecycle terminal events, not at action selection.
- **SC-003**: 100% of completion and drop reward sign checks are consistent with paper-backed evidence or explicitly flagged as divergent.
- **SC-004**: The validation report identifies the objective granularity as per-task, per-slot, or per-episode when recoverable.
- **SC-005**: The reward contract is reproducible across repeated validation runs.

## Assumptions

- Feature 026 lifecycle tracing remains the source of event-level timing evidence.
- Feature 028 computation-delay validation remains the source of unit and timing context.
- If the paper does not directly recover a reward term or aggregation rule, it remains unrecoverable rather than inferred.
- If the runtime sign or timing semantics differ from paper-backed behavior, the report will classify the divergence honestly instead of normalizing it away.

## Production Constraints

- [ ] Performance budgets identified
- [ ] Artifact handling rules identified
- [ ] Security and secret-hygiene constraints identified
- [ ] CI quality gate impact identified

## Public Interfaces Affected

- [ ] Environment reset/step
- [ ] Policy interface
- [ ] Task model
- [ ] Topology interface
- [ ] Runtime model interface
- [ ] Evaluation metric interface
- [ ] Config schema
- [ ] Artifact schema

## Config / Schema Impact

- [ ] Required config fields identified
- [ ] Validation rules identified
- [ ] Backward-compatibility impact identified

## Artifact Impact

- [ ] Raw metrics
- [ ] Plots
- [ ] Reports
- [ ] Checkpoints
- [ ] Debug traces
- [ ] Validation summaries

## Security Considerations

- [ ] Secrets / tokens / credentials reviewed
- [ ] Remote code execution reviewed
- [ ] External references documented

## Definition of Done

- [ ] Spec matched by plan
- [ ] Tests identified
- [ ] Assumptions documented
- [ ] Configs validated or updated
- [ ] Paper-to-code mapping updated
- [ ] Artifacts handled per lifecycle rules
- [ ] Review and merge gate satisfied
