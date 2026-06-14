# HOODIE Base-Paper Metric Experiment

- run_id: phase7_1_medium_20260614_081135
- mode: medium
- episodes: 30
- seed: 42
- requested_policies: HOODIE, RO, FLC, VO, HO, BCO, MLEO
- completed_policies: BCO, FLC, HO, HOODIE, MLEO, RO, VO
- failed_or_unavailable_policies: none
- sweeps_completed: task_arrival_probability_sweep, local_cpu_capacity_sweep, task_timeout_sweep
- metric_source: figure10_validation_runner
- raw_metrics_path: /Users/hadi/Documents/GitHub/hoodie_sim_v2_runs/phase7_1/phase7_1_medium_20260614_081135/paper_metric_outputs/base_paper_metrics_raw.csv
- summary_csv_path: /Users/hadi/Documents/GitHub/hoodie_sim_v2_runs/phase7_1/phase7_1_medium_20260614_081135/paper_metric_outputs/base_paper_metrics_summary.csv
- summary_json_path: /Users/hadi/Documents/GitHub/hoodie_sim_v2_runs/phase7_1/phase7_1_medium_20260614_081135/paper_metric_outputs/base_paper_metrics_summary.json
- plots_dir: /Users/hadi/Documents/GitHub/hoodie_sim_v2_runs/phase7_1/phase7_1_medium_20260614_081135/paper_metric_outputs/plots

This is a non-official reproduction-oriented metric experiment. It is intended for visual comparison, not exact paper reproduction.

## Warnings
- non_official_reproduction_oriented_experiment_output

## Limitations
- Deadline-aware/QoS/queueing extensions are disabled in this phase.
- Unavailable policies are recorded rather than aborting the whole experiment.
- Figure 10 style output is non-official and derived from simulator execution.
