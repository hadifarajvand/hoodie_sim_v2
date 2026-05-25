# Real Torch Trainer Binding Audit Report Contract

Required JSON artifact:

```text
artifacts/analysis/real-torch-trainer-binding-audit/real-torch-trainer-binding-audit-report.json
```

Required Markdown artifact:

```text
artifacts/analysis/real-torch-trainer-binding-audit/real-torch-trainer-binding-audit-report.md
```

## Required top-level fields

```text
feature_id
prerequisite_tags_verified
python_environment_summary
torch_availability_summary
feature_060_claim_summary
feature_060_code_binding_summary
real_trainer_candidate_summary
simulation_fallback_summary
binding_audit_summary
remaining_blockers
recommended_next_feature
final_verdict
```

## Expected current verdict

Given the current Feature 060 implementation, the likely correct verdict is:

```text
real_torch_trainer_binding_missing_repair_required
```

with next feature:

```text
Feature 060B — Bind Full Campaign Execution to Real Torch Trainer
```

## Passing real-binding verdict

Only allowed if Feature 060 imports and calls the real Torch/TorchRL trainer path:

```text
real_torch_trainer_binding_verified
```

with next feature:

```text
Feature 061 — Campaign Result Integrity and Comparison Readiness Audit
```

## Required blocker evidence

If binding is missing, blockers must include the exact missing evidence, such as:

- `feature_060_runner_missing_torch_import`
- `feature_060_runner_missing_torchrl_import`
- `feature_060_runner_missing_real_trainer_instantiation`
- `feature_060_runner_uses_scalar_fallback_campaign`
- `feature_060_claim_not_supported_by_real_trainer_binding`
