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
Medium smoke at budgets [50, 100, 200, 300]; the paper's 5000-episode campaign is
preserved as config-only and requires explicit user approval to execute.

## Entry point
`python -m src.analysis.paper_faithful_simulation_production.runner --medium-smoke --json`

## Energy/cost
Not modeled by the base reward (Eq. 20 is delay + drop only);
`energy_metric_status = not_implemented`, reported as None in the schema.
