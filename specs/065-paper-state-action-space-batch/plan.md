# Implementation Plan: Feature 065

## Feature

065 — Paper-Faithful State and Action Space Batch

## Batch coverage

This feature batches:

1. Full paper state vector
2. Private/offloading waiting times
3. Public queue length vector
4. `W × (N+1)` load history matrix
5. LSTM forecast input based on node active queues
6. Destination-specific action space
7. Legal action masking for exact Edge-Agent/Cloud destinations

## Goal

Repair the biggest fidelity gap in the current implementation: the simplified `state_dim = 3` and `action_count = 3` abstraction. The result must expose a paper-faithful state/action contract that later distributed multi-agent training can consume.

## Non-goals

- Do not rerun the full training campaign.
- Do not create a new release tag.
- Do not claim paper reproduction.
- Do not replace the final release-gated artifacts from Features 063–064.
- Do not change dependency files.

## Package architecture

Create:

```text
src/analysis/paper_state_action_space_batch/
```

Required files:

```text
__init__.py
__main__.py
config.py
model.py
runner.py
report.py
```

Expected implementation touchpoints:

```text
src/environment/gym_adapter.py
src/environment/topology.py
src/analysis/full_training_reproduction_campaign/replay.py
src/analysis/paper_hoodie_network_implementation/network.py
```

Only touch these environment/training files if needed to expose the new paper-faithful state/action contract. Keep backward compatibility for older tests.

## Required artifacts

```text
artifacts/analysis/paper-state-action-space-batch/paper-state-action-space-batch-report.json
artifacts/analysis/paper-state-action-space-batch/paper-state-action-space-batch-report.md
artifacts/analysis/paper-state-action-space-batch/paper-state-vector-contract.json
artifacts/analysis/paper-state-action-space-batch/paper-action-space-contract.json
artifacts/analysis/paper-state-action-space-batch/paper-load-history-contract.json
artifacts/analysis/paper-state-action-space-batch/paper-lstm-forecast-input-contract.json
artifacts/analysis/paper-state-action-space-batch/legal-destination-mask-contract.json
```

## Design constraints

### State

The state contract must be structured first and tensorized second. Do not hide paper components in an opaque vector.

Minimum components:

- task size
- task processing density / cycles required
- task timing/deadline information
- private queue waiting time
- offloading queue waiting time
- public queue length vector ordered by exact node IDs plus Cloud
- `W × (N+1)` load history matrix
- destination-specific legal mask

### Action

Action space must be exact-destination based. Required semantic groups:

- local/self
- horizontal to exact neighboring Edge Agent
- vertical to Cloud

No implementation may collapse all horizontal actions into one generic action.

### Compatibility

Existing 3-action flows may remain as legacy compatibility, but the Feature 065 report must clearly show the new paper-faithful action registry is available and validated.

## Validation command

```bash
python3 -m unittest \
  tests.unit.test_paper_state_action_space_batch_schema \
  tests.unit.test_paper_state_action_space_batch_metrics \
  tests.unit.test_paper_state_action_space_batch_behavior_equivalence \
  tests.integration.test_paper_state_action_space_batch \
  tests.integration.test_paper_state_action_space_batch_report \
  tests.integration.test_paper_state_action_space_batch_scope_guard

python3 -m src.analysis.paper_state_action_space_batch
```

## Expected final verdict

```text
paper_state_action_space_batch_passed
```

## Expected next feature

```text
Feature 066 — Distributed Multi-Agent HOODIE Training Batch
```

## Approved paths

```text
specs/065-paper-state-action-space-batch/
src/analysis/paper_state_action_space_batch/
src/environment/gym_adapter.py
src/environment/topology.py
src/analysis/full_training_reproduction_campaign/replay.py
src/analysis/paper_hoodie_network_implementation/network.py
tests/unit/test_paper_state_action_space_batch_*.py
tests/integration/test_paper_state_action_space_batch*.py
artifacts/analysis/paper-state-action-space-batch/
```

## Forbidden paths

```text
.specify/feature.json
AGENTS.md
.gitignore
dependency files
prior Feature 037-064 artifacts
model checkpoint binaries
release tags
paper reproduction outputs
uncontrolled campaign outputs
```

## Auto-commit/push authorization

Guarded auto-commit/push is allowed only after tests pass, report verdict is internally consistent, blockers are empty, dirty paths are approved, and forbidden paths are absent.
