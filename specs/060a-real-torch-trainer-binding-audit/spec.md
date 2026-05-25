# Feature 060A — Real Torch Trainer Binding Audit

## Purpose

Audit Feature 060 and prove whether the claimed full paper-default training campaign execution is actually bound to the real Torch/TorchRL trainer path or only to deterministic scalar artifact generation.

## Problem

Feature 060 reported `full_paper_default_training_campaign_execution_passed`, but inspection shows the execution runner builds replay, loss, optimizer-step counts, and target-sync counts using Python scalar math and `random.Random`, not a real Torch/TorchRL training path. The local environment proof also shows both `torch` and `torchrl` are installed, so a fallback claim such as "torch is unavailable" is not acceptable without exact interpreter evidence.

This feature must not repair Feature 060 silently. It must produce a machine-readable audit that either:

1. verifies Feature 060 is truly bound to the real Torch/TorchRL trainer, or
2. explicitly blocks Feature 060's full-campaign claim and routes to a real trainer-binding repair.

## Local environment proof to validate

The implementer must run and capture:

```bash
which python3
python3 -c "import sys; print(sys.executable)"
python3 -c "import importlib.util; print('torch=', importlib.util.find_spec('torch')); print('torchrl=', importlib.util.find_spec('torchrl'))"
python3 -c "import torch; print(torch.__version__)"
python3 -m pip show torch torchrl
```

Expected from current environment:

```text
python3 = /Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python3
torch available = true
torchrl available = true
torch version = 2.12.0
torchrl version = 0.12.0
```

## Required prior inputs

- Feature 060 branch/report/code:
  - `artifacts/analysis/full-paper-default-training-campaign-execution/full-paper-default-training-campaign-report.json`
  - `src/analysis/full_paper_default_training_campaign_execution/runner.py`
  - `src/analysis/full_paper_default_training_campaign_execution/config.py`
- Real trainer/learner candidates:
  - `src/agents/torchrl_hoodie_learner.py`
  - `src/analysis/full_training_reproduction_campaign/`
  - `src/analysis/paper_hoodie_network_implementation/`

## Required output artifacts

- `artifacts/analysis/real-torch-trainer-binding-audit/real-torch-trainer-binding-audit-report.json`
- `artifacts/analysis/real-torch-trainer-binding-audit/real-torch-trainer-binding-audit-report.md`

## Required report decisions

Required top-level fields:

- `feature_id`
- `prerequisite_tags_verified`
- `python_environment_summary`
- `torch_availability_summary`
- `feature_060_claim_summary`
- `feature_060_code_binding_summary`
- `real_trainer_candidate_summary`
- `simulation_fallback_summary`
- `binding_audit_summary`
- `remaining_blockers`
- `recommended_next_feature`
- `final_verdict`

## Required audit logic

The audit must fail the real-binding claim if any of these are true:

- Feature 060 runner does not import `torch`
- Feature 060 runner does not import or instantiate the real Torch/TorchRL trainer/learner
- Feature 060 runner manually simulates replay/loss/optimizer steps with scalar math
- Feature 060 report claims full campaign execution while real Torch trainer binding is absent
- environment shows `torch` and `torchrl` are available but Feature 060 used a fallback path

## Allowed final verdicts

- `real_torch_trainer_binding_verified`
- `real_torch_trainer_binding_missing_repair_required`
- `torch_environment_blocked`
- `feature_060_artifact_missing`
- `feature_060_code_missing`
- `audit_scope_blocked`

## Routing

If Feature 060 is truly bound to the real trainer:

- `final_verdict = real_torch_trainer_binding_verified`
- `recommended_next_feature = Feature 061 — Campaign Result Integrity and Comparison Readiness Audit`
- `remaining_blockers = []`

If the environment has torch/torchrl but Feature 060 is not bound to the real trainer:

- `final_verdict = real_torch_trainer_binding_missing_repair_required`
- `recommended_next_feature = Feature 060B — Bind Full Campaign Execution to Real Torch Trainer`
- `remaining_blockers` must include the exact missing binding evidence

## Hard scope

Allowed:

- audit Feature 060 report/code
- audit Torch/TorchRL environment availability
- audit real trainer candidate imports and call sites
- generate audit artifacts and tests

Forbidden:

- modifying Feature 060 execution logic
- rewriting Feature 060 artifacts
- installing dependencies
- changing dependency files
- changing policies
- changing environment semantics
- changing reward timing
- writing model checkpoint binaries
- claiming paper reproduction or performance superiority
- `.specify/feature.json` committed diff
- `AGENTS.md` rewrite
