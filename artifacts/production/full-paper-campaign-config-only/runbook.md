# Full HOODIE Paper Campaign — Config-Only Runbook (N_E=5000)

> **CONFIG ONLY — this branch does not run the campaign.** Executing 5000 episodes
> is a deliberate, separately authorized action. Nothing here starts training.

## 1. Configuration (paper-faithful)
- N_E (training episodes): **5000**  | T = 110 | N agents = 20
- Epsilon: 1.0 -> 0.0 linearly over first 2500 episodes (episode-based), 0 after. _Algorithm 1 line 680 (linear 1->0 over first N_E/2 episodes, 0 after)_
- Target update: every 2000 episodes. _Algorithm 1 line 587 / Table 4 N_copy=2000_
- Optimizer: Adam lr=7e-07 loss=MSE | gamma=0.99 | batch=64 | replay=10000
- Network: LSTM 20 cells (lookback 10) -> [1024, 1024, 1024] -> dueling V/A | Double DQN
- Reward: Eq. 20: completed -> -Phi_n(t); dropped -> -C (C=40)
- Credit assignment: per_task_delayed_reward | Reconciliation: horizon_aware_recovered_reward_event
- State profile: deadline_queue_feasibility_v1 | Calibration: paper_aligned_feasible_v1
- Eval: 100 episodes at checkpoints [250, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]

## 2. Compute / time / storage estimates
- Hardware assumption: single CPU core (no GPU; model is small, GPU gives little benefit)
- Measured: 1.73 s/train-episode, 1.29 s/eval-episode
- **Training: ~2.4 h** | Evaluation: ~0.61 h | **Total point estimate: ~3.01 h** (range [2.83, 4.22] h)
- Caveat: Per-episode time may rise modestly once the replay buffer fills (more consistent per-step batch updates); range brackets 1.6-2.6 s/episode.
- Storage: ~503.5 MB checkpoints (20 ckpts) + ~23.3 MB replay + artifacts ≈ **~726.9 MB total**

## 3. Checkpoint / resume strategy
- Checkpoint every **250 episodes** to `artifacts/production/full-paper-campaign-run/checkpoints/ckpt_ep{episode:05d}.pt`
- Checkpoint contents: online_network.state_dict(); target_network.state_dict(); optimizer.state_dict() (Adam moments); cumulative_training_episode_count; optimizer_step_count; target_sync_count; exploration RNG state + cumulative episode index (for epsilon schedule); replay buffer snapshot (optional; deterministic re-fill also acceptable); seed bundle (training/eval trace generation, replay sampling)
- Resume protocol:
  - Locate the highest-numbered ckpt_ep*.pt.
  - Load all four state_dicts and counters; restore exploration episode index.
  - Resume train_to_budget from cumulative_training_episode_count to N_E=5000.
  - Epsilon is a pure function of the cumulative episode index, so resume is exact.
  - Re-anchor the eval trace bank by seed (disjoint from training bank).
- Determinism: All seeds are fixed; epsilon is episode-indexed; target sync is episode-indexed. Resume reproduces the same trajectory as an uninterrupted run if replay is snapshotted; if replay is re-filled, minor sampling drift is possible but schedule/sync stay exact.

## 4. Monitoring
- progress_log: tail -f artifacts/production/full-paper-campaign-run/progress.jsonl
- watch_loss_and_epsilon: Monitor: each checkpoint row should report loss_is_finite=true and the episode-indexed epsilon (1.0 at ep0 -> 0.0 at ep2500 -> 0.0 after).
- watch_action_distribution: Per-checkpoint candidate eval action_distribution should begin to spread from pure-local toward a mix as epsilon decays past ~ep2500.
- watch_reconciliation: Every candidate/baseline row must keep reward_reconciled=true, terminal_reconciled=true, raw_vs_canonical_delta=0, coverage=1.0.
- suggested_commands:
  - `grep -c 'checkpoint_written' artifacts/production/full-paper-campaign-run/progress.jsonl`
  - `python -m src.analysis.paper_faithful_simulation_production.runner --json  # schema check on latest metrics`

## 5. Abort conditions
- **loss becomes NaN/Inf** -> abort; inspect td-target-loss; do not continue
- **reward_reconciled or terminal_reconciled becomes false at any checkpoint** -> abort; reconciliation regression must be root-caused before resuming
- **raw_vs_canonical_reward_delta != 0** -> abort; reward accounting corrupted
- **terminal_event_coverage_ratio < 1.0** -> abort; horizon recovery incomplete
- **wall-clock exceeds 2x upper estimate (~ >9h)** -> pause; profile per-episode cost
- **checkpoint write fails / disk full** -> abort; free storage, resume from last good ckpt
- **epsilon not reaching 0 by episode 2500** -> abort; schedule misconfigured

## 6. Expected artifacts
- Root: `artifacts/production/full-paper-campaign-run/`
- Per checkpoint: candidate-metrics-ep{N}.json (paper-compatible schema); checkpoints/ckpt_ep{N}.pt
- Final: candidate-metrics-full-campaign.json; baseline-and-oracle-metrics.json; reward-terminal-reconciliation-full-campaign.json; learning-health-full-campaign.json; readiness-gates.json; claim-safety.json; final-report.json; final-report.md; figures/ (learning curve, action distribution vs episode, candidate vs oracle)
- Metric schema: PAPER_COMPATIBLE_METRIC_FIELDS (energy/cost = None, not_implemented)

## 7. Remaining approximation — shared-parameter trainer vs paper per-EA distributed models
- **Paper design:** HOODIE is distributed multi-agent: each of the N=20 EAs runs its own DRL model (theta_n), trained on its own local task traffic; agents do not share parameters and do not know other agents' decisions (paper lines 99, 401, 405, 587). Inference deploys N separate Q-models.
- **Repo implementation:** A single shared-parameter trainer (one online + one target network) selects for whichever EA's task is current. This is a centralized shared-policy approximation of the paper's per-EA distributed models.
- **Status:** `known_approximation_not_repaired`
- **Impact:** A shared policy averaged over 20 heterogeneous EAs (different topology positions/neighbors) tends toward a generic policy and cannot personalize per-EA load-spreading the way per-EA models can. This is the leading candidate explanation for residual local-collapse beyond training budget.
- **Implication for the full campaign:** Running N_E=5000 on the shared-parameter trainer tests the shared-policy ceiling, NOT the paper's per-EA distributed ceiling. If the shared agent still underperforms the capacity-split oracle after 5000, the next step is a per-EA distributed trainer (20 models), each trained to its own N_E.
- **Scope:** Implementing per-EA distributed training is out of scope for this config-only branch.

## 8. Claim safety
- training_5000_run: False | config_only: True
- No paper-reproduction or superiority claims; reward & environment unmodified.

## 9. How to execute (when authorized)
- Execution is a deliberate, separate, authorized action — NOT part of this branch.
- Prerequisite: explicit operator approval + storage/time budget confirmed
- A dedicated runner (e.g. --full-campaign-execute) would consume this config, honor checkpoint/resume, and emit the expected artifacts. It is intentionally NOT implemented here so this branch cannot start a 5000-episode run.