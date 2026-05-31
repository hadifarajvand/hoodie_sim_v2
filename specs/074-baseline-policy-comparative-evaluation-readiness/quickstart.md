# Quickstart: Feature 074

## Purpose

Feature 074 creates baseline policy comparative evaluation readiness after Feature 073 controlled evaluation batch readiness.

## Required Base

Branch: `074-baseline-policy-comparative-evaluation-readiness`

Base dependency: Feature 073 branch `073-controlled-evaluation-batch-readiness` at commit `d7ec5c4e69ea0faf3220e40a00f1bff1ada05c6d` or newer.

Before implementation, verify:

- Feature 073 report passes.
- Controlled metrics are derived from evidence and helpers.
- Compatibility mode is excluded from the default batch.
- No final evaluation claim is made.

## Validation Commands

Use `src/.venvmac/bin/python`.

Run targeted regression slices for Features 068R, 069, 070, 071, 072, and 073.

Run Feature 074 unit and integration tests:

- `src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_baseline_policy_comparative_evaluation_readiness_*.py'`
- `src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_baseline_policy_comparative_evaluation_readiness_*.py'`

Also run:

- `git diff --check`
- Feature 074 scope validator

## Output Rule

Commit and push only.

Do not open a PR.
Do not merge.
Do not generate campaign artifacts.
