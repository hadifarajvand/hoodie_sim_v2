# Feature Specification: TorchRL-backed HOODIE Training

**Feature Branch**: `[003-torchrl-hoodie-training]`  
**Created**: 2026-04-26  
**Status**: Draft  
**Input**: User description: "Create Phase 12 specification for TorchRL-backed HOODIE DRL integration."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Train HOODIE with DRL tooling (Priority: P1)

A researcher wants HOODIE training to use a modern reinforcement-learning learner so the policy can improve from delayed rewards without changing the simulator or evaluation contract.

**Why this priority**: Training capability is the main value of the feature; without it, the integration does nothing useful.

**Independent Test**: Run a deterministic training workflow and confirm it produces a trained HOODIE state while leaving simulator and evaluation outputs intact.

**Acceptance Scenarios**:

1. **Given** a valid reproducibility configuration, **When** HOODIE training runs, **Then** the workflow completes and produces a trained policy state for later validation.
2. **Given** the same configuration and seed, **When** training is repeated, **Then** the resulting trained policy state is reproducible.

---

### User Story 2 - Preserve existing reproduction contracts (Priority: P1)

A researcher reruns validation after enabling the new training path and expects simulator behavior, metrics, validation comparison, packaging, and provenance to remain stable.

**Why this priority**: Compatibility is mandatory; training must not break the current reproduction pipeline.

**Independent Test**: Run validation-only and full-pipeline workflows before and after enabling the feature and confirm that artifact structure, metrics, and provenance remain consistent.

**Acceptance Scenarios**:

1. **Given** a validation-only run, **When** no trained state is provided, **Then** validation continues to use the fresh/default HOODIE path.
2. **Given** a trained-state source, **When** validation is run in trained mode, **Then** the trained HOODIE state is used without changing metric formulas or packaging structure.

---

### User Story 3 - Keep training auditable and reproducible (Priority: P2)

A reviewer inspects outputs and needs to know which config, seed, and trained state produced a result.

**Why this priority**: Auditability is essential for reproducibility, but it is secondary to the core training and compatibility requirements.

**Independent Test**: Inspect packaged results and confirm they identify the config snapshot, validation mode, and trained-state provenance unambiguously.

**Acceptance Scenarios**:

1. **Given** a deterministic run, **When** outputs are packaged, **Then** provenance fields identify the config and trained-state source used.
2. **Given** two identical deterministic runs, **When** outputs are compared, **Then** the packaged artifacts are byte-identical.

### Edge Cases

- What happens when trained-mode validation is requested but no trained state exists?
- What happens when validation-only is run without any checkpoint or exported state?
- What happens when the training path is enabled but the current config does not support a trained-state handoff?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST support HOODIE training through the existing reproduction workflow while preserving current simulator behavior.
- **FR-002**: The system MUST keep validation-only behavior valid and usable when no trained state is supplied.
- **FR-003**: The system MUST allow a trained HOODIE state to be handed from training into validation when trained-mode validation is requested.
- **FR-004**: The system MUST keep the dependency boundary so modern reinforcement-learning tooling is used only in the HOODIE learning/training path and does not alter simulator, baseline, evaluation, validation-comparison, analysis, or packaging behavior.
- **FR-005**: The system MUST keep the model architecture boundary so the learned policy is still consumed through the existing HOODIE policy contract and shared action-mask contract.
- **FR-006**: The system MUST keep replay and loss ownership inside the training workflow rather than moving them into evaluation or simulation logic.
- **FR-007**: The system MUST preserve deterministic seeding so identical inputs produce the same trained state and the same packaged outputs.
- **FR-008**: The system MUST use a versioned, deterministic checkpoint format that can be reloaded for later validation.
- **FR-009**: The system MUST remain compatible with the current unified config shape, adding only explicit fields needed for training, checkpoints, and deterministic provenance.
- **FR-010**: The system MUST clearly label any items whose exact behavior cannot be recovered from paper evidence as assumption-backed.
- **FR-011**: The system MUST provide a migration path from the current preference-update fallback to the TorchRL-backed learner without changing validation-only defaults.
- **FR-012**: The system MUST fail clearly when trained validation is requested but no trained state or checkpoint source is available.
- **FR-013**: The system MUST not claim paper-faithful HOODIE superiority unless supporting evidence is available.

### Key Entities *(include if feature involves data)*

- **Training configuration**: The unified configuration and seed context used to control training and validation behavior.
- **HOODIE learned state**: The trained policy state that can be exported, reloaded, and reused for validation.
- **Checkpoint manifest**: The reproducible artifact that records trained-state versioning and provenance.
- **Validation mode**: The execution mode that determines whether validation uses a fresh or trained HOODIE state.
- **Assumption-backed item**: A behavior that is intentionally documented as unresolved or partially recovered from the paper.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A deterministic training run can be repeated with identical inputs and produce byte-identical packaged outputs.
- **SC-002**: Validation-only runs continue to succeed without requiring a checkpoint, and trained-mode validation fails clearly when no trained state is available.
- **SC-003**: Packaged outputs preserve the existing provenance fields and make the trained-state source unambiguous.
- **SC-004**: Identical configs and seeds produce the same trained-state artifact content across repeated runs.
- **SC-005**: Reviewers can distinguish fresh validation from trained validation without ambiguity in the packaged metadata.
- **SC-006**: At least 95% of repeated deterministic runs complete with the same artifact structure and provenance fields.

## Assumptions

- The current simulator, evaluation, validation, packaging, and reproducibility contracts remain authoritative.
- Any paper detail that is not recovered with confidence remains assumption-backed rather than invented.
- Validation-only behavior remains the default unless the user explicitly provides a trained-state source.
- The project will preserve deterministic packaging and provenance as first-class requirements.
- The feature may rely on the project’s approved Python environment and its currently accepted scientific stack.
