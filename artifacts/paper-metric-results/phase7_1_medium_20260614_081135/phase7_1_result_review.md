# Phase 7.1 Result Review

- Source output directory: `/Users/hadi/Documents/GitHub/hoodie_sim_v2_runs/phase7_1/phase7_1_medium_20260614_081135`
- Run status: accepted
- Raw row count: 6300
- Summary row count: 105
- Plots count: 7
- Completed policies: BCO, FLC, HO, HOODIE, MLEO, RO, VO
- Failed/unavailable policies: none
- Completed sweeps:
  - task_arrival_probability_sweep
  - local_cpu_capacity_sweep
  - task_timeout_sweep
- Manifest flags:
  - simulator_derived_metrics=true
  - synthetic_metric_profile_used=false
  - official_paper_reproduction=false
  - exact_figure_reproduction_claim=false
  - deadline_aware_extension=false
  - qos_extension=false
  - queueing_extension=false
  - contribution_enabled=false
- Packaged plots:
  - delay_vs_local_cpu_capacity.png
  - delay_vs_task_arrival_probability.png
  - delay_vs_task_timeout.png
  - drop_ratio_vs_local_cpu_capacity.png
  - drop_ratio_vs_task_arrival_probability.png
  - drop_ratio_vs_task_timeout.png
  - hoodie_action_distribution.png

These artifacts are for visual comparison with the HOODIE paper metrics, not exact official reproduction.

Next recommended step: visual comparison against the paper figures before any QoS/deadline/queueing contribution.
