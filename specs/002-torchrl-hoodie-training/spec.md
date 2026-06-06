# Feature Specification: HOODIE Training Integration

**Feature Branch**: `[002-torchrl-hoodie-training]`  
**Created**: 2026-04-26  
**Status**: Draft  
**Input**: User description: "Integrate PyTorch + TorchRL for HOODIE DRL training while preserving the existing simulator, evaluation, validation, packaging, and reproducibility contracts."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Train HOODIE with modern DRL tooling (Priority: P1)

A researcher runs HOODIE training through the existing reproduction workflow and expects the policy to learn from delayed rewards without changing the simulator or evaluation rules.

**Why this priority**: Training is the feature's core value; without it, the integration adds no practical benefit.

**Independent Test**: Run a deterministic training workflow and verify that training completes, produces a trained HOODIE state, and leaves the simulator and evaluation outputs unchanged in form.

**Acceptance Scenarios**:

1. **Given** a valid reproducibility config, **When** HOODIE training is started, **Then** training completes and produces a trained policy state for later validation.
2. **Given** the same config and seed, **When** training is repeated, **Then** the resulting trained policy state is reproducible.

---

### User Story 2 - Preserve current simulator and validation contracts (Priority: P1)

A researcher reruns validation after enabling the new training stack and expects the simulator, metrics, packaging, and reproducibility outputs to remain stable and comparable.

**Why this priority**: The feature must not distort the existing reproduction pipeline; compatibility is as important as training itself.

**Independent Test**: Run validation-only and full-pipeline workflows before and after the training integration and verify that evaluation artifacts, provenance fields, and metrics remain consistent.

**Acceptance Scenarios**:

1. **Given** a validation-only run, **When** no trained state is provided, **Then** validation uses the fresh/default HOODIE path and produces the same class of outputs as before.
2. **Given** a trained-state path, **When** validation is run, **Then** the trained HOODIE state is consumed without changing metric formulas or packaging structure.

---

### User Story 3 - Keep artifacts auditable (Priority: P2)

A reviewer inspects outputs and wants to trace which configuration, seed, and HOODIE state produced each result.

**Why this priority**: Auditability matters for reproduction, but it is secondary to getting the training flow correct.

**Independent Test**: Inspect generated metadata and package contents to confirm they identify the config snapshot, run mode, and trained-state provenance unambiguously.

**Acceptance Scenarios**:

1. **Given** a deterministic run, **When** artifacts are packaged, **Then** the provenance fields identify the exact config and trained-state source used.
2. **Given** two identical deterministic runs, **When** outputs are compared, **Then** the packaged artifacts are byte-identical.

### Edge Cases

- What happens when a trained validation run is requested but no trained state exists?
- How does the workflow behave when the same config is run in fresh and trained validation modes?
- What happens when the training stack cannot produce a usable trained state for validation?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST support HOODIE training through the existing reproduction workflow while preserving the current simulator behavior.
- **FR-002**: The system MUST keep evaluation, validation, packaging, and reproducibility outputs stable in format and meaning when training integration is enabled.
- **FR-003**: The system MUST allow a trained HOODIE state to be handed from training into validation when trained-mode validation is requested.
- **FR-004**: The system MUST keep validation-only runs fresh by default unless an explicit trained-state source is provided.
- **FR-005**: The system MUST reject trained-mode validation clearly when no trained-state source is available.
- **FR-006**: The system MUST preserve deterministic behavior for identical configs and seeds.
- **FR-007**: The system MUST record provenance for config, run mode, and trained-state source in packaged artifacts.
- **FR-008**: The system MUST not change metric formulas, reward semantics, or simulator ownership boundaries as part of the training integration.

### Key Entities *(include if feature involves data)*

- **HOODIE training state**: The learned policy state produced after training and eligible for later validation use.
- **Training run provenance**: The configuration and seed context that identifies how a run was produced.
- **Validation mode**: The execution mode that determines whether validation uses a fresh or trained HOODIE state.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A deterministic training run can be repeated with identical inputs and produce byte-identical packaged outputs.
- **SC-002**: At least 95% of repeated deterministic runs complete with the same trained-state provenance fields and output structure.
- **SC-003**: Validation-only runs continue to produce the existing artifact types and metric outputs without requiring a trained state.
- **SC-004**: Trained-mode validation fails fast and clearly when no trained state is available, instead of silently using a fresh policy.
- **SC-005**: Reviewers can trace each packaged result back to a specific config snapshot and validation mode without ambiguity.

## Assumptions

- The project will keep the current simulator and evaluation contracts as the source of truth.
- Existing deterministic reproducibility guarantees remain in force for identical configs and seeds.
- The training integration is expected to reuse the current artifact and provenance structure rather than invent a new experiment format.
- The feature may rely on the approved Python environment and the project's currently allowed scientific stack.
