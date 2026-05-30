# Plan Details: Feature 068

## Technical context

Feature 068 is a policy-layer fidelity feature. It uses existing Python code and existing project dependencies only.

Primary code areas:

- `src/policies/`
- `src/evaluation/policy_registry.py`
- `tests/unit/`
- `tests/integration/`

Forbidden areas:

- `src/environment/`
- `src/training/`
- `src/agents/`
- generated artifacts
- dependency files

## Constitution gates

- Dependency control: no dependency changes.
- Environment rule: no simulator lifecycle changes.
- Assumptions rule: fallback behavior must be documented.
- Fidelity rule: baseline behavior must match named baseline intent.
- Testing rule: unit and integration tests are required.
- Baseline fairness rule: all baselines use shared context and masks.
- Definition of done: changed files, commands, tests, and risks must be reported.

## Design decisions

### Registry first

All required names must resolve before behavior repair is considered complete.

### Shared context only

Baselines must not inspect environment internals. PolicyContext is the contract.

### Mask before preference

Each baseline filters or checks allowed actions before selecting.

### MLEO candidates

MLEO builds candidates from observation fields, removes unavailable candidates, then ranks by total delay.

### Fallbacks are visible

Fallback behavior is acceptable only when missing data is visible in tests or notes.

## Validation gates

- registry coverage test
- mask compliance test
- MLEO ranking test
- MLEO fallback test
- shared policy integration test
- changed-file scope audit

## Non-goals

- no HOODIE network work
- no training campaign
- no simulator timing repair
- no artifact refresh
