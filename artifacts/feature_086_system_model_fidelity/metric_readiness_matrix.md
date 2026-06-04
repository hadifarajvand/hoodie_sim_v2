# Feature 086 Metric Readiness Matrix

| metric | classification | status | paper_use |
| --- | --- | --- | --- |
| task_completion_delay | paper_primary_metric | ready | headline_paper-comparison metric |
| task_drop_ratio | paper_primary_metric | ready | headline_paper-comparison metric |
| completion_rate | paper_secondary_or_derived_metric | ready | derived reliability metric for supporting analysis |
| timeout_drop_rate | repository_diagnostic_metric | diagnostic_only | runtime diagnostic; not a paper headline metric |
| unavailable_drop_rate | repository_diagnostic_metric | diagnostic_only | runtime diagnostic; not a paper headline metric |
| deadline_violation_rate | repository_diagnostic_metric | diagnostic_only | runtime diagnostic; not a paper headline metric |
| average_reward | paper_secondary_or_repository_metric | ready_with_boundary | supporting optimization metric with an explicit claim boundary |
| total_reward | paper_secondary_or_repository_metric | ready_with_boundary | supporting optimization metric with an explicit claim boundary |
| throughput | paper_secondary_or_repository_metric | ready_with_boundary | supporting system-throughput metric with an explicit claim boundary |
| queue_stability_score | repository_diagnostic_metric | diagnostic_only | internal diagnostic only |
| illegal_action_rejection_count | repository_diagnostic_metric | diagnostic_only | legal-action diagnostic only |
