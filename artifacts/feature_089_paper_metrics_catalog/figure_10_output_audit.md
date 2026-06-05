# Feature 089 Figure 10 Output Audit

| figure_id | metric | x_axis | csv_artifact | json_artifact | row_count | expected_row_count | policy_count | expected_policy_count | sweep_count | expected_sweep_count | raw_positive_delay_valid | paper_style_negative_delay_valid | drop_ratio_valid | drop_percent_valid | claim_boundary_valid | status_valid | audit_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Figure 10a | average_task_completion_delay | task_arrival_probability | figure_10a_delay_vs_arrival_probability.csv | figure_10a_delay_vs_arrival_probability.json | 63 | 63 | 7 | 7 | 9 | 9 | True | True | True | True | True | True | pass |
| Figure 10b | average_task_completion_delay | cpu_computation_capacity_ghz | figure_10b_delay_vs_cpu_capacity.csv | figure_10b_delay_vs_cpu_capacity.json | 35 | 35 | 7 | 7 | 5 | 5 | True | True | True | True | True | True | pass |
| Figure 10c | average_task_completion_delay | task_timeout_sec | figure_10c_delay_vs_timeout.csv | figure_10c_delay_vs_timeout.json | 35 | 35 | 7 | 7 | 5 | 5 | True | True | True | True | True | True | pass |
| Figure 10d | task_drop_ratio | task_arrival_probability | figure_10d_drop_ratio_vs_arrival_probability.csv | figure_10d_drop_ratio_vs_arrival_probability.json | 63 | 63 | 7 | 7 | 9 | 9 | True | True | True | True | True | True | pass |
| Figure 10e | task_drop_ratio | cpu_computation_capacity_ghz | figure_10e_drop_ratio_vs_cpu_capacity.csv | figure_10e_drop_ratio_vs_cpu_capacity.json | 35 | 35 | 7 | 7 | 5 | 5 | True | True | True | True | True | True | pass |
| Figure 10f | task_drop_ratio | task_timeout_sec | figure_10f_drop_ratio_vs_timeout.csv | figure_10f_drop_ratio_vs_timeout.json | 35 | 35 | 7 | 7 | 5 | 5 | True | True | True | True | True | True | pass |
