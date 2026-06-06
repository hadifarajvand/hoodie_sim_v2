# Implementation Plan: Feature 071

**Feature**: Runtime Paper-Faithful Semantics Alignment  
**Status**: Spec Kit created; implementation pending  
**Depends On**: Feature 070 evidence recovery branch

## Summary

Feature 070 recovered the paper equations and kept runtime divergences visible. Feature 071 must close those divergences in runtime helper behavior by adding paper-mode semantics and preserving legacy behavior only as explicit compatibility mode.

## Implementation Boundary

Allowed paths:

- `specs/071-runtime-paper-faithful-semantics-alignment/**`
- `src/analysis/runtime_paper_faithful_semantics_alignment/**`
- `src/environment/paper_timeout.py`
- `src/environment/deadline_rules.py`
- `src/environment/reward_timing.py`
- `src/environment/runtime_model.py` only if required for terminal-state integration and justified in the report
- `tests/unit/test_runtime_paper_faithful_semantics_alignment_*.py`
- `tests/integration/test_runtime_paper_faithful_semantics_alignment_*.py`

Forbidden paths:

- `src/training/**`
- `src/agents/**`
- `artifacts/**`
- `resources/**`
- dependency files
- lock files
- generated campaign outputs
- Feature 072+ files

## Execution Order

1. Start from Feature 070 branch commit `3851cd3be63de09189d4ed45c038b34c9ca57aee` or newer.
2. Verify Feature 070 report passes with runtime divergence visible.
3. Add contract tests for paper-mode deadline strictness.
4. Add contract tests for compatibility mode.
5. Add terminal-state consistency tests.
6. Add reward Eq. (20)-(23) tests.
7. Add Feature 071 analysis/report package.
8. Modify runtime helper files only as narrowly as needed.
9. Preserve Feature 068R, Feature 069, and Feature 070 targeted regression gates.
10. Commit and push only. No PR. No merge.

## Do Not Proceed Gates

Stop if:

- Feature 070 branch is missing or not synced.
- Feature 070 report does not pass.
- Feature 070 runtime-divergence evidence is missing.
- Implementation would require training, agents, campaign artifacts, dependencies, or lock files.
- Paper-mode behavior cannot be added without broad runtime rewrites.

## Runtime Mode Policy

Runtime helpers must support:

- `paper`: strict HOODIE paper semantics.
- `compatibility`: legacy runtime behavior where required.

Feature 071 validation defaults to `paper` mode. Compatibility mode is allowed only when explicitly requested and tested.

## Validation Gates

- Feature 068R targeted regression.
- Feature 069 targeted regression.
- Feature 070 targeted regression.
- Feature 071 deadline strictness tests.
- Feature 071 terminal-state tests.
- Feature 071 reward Eq. (20)-(23) tests.
- Scope audit.
- `git diff --check`.

## Claim Boundary

Feature 071 can claim runtime paper-faithful semantics alignment for the helper layer. It cannot claim full end-to-end paper reproduction. Feature 072 must handle golden-trace end-to-end validation.
