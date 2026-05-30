# Quickstart: Feature 068

## Purpose

Validate paper baseline policy fidelity for RO, FLC, VO, HO, BCO, and MLEO before any implementation claim.

## Read before implementation

- `spec.md`
- `plan.md`
- `research.md`
- `data-model.md`
- `tasks.md`
- `checklists/requirements.md`
- `.specify/memory/constitution.md`

## Allowed implementation areas

- `src/policies/`
- `src/evaluation/policy_registry.py`
- `tests/unit/`
- `tests/integration/`
- this feature directory for final notes only

## Forbidden implementation areas

- `src/environment/`
- `src/training/`
- `src/agents/`
- generated artifacts
- campaign outputs
- dependency files
- lock files

## Validation focus

- registry coverage
- action-mask compliance
- seeded RO behavior
- BCO balancing behavior
- MLEO delay ranking
- MLEO fallback behavior
- controlled baseline differentiation
- scope audit

## Validation commands

Use the approved interpreter when available:

```bash
/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest discover tests/unit
/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest discover tests/integration
```

If the approved interpreter is unavailable, record the exact replacement command.

## Expected report

The implementation PR must list:

- changed files
- commands run
- test results
- fallback assumptions
- scope audit result
- open risks
