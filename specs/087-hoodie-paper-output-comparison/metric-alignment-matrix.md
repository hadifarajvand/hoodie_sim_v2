# Feature 087 Metric Alignment Matrix

| paper_metric | simulator_metric | classification | mapping_status | allowed_for_comparison | caveat |
| --- | --- | --- | --- | --- | --- |
| task_completion_delay | task_completion_delay | paper_primary_metric | approximate_metric_match | True | Paper reports average computation delay / completion delay across comparative sweeps; the simulator reports task_completion_delay under the Feature 086 approximation boundary. |
| task_drop_ratio | task_drop_ratio | paper_primary_metric | exact_metric_match | True | Paper explicitly compares drop ratio in the evaluation section. |
| completion_rate | completion_rate | paper_secondary_or_derived_metric | derived_metric_match | True | Derived from drop/completion counts; the paper does not foreground it as the primary comparative metric. |
| average_reward | average_reward | paper_secondary_or_repository_metric | approximate_metric_match | True | Paper reward curves are training/behavioral outputs and are not the main comparison metric; simulator average_reward is available but must be read under the claim boundary. |
| total_reward | total_reward | paper_secondary_or_repository_metric | approximate_metric_match | True | Paper discusses cumulative reward during training; simulator total_reward is available for comparison but is not a direct evaluation headline metric. |
| throughput | throughput | paper_secondary_or_repository_metric | derived_metric_match | True | Paper discusses throughput in the objective framing rather than as the main comparative figure; simulator throughput is derived from completion counts. |
| timeout_drop_rate | timeout_drop_rate | repository_diagnostic_metric | not_reported_by_paper | False | Repository diagnostic only unless the paper explicitly supports the denominator and drop semantics. |
| unavailable_drop_rate | unavailable_drop_rate | repository_diagnostic_metric | not_reported_by_paper | False | Repository diagnostic only unless the paper explicitly supports the denominator and drop semantics. |
| deadline_violation_rate | deadline_violation_rate | repository_diagnostic_metric | not_reported_by_paper | False | Repository diagnostic only; the paper discusses deadline violations qualitatively but does not expose this as a paper headline metric. |
| queue_stability_score | queue_stability_score | repository_diagnostic_metric | not_reported_by_paper | False | Repository diagnostic only. |
| illegal_action_rejection_count | illegal_action_rejection_count | repository_diagnostic_metric | not_reported_by_paper | False | Repository diagnostic only. |
