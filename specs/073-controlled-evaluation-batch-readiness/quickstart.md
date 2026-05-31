# Quickstart: Feature 073

## Purpose

Feature 073 creates controlled evaluation batch readiness after Feature 072 deterministic golden trace validation.

## Required Base

Branch: `073-controlled-evaluation-batch-readiness`

Base dependency: Feature 072 branch `072-golden-trace-validation` at commit `66f140c020ddf7f362d331523148782d923f2bdf` or newer.

Before implementation, verify:

- Feature 072 report passes.
- Golden trace expected and actual outputs are independent.
- Feature 071 paper mode is default.
- Feature 070 Figure 7 topology is available.
- No full paper reproduction claim is made.

## Validation Commands

Use `src/.venvmac/bin/python`.

Run targeted regression slices for Features 068R, 069, 070, 071, and 072.

Run Feature 073 unit and integration tests:

- `src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_controlled_evaluation_batch_readiness_*.py'`
- `src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_controlled_evaluation_batch_readiness_*.py'`

Also run:

- `git diff --check`
- Feature 073 scope validator

## Output Rule

Commit and push only.

Do not open a PR.
Do not merge.
Do not generate campaign artifacts.
