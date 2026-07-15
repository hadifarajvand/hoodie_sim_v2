# Run log: HOODIE learning and baseline fairness milestone

## Files changed
- `src/agents/ddqn.py`
- `src/agents/lstm_dueling_dqn.py`
- `src/agents/__init__.py`
- `src/policies/bco.py`
- `src/policies/mleo.py`
- `src/policies/ro.py`
- `src/evaluation/paired_evaluation.py`
- `tests/unit/test_hoodie_learning_real.py`
- `docs/plans/2026-07-15-hoodie-learning-baseline-fairness-milestone.md`

## Validation results
- Focused learner test: passed.
- Baseline/policy slice: passed after BCO fix.
- Full suite: blocked by legacy collection errors in `resources/references/simpy`.

## Known failures
- `python3 -m pytest -q` fails in vendored `resources/references/simpy/docs` due `_pytest.assertion.util._diff_text` import mismatch.
- `python3 -m pytest tests/test_hoodie_kernel.py ... tests/test_paired_evaluation.py` cannot run as requested because those paths do not exist in repo.
