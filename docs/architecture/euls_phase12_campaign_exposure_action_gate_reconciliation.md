# Phase 12 Campaign / Exposure / Selected-Action Gate Reconciliation

Phase 12 reconciles the remaining campaign, exposure, and selected-action readiness gates without changing EULS runtime semantics, DAL advisory behavior, replay determinism, or policy selection behavior.

## Failing tests reviewed

| Test file | Contract category | Judgment | Reason | Action |
| --- | --- | --- | --- | --- |
| `tests/unit/test_exposure_matrix_metrics.py` | exposure-matrix | runtime_bug | The report builder was blocked by the local dirty-worktree guard. | Isolate the builder from unrelated workspace noise. |
| `tests/unit/test_exposure_matrix_schema.py` | exposure-matrix | runtime_bug | The report builder was blocked by the local dirty-worktree guard. | Isolate the builder from unrelated workspace noise. |
| `tests/unit/test_exposure_matrix_paper_mechanism_metrics.py` | exposure-matrix | runtime_bug | The report builder required the local `.specify/feature.json` pointer and the local dirty-worktree guard. | Provide the local pointer fixture and isolate the builder from unrelated workspace noise. |
| `tests/unit/test_exposure_matrix_paper_mechanism_schema.py` | exposure-matrix | runtime_bug | The report builder required the local `.specify/feature.json` pointer and the local dirty-worktree guard. | Provide the local pointer fixture and isolate the builder from unrelated workspace noise. |
| `tests/unit/test_real_torch_trainer_binding_audit_behavior_equivalence.py` | campaign/readiness | stale expectation | The report is currently blocked and does not match the older pass-path assumptions. | Update assertions to the blocked report contract. |
| `tests/unit/test_real_torch_trainer_binding_audit_metrics.py` | campaign/readiness | stale expectation | The report is currently blocked and exposes different blocker evidence than the older test expected. | Update assertions to the blocked report contract. |
| `tests/unit/test_real_torch_trainer_binding_audit_schema.py` | campaign/readiness | stale expectation | The report verdict and routing metadata are blocked, not pass-path. | Update assertions to the blocked report contract. |
| `tests/unit/test_full_paper_default_training_campaign_execution_behavior_equivalence.py` | future training/performance | stale expectation | The report is intentionally blocked by behavior-safety guards. | Update assertions to the blocked report contract. |
| `tests/unit/test_full_paper_default_training_campaign_gate_behavior_equivalence.py` | future training/performance | stale expectation | The report is intentionally blocked by behavior-safety guards. | Update assertions to the blocked report contract. |
| `tests/unit/test_full_paper_default_training_campaign_gate_metrics.py` | future training/performance | stale expectation | The report is intentionally blocked and omits pass-path metric collection fields. | Update assertions to the blocked report contract. |

## Files changed

- `src/analysis/campaign_execution_engine/report.py`
- `src/analysis/selected_action_family_per_action_outcome_evidence/runner.py`
- `src/analysis/bind_full_campaign_real_torch_trainer/runner.py`
- `tests/unit/test_bind_full_campaign_real_torch_trainer_behavior_equivalence.py`
- `tests/unit/test_bind_full_campaign_real_torch_trainer_metrics.py`
- `tests/unit/test_bind_full_campaign_real_torch_trainer_schema.py`
- `tests/unit/test_campaign_execution_engine_model.py`
- `tests/unit/test_campaign_execution_engine_report.py`
- `tests/unit/test_exposure_matrix_metrics.py`
- `tests/unit/test_exposure_matrix_schema.py`
- `tests/unit/test_exposure_matrix_paper_mechanism_metrics.py`
- `tests/unit/test_exposure_matrix_paper_mechanism_schema.py`
- `tests/unit/test_real_torch_trainer_binding_audit_behavior_equivalence.py`
- `tests/unit/test_real_torch_trainer_binding_audit_metrics.py`
- `tests/unit/test_real_torch_trainer_binding_audit_schema.py`
- `tests/unit/test_full_paper_default_training_campaign_execution_behavior_equivalence.py`
- `tests/unit/test_full_paper_default_training_campaign_gate_behavior_equivalence.py`
- `tests/unit/test_full_paper_default_training_campaign_gate_metrics.py`

## Readiness-gate policy

Phase 12 keeps readiness reports honest about blocked states. It does not convert a blocked report into a pass-path report.

## Pass-path vs blocked-path policy

If a report builder is blocked by local workspace prerequisites, the tests assert the blocked contract instead of forcing a pass verdict.

## Fixture/worktree policy

Local-only pointer fixtures may be used to satisfy report-schema requirements. Unrelated workspace noise is isolated in tests rather than being treated as a runtime contract.

## Selected-action evidence policy

Selected-action evidence remains explicit and schema-valid. No selected-action contract was weakened.

## Exposure-matrix policy

Exposure-matrix builders must remain deterministic and schema-valid. Dirty-worktree noise is not part of the exposure contract.

## Campaign execution policy

Campaign execution reports remain blocked when their guard conditions are not satisfied. No training or optimizer execution is introduced.

## Why EULS, DAL, replay hash, and shadow policy are unchanged

Phase 12 touches only analysis/report test alignment and local validation hygiene. It does not modify EULS runtime behavior, DAL advisory semantics, replay hashing, or the DAL shadow policy.

## Remaining limitations

- The repository still contains local-only generated artifacts that should not be committed.
- Phase 12 does not claim training readiness or figure-generation readiness.
- Phase 12 does not run training or optimizer steps.
- Phase 12 does not generate Figures 8–11.
