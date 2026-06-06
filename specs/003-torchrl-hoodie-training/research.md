# Research: TorchRL-backed HOODIE Training

## Decision 1: Dependency boundary

- Decision: TorchRL and PyTorch are used only inside the HOODIE training path.
- Rationale: The simulator, baseline policies, evaluation, validation, packaging, and reproducibility contracts are already stable and must not inherit new framework behavior.
- Alternatives considered: Pulling TorchRL into validation or agent construction. Rejected because it would blur ownership boundaries and risk changing comparison behavior.

## Decision 2: Model architecture boundary

- Decision: Keep the current HOODIE policy contract and action-mask interface, with TorchRL-backed learning hidden behind the existing agent abstraction.
- Rationale: Validation and baseline comparison already consume the agent through a stable policy contract; changing that contract would ripple into evaluation and packaging.
- Alternatives considered: Replacing the HOODIE policy entrypoint with a new learner-facing API. Rejected because it would force changes in evaluation and validation layers.

## Decision 3: Replay and loss ownership

- Decision: Replay sampling and loss computation stay inside the training workflow.
- Rationale: Training is the only layer that should mutate learned parameters; evaluation and simulator code must remain read-only with respect to training state.
- Alternatives considered: Moving replay sampling into the agent or evaluation layer. Rejected because it would make learning state ownership ambiguous.

## Decision 4: Checkpoint format

- Decision: Use a deterministic JSON manifest plus a versioned binary checkpoint payload for learned weights.
- Rationale: JSON preserves provenance and auditability, while the binary payload keeps learned parameters portable and compact.
- Alternatives considered: JSON-only checkpoints. Rejected because learned model weights are not a natural fit for pure JSON and would be noisy and error-prone.

## Decision 5: Deterministic seeding

- Decision: Derive separate deterministic seeds for training, replay sampling, and TorchRL internals from the unified config seed.
- Rationale: The project already requires reproducibility across identical configs; hidden randomness in the learner would break that contract.
- Alternatives considered: Using a single shared RNG for all learner operations. Rejected because it would couple unrelated randomness and make debugging harder.

## Decision 6: Config compatibility

- Decision: Preserve the current unified config shape and add only explicit training/checkpoint fields needed for the learner.
- Rationale: Existing reproducibility and provenance tooling depends on the current config contract.
- Alternatives considered: Introducing a new learner-specific config file. Rejected because it would fracture provenance and make full-pipeline reproduction harder.

## Decision 7: Assumption-backed items

- Decision: Any unrecovered HOODIE paper detail remains documented as assumption-backed rather than invented.
- Rationale: The project has a formal assumptions log and cannot silently fill scientific gaps.
- Alternatives considered: Inferring missing paper details from the current fallback implementation. Rejected because that would conflate approximation with evidence.
