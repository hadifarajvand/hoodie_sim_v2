# Formula-to-Code Mapping Matrix — Feature 085

| Paper Eq/Fig/Alg | Meaning | Expected Simulation | Code Location | Status | Required Fix |
|---|---|---|---|---|---|
| task_completion_delay | Mean completion latency for completed tasks | Use completion time minus arrival time over completed tasks | `src/analysis/hoodie_runtime_evaluation_runner/metrics.py`, `src/analysis/hoodie_runtime_evaluation_runner/model.py` | needs audit | Verify formula labels and report tables use the canonical name everywhere |
| task_drop_ratio | Ratio of dropped tasks to total tasks | Use timeout drops plus unavailable drops divided by total tasks | `src/analysis/hoodie_runtime_evaluation_runner/metrics.py`, `src/analysis/hoodie_runtime_evaluation_runner/model.py` | needs audit | Ensure audit report uses the formula and not a renamed alias |
| reward calculation | Reward accumulation used by paper-backed evaluation | Sum per-task reward with negative penalties for delay and loss | `src/analysis/hoodie_runtime_evaluation_runner/metrics.py`, `src/analysis/hoodie_runtime_evaluation_runner/scenarios.py` | needs audit | Trace the reward components to the code path used by evaluation rows |
| vertical offload delay | Vertical/cloud placement latency | Use cloud placement delay and cloud availability in task outcomes | `src/analysis/hoodie_runtime_evaluation_runner/scenarios.py`, `src/policies/vo.py` | needs audit | Confirm vertical delay is consistent in task outcomes and report columns |
| horizontal offload delay | Horizontal placement latency | Use legal horizontal destination delay and legal-mask gating | `src/analysis/hoodie_runtime_evaluation_runner/scenarios.py`, `src/policies/ho.py` | needs audit | Confirm horizontal delay and destination selection are reflected in audit traces |
| DQN interface | Proposed-method action-value interface | Provide state/action scoring for proposed method evaluation | `src/analysis/hoodie_proposed_method/model.py`, `src/analysis/hoodie_proposed_method/learning_model.py` | verified | none |
| DDQN interface | Target-selection interface for the proposed method | Keep target-update behavior deterministic and traceable | `src/analysis/hoodie_proposed_method/model.py`, `src/analysis/hoodie_proposed_method/learning_model.py` | verified | none |
| Dueling interface | Value/advantage aggregation interface | Decompose Q into value and advantage terms | `src/analysis/hoodie_proposed_method/model.py`, `src/analysis/hoodie_proposed_method/learning_model.py` | verified | none |
| LSTM interface | Recovery / forecast interface for the proposed method | Provide deterministic forecast and recovery traces | `src/analysis/hoodie_proposed_method/model.py`, `src/analysis/hoodie_proposed_method/learning_model.py` | verified | none |

## Notes

- This matrix is an audit artifact, not a new algorithm proposal.
- If a row is marked `needs audit`, the implementation must show the exact code location and the resulting validation evidence.
