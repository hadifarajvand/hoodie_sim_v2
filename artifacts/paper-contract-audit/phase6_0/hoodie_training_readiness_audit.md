# Phase 6.0 — HOODIE training readiness audit

## Executive verdict

Blocked for paper-grade reproduction. We cannot start paper-grade Figure 8/9/10/11 reproduction yet.

- Figure 8: partially possible only — the training entrypoint and reward logging exist, but a safe end-to-end protocol and checkpoint interoperability are required before any official runs proceed.
- Figure 9: blocked — action-distribution logging is not present in a form suitable for sweep-driven Figure 9 generation.
- Official Figure 10: blocked — there is no trained, runtime-compatible HOODIE checkpoint in the repository and trainer checkpoints are in a JSON-array format incompatible with `Agent.load_model()`.
- Figure 11: blocked — LSTM code is present, but paper-faithful LSTM ablation has not been verified; ablation cannot be claimed yet.

Next steps: do NOT run training now. The next implementation phase should be checkpoint interoperability plus adding action-distribution logging; after that, a controlled, resource-light training verification can be executed under an agreed protocol.

## Current readiness status

- overall: blocked
- figure8: partially_ready
- figure9: blocked
- figure10 official: blocked
- figure11: blocked

## Blockers for Figure 8

- No trained HOODIE checkpoint in the repo (required to claim paper reproduction).
- Paper-faithful LSTM and some training-time reward/timing fidelity issues remain (see docs/phase3_fidelity_audit.md).
- Full-scale training requires substantial compute/time and hyperparameter validation.

## Blockers for Figure 9

- HOODIE checkpoint missing; action-distribution plots can be generated from traces or checkpointed evaluation only.
- Parameter sweep orchestration exists, but centralization of HOODIE checkpoint artifacts and automated post-processing remain to be validated.

## Blockers for official Figure 10

- Official Figure 10 requires a trained HOODIE checkpoint; currently unavailable (the repo intentionally excludes HOODIE for baseline-only smoke runs).

## Blockers for Figure 11

- LSTM module exists but docs state the runtime persistence forecast is not yet the paper LSTM. A paper-faithful LSTM implementation/validation is needed for a formal ablation.

## Training entrypoint findings

- Primary trace-trained entrypoint: `training/train_phase3.py` (trace dataset → DQNTrainer, saves JSON checkpoints and `training_metrics.json`).
- There is a modular trainer `training/trainers.py` (DQNTrainer) and a PyTorch agent implementation `decision_makers/agent.py` used for runtime runs.
- `main.py` wires `HOODIE` → `Agent` and includes `--hoodie-checkpoint-dir` for validation/evaluation runs.
- The CLI distinguishes training vs evaluation: training via `training/train_phase3.py` (trace-based), evaluation/validation via `main.py` / `figure10_validation.py` with `--hoodie-checkpoint-dir`.

## HOODIE policy implementation findings

- HOODIE is implemented as a real DRL agent: runtime agent class `decision_makers.agent.Agent` (PyTorch, DeepQNetwork with optional LSTM, replay memory, optimizer, epsilon schedule).
- Policy mapping: `main.py` and `figure10_validation.py` map the string `"HOODIE"` to the `Agent` class.
- The code intentionally treats HOODIE as unavailable when checkpoints are missing; `figure10_validation` has explicit blocking logic (`hoodie_checkpoint_status=unavailable_not_trained`).

## Model architecture findings

- Two trainer styles present:
  - `training/trainers.py` implements a NumPy-based `DQNTrainer` (LinearQModel) used for trace-driven training and saving JSON checkpoints.
  - `decision_makers/agent.py` implements a PyTorch `DeepQNetwork` with optional LSTM, dueling architecture, optimizer, target-network update, replay-style memory and learning loop.
- LSTM support: Present in both `decision_makers.Agent` and `training/lstm_forecaster.py`.
- Target-network / double-DQN support: `training/trainers.py` supports ddqn via config and keeps a `target_net` copy and update interval.
- Replay buffer and batch sampling: `training/replay_buffer.py` and agent memory arrays exist.
- Optimizer and scheduler: PyTorch `optimizer` used in `Agent`; training code uses `optimizer` parameters from hyperparameters; `training/trainers.py` uses simple gradient steps and supports learning rate in config.

