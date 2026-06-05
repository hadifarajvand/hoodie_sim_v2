# Feature 089 Figure 10 Trend Analysis

| figure_id | metric | metric_field | trend_direction | series_start_value | series_end_value | series_delta | claim_alignment_status | feature_088_repair_recommended | trend_summary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Figure 10a | average_task_completion_delay | paper_style_delay_for_plotting | non_monotonic | -60.0 | -0.0 | 60.0 | not_supported | True | Average delay should stay lower than baselines as arrival probability increases; MLEO should fall behind HOODIE at high load. |
| Figure 10b | average_task_completion_delay | paper_style_delay_for_plotting | flat | -0.0 | -0.0 | 0.0 | not_supported | True | Increasing CPU capacity should generally reduce average delay while HOODIE remains better than baselines. |
| Figure 10c | average_task_completion_delay | paper_style_delay_for_plotting | decreasing | -0.0 | -100.0 | -100.0 | partial_directional_only | True | Increasing timeout should slightly improve average delay while HOODIE remains lower-delay than baselines. |
| Figure 10d | task_drop_ratio | task_drop_ratio | flat | 1.0 | 1.0 | 0.0 | not_supported | True | HOODIE should maintain the lowest drop ratio as arrival probability increases; FLC and HO should be weak at high load. |
| Figure 10e | task_drop_ratio | task_drop_ratio | flat | 1.0 | 1.0 | 0.0 | not_supported | True | Increasing CPU capacity should reduce drop ratio, with HOODIE showing strong reduction at low CPU capacity. |
| Figure 10f | task_drop_ratio | task_drop_ratio | flat | 1.0 | 1.0 | 0.0 | not_supported | True | Increasing timeout should reduce drop ratio while HOODIE maintains the lowest drop ratio. |
