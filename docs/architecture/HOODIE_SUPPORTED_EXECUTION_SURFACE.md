# HOODIE Supported Execution Surface

Canonical supported surface contains only code needed to reproduce original HOODIE behavior and publication artifacts:

- `src/agents/`
- `src/policies/`
- `src/evaluation/`
- `src/config/`
- `src/repro/`
- `src/analysis/distributed_multi_agent_hoodie_training/`
- `tests_supported/hoodie/`

Supported capabilities:

- original HOODIE simulation and training
- LSTM and no-LSTM variants
- six baseline policies
- paired evaluation
- dataset generation
- reporting, rendering, and reproducibility verification

Historical analysis batches, legacy gates, and archived tests remain outside supported execution.