## Reward and transition findings

- Delayed reward pairing and contract validated by tests (`tests/test_delayed_reward_pairing.py`).
- Replay tuple structure and trace pairing exist; reward/delay/drop penalty terms are present in code and paper hyperparameters (drop penalty C, gamma, etc.).
- Tests and docs indicate some timing/reward subtleties remain (docs/phase3_fidelity_audit.md mentions delayed task-completion replay is not yet native). These are flagged to be fixed before claiming paper-faithful training.

## Checkpoint findings

- Checkpoint saving/loading:
  - `training/trainers.DQNTrainer.save()` writes JSON checkpoints with metadata (algorithm, seed, state_dim, action_count, epochs_completed, training_config, policy weights, etc.).
  - `decision_makers.Agent.store_model()` uses `torch.save` to persist the full model to `*.pth` files.
- The validation runner (`figure10_validation.py`) expects per-agent checkpoint files like `agent_{idx}.pth` and will mark HOODIE unavailable if they are missing; copy helpers exist (`_copy_hoodie_checkpoints`).
- Checkpoint metadata: JSON trainer checkpoints include rich metadata; `torch.save` of model objects may not include a separate metadata JSON — this is a small hygiene warning.

## Logging/metrics findings (Figure 8/9/11 readiness)

- Training metrics: `training/train_phase3.py` writes `training_metrics.json` with per-epoch loss and average_reward fields usable for convergence plots.
- Step-level metrics: `training/trainers.DQNTrainer.train_step()` returns `TrainingStepMetrics(loss, average_reward, epsilon, transitions_consumed, gradient_steps)`.
- Action distribution: phase/plotting scripts and `phase5_generate_figures.py` expect and produce `figure_10_action_distribution.csv` (tests exist to validate generation).
- LSTM ablation logging: LSTM checkpoints and forecaster artifacts are written by training scripts (forecaster.save). Ablation can be reproduced by configuring zero LSTM layers or disabling sequence components.

Note: existing plotting helpers or CSV-generators do not suffice for paper-grade Figure 9 without validated HOODIE action-distribution logging from checkpointed evaluation/sweeps. `action_distribution_logging_support` is false in the status JSON and Figure 9 is therefore blocked.

## Artifact hygiene findings

- `.gitignore` covers `*.pth`, `*.pt`, `*.pkl`, `*.pickle`, and the smoke sweep `artifacts/figure10_validation/sweeps/` paths. Good hygiene mitigations are present.

## Existing tests found

- Many relevant tests exist and passed in this audit run. Notable tests:
  - `tests/test_delayed_reward_pairing.py`
  - `tests/test_phase3_training.py` (replay buffer and checkpoint tests)
  - `tests/test_figure10_validation_workflow.py` (readiness and HOODIE checkpoint blocking)
  - `tests/test_phase5_figures.py` (action distribution/figure outputs)

## Required implementation work before training

1. Produce a paper-faithful LSTM forecaster (docs indicate current persistence baseline is not yet paper LSTM).
2. Ensure delayed-reward replay pairing is fully native at training-time (docs mention not yet native).
3. Decide canonical checkpoint format and add lightweight metadata sidecar for `torch.save` checkpoints (seed, hyperparameters, epoch) to avoid relying solely on model object files.
4. Add documented training-run dry-run / resource estimation guidance and example configs for Figure 8 reproduction (epochs, env size, seeds, agents count).

## Safe next step recommendation

1. Create a paper-faithful LSTM forecaster implementation or confirm `training/lstm_forecaster.py` satisfies paper constraints; add unit tests asserting shape/behavior.
2. Implement small checkpoint metadata sidecars when using `torch.save` (e.g., `agent_0.pth.meta.json`) and add loader logic.
3. Run a controlled, resource-light training smoke (trace-trained) to validate end-to-end save/load and logging, then scale to full training only once compute/time budget is approved.

## Evidence and references

- Key files inspected: `decision_makers/agent.py`, `training/trainers.py`, `training/train_phase3.py`, `training/replay_buffer.py`, `figure10_validation.py`, `main.py`, `training/lstm_forecaster.py`, `hyperparameters/hyperparameters.json`, `.gitignore`, `scripts/*`.
- Relevant docs: `docs/phase3_fidelity_audit.md`, `scripts/README_figure10_validation.md`.

