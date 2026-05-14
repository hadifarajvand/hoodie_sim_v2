# Feature Specification: Training Foundation Contract

**Feature Branch**: `[038-training-foundation-contract]`  
**Created**: 2026-05-13  
**Status**: Draft  
**Input**: User description: "Create Feature 038 specification"

## Clarifications

### Session 2026-05-13

- Q: Should the state contract include only paper-supported variables, or also runtime diagnostic fields needed for debugging? → A: Use paper/runtime-supported observable fields only for training state; keep diagnostics outside the model input.
- Q: Should horizontal offload be represented as one generic horizontal action resolved by policy/helper to a legal neighbor, or one action per possible destination with masks for illegal/non-neighbor nodes? → A: Keep one generic horizontal action resolved by the helper to a legal neighbor. That preserves the current environment semantics without inflating the action space or baking topology details into the policy contract.
- Q: Should replay store intermediate non-reward transitions separately from terminal reward-bearing updates? → A: Yes. Store `reward_available=false` for non-terminal steps. Reward must only become available on completion/drop.
- Q: Should pending tasks at episode horizon be kept, excluded, drained, or treated as a readiness failure? → A: For Feature 038, define schema and readiness gate only. Do not add drain-phase behavior unless separately approved because it may change the paper-default episode contract.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Training Data Contract (Priority: P1)

As a future HOODIE training implementer, I need a frozen contract for state vectors, action indexing, and replay transitions so that any later DRL implementation consumes the same semantics across training and evaluation.

**Why this priority**: If the state/action/replay contract is sloppy, every later training result is garbage with a polished wrapper. This is the core foundation.

**Independent Test**: A spec-driven audit can verify the field order, shape, semantic mapping, and delayed-reward replay schema without running any training code.

**Acceptance Scenarios**:

1. **Given** the paper-default runtime contracts and `HoodieGymEnvironment`, **When** a state/action/replay contract is generated, **Then** it must define exact field ordering, shape, mask handling, delayed-reward handling, and no privileged future information.
2. **Given** a replay sample for a terminal or pending-at-horizon transition, **When** the schema is validated, **Then** terminal samples and pending samples must be distinguishable and pending samples must not be misclassified as successful terminal data.

### User Story 2 - Training Control Contract (Priority: P2)

As a future training owner, I need deterministic seed, split, checkpoint, and target-update contracts so that training and evaluation can be reproduced and audited before any optimizer exists.

**Why this priority**: Reproducibility and split hygiene are the second gate. Without them, training can "work" while actually leaking evaluation data or varying by accident.

**Independent Test**: A contract audit can verify the seed bundle, train/eval separation, checkpoint metadata, and update-frequency definition without executing training.

**Acceptance Scenarios**:

1. **Given** a planned training rollout, **When** the seed protocol is inspected, **Then** the report must distinguish trace-generation, replay-sampling, initialization, and exploration seeds.
2. **Given** a checkpoint draft, **When** the schema is validated, **Then** it must include the feature identifier, commit SHA, schema versions, seed bundle, counters, and runtime-contract references.

### User Story 3 - Readiness Gate and Audit Contract (Priority: P3)

As a project maintainer, I need a terminal-outcome exposure gate and a readiness report so that DRL training cannot start while the runtime still produces mostly pending-at-horizon traces.

**Why this priority**: Feature 037 showed sparse terminal outcomes under paper_default. That is a readiness blocker, not something to bury in a dashboard.

**Independent Test**: A readiness audit can compute terminal-outcome exposure metrics from existing traces and determine whether training is blocked without training any model.

**Acceptance Scenarios**:

1. **Given** paper-default trace generation, **When** the readiness audit runs, **Then** it must report generated arrivals, decisions exposed, finalized terminal tasks, pending-at-horizon count, and transition ratios.
2. **Given** a trace bank with insufficient terminal outcomes, **When** the readiness gate is evaluated, **Then** training must remain blocked and the report must say so explicitly.

### Edge Cases

