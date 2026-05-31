# Quickstart: Feature 072

## Purpose

Feature 072 validates deterministic end-to-end HOODIE semantic traces after Feature 071 runtime paper-faithful helper alignment.

## Required Base

Branch: `072-golden-trace-validation`

Base dependency: Feature 071 branch `071-runtime-paper-faithful-semantics-alignment` at commit `4a3b33388074e60aa4462ce4fb71e282cfccc81c` or newer.

Before implementation, verify:

- Feature 071 report passes.
- Paper mode is default.
- Compatibility mode is explicit.
- Feature 070 Figure 7 topology is available.
- No full paper reproduction claim is made.

## Required validation commands

- Feature 068R targeted regression slice.
- Feature 069 targeted regression slice.
- Feature 070 targeted regression slice.
- Feature 071 unit and integration targeted slices.
- Feature 072 unit and integration targeted slices.
- `git diff --check`.
- Feature 072 scope validator.

Use `src/.venvmac/bin/python` for Python validation.

## Output Rule

Commit and push only.

Do not open a PR.
Do not merge.
Do not generate campaign artifacts.
