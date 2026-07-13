# Failure clusters

clean-head: passed=1387, failed=246, errors=8, xfailed=5
current-worktree: passed=1385, failed=249, errors=8, xfailed=5

## High-frequency first-cause messages
- 29x `AssertionError: False is not true`
- 18x `ValueError: Topology adjacency must be symmetric`
- 13x `RuntimeError: Dirty paths outside approved Feature 049 scope block report generation: agentdb.rvf.lock, artifacts/analysis/baseline-fairness-rebuild/baseline-fairness-rebuild.csv, `
- 12x `FileNotFoundError: [Errno 2] No such file or directory: '.specify/feature.json'`
- 12x `ValueError: Feature 045 verdict prerequisite failed.`
- 11x `TypeError: BindFullCampaignRealTorchTrainerReport.__init__() got an unexpected keyword argument 'baseline_evaluation_summary'`
- 10x `RuntimeError: Dirty paths outside approved Feature 045 paths block report generation: agentdb.rvf.lock, artifacts/analysis/baseline-fairness-rebuild/baseline-fairness-rebuild.csv, `
- 9x `RuntimeError: Dirty paths outside approved Feature 047 paths block report generation: agentdb.rvf.lock, artifacts/analysis/baseline-fairness-rebuild/baseline-fairness-rebuild.csv, `
- 8x `AssertionError: True is not false`
- 6x `IndexError: list index out of range`
- 5x `AssertionError: True is not false : forbidden path changed: src/policies/policy_interface.py`
- 5x `RuntimeError: Dirty paths outside approved Feature 049 scope block report generation: agentdb.rvf.lock, artifacts/analysis/baseline-fairness-rebuild/baseline-fairness-rebuild.csv, `
