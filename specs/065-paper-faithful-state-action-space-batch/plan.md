# Implementation Plan: Feature 065

## Feature

065 — Paper-Faithful State and Action Space Batch

## Goal

Introduce paper-faithful state/action contracts needed before distributed multi-agent HOODIE training can be repaired. This feature is a contract and adapter feature, not a training feature.

## Batch coverage

1. Full paper state vector
2. Private/offloading waiting times
3. Public queue length vector
4. `W × (N+1)` load history matrix
5. LSTM forecast input based on node active queues
6. Destination-specific action space
7. Legal action masking for exact Edge-Agent and Cloud destinations

## Inputs

- Feature 064 report and release-gate artifacts
- Recovered 20-node topology registry
- Existing environment queue lifecycle
- Existing legacy compact state/action trainer

## Outputs

- Paper-faithful state contract artifact
- Destination-specific action-space contract artifact
- Destination-specific legal-mask contract artifact
- Load-history and forecast-input contract artifact
- Migration-readiness artifact for Feature 066
- Final Feature 065 report

## Architecture

Create analysis package:

```text
src/analysis/paper_faithful_state_action_space_batch/
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

Create environment contract modules:

```text
src/environment/paper_state.py
src/environment/paper_action_space.py
src/environment/paper_load_history.py
src/environment/paper_lstm_forecast.py
```

## Design constraints

- Preserve legacy compact state/action behavior for current trained artifacts.
- Add paper-facing contracts and tests.
- Do not bind Feature 060/061/062/063/064 training/evaluation code to the new contract in this feature.
- Feature 066 will perform the training migration.

## Validation Handoff Packet

Required tests:

```bash
python3 -m unittest \
  tests.unit.test_paper_faithful_state_action_space_batch_schema \
  tests.unit.test_paper_faithful_state_action_space_batch_metrics \
  tests.unit.test_paper_faithful_state_action_space_batch_behavior_equivalence \
  tests.unit.test_paper_state_vector \
  tests.unit.test_paper_action_space \
  tests.unit.test_paper_load_history \
  tests.integration.test_paper_faithful_state_action_space_batch \
  tests.integration.test_paper_faithful_state_action_space_batch_report \
  tests.integration.test_paper_faithful_state_action_space_batch_scope_guard
```

Required module run:

```bash
python3 -m src.analysis.paper_faithful_state_action_space_batch
```

Expected final verdict:

```text
paper_faithful_state_action_space_batch_passed
```

Expected next feature:

```text
Feature 066 — Distributed Multi-Agent HOODIE Training Batch
```

## Approved paths

```text
specs/065-paper-faithful-state-action-space-batch/
src/analysis/paper_faithful_state_action_space_batch/
src/environment/paper_state.py
src/environment/paper_action_space.py
src/environment/paper_load_history.py
src/environment/paper_lstm_forecast.py
tests/unit/test_paper_faithful_state_action_space_batch_schema.py
tests/unit/test_paper_faithful_state_action_space_batch_metrics.py
tests/unit/test_paper_faithful_state_action_space_batch_behavior_equivalence.py
tests/unit/test_paper_state_vector.py
tests/unit/test_paper_action_space.py
tests/unit/test_paper_load_history.py
tests/integration/test_paper_faithful_state_action_space_batch.py
tests/integration/test_paper_faithful_state_action_space_batch_report.py
tests/integration/test_paper_faithful_state_action_space_batch_scope_guard.py
artifacts/analysis/paper-faithful-state-action-space-batch/
```

## Forbidden paths

```text
.specify/feature.json
AGENTS.md
.gitignore
dependency files
prior Feature 037-064 artifacts
model checkpoint binaries
new training campaign artifacts
release tags
```

## Auto-commit/push authorization

Guarded auto-commit/push is allowed after all tests pass, final report has passing verdict and empty blockers, and dirty-path classification contains only approved Feature 065 paths.
