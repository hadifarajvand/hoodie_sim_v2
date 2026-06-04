# Metric Readiness Matrix

| Metric | Use | Classification | Status | Required Evidence |
|---|---|---|---|---|
| `task_completion_delay` | Primary comparison | paper_primary_metric | ready_pending_system_model_gate | Formula mapping, completed-task denominator, scenario coverage. |
| `task_drop_ratio` | Primary comparison | paper_primary_metric | ready_pending_system_model_gate | Drop denominator and drop semantics evidence. |
| `completion_rate` | Derived reliability | paper_secondary_or_derived_metric | ready_pending_system_model_gate | Derive from completed/generated or non-dropped tasks. |
| `timeout_drop_rate` | Drop diagnostic | repository_diagnostic_metric | diagnostic_ready | Do not present as paper headline unless paper explicitly separates timeout drops. |
| `unavailable_drop_rate` | Drop diagnostic | repository_diagnostic_metric | diagnostic_ready | Repository diagnostic only unless paper directly supports it. |
| `deadline_violation_rate` | Deadline diagnostic | repository_diagnostic_metric | diagnostic_ready | Explain relation to timeout/drop. |
| `average_reward` | Optimization/report diagnostic | paper_secondary_or_repository_metric | needs_formula_confirmation | Confirm paper reward formula and sign convention. |
| `total_reward` | Optimization/report diagnostic | paper_secondary_or_repository_metric | needs_formula_confirmation | Confirm aggregation and paper support. |
| `throughput` | Performance output | paper_secondary_or_repository_metric | needs_paper_confirmation | Use for paper comparison only if paper reports it. |
| `queue_stability_score` | Internal sanity check | repository_diagnostic_metric | diagnostic_ready | Not a paper headline metric unless paper defines it. |
| `illegal_action_rejection_count` | Runtime legality diagnostic | repository_diagnostic_metric | diagnostic_ready | Useful for simulator validation, not paper comparison. |