## Confirmed restrictions

- No training, long validation, simulation, or checkpoint creation was performed during this audit. All checks were read-only or executed lightweight unit tests only.

## Appendix: quick answers (acceptance criteria)

1. Can we start Figure 8 training now?
   - Not yet for official paper reproduction: training pipeline exists but needs paper-faithful LSTM and a plan for resource allocation. Status: partially_ready.
2. If not, what blocks it?
   - Missing trained HOODIE checkpoint and fidelity gaps (LSTM/replay timing).
3. Is HOODIE implemented or only mapped as a placeholder?
   - Implemented: `decision_makers.agent.Agent` is a full DRL agent (PyTorch).
4. Is checkpoint save/load ready?
   - Yes: both JSON trainer checkpoints and `torch.save` models supported; loader logic present in agent and validation code.
5. Is reward logging sufficient for convergence plots?
   - Yes: trainers produce epoch-level loss and average_reward; `training_metrics.json` is written.
6. Is action distribution logging sufficient for Figure 9?
   - No. Existing plotting/helpers are not enough; paper-grade Figure 9 is blocked until HOODIE action distribution is logged and validated during checkpointed evaluation/sweeps.
7. Is LSTM ablation supported for Figure 11?
   - Not yet for paper-grade reproduction. LSTM support is detected, but Figure 11 is blocked until a verified with-LSTM vs without-LSTM ablation protocol exists.
8. Is official Figure 10 still blocked by missing checkpoint?
   - Yes.
9. Safest next implementation phase?
   - Phase 6.1 — checkpoint interoperability and action-distribution logging readiness.

## Detailed evidence (file → symbol → finding → readiness impact)

- `training/trainers.py` → `DQNTrainer.save()` / `DQNTrainer.load()`
   - Finding: `save()` writes a JSON-style checkpoint payload containing `policy_weights`, `policy_bias`, `target_weights`, `target_bias`, training_config, and `epochs_completed`. `load()` restores NumPy arrays into the `LinearQModel` weights.
   - Impact: rich metadata present and suitable for numeric reproducibility, but format is JSON arrays (not a PyTorch `state_dict`). This requires a conversion step for runtime `Agent` consumption.

- `training/train_phase3.py` → `main()` / training loop
   - Finding: entrypoint writes `training_metrics.json` (per-epoch `loss` and `average_reward`) and `phase3_model.chkpt` (trainer checkpoint via `DQNTrainer.save()`), plus optional LSTM forecaster checkpoint via `LSTMForecaster.save()`.
   - Impact: reward logging exists for Figure 8; trainer checkpoints exist but are trainer-format `.chkpt` files (JSON arrays), not runtime PyTorch objects.

- `decision_makers/agent.py` → `Agent`, `DeepQNetwork`, `Agent.store_model()`, `Agent.load_model()`
   - Finding: `Agent.store_model()` uses `torch.save(self.Q_eval_network, path)` (saves the full model object). `Agent.load_model()` calls `torch.load(path, map_location=self.device)` and expects a PyTorch-saved model object.
   - Impact: runtime expects PyTorch objects; trainer checkpoint format mismatch prevents direct runtime loading of trainer `.chkpt` files.

- `main.py` → policy mapping
   - Finding: `"HOODIE": Agent` maps the name to the runtime class and `main.py` propagates `checkpoint_folder` args into the agent instantiation.
   - Impact: runtime wiring exists to load HOODIE from a checkpoint path, but success depends on format compatibility.

- `.gitignore`
   - Finding: repository ignores `artifacts/figure10_validation/sweeps/` and `artifacts/**/logs/*.pth` and common model file patterns.
   - Impact: trained models and large run artifacts are intentionally excluded from git; plan for external artifact distribution required for audit-grade checkpoints.

- Tests (examples)
   - `tests/test_figure10_sweep_aggregation.py`: asserts `HOODIE` absent from `policies_plotted` if the checkpoint is missing and that row-level `hoodie_included` is False.
   - `tests/test_figure10_validation_runbook.py`: expects runbook to advertise `--hoodie-checkpoint-dir <PATH_TO_TRAINED_HOODIE_CHECKPOINT_DIR>`.

End of detailed evidence.
