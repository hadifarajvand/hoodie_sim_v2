# Workflow Reconstruction Audit

## Scope

This audit reconstructs the intended workflow boundaries from the spec, plan, assumptions, and paper notes, and compares them to the current implementation surface in `src/environment/`, `src/evaluation/`, `src/training/`, `src/agents/`, and `src/run_pipeline.py`.

It is a diagnostic artifact only. It does not claim paper-faithful HOODIE superiority.

## 1. Workflow Map

### Environment / Runtime

- Intended responsibility:
  - Own slot progression, queue admission, service timing, terminal resolution, and delayed reward emission.
  - Keep policy code out of state mutation.
- Current implementation path:
  - `src/environment/slot_engine.py` drives the slot flow.
  - `src/environment/runtime_model.py` provides shared runtime parameters and service-delay logic.
  - `src/environment/slot_boundaries.py`, `src/environment/deadline_rules.py`, and `src/environment/reward_timing.py` handle terminal and reward timing.
  - `src/environment/environment.py` applies policy action outcomes and finalizes task runtime state.
- Assumptions used:
  - `A-009`, `A-010` for runtime calibration and deadline grace.
  - `A-012` for reward emission semantics.
- Paper-backed evidence level:
  - Mixed. Slot progression, FIFO ordering, deadlines, and reward timing are partially paper-backed or OCR-supported.
  - Runtime timing parameters are mostly paper-backed via Table 4, with some assumption-backed grace behavior.
- Code files involved:
  - `src/environment/environment.py`
  - `src/environment/slot_engine.py`
  - `src/environment/slot_boundaries.py`
  - `src/environment/runtime_model.py`
  - `src/environment/reward_timing.py`
  - `src/environment/deadline_rules.py`
  - `src/environment/private_queue.py`
  - `src/environment/public_queue.py`
  - `src/environment/offloading_queue.py`
- Remaining gaps:
  - The runtime model is still not a full paper-equation reconstruction.
  - Timeout grace remains assumption-backed.

### Policy Selection

- Intended responsibility:
  - Convert the current observation and legal-action mask into one action.
  - Remain stateless with respect to environment ownership.
- Current implementation path:
  - Baselines live in `src/policies/`.
  - Validation policy construction happens in `src/run_pipeline.py::_build_validation_policies()`.
  - `EvaluationRunner` builds `PolicyContext` and calls `choose_action()`.
- Assumptions used:
  - `A-005` for baseline heuristics.
  - `validation.policy_seed` / `evaluation.seed` derivation for stochastic shared-policy reproducibility.
- Paper-backed evidence level:
  - Baselines are only partially paper-backed; fallback heuristics are explicitly assumption-backed.
  - The shared policy interface is a spec-level architectural decision, not a paper claim.
- Code files involved:
  - `src/policies/policy_interface.py`
  - `src/policies/flc.py`
  - `src/policies/ro.py`
  - `src/policies/ho.py`
  - `src/policies/vo.py`
  - `src/policies/mleo.py`
  - `src/policies/bco.py`
  - `src/run_pipeline.py`
  - `src/evaluation/runner.py`
- Remaining gaps:
  - HOODIE and the baselines do not yet share a paper-exact policy model.

### HOODIE Inference

- Intended responsibility:
  - Use a learned model path with history, legal-action masking, and deterministic action scoring.
  - Distinguish learned preferences from fallback hints.
- Current implementation path:
  - `src/agents/hoodie_agent.py::choose_action()` builds history, scores legal actions through `HoodieModel.forward()`, and selects via `DoubleDQNSelector`.
  - `src/agents/hoodie_model.py` combines `DuelingDQN` scores, deterministic fallback hints, and learned action preferences.
  - `src/agents/history_builder.py` carries observation/legal-action history into a `HistoryWindow`.
- Assumptions used:
  - `A-011` for the HOODIE skeleton.
  - `A-013` for deterministic untrained action scoring using fallback hints.
  - `A-014` for the deterministic preference update rule.
- Paper-backed evidence level:
  - Partially paper-backed. The existence of history, dueling, double DQN, replay, and target network is aligned with the spec and paper notes.
  - The specific scoring path and update rule are still assumption-backed.
- Code files involved:
  - `src/agents/hoodie_agent.py`
  - `src/agents/hoodie_model.py`
  - `src/agents/history_builder.py`
  - `src/agents/dueling_dqn.py`
  - `src/agents/double_dqn.py`
- Remaining gaps:
  - No paper-exact network architecture.
  - Learned preferences are still a simplified preference store, not a recovered deep Q-network.

### Delayed Reward

- Intended responsibility:
  - Convert completed/dropped task outcomes into a delayed reward signal.
  - Emit the signal after terminal resolution and before metric updates.
