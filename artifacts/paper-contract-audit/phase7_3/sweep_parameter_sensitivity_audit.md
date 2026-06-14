# Phase 7.3 Sweep Parameter Sensitivity Audit

## Scope
This audit checks whether the three Phase 7.0 / Phase 7.1 sweep dimensions actually affect the runtime configuration and the resulting simulator metrics:

- `task_arrival_probability_sweep`
- `local_cpu_capacity_sweep`
- `task_timeout_sweep`

## Inspected Files

- `scripts/run_hoodie_base_paper_metric_experiment.py`
- `figure10_validation.py`
- `environment/environment.py`
- `environment/server.py`
- `environment/queues.py`
- `artifacts/paper-metric-results/phase7_1_medium_20260614_081135/base_paper_metrics_summary.csv`
- `artifacts/paper-metric-results/phase7_1_medium_20260614_081135/base_paper_metric_experiment_manifest.json`
- `artifacts/paper-metric-results/phase7_1_medium_20260614_081135/paper_metric_outputs/runs/task_timeout_sweep/2.4/figure10_run_config_snapshot.json`

## Phase 7.1 Result Summary

The packaged Phase 7.1 summary is not flat across all sweeps.

- `task_arrival_probability_sweep` changes `mean_average_delay` and `mean_drop_ratio` for the completed policies.
- `task_timeout_sweep` changes `mean_average_delay` and, for several policies, `mean_drop_ratio`.
- `local_cpu_capacity_sweep` is flat for every completed policy in the packaged summary.

Distinct value check from the packaged summary:

- `task_arrival_probability_sweep`: non-flat for delay and drop ratio
- `local_cpu_capacity_sweep`: flat for delay and drop ratio across every completed policy
- `task_timeout_sweep`: non-flat for delay; drop ratio is non-flat for several policies

## Per-Sweep Diagnosis

| Sweep | Runtime config field | Environment consumption | Phase 7.1 output sensitivity | Diagnosis |
|---|---|---|---|---|
| `task_arrival_probability_sweep` | `task_arrive_probabilities` | Passed into `TaskGenerator(task_arrive_probability=...)` | Sensitive | Wired correctly and reflected in output |
| `local_cpu_capacity_sweep` | `private_cpu_capacities` | Passed into `Server(private_queue_computational_capacity=...)` and used by `ProcessingQueue` | Flat across all policies | Wired into the environment, but not effective in the observed experiment output |
| `task_timeout_sweep` | `timeout_delay_mins`, `timeout_delay_maxs`, `timeout_delay_distributions` | Passed into `TaskGenerator` and `Environment.episode_time_end` | Sensitive | Wired correctly and reflected in output |

## Root Cause Diagnosis For `local_cpu_capacity_sweep`

The sweep is not a config-adapter bug. The runner updates `private_cpu_capacities`, and the environment/server stack consumes that field.

The packaged outputs show the real problem:

- every policy is flat across local CPU values in Phase 7.1,
- the sweep is therefore not producing measurable variation in this experiment setup,
- the likely cause is experiment/simulator insensitivity rather than a broken parameter handoff.

Most likely explanations:

- the chosen policies and episode settings do not exercise private CPU enough for the change to move the aggregate metrics,
- local processing is not the dominant bottleneck in this setup,
- the current metric aggregation is correctly reporting what the simulator produced, but the sweep is too weak to produce visible separation.

## Classification

- Config adapter issue: no
- Validation runner issue: no
- Environment consumption issue: no direct evidence
- Metric aggregation issue: no
- Expected behavior under current smoke/untrained fixture setup: yes, most likely

## Recommendation

Accept as non-blocking for Phase 7.3.

Do not treat the flat local CPU curve as a wiring failure. It is a sensitivity limitation of the current experiment setup, not a missing parameter handoff.

Recommended next step:

- keep Phase 7.1 packaged artifacts as-is,
- optionally revisit the local CPU sweep design later if a stronger separation is needed,
- do not rerun Phase 7.1 for this issue alone.

## Notes

- No code fix was required.
- No additional simulation smoke was needed.
- Official reproduction remains blocked.
