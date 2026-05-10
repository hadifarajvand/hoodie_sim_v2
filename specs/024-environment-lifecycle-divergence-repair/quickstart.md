# Quickstart: Environment Lifecycle Divergence Repair

## Purpose

Run the Feature 024 repair workflow to verify whether remaining lifecycle divergences can be fixed surgically without expanding scope.

## Required Inputs

- Feature 018 differential audit:
  - `artifacts/analysis/differential-environment-audit/differential-audit.json`
  - `artifacts/analysis/differential-environment-audit/differential-audit.md`
- Feature 019 mechanism repair summary:
  - `artifacts/analysis/mechanism-repair/repair-summary.json`
  - `artifacts/analysis/mechanism-repair/repair-summary.md`
- Reference lifecycle kernel:
  - `src/reference_model/__init__.py`
  - `src/reference_model/ledger.py`
  - `src/reference_model/lifecycle.py`
  - `src/reference_model/models.py`
- HOODIE paper OCR only if delayed reward timing needs paper grounding:
  - `resources/papers/hoodie/ocr/merged.tex`

## Expected Outputs

- `artifacts/analysis/environment-lifecycle-divergence-repair/repair-summary.json`
- `artifacts/analysis/environment-lifecycle-divergence-repair/repair-summary.md`
- `artifacts/analysis/differential-environment-audit/differential-audit.json`
- `artifacts/analysis/differential-environment-audit/differential-audit.md`

## Validation Guidance

- Use the approved project interpreter at `/Users/hadi/Documents/GitHub/hoodie_sim_v2/src/.venvmac/bin/python`
- Run the unit regression tests for local compute completion, deterministic ordering, and scope guards
- Run the integration regression tests comparing `HoodieGymEnvironment` to the reference lifecycle kernel
- Confirm the regenerated differential audit no longer classifies `case-local-compute` or `case-deterministic-ordering` as `divergence / likely_environment_bug`

## Scope Reminder

- No DRL training is introduced
- No neural-network code is introduced
- No TorchRL, Gymnasium, ns-3, or ns-3-gym is introduced
- No policy redesign, metric change, baseline redesign, or campaign rerun is allowed
- No paper-validity claim is made