- Current implementation path:
  - `src/training/delayed_reward_training.py` stages transitions and releases them when reward is ready.
  - `src/environment/reward_timing.py` and `src/environment/slot_boundaries.py` own environment reward emission.
- Assumptions used:
  - `A-012` for reward semantics.
  - `docs/paper_notes/reward_evidence.md` for the delayed reward interpretation.
- Paper-backed evidence level:
  - Strong for the reward semantics.
  - Weak only where `Phi_n(t)` remains approximated in code.
- Code files involved:
  - `src/training/delayed_reward_training.py`
  - `src/environment/reward_timing.py`
  - `src/environment/slot_boundaries.py`
- Remaining gaps:
  - The exact closed-form `Phi_n(t)` is still not fully recovered.

### Training Update

- Intended responsibility:
  - Consume delayed rewards, sample replay data, update learned preferences, and sync the target network.
- Current implementation path:
  - `src/training/training_loop.py` records delayed transitions into the replay buffer and calls `HoodieAgent.learn_from_replay()`.
  - `src/agents/hoodie_model.py::learn_from_transitions()` updates learned action preferences deterministically.
  - `src/agents/hoodie_agent.py::sync_target_network()` exports learned parameters into `TargetNetwork`.
- Assumptions used:
  - `A-014` for the update rule.
- Paper-backed evidence level:
  - Partially paper-backed at the component level, but the concrete update rule is assumption-backed.
- Code files involved:
  - `src/training/training_loop.py`
  - `src/agents/hoodie_model.py`
  - `src/agents/hoodie_agent.py`
  - `src/agents/replay_buffer.py`
  - `src/agents/target_network.py`
- Remaining gaps:
  - The update is auditable and deterministic, but not paper-exact.
  - Replay sampling is deterministic and last-N based, not a recovered paper sampling rule.

### Validation

- Intended responsibility:
  - Run identical evaluation traces across policies and compare metrics from a shared evaluation path.
- Current implementation path:
  - `src/evaluation/validation_runner.py` enforces shared traces and fairness checks.
  - `src/evaluation/runner.py` runs per-policy traces and collects metric payloads.
  - `src/evaluation/validation_artifacts.py` packages validation results.
- Assumptions used:
  - `A-006` for deterministic trace generation.
  - `docs/assumptions/validation_deviations.md` for documented deviations.
- Paper-backed evidence level:
  - Strong for shared evaluation and metric centralization.
  - Still assumption-backed for trace-bank synthesis when no bank is recovered.
- Code files involved:
  - `src/evaluation/validation_runner.py`
  - `src/evaluation/runner.py`
  - `src/evaluation/comparison_runner.py`
  - `src/evaluation/validation_artifacts.py`
  - `src/evaluation/metrics.py`
- Remaining gaps:
  - Validation still depends on deterministic trace generation rather than a recovered paper trace bank.

### Full Pipeline Packaging

- Intended responsibility:
  - Load a unified config, validate it, run training/validation/analysis, and package outputs reproducibly.
- Current implementation path:
  - `src/run_pipeline.py` loads the unified config, runs optional training, builds validation artifacts, runs analysis, and hands everything to the packager.
  - When training is enabled, the same process can validate against the trained in-memory `HoodieAgent`.
  - When validation is run separately, `validation.hoodie_state_path` can load a saved trained HOODIE state.
  - Phase 12 setup scaffolding adds explicit optional learner/checkpoint config fields without changing the existing fresh-validation default.
  - `src/repro/output_packager.py` writes `metadata.json`, `validation_artifacts.json`, and analysis outputs.
  - `docs/reproducibility.md` documents the authoritative snapshot/hash fields.
- Assumptions used:
  - Deterministic package identity depends on the config hash and deterministic mode.
- Paper-backed evidence level:
  - This is a repository-level reproducibility contract, not a paper claim.
- Code files involved:
  - `src/run_pipeline.py`
  - `src/repro/output_packager.py`
  - `src/repro/repro_guard.py`
  - `src/config/config_loader.py`
- Remaining gaps:
  - The packaging layer is correct for provenance, but it does not make the learning path paper-faithful.

### Analysis / Export

- Intended responsibility:
  - Convert packaged validation outputs into analysis artifacts and exports.
- Current implementation path:
  - `src/analysis/analysis_runner.py` consumes packaged validation payloads.
  - `src/repro/output_packager.py` writes final exported files.
- Assumptions used:
  - None beyond the already documented reproducibility and metric assumptions.
- Paper-backed evidence level:
  - Low direct paper evidence; this is an implementation convenience for reproducibility and review.
- Code files involved:
  - `src/analysis/analysis_runner.py`
  - `src/repro/output_packager.py`
- Remaining gaps:
  - No paper-backed analysis/export format was recovered; current outputs are pragmatic packaging artifacts.

## 2. Drift Matrix

