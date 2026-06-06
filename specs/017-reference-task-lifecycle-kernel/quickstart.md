# Quickstart: Reference Task Lifecycle Kernel

## Purpose

Validate the reference-only lifecycle kernel with deterministic ledgers and no simulator mutation.

## Validation Commands

Run the planned test suite with the approved environment:

```bash
/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python -m unittest \
  tests.unit.test_reference_task_lifecycle_kernel \
  tests.integration.test_reference_task_lifecycle_kernel_flow
```

## Expected Outcomes

- The local-compute test emits the exact ordered ledger defined in the spec.
- The horizontal-offload test emits the exact ordered ledger defined in the spec.
- The vertical-offload test emits the exact ordered ledger defined in the spec.
- The timeout/drop test emits `dropped_timeout` followed by terminal-slot `reward_emitted`.
- The delayed-reward test confirms no reward at `selected_action`.
- The deterministic-ordering test reproduces the same ledger across repeated runs.
- The repository-scope guard confirms `src/reference_model` has no forbidden imports or references to simulator lifecycle modules, and no simulator, campaign, artifact, or dependency files are mutated.

## Notes

- The feature is intentionally isolated under `src/reference_model/`.
- No external service, policy, training loop, or metric logic is part of this feature.
