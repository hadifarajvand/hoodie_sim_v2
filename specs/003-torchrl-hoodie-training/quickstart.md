# Quickstart: TorchRL-backed HOODIE Training

## Purpose

This feature extends the existing HOODIE reproduction workflow so the training path can use a TorchRL-backed learner while preserving the current simulator, validation, packaging, and reproducibility contracts.

## Primary Workflow

1. Prepare a deterministic unified config that includes the current training, evaluation, runtime, and validation sections.
2. Add explicit Phase 12 training fields only when you intend to use the TorchRL learner backend:
   - `training.learner_type`
   - `training.replay_seed`
   - `training.torch_seed`
   - `training.checkpoint_manifest_path`
   - `training.checkpoint_state_path`
3. Run the pipeline in training mode to produce a trained HOODIE state and a deterministic checkpoint manifest.
4. Run validation in fresh mode to confirm the default path still works without a checkpoint.
5. Run validation in trained mode using the saved trained-state source to confirm the learned HOODIE state is reloaded correctly.
6. Compare packaged outputs from repeated identical runs to confirm byte-identical reproducibility.

## Expected Outputs

- A deterministic checkpoint manifest for the trained HOODIE state.
- A reloadable trained-state artifact.
- Validation artifacts that still preserve the existing provenance fields and metrics.
- Packaged outputs that remain byte-identical for repeated deterministic runs.

## Acceptance Check

- Fresh validation still works without a checkpoint.
- Trained validation requires an explicit trained-state source.
- Validation metrics and packaging remain stable in format and meaning.
- Repeated deterministic runs produce identical packaged artifacts.
