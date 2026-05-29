# Implementation Plan: Feature 068

**Branch**: `068-paper-baseline-policy-fidelity-batch`
**Date**: 2026-05-29
**Spec**: `spec.md`

## Summary

Implement and validate paper baseline policy fidelity for RO, FLC, VO, HO, BCO, and MLEO. The priority is to replace placeholder baseline behavior with documented policy decisions that obey legal action masks and use shared policy inputs. MLEO must estimate delay across legal candidate actions.

## Technical Context

- Language: Python
- Dependencies: existing project dependencies only
- Testing: unittest or existing pytest-compatible test layout
- Target modules: `src/policies/`, `src/evaluation/policy_registry.py`, and targeted tests
- Forbidden changes: simulator lifecycle, training, neural network code, generated artifacts, dependency files

## Constitution Check

- Dependency impact: none expected
- Environment impact: none expected
- Assumption impact: MLEO fallback behavior must be documented
- Fidelity impact: baseline behavior is paper-facing and must be tested
- Testing impact: unit and integration coverage required
- Baseline fairness impact: all baselines must use shared policy context

## Project Structure

Expected implementation areas:

```text
src/policies/
  flc.py
  vo.py
  ho.py
  ro.py
  bco.py
  mleo.py
  common.py
src/evaluation/policy_registry.py
tests/unit/
tests/integration/
specs/068-paper-baseline-policy-fidelity-batch/
```

## Design Notes

- MLEO should compute candidate delays from observation fields when available.
- Illegal actions must be excluded before ranking.
- Fallback behavior must be explicit and test-covered.
- Baselines must not call environment internals directly.
