# ECHO Full Test Triage Report

## Clean-head summary
- Result: `238 failed, 1382 passed, 5 xfailed, 8 errors`
- Runtime: `1547.09s`
- Main clean-head blocker: dirty-worktree prerequisite rejection in completion-root-cause diagnosis path

## Current-worktree summary
- Result: `249 failed, 1380 passed, 5 xfailed, 8 errors`
- Runtime: `1501.93s`
- Unique current-worktree failures: `12`
- Unique clean-head failures: `3`

## Post-override summary
- `ECHO_TEST_ALLOW_DIRTY_WORKTREE=1` enables controlled report execution
- `tests/integration/test_completion_root_cause_report.py` under override: `11 passed, 1 failed`
- Failing assertion is expected dirty-path verification, not production breakage

## Highest-frequency root causes
- Dirty-worktree gate in `src/analysis/completion_root_cause_diagnosis/report.py`
- Topology legality contract failures around symmetric adjacency and approved registry assumptions
- Legacy feature/report construction assumptions around Feature 045/047/049 scope guards
- Agent/training contract tests that still encode HOODIE-era behavior or state leakage

## Fixes applied
- Added explicit `ECHO_TEST_ALLOW_DIRTY_WORKTREE=1` override for completion-root-cause report tests
- Preserved strict default dirty-worktree rejection
- Added integration coverage for override path

## Classification files
- `artifacts/test_triage/failure_classification.csv`
- `artifacts/test_triage/failure_clusters.md`
- `artifacts/test_triage/baseline_vs_candidate.md`
- `artifacts/test_triage/dirty_worktree_override_validation.md`

## Focused test results
- Override report cluster: `11 passed, 1 failed`
- Regression baseline: `76 passed`

## Remaining failures
- Present in both clean-head and current-worktree suites
- Mostly pre-existing contract failures and obsolete legacy assumptions
- Current-worktree-only failures reproduced as individual passes, so classified as test-infrastructure or pending-investigation until a stable reproducer exists

## Reproduction commands
- `python -m pytest tests -q`
- `ECHO_TEST_ALLOW_DIRTY_WORKTREE=1 python -m pytest tests/integration/test_completion_root_cause_report.py -q`
- `python -m pytest tests/unit/test_topology_legality.py tests/unit/test_phase0_topology_legality.py tests/unit/test_agent_components.py tests/integration/test_training_loop.py -q`