- What happens when a trace has many generated arrivals but zero finalized terminal tasks?
- How does the contract represent pending-at-horizon transitions without pretending they are successful training samples?
- What happens when a selected action is legal in the mask but illegal under the approved topology semantics?
- How is the cloud/vertical action represented when it is independent of Figure 7 horizontal adjacency?
- What happens if the paper's "iteration" wording for target updates is ambiguous?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The feature MUST define a versioned state-vector contract for `HoodieGymEnvironment` observations keyed by edge-agent ID.
- **FR-002**: The state contract MUST specify field ordering, type/shape, normalization rules if any, missing/no-task encoding, and separation between current observable state and the history buffer, using only paper/runtime-supported observable variables and excluding runtime diagnostic fields from the model input.
- **FR-003**: The state contract MUST define `LSTM` lookback `W=10` handling as a contract-only requirement and MUST forbid privileged future information in the training state.
- **FR-004**: The feature MUST define a stable action-index contract that maps integer indices to semantic actions including local/private, one generic helper-resolved horizontal action, and vertical/cloud offload semantics.
- **FR-005**: The action contract MUST require horizontal actions to resolve only to approved Figure 7 neighbor destinations and MUST keep the cloud/vertical action independent from Figure 7 adjacency.
- **FR-006**: The action contract MUST define illegal-action behavior and whether action masks are exposed as observation fields or separate metadata.
- **FR-007**: The feature MUST define a replay-transition schema with explicit delayed-reward handling, explicit pending-at-horizon marking, and a representation for non-terminal steps where `reward_available=false` until completion or drop.
- **FR-008**: The replay schema MUST include, at minimum, the fields `state_t`, `action_index`, `action_semantics`, `legal_action_mask_t`, `reward_t_plus_k`, `reward_available`, `next_state`, `done`, `truncated`, `task_id`, `source_agent_id`, `selected_destination`, `arrival_slot`, `decision_slot`, `terminal_slot`, `terminal_outcome`, `delay_slots`, `seed`, `trace_id`, `episode_id`, and `runtime_contract_version`.
- **FR-009**: The replay schema MUST distinguish terminal completion/drop outcomes from pending-at-horizon transitions and MUST not silently promote pending transitions to successful terminal samples.
- **FR-010**: The feature MUST define a target-update frequency contract and MUST record the meaning of "iteration" before implementation depends on it.
- **FR-011**: If the paper wording for target-update frequency is ambiguous, the feature MUST preserve the candidate interpretation choices as contract metadata and MUST not implement a hidden assumption.
- **FR-012**: The feature MUST define a seed protocol that separates trace-generation seeds, evaluation-trace seeds, replay-sampling seeds, neural-network-initialization seeds, and action-exploration seeds.
- **FR-013**: The seed protocol MUST state that Python and NumPy are seeded now and that future Torch seeding will be required when training is implemented.
- **FR-014**: The feature MUST define a train/eval split protocol that keeps evaluation traces out of the training trace bank and assigns explicit trace IDs and separate seed bundles.
- **FR-015**: The feature MUST define a checkpoint schema for metadata only, including feature ID, commit SHA, config hash/path, contract versions, seed bundle, counters, target-update counter, runtime-contract refs, and paper-default parameter refs.
- **FR-016**: The feature MUST define a training-readiness report schema and required artifact paths under `artifacts/analysis/training-foundation-contract/`.
- **FR-017**: The report schema MUST include the fields `feature_id`, `prerequisite_tags_verified`, `state_contract`, `action_index_contract`, `replay_schema`, `target_update_frequency_contract`, `seed_protocol`, `train_eval_split_protocol`, `checkpoint_schema`, `terminal_outcome_exposure_gate`, `runtime_contracts_verified`, `no_training_started`, `no_neural_network_change`, `no_dependency_drift`, `no_environment_contract_drift`, `no_reward_timing_change`, `no_policy_drift`, `no_curve_fitting`, `no_paper_reproduction_claim`, and `final_verdict`.
- **FR-018**: The terminal-outcome exposure gate MUST report generated arrivals, decisions exposed, finalized terminal tasks, completed tasks, dropped tasks, pending-at-horizon, terminal-transition ratio, reward-bearing-transition ratio, pending-transition ratio, per-policy or random-policy smoke statistics if used, and whether training is blocked.
- **FR-019**: The terminal-outcome exposure gate MUST treat sparse terminal rewards as a readiness blocker and MUST explicitly preserve that blocker in the report rather than hiding it.
- **FR-020**: The feature MUST record that Feature 037 revealed sparse terminal outcomes under paper_default and that Feature 038 does not change runtime behavior.
- **FR-021**: The feature MUST NOT introduce DRL training, neural-network code, replay execution, optimizer behavior, or production training loops.
- **FR-022**: The feature MUST NOT change dependencies, runtime contracts from Features 032–037, baseline policies, topology, timeout/deadline, execution, transmission, capacity sharing, reward timing, or reward equation.
- **FR-023**: The feature MUST NOT claim paper reproduction success and MUST NOT tune simulator output to resemble paper curves.