| Workflow section | Intended behavior from docs/specs | Current code behavior | Status | Exact fix needed |
|---|---|---|---|---|
| Environment/runtime | Slot-based shared runtime owns admission, execution, deadline, and delayed reward timing | Implemented in `src/environment/*` with a shared runtime model and slot engine | Partially aligned | Recover or document the remaining assumption-backed runtime parameters, especially timeout grace and any unresolved `Phi_n(t)` detail |
| Policy selection | All policies consume the same observation/mask path and stay outside environment mutation | Implemented via `PolicyContext` and `EvaluationRunner` | Aligned | None for current scope |
| HOODIE inference | HOODIE should score legal actions through model/history path, not collapse to a dummy heuristic | `HoodieAgent` now uses `HoodieModel.forward()` with learned preferences plus fallback hints | Partially aligned | Replace the remaining fallback-hint scoring with a paper-backed learned inference model if exact equations are recovered |
| Delayed reward | Reward is emitted after terminal resolution and before metric update | Implemented and threaded through training and environment timing | Aligned | None for current scope |
| Training update | Delayed rewards and replay samples must update model parameters deterministically | Implemented as a simple deterministic preference update | Partially aligned | Recover the exact paper update equation or clearly keep the assumption-backed rule |
| Validation | Identical traces, fairness checks, and shared metrics across compared policies | Implemented in `validation_runner` and `runner` | Aligned | None for current scope |
| Full pipeline packaging | Metadata must preserve full config provenance; validation artifacts must distinguish evaluation vs full config provenance | Implemented and documented | Aligned | None for current scope |
| Analysis/export | Packaged validation outputs should feed analysis/export deterministically | Implemented | Aligned | None for current scope |

## 3. Critical Blockers Before Full Training-Validation

### Topology-backed training

- Blocker:
  - Training currently depends on a topology-backed path to resolve offload destinations.
- Why it matters:
  - Without topology-backed destination resolution, training can abort on offload-capable actions.
- What blocks it:
  - Training configs that do not carry a compatible topology or that permit offload actions without valid destinations.

### Trained HOODIE evaluation

- Blocker:
  - Evaluation can consume a trained agent object, and the run pipeline can now reload a saved `hoodie_state.json` when a checkpoint path is provided.
- Why it matters:
  - A trained agent must be handed into validation, not recreated from scratch.
- What blocks it:
  - Fresh validation remains the default unless the validation config points at the saved state.

### Model state handoff from training to validation

- Blocker:
  - `run_pipeline()` now keeps training and validation in one process and exports a deterministic model artifact.
  - Separate-process reuse still depends on an explicit checkpoint path.
- Why it matters:
  - Cross-process reuse of a trained HOODIE state is not yet available.
- What blocks it:
  - The checkpoint is explicit and user-directed, not auto-discovered.

### Checkpoint or in-memory trained-agent reuse

- Blocker:
  - In-memory reuse of the trained `HoodieAgent` is available during the same pipeline run, and saved-state reuse is available when explicitly requested by path.
- Why it matters:
  - Repeated validation in a separate invocation will use a fresh agent unless a checkpoint mechanism is added.
- What blocks it:
  - The pipeline does not automatically infer which saved state to reload.

### Avoiding evaluation with fresh untrained HOODIE

- Blocker:
  - Validation-only runs still instantiate a new `HoodieAgent()` unless `validation.hoodie_state_path` is provided.
- Why it matters:
  - This is fine for baseline validation, but not for trained-agent evaluation.
- What blocks it:
  - No explicit distinction between validation-only and trained-agent evaluation injection unless a checkpoint path is supplied.

## 4. Recommended Implementation Order

1. Keep the deterministic preference-update rule auditable and unchanged unless the paper equation is recovered.
2. Tighten validation/training orchestration so a trained `HoodieAgent` can be exported, reloaded, and passed directly into evaluation.
3. If the paper provides exact learning math, replace the assumption-backed preference update and the deterministic replay sampling rule.
4. Only after the learning path is stable, revisit any remaining HOODIE superiority claims.

## 5. Ledger Cleanup Check

`specs/001-hoodie-reproduction/tasks.md` still contains both:

- a canonical completed learning-update block:
  - `T178` through `T182`
- an obsolete unchecked audit block:
  - `T167` through `T172`

There are no duplicate IDs in the ledger, but there are duplicate Phase 11 workflow intents. The tasks are not broken, but the audit block and the completed learning-update block overlap in scope.

## Bottom Line

The workflow is now structurally coherent enough to explain the implementation surface, but it is not fully paper-faithful. The environment, validation, and packaging paths are largely aligned; HOODIE inference and learning are only partially aligned because the current update rule is still assumption-backed, and the checkpointed handoff path is explicit but still user-directed rather than paper-recovered.
