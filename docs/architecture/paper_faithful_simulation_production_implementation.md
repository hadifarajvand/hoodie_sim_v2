# Paper-Faithful Simulation Production Implementation

## Purpose
Integrate the HOODIE simulation/evaluation work into a single production-style
pipeline that audits the paper, maps mechanisms, runs a bounded medium-smoke
campaign, reconciles reward/terminal accounting, and emits paper-compatible
metrics, figures, gates, and a final report.

## Paper sources (already staged)
- PDF: `resources/papers/hoodie/original/HOODIE_paper.pdf`
- OCR text/markdown/tex/json: `resources/papers/hoodie/ocr/merged.*`

Re-OCR was not required — text extraction was already available.

### Paper-exact parameters recovered (Table 4)
| Parameter | Value |
|---|---|
| Number of agents (EA) | 20 |
| Number of time slots T | 110 |
| Time slot duration Δ | 0.1 sec |
| Task timeout | 20 slots (2 sec) |
| CPU freq private/public | 5 GHz |
| CPU freq cloud | 30 GHz |
| Drop penalty C | 40 |
| Learning rate | 7e-7 |
| Q-network hidden | 3 × 1024 neurons |
| LSTM | 1 × 20 cells |
| Replay memory | 10000 |
| Batch size | 64 |
| Optimizer / loss | Adam / MSE |
| Training episodes N_E | 5000 (NOT executed; config-only) |
| Techniques | LSTM, Dueling DQN, Double DQN |

Topology (Fig. 7) is image-based; the exact adjacency matrix G was not
numerically recovered and is run with a calibrated topology.

## Profiles
- simulation_profile = `paper_faithful_base`
- calibration_profile = `paper_aligned_feasible_v1`
- state_representation_profile = `deadline_queue_feasibility_v1`
- reconciliation_profile = `horizon_aware_recovered_reward_event`

## Reuse
Training/evaluation reuses the Feature 072 `StateRepresentationTrainingSession`;
reconciliation reuses the Feature 081 `horizon_aware_recovered_reconciliation`.
No environment, reward, policy, or dependency changes were made.

## Budget policy
Medium smoke at budgets [50, 100, 200, 300]. An **extended** medium smoke runs
budgets [300, 500, 750, 1000] (`--extended-smoke`, output under
`artifacts/production/paper-faithful-simulation-extended/`). The pipeline enforces
an absolute smoke ceiling of 1000 episodes; the paper's 5000-episode campaign is
preserved as config-only and requires explicit user approval to execute.

The extended run additionally emits `extended-stability-report.json` validating:
reconciliation stability across all checkpoints, completion/drop/reward trends,
late-budget non-regression, plateau detection, and a diagnostic (non-superiority)
baseline comparison.

## Entry point
`python -m src.analysis.paper_faithful_simulation_production.runner --medium-smoke --json`

## Energy/cost
Not modeled by the base reward (Eq. 20 is delay + drop only);
`energy_metric_status = not_implemented`, reported as None in the schema.

## Training-stability / exploration repair

The extended smoke surfaced an action-collapse blocker (candidate = fixed_local at
every budget). Root cause: `DDQNTrainer._episode_rollout` selected actions with a
pure greedy `argmax` and **no epsilon-greedy exploration**, so replay filled with a
single action and the policy collapsed. The paper (Algorithm 1, line 16) uses an
epsilon-greedy policy.

Fix (paper-consistent, training-only): a configurable `EpsilonGreedyExploration`
schedule was added to `DDQNTrainer` (default `None` preserves legacy behavior) and
enabled in the production training session. Evaluation stays deterministic/greedy
(`epsilon_eval = 0.0`). Double-DQN, target-update, and dueling wiring were verified
correct and **not** modified.

Entry point: `python -m src.analysis.paper_faithful_simulation_production.runner --training-stability-repair --json`

Result (budgets 50→1000): exploration now active (random ratio 0.88→0.29),
Q-values separate (gap ~1.19), and the greedy eval policy is no longer frozen — it
selects horizontal→vertical→local across budgets. The **exploration-collapse root
cause is fixed**. A *separate* issue remains: the eval policy still picks one action
per checkpoint (reward-signal / state-discrimination), so training-health verdict is
`training_stability_repair_blocked` with next step `inspect_reward_signal`. No
environment/reward/policy-algorithm/dependency semantics were changed.
