# Phase 4 200-Episode Validation

Phase 4 is a validation-only stage. It does not repair the simulator, the queue model, the reward logic, the topology, or the action legality layer. Its job is to run the current Phase 3-enabled pipeline for a large episode count, collect summarized artifacts, and decide whether the codebase is ready for later Figure 8-11 generation work.

## What this phase checks

- 200-episode execution with trace output enabled
- Required trace file presence
- Action legality statistics
- Runtime paper-state completeness
- `paper_state_trace.csv` shape and consistency
- Dataset readiness through `training.trace_dataset`
- A short training smoke run on the generated traces
- Readiness for later figure-generation work

## Readiness rules

`ready_for_phase5_figures` is set to `true` only when all of the following hold:

- 200 episodes complete
- `episode_metrics.csv` has 200 rows
- `paper_state_trace.csv` exists and is non-empty
- invalid action ratio is zero
- non-neighbor horizontal offloads are zero
- self-offload violations are zero
- `state_dim` is stable and greater than 2
- `L(t)` has shape `W x (N+1)`
- `active_load_vector` has length `N+1`
- `predicted_next_load` has length `N+1`
- `state_source` and `next_state_source` are both `runtime_paper_state_trace`
- there are no non-terminal `next_state` copies
- no paper-performance claim is made

If any of these fail, the validator reports blockers instead of hiding the issue.

## Outputs

The validator writes summarized artifacts under `artifacts/phase4_validation/`:

- `validation_config.json`
- `phase4_validation_report.json`
- `phase4_validation_report.md`
- `episode_metrics_summary.csv`
- `policy_action_summary.csv`
- `state_lstm_summary.json`
- `readiness_matrix.csv`

Raw traces are kept outside the artifact directory unless `--keep-raw-traces` is set.

## How to run

Smoke mode:

```bash
./.venvmac/bin/python phase4_validation.py \
  --episodes 2 \
  --output-dir artifacts/phase4_validation_smoke \
  --seed 42 \
  --mode smoke
```

Full validation:

```bash
./.venvmac/bin/python phase4_validation.py \
  --episodes 200 \
  --output-dir artifacts/phase4_validation \
  --seed 42 \
  --mode full
```

## Interpretation

- `PASSED`: the validator found no blockers and no warnings.
- `PASSED_WITH_WARNINGS`: the run is structurally valid, but the validator recorded non-blocking warnings.
- `FAILED`: at least one blocker was found.

## Current limitation

This phase does not claim paper reproduction. If `predicted_next_load_method` is still a persistence baseline, the report must say so explicitly and the figure-generation readiness gate remains false.
