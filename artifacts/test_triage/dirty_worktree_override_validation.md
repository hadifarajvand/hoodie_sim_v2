# Dirty-worktree override validation

- strict default: report tests still reject dirty workspace when env var absent
- explicit override: `ECHO_TEST_ALLOW_DIRTY_WORKTREE=1` allows controlled report execution
- scope check: env var only referenced in `src/analysis/completion_root_cause_diagnosis/report.py` and override test
- no pytest config enables override globally
- focused run result: `tests/integration/test_completion_root_cause_report.py` => `11 passed, 1 failed` under override; failing assertion is expected dirty-path verification
- strict-path reproduction: clean-head/full suite still shows dirty-path prerequisite errors without override
