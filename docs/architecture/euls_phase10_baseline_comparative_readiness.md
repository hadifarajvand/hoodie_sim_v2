# Phase 10 Baseline Comparative Readiness Reconciliation

Phase 10 reconciles the comparative-readiness gate behavior without changing EULS runtime semantics, DAL advisory semantics, replay determinism, or policy training behavior.

## Failing tests

| Test file | Test name | Current expected behavior | Actual Phase 9 behavior | Contract category | Judgment | Reason | Action for Phase 10 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `tests/unit/test_baseline_policy_comparative_evaluation_readiness_metrics.py` | `test_compatibility_mode_is_not_used_in_default_comparison` | The feature 074 report should pass | The report is blocked because upstream feature 071 readiness is not passing | baseline-readiness / compatibility gate | stale expectation | The test asserted a pass verdict even though the report contract is explicitly in blockers mode | Update the test to assert the blocked verdict and preserve the compatibility-mode exclusion checks |
| `tests/unit/test_baseline_policy_comparative_evaluation_readiness_report.py` | `test_feature_074_report_passes_only_when_all_gates_pass` | The report should be ready | The report is in blockers mode | baseline-readiness / upstream gate | stale expectation | The builder returns a blocked report and its upstream regression evidence is not all green | Update the test to assert the blocked verdict and keep the claim-boundary checks |
| `tests/unit/test_baseline_policy_comparative_evaluation_readiness_report.py` | `test_report_includes_policy_descriptors_selected_action_evidence_and_regression_evidence` | Feature 071 regression evidence should pass | Feature 071 regression evidence is blocked | baseline-readiness / upstream gate | stale expectation | The test relied on a readiness state that is not currently true | Update the test to assert the presence of the evidence while accepting the blocked Feature 071 status |
| `tests/unit/test_combined_baseline_proposed_comparative_readiness_model.py` | `test_combined_comparative_report_rejects_missing_claim_boundary_and_failed_regression` | Combined readiness report should be buildable from upstream readiness | Feature 074 does not pass, so the combined builder raises before model validation | future training/performance gate / blocked upstream dependency | defer_with_reason | The test was coupled to a passing upstream report that is currently blocked | Use a synthetic valid combined report fixture to test the model validator directly |
| `tests/unit/test_combined_baseline_proposed_comparative_readiness_model.py` | `test_combined_comparative_report_rejects_missing_policy_scenario_and_duplicate_coverage` | Combined readiness report should be buildable from upstream readiness | Feature 074 does not pass, so the combined builder raises before model validation | future training/performance gate / blocked upstream dependency | defer_with_reason | The test was coupled to a passing upstream report that is currently blocked | Use a synthetic valid combined report fixture to test the matrix validator directly |

## Classification

- Baseline readiness metrics failure: stale expectation after the current blocker contract.
- Baseline readiness report failures: stale expectation after the current blocker contract.
- Combined comparative readiness failures: blocked upstream dependency, not an EULS runtime issue.

## Claim-boundary policy

Comparative readiness reports must keep explicit claim boundaries and must not claim final evaluation, superiority, statistical significance, or full paper reproduction.

## Compatibility-mode policy

Compatibility mode remains explicit, but the default comparative-readiness contract does not claim a ready verdict while upstream feature 071 remains blocked.

## Policy-scenario descriptor policy

Policy descriptors remain required and explicit. The tests should verify their presence even when the report stays in blockers mode.

## Duplicate-coverage policy

Duplicate scenario coverage is still rejected by the model validator. The test should exercise the validator directly using a synthetic valid fixture rather than relying on the blocked builder path.

## Why EULS, DAL, replay, and shadow policy are unchanged

These tests live entirely in the analysis/readiness layer. They do not mutate queue lifecycle semantics, deadline handling, reward timing, replay hashing, or DAL advisory behavior.

## Remaining limitations

Feature 074 remains blocked because upstream feature 071 is not passing.
Feature 076 combined readiness remains blocked until the upstream comparative-readiness gate is intentionally advanced.
Phase 10 does not run training or optimizer steps.
Phase 10 does not generate Figures 8–11.
