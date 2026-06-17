# EULS Phase 4 Validation Hygiene

## Root cause

The remaining `tests/unit/test_completion_root_cause_schema.py` blocker was not an EULS runtime contract failure. The schema test was coupled to the completion-root-cause report generator's workspace guard, which rejects dirty tracked paths outside a narrow allowlist. In this repository state, the guard was catching validation artifacts and unrelated local workspace noise, which made the test nondeterministic.

## Files changed

- `src/analysis/completion_root_cause_diagnosis/report.py`
- `tests/unit/test_completion_root_cause_schema.py`

## Generated artifact policy

Generated validation outputs under `artifacts/analysis/completion-root-cause-diagnosis/` are treated as report products, not source edits. The report guard now recognizes the known analysis output prefixes used by the completion-root-cause workflow so that tests do not fail because of the presence of expected generated artifacts.

## Dirty-worktree guard policy

The guard remains meaningful for source hygiene. It still blocks unrelated dirty tracked files and still protects the report workflow from running against an uncontrolled workspace. The test patch isolates the schema assertion by mocking the prerequisite gate collectors, so the schema check no longer depends on the current branch state or transient local artifacts.

## Why the fix does not weaken EULS contracts

This phase does not alter queue semantics, deadline behavior, reward timing, public queue identity, termination logic, or trace emission rules. It only makes the validation path deterministic and keeps the completion-root-cause schema test focused on report structure rather than workspace state.

## Remaining limitations

- The repository still contains unrelated local workspace noise outside the validated EULS contract path.
- This phase does not expand the completion-root-cause analysis model or change the accepted Phase 3B EULS runtime contract.
- Generated artifacts remain a validation concern, not a runtime contract concern.
