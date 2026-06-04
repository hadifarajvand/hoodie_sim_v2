# Metric Readiness Matrix

| Metric | Use | Classification | Status | Required Evidence |
|---|---|---|---|---|
| `task_completion_delay` | Primary comparison | paper_primary_metric | ready | Paper OCR defines delay comparison and runtime rows expose completion-time delay. |
| `task_drop_ratio` | Primary comparison | paper_primary_metric | ready | Drop ratio is supported by runtime drop outcomes and paper comparison framing. |
| `completion_rate` | Derived reliability | paper_secondary_or_derived_metric | ready | Derived from completed versus dropped outcomes. |
| `timeout_drop_rate` | Drop diagnostic | repository_diagnostic_metric | diagnostic_only | Keep as a diagnostic and do not promote to headline paper comparison. |
| `unavailable_drop_rate` | Drop diagnostic | repository_diagnostic_metric | diagnostic_only | Keep as a diagnostic and do not promote to headline paper comparison. |
| `deadline_violation_rate` | Deadline diagnostic | repository_diagnostic_metric | diagnostic_only | Keep as a diagnostic and do not promote to headline paper comparison. |
| `average_reward` | Optimization/report diagnostic | paper_secondary_or_repository_metric | ready_with_boundary | Supporting metric with an explicit claim boundary. |
| `total_reward` | Optimization/report diagnostic | paper_secondary_or_repository_metric | ready_with_boundary | Supporting metric with an explicit claim boundary. |
| `throughput` | Performance output | paper_secondary_or_repository_metric | ready_with_boundary | Supporting metric with an explicit claim boundary. |
| `queue_stability_score` | Internal sanity check | repository_diagnostic_metric | diagnostic_only | Not a paper headline metric. |
| `illegal_action_rejection_count` | Runtime legality diagnostic | repository_diagnostic_metric | diagnostic_only | Useful for simulator validation, not paper comparison. |
