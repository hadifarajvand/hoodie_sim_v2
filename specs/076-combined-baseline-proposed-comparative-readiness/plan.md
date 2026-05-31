# Feature 076 Plan: Combined Baseline + Proposed Comparative Readiness

## Purpose

Feature 076 combines the action-bound baseline comparison from Feature 074 and the action-bound proposed-method readiness from Feature 075 into one controlled comparative readiness layer.

This is a readiness feature only. It is not the final experiment, not a training feature, and not a claim of superiority.

## Dependency Chain

Feature 076 starts from:

- Feature 075 branch: `075-proposed-integration-readiness`
- Expected base commit: `b23b2fa5b1c8fc6d58f3eb533164f83c05c2ec61` or newer

Required upstream feature contracts:

- Feature 068R: baseline policy fidelity and legal-mask authority
- Feature 069: full HOODIE mechanism-fidelity readiness boundary
- Feature 070: topology, timeout/drop, and reward evidence recovery
- Feature 071: runtime paper-mode timeout and reward semantics
- Feature 072: golden trace validation
- Feature 073: controlled evaluation batch readiness
- Feature 074: baseline action-bound comparative readiness
- Feature 075: proposed-method action-bound integration readiness

## Implementation Shape

Create one read-only analysis package:

```text
src/analysis/combined_baseline_proposed_comparative_readiness/
```

Expected files:

```text
__init__.py
__main__.py
config.py
model.py
report.py
runner.py
```

Create tests only under:

```text
tests/unit/test_combined_baseline_proposed_comparative_readiness_*.py
tests/integration/test_combined_baseline_proposed_comparative_readiness_*.py
```

## Data Flow

1. Load Feature 074 baseline comparison rows.
2. Load Feature 075 proposed-method rows.
3. Normalize both sources into a common row schema.
4. Validate full policy/method coverage.
5. Validate full scenario coverage.
6. Validate action-bound terminal and reward metrics.
7. Compute aggregate metrics per policy/method.
8. Produce one combined readiness report.

## Required Methods

The combined matrix must contain exactly these policy/method identifiers:

```text
FLC
VO
HO
RO
BCO
MLEO
PROPOSED_DCQ
```

Feature 076 must reject readiness if one of these is missing.

## Required Scenarios

The combined matrix must contain exactly these scenario identifiers for every policy/method:

```text
light_load_no_deadline_pressure
tight_deadline_pressure
legal_horizontal_offload
illegal_horizontal_destination_attempt
cloud_vertical_fallback
timeout_drop_case
mixed_local_horizontal_cloud_candidates
```

Feature 076 must reject readiness if one scenario is missing from any policy/method.

## Row Contract

Each normalized combined row must include:

- `policy_id`
- `policy_family`
- `scenario_id`
- `selected_action_id`
- `selected_action_family`
- `action_legality`
- `action_bound_terminal_status`
- `action_bound_reward_value`
- `action_bound_metrics_derived`
- `compatibility_mode_used`
- `decision_trace_present`
- `completed_count`
- `dropped_timeout_count`
- `dropped_unavailable_count`
- `deadline_violation_count`
- `illegal_action_rejection_count`
- `average_delay`
- `average_reward`

## Aggregate Contract

Compute per policy/method:

- `scenario_count`
- `completed_count`
- `dropped_timeout_count`
- `dropped_unavailable_count`
- `deadline_violation_count`
- `illegal_action_rejection_count`
- `mean_delay`
- `mean_reward`

Do not compute winners. Do not rank methods by superiority.

## Scope Guard

Allowed paths:

```text
specs/076-combined-baseline-proposed-comparative-readiness/**
src/analysis/combined_baseline_proposed_comparative_readiness/**
tests/unit/test_combined_baseline_proposed_comparative_readiness_*.py
tests/integration/test_combined_baseline_proposed_comparative_readiness_*.py
```

Forbidden paths:

```text
src/environment/**
src/policies/**
src/training/**
src/agents/**
artifacts/**
resources/**
Feature 077+ paths
dependency files
lock files
```

## Validation Plan

Run targeted regression slices for Features 068R through 075, then run Feature 076 unit and integration tests.

Required commands should use:

```text
src/.venvmac/bin/python
```

Minimum validation:

```text
src/.venvmac/bin/python -m unittest tests.unit.test_policy_registry tests.unit.test_baseline_policy_fidelity tests.unit.test_mleo_policy tests.integration.test_baseline_policy_fidelity_flow
src/.venvmac/bin/python -m unittest tests.unit.test_full_hoodie_mechanism_fidelity_batch_report tests.unit.test_full_hoodie_mechanism_fidelity_batch_scope_guard tests.integration.test_full_hoodie_mechanism_fidelity_batch_report
src/.venvmac/bin/python -m unittest tests.unit.test_topology_timeout_reward_fidelity_report tests.unit.test_topology_timeout_reward_fidelity_models tests.unit.test_topology_timeout_reward_fidelity_scope_guard tests.integration.test_topology_timeout_reward_fidelity_report
src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_runtime_paper_faithful_semantics_alignment_*.py'
src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_runtime_paper_faithful_semantics_alignment_*.py'
src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_end_to_end_hoodie_golden_trace_validation_*.py'
src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_end_to_end_hoodie_golden_trace_validation_*.py'
src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_controlled_evaluation_batch_readiness_*.py'
src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_controlled_evaluation_batch_readiness_*.py'
src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_baseline_policy_comparative_evaluation_readiness_*.py'
src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_baseline_policy_comparative_evaluation_readiness_*.py'
src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_proposed_method_integration_readiness_*.py'
src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_proposed_method_integration_readiness_*.py'
src/.venvmac/bin/python -m unittest discover tests/unit -p 'test_combined_baseline_proposed_comparative_readiness_*.py'
src/.venvmac/bin/python -m unittest discover tests/integration -p 'test_combined_baseline_proposed_comparative_readiness_*.py'
git diff --check
```

## Completion Criteria

Feature 076 is complete only when:

- combined report status is `combined_baseline_proposed_comparative_readiness_ready`
- report `passed=True`
- all 7 methods are present
- all 7 scenarios are present per method
- total combined rows equal 49
- every row is action-bound
- no row uses compatibility mode
- all aggregate metrics are computed
- claim boundaries are explicit
- scope validator passes
- no PR is opened
- no merge is performed
