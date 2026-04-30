# Reproducibility

This repository exposes a single packaging-oriented pipeline that loads a unified config, validates it, runs the shared validation path, and packages the results for analysis.

## Configuration

Use one JSON or TOML config with three required sections:

- `training`
- `evaluation`
- `runtime`

The loader does not invent hidden config paths. Every required field must be present in the config you pass to the CLI.

Required consistency checks:

- `training.seed_management.evaluation_seed` must match `evaluation.seed`
- `training.trace_id` must match `evaluation.trace_id`
- `training.episode_count` must match `evaluation.episode_count`
- `training.episode_length` must match `evaluation.episode_length`
- `training.trace_mode` must match `evaluation.trace_mode`
- `training.learner_type`, when present, selects the HOODIE learning backend and must not change simulator, validation, or baseline behavior
- `training.learner_type = "learner_adapter"` activates the deterministic dormant learner path used for the current TorchRL-free implementation slice
- `training.replay_seed`, when present, is the deterministic seed for replay sampling
- `training.torch_seed`, when present, is the deterministic seed for Torch/PyTorch learner internals
- `training.checkpoint_manifest_path`, when present, points to the deterministic learned-state manifest
- `training.checkpoint_state_path`, when present, points to the learned-weight payload
- `runtime.runtime_variant` must be one of the supported runtime variants
- `validation.policies` must list only supported shared-policy names from the codebase
- `validation.policies` is ordered and that order is part of the validation configuration
- `validation.policy_seed`, when present, controls stochastic shared-policy randomness and is independent of trace metadata
- `validation.hoodie_state_path`, when present, points to a saved HOODIE state JSON that should be loaded for trained validation

Validation policy ordering contract:

- `validation.policies[0]` is the baseline policy
- every later policy in `validation.policies` is compared against that baseline
- `policy_order` is preserved in validation artifacts, analysis output, and packaged metadata
- changing policy order changes the comparison baseline and must be treated as a different validation configuration
- stochastic policy randomness is derived from `validation.policy_seed` when provided, otherwise from `evaluation.seed` and the policy name only
- `trace_id` and `episode_length` do not participate in stochastic policy seed derivation

Supported validation policy names:

- `FLC`
- `HOODIE`
- `RO`
- `HO`
- `VO`
- `MLEO`
- `BCO`

## Running The Pipeline

Run the full pipeline:

```bash
python -m src.cli run --config path/to/config.json --output-dir path/to/output
```

Run training first, then validation and analysis:

```bash
python -m src.cli run --config path/to/config.json --output-dir path/to/output --with-training
```

Run validation only:

```bash
python -m src.cli validation --config path/to/config.json --output-dir path/to/output
```

Run analysis only from a previously packaged output directory:

```bash
python -m src.cli analysis --config path/to/config.json --output-dir path/to/output
```

The validation command produces the packaged validation artifacts. The analysis command consumes
those packaged validation artifacts and emits the analysis outputs. The full `run` command can
include the training loop first, but it still routes validation and analysis through the same shared
artifact path.

## Seed Handling

- Training and evaluation seeds are stored separately.
- The pipeline checks that evaluation uses the evaluation seed from the config.
- Phase 12 scaffolding adds optional TorchRL-specific seeds for replay and learner internals, but non-TorchRL runs must not require them.
- Re-running with the same config and seeds must produce identical packaged content in deterministic mode.

## Deterministic Mode

Use `--deterministic` to force reproducible timestamps and run identifiers.

In deterministic mode:

- the run identifier is derived from the config hash
- the packaged timestamp is stable
- identical inputs produce identical output files

## Paper-Faithful Behavior

Paper-backed behavior:

- shared validation artifacts
- shared evaluation traces
- shared metric formulas
- delayed reward semantics

Still assumption-backed:

- `A-012` reward approximation: `Phi_n(t)` is still approximated as `(completion_slot - arrival_slot)` unless a later recovered formula is documented elsewhere
- runtime model approximations documented in `docs/assumptions/hoodie_assumptions.md`

The packaging layer does not change runtime, reward, or metric behavior. It only freezes, validates, and exports the results produced by the existing simulator and analysis paths.

Authoritative config provenance:

- `metadata.json` is authoritative for the full unified pipeline config snapshot/hash.
- `validation_artifacts.json` carries both `full_config_snapshot` / `full_config_hash` and `evaluation_config_snapshot` / `evaluation_config_hash`.
- `full_config_*` reflects the complete unified config used by the pipeline run.
- `evaluation_config_*` reflects the `EvaluationConfig` used by validation.

HOODIE trained-state handoff:

- `hoodie_state.json` is the deterministic JSON export of a trained HOODIE agent.
- Its schema version is recorded in the file itself and echoed into packaged metadata as `hoodie_state_schema_version`.
- When `training.learner_type = "learner_adapter"` is used, the exported state also includes schema-versioned `learner_state` and `learner_enabled` so training runs can package learner-backed state deterministically.
- Packaged metadata records `hoodie_validation_mode` as `fresh` or `trained`.
- Validation-only runs remain fresh by default.
- If `validation.hoodie_state_path` is provided and points at a saved state, validation loads that trained state instead of creating a fresh HOODIE agent.
- If a trained validation is requested via `validation.hoodie_state_path` but the file is missing, the pipeline fails clearly instead of silently falling back.

## Smoke Experiment Configs

These are the minimal deterministic smoke configs for exercising the existing CLI pipeline:

- `configs/smoke/smoke_validation_flc_hoodie.json`
- `configs/smoke/smoke_validation_all_baselines.json`

Run them only from the approved virtual environment declared in `.specify/memory/constitution.md`:

```bash
source /Users/hadi/Documents/GitHub/hoodie_sim_v2/.venv/bin/activate
```

Run the first smoke config:

```bash
python -m src.cli validation --config configs/smoke/smoke_validation_flc_hoodie.json --output-dir outputs/smoke --deterministic
```

Run the baseline sweep smoke config:

```bash
python -m src.cli validation --config configs/smoke/smoke_validation_all_baselines.json --output-dir outputs/smoke --deterministic
```

Both smoke configs declare an explicit `validation.topology` with legal offload destinations for
the smoke trace sources, so offload-capable policies have valid topology-backed destinations.

The `smoke_validation_flc_hoodie.json` config is tuned to produce at least one completed task under
the baseline FLC path so the smoke output is not limited to drop-only behavior.

Expected output structure:

```text
outputs/smoke/outputs/<run_id>/
  metadata.json
  validation_artifacts.json
  report.json
  plots.json
```