### Key Entities *(include if feature involves data)*

- **State Contract**: The versioned description of observation fields, history-buffer handling, masking, and normalization rules consumed by future training code.
- **Action Contract**: The versioned mapping between action indices and semantic actions, including legality rules and mask semantics.
- **Replay Transition**: A delayed-reward sample record that captures one decision, its legal mask, eventual terminal outcome, or explicit pending-at-horizon status.
- **Seed Bundle**: A named collection of independent seed domains for trace generation, evaluation, replay sampling, initialization, and exploration.
- **Checkpoint Metadata**: Non-model training metadata that captures contract versions, counters, configuration references, and reproducibility inputs.
- **Readiness Gate**: A deterministic audit that decides whether training may start based on observable terminal-outcome exposure.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The feature produces a report that explicitly versions the state, action, replay, seed, split, checkpoint, and readiness contracts.
- **SC-002**: The report explicitly records that training is blocked until the terminal-outcome exposure gate is satisfied.
- **SC-003**: The report explicitly distinguishes terminal outcomes from pending-at-horizon transitions and records the corresponding ratios.
- **SC-004**: The feature introduces no runtime-semantic changes, no dependency drift, no policy drift, and no training implementation.
- **SC-005**: The readiness contract is strong enough that a later DRL implementation can be audited against it without re-litigating the observation, action, replay, or seed semantics.

## Assumptions

- The paper-default runtime contracts from Features 032–037 remain authoritative and unchanged.
- `HoodieGymEnvironment` remains the shared interface for future training and evaluation.
- Feature 037's sparse terminal-outcome finding is treated as a blocker for training readiness, not as a prompt to reshape the runtime to look nicer.
- The target-update frequency is documented as a contract with an explicit iteration definition requirement; if the paper wording remains ambiguous, the ambiguity is recorded rather than silently resolved.
- Future training features may use the contracts defined here, but this feature itself does not implement training.

## Production Constraints

- [x] Performance budgets identified
- [x] Artifact handling rules identified
- [x] Security and secret-hygiene constraints identified
- [x] CI quality gate impact identified

The production constraint is simple: no DRL implementation may begin until the readiness gate and contract schema are in place and auditable.

## Public Interfaces Affected

- [x] Environment reset/step
- [x] Policy interface
- [x] Task model
- [x] Topology interface
- [x] Runtime model interface
- [x] Evaluation metric interface
- [x] Config schema
- [x] Artifact schema

This feature defines contracts that future implementations must honor; it does not change the runtime behavior of those interfaces.

## Config / Schema Impact

- [x] Required config fields identified
- [x] Validation rules identified
- [x] Backward-compatibility impact identified

The feature introduces schema/version requirements for:
- state vectors
- action indexing
- replay transitions
- seed bundles
- train/eval splits
- checkpoint metadata
- readiness reports

## Artifact Impact

- [x] Raw metrics
- [x] Plots
- [x] Reports
- [x] Checkpoints
- [x] Debug traces
- [x] Validation summaries

This feature requires future artifact schemas only. It does not produce model checkpoints, learned weights, or training traces.

## Security Considerations

- [x] Secrets / tokens / credentials reviewed
- [x] Remote code execution reviewed
- [x] External references documented

No secret-bearing or remote-execution surface is introduced. External references remain non-authoritative and must be mapped to the HOODIE paper or assumptions log before any borrowing is approved.

## Definition of Done

- [x] Spec matched by plan
- [x] Tests identified
- [x] Assumptions documented
- [x] Configs validated or updated
- [x] Paper-to-code mapping updated
- [x] Artifacts handled per lifecycle rules
- [x] Review and merge gate satisfied

Feature 038 is done when the spec, plan, and tasks all agree on the training foundation contracts and explicitly block DRL implementation until the readiness gate passes.
