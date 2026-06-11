# Phase 6.2 - HOODIE Runtime-Compatible Checkpoint Training Protocol

This phase defines the protocol, guards, metadata, and preflight checks required before any real HOODIE training is allowed to run.

It does not run training.
It does not create checkpoints.
It does not validate official figures.
It does not claim paper reproduction readiness.

Figure 8 remains blocked.
Figure 9 remains blocked until checkpointed evaluation produces real action-distribution logs.
Figure 10 remains blocked until a runtime-compatible HOODIE checkpoint exists and the official 200-episode validation protocol is run.
Figure 11 remains blocked until an LSTM ablation protocol is defined and executed.

Trainer JSON checkpoint files are not accepted as runtime HOODIE checkpoints.
Runtime-compatible checkpoints must be loadable or structurally inspectable by the Phase 6.1 interop utilities.

## 1. Canonical checkpoint directory layout

Target layout:

```text
artifacts/hoodie_checkpoints/<run_id>/
  manifest.json
  training_config_snapshot.json
  paper_contract_snapshot.json
  agent_0.pth
  agent_0.pth.meta.json
  agent_1.pth
  agent_1.pth.meta.json
  ...
  agent_N.pth
  agent_N.pth.meta.json
  training_metrics_summary.json
  training_readiness_report.json
```

This layout is documented for later training runs. This phase does not create real `.pth` files outside temporary test directories.

## 2. Required runtime checkpoint files

For a HOODIE run with `K` agents:

- exactly `K` runtime-compatible agent checkpoint files, `agent_0.pth` through `agent_{K-1}.pth`
- exactly `K` metadata sidecars, `agent_0.pth.meta.json` through `agent_{K-1}.pth.meta.json`

The checkpoint files must be runtime-compatible, not trainer JSON artifacts disguised as model files.

## 3. Required metadata fields

Each agent sidecar must contain at least:

- `policy_name: "HOODIE"`
- `checkpoint_format: "pytorch_model_file"` or `checkpoint_format: "pytorch_state_dict_file"`
- `created_by`
- `seed`
- `state_dim`
- `action_count`
- `agent_index`
- `agent_count`
- `episode_count` or `epoch_count`
- `paper_contract_ref` or `config_ref`
- `paper_contract_hash` or `config_hash` if available
- `git_commit`
- `branch`
- `training_command`
- `training_start_time_utc`
- `training_end_time_utc` or `null` if incomplete
- `runtime_loader_target`
- `official_claim_allowed: false`
- `validation_required_before_official_claim: true`

The Phase 6.1 sidecar validator already requires the core metadata fields and defaults `official_claim_allowed` to `false`.

## 4. Required manifest fields

`manifest.json` must contain:

- `run_id`
- `policy_name`
- `agent_count`
- `seed`
- `git_commit`
- `branch`
- `config_ref`
- `paper_contract_ref`
- `paper_contract_hash` or `config_hash`
- `training_command`
- `expected_checkpoint_files`
- `expected_metadata_files`
- `checkpoint_format`
- `runtime_compatibility_status`
- `training_status`
- `training_episode_target`
- `training_episode_completed`
- `smoke_validation_status`
- `official_validation_status`
- `official_claim_allowed: false`
- `created_at_utc`
- `warnings`
- `blockers`

## 5. Required paper contract inputs

The protocol must reference the Table 4 / paper contract requirements:

- `delta_sec = 0.1`
- `action_slots = 100`
- `drain_slots = 10`
- `validation_episodes = 200`
- `task_arrival_probability = 0.5`
- task sizes `2-5` with step `0.1`
- `task density = 0.297`
- private CPU = `5 GHz`
- public CPU = `5 GHz`
- cloud CPU = `30 GHz`
- horizontal rate = `30 Mbps`
- vertical rate = `10 Mbps`
- number of edge agents = `20`
- timeout = `20 slots / 2 sec`
- learning rate = `7e-07`
- gamma = `0.99`
- replay memory = `10000`
- batch size = `64`
- drop penalty = `40`
- LSTM window = `10`
- training episode target = `5000`

The current repository contract snapshot at `config/paper_table4_contract.json` already exposes these values. If runtime defaults differ, that mismatch must be documented as a blocker or warning. Do not silently normalize it.

## 6. Training stages

### Stage 0 - preflight only

- Check repo cleanliness for training.
- Check branch and commit.
- Check paper contract.
- Check output directory.
- Check `.gitignore` protects checkpoints and traces.
- Check runtime checkpoint compatibility requirements.
- No training.

### Stage 1 - tiny wiring smoke, optional later

- Very small episode count only.
- Must output to a clearly non-official temporary directory.
- Must use `official_claim_allowed = false`.
- Must not be used for paper figures.

### Stage 2 - controlled medium training, later

- Used to validate checkpoint saving/loading and action-distribution logging.
- Not official paper training.

### Stage 3 - paper-grade training, later

- `5000` episodes or the paper-equivalent configured target.
- Must produce runtime-compatible checkpoints.
- Must pass smoke runtime evaluation before Figure 8/9/10/11 claims.

## 7. Acceptance gates

- Gate A: preflight passed
- Gate B: runtime checkpoint format confirmed
- Gate C: all agent checkpoints present
- Gate D: all sidecars present
- Gate E: manifest complete
- Gate F: runtime loader can inspect/load checkpoints
- Gate G: checkpointed evaluation can run small smoke
- Gate H: action-distribution logging works from checkpointed evaluation
- Gate I: official validation still blocked until the 200-episode protocol is run
- Gate J: official claim only allowed after paper-contract validation passes

## 8. Current phase status

This phase is a protocol definition phase only. It is intentionally conservative:

- `stage0_preflight_ready` can be true only if a machine-readable checker exists.
- `stage1_tiny_smoke_ready` remains false unless a safe tiny-smoke command is fully specified and guarded.
- `stage2_controlled_training_ready` remains false.
- `stage3_paper_grade_training_ready` remains false.

The runtime-compatible checkpoint protocol is defined here, and this phase adds a lightweight preflight checker. The repository still needs a guarded tiny non-official training smoke in the next phase before any official claim can be made.
