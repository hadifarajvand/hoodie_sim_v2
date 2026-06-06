# Data Model: TorchRL-backed HOODIE Training

## Entities

### TrainingConfiguration

- Purpose: Defines the unified configuration controlling training, validation, checkpointing, and reproducibility.
- Key attributes:
  - unified config snapshot
  - config hash
  - training seed
  - evaluation seed
  - replay seed
  - checkpoint source path
  - validation mode
  - deterministic mode flag
- Relationships:
  - Produces one or more training runs.
  - Controls how a HOODIE learned state is exported or reloaded.
- Validation rules:
  - Must preserve the current unified config structure.
  - Must not introduce hidden defaults.
  - Must record explicit seed derivations.

### HOODIELearnedState

- Purpose: Represents the trained HOODIE parameters used for later validation.
- Key attributes:
  - schema version
  - learned preference parameters
  - model weight payload
  - target-network payload
  - policy name
- Relationships:
  - Produced by training.
  - Consumed by validation when trained mode is requested.
- Validation rules:
  - Must be versioned.
  - Must be deterministic for identical inputs.
  - Must be reloadable into a fresh agent instance.

### CheckpointManifest

- Purpose: Records the provenance and location of the learned state.
- Key attributes:
  - checkpoint schema version
  - config snapshot/hash
  - run mode
  - artifact file paths
  - validation mode
  - trained-state source
- Relationships:
  - Belongs to a training run.
  - References the HOODIELearnedState payload.
- Validation rules:
  - Must be deterministic.
  - Must clearly distinguish fresh validation from trained validation.

### ReplaySample

- Purpose: Captures a stored transition used for learning updates.
- Key attributes:
  - observed state or history
  - selected action
  - delayed reward
  - terminal outcome
  - source policy context
- Relationships:
  - Drawn from the training replay store.
  - Consumed by the training loss/update step.
- Validation rules:
  - Must not influence evaluation behavior directly.
  - Must be deterministic under fixed seeds and config.

### ValidationMode

- Purpose: Describes how validation consumes HOODIE state.
- Values:
  - fresh
  - trained
- Relationships:
  - Selected by the pipeline or config.
  - Controls whether validation reads a saved state.
- Validation rules:
  - Fresh is the default.
  - Trained mode requires an explicit trained-state source.

## State Transitions

- TrainingConfiguration → HOODIELearnedState: occurs after a successful training run.
- HOODIELearnedState → ValidationMode trained: occurs when a checkpoint is loaded for validation.
- ValidationMode fresh: occurs when no checkpoint is supplied.
- ReplaySample stored → consumed: occurs when the training loop samples replay and performs a learning update.

## Notes

- TorchRL-specific internals are intentionally not modeled as external entities; they remain implementation details inside the training path.
- The simulator remains the source of truth for task, reward, and timing state.
