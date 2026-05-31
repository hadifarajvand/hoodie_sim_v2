# Quickstart: Feature 071

## Purpose

Feature 071 aligns runtime helper semantics with the recovered HOODIE paper equations from Feature 070.

## Required Base

This branch must be based on Feature 070 evidence branch commit `3851cd3be63de09189d4ed45c038b34c9ca57aee` or newer.

Before implementation, verify Feature 070 report:

- `passed=True`
- `status=blocker_resolution_readiness_with_runtime_divergence`
- blockers are empty
- runtime divergence remains visible
- no full paper reproduction claim is made

## Implementation Validation

Run:

```bash
src/.venvmac/bin/python -m unittest tests.unit.test_policy_registry tests.unit.test_baseline_policy_fidelity tests.unit.test_mleo_policy tests.integration.test_baseline_policy_fidelity_flow
src/.venvmac/bin/python -m unittest tests.unit.test_full_hoodie_mechanism_fidelity_batch_report tests.unit.test_full_hoodie_mechanism_fidelity_batch_scope_guard tests.integration.test_full_hoodie_mechanism_fidelity_batch_report
src/.venvmac/bin/python -m unittest tests.unit.test_topology_timeout_reward_fidelity_report tests.unit.test_topology_timeout_reward_fidelity_models tests.unit.test_topology_timeout_reward_fidelity_scope_guard tests.integration.test_topology_timeout_reward_fidelity_report
src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_runtime_paper_faithful_semantics_alignment_*.py'
src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_runtime_paper_faithful_semantics_alignment_*.py'
git diff --check
```

Run the Feature 071 scope validator once implemented.

## Output Rule

Commit and push only.

Do not open a PR.
Do not merge.
Do not generate campaign artifacts.
