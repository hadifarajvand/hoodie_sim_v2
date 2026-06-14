# Phase 7.4 Visual Comparison Report

This is a visual/paper-metric comparison report. It is not official paper reproduction, it is not exact figure reproduction, and it does not enable contribution logic.

## Scope

Phase 7.4 compares the accepted Phase 7.1 generated plots against the HOODIE paper's relevant simulation figures and metric trends.

## Source Artifacts

- Phase 7.1 artifacts: `artifacts/paper-metric-results/phase7_1_medium_20260614_081135/`
- Phase 7.3 sensitivity audit: `artifacts/paper-contract-audit/phase7_3/sweep_parameter_sensitivity_audit.md`
- Phase 7.1 plots reviewed:
  - `delay_vs_local_cpu_capacity.png`
  - `delay_vs_task_arrival_probability.png`
  - `delay_vs_task_timeout.png`
  - `drop_ratio_vs_local_cpu_capacity.png`
  - `drop_ratio_vs_task_arrival_probability.png`
  - `drop_ratio_vs_task_timeout.png`
  - `hoodie_action_distribution.png`

## Paper Source Availability

The repository includes the HOODIE paper source and OCR TeX:

- `HOODIE_paper.pdf`
- `resources/papers/hoodie/ocr/merged.tex`

Relevant paper captions and discussion were available in `merged.tex`, so this report uses paper figure/metric mapping rather than a blind qualitative guess.

## Manifest Verification

Phase 7.1 flags confirmed from the packaged manifest:

- `simulator_derived_metrics=true`
- `synthetic_metric_profile_used=false`
- `official_paper_reproduction=false`
- `exact_figure_reproduction_claim=false`
- `deadline_aware_extension=false`
- `qos_extension=false`
- `queueing_extension=false`
- `contribution_enabled=false`

## Plot-to-Paper Mapping

| Phase 7.1 plot | Target paper metric / figure | Visual comparison status | Usability for Chapter 4 | Notes |
|---|---|---|---|---|
| `delay_vs_task_arrival_probability.png` | Fig. 10a-style average delay vs task arrival probability | `usable_for_visual_comparison` | Safe to use as non-official reproduction-oriented visual comparison | Clear policy separation and monotonic trend are visible |
| `drop_ratio_vs_task_arrival_probability.png` | Fig. 10d-style drop ratio vs task arrival probability | `usable_for_visual_comparison` | Safe to use as non-official reproduction-oriented visual comparison | Clear policy separation and monotonic trend are visible |
| `delay_vs_local_cpu_capacity.png` | Fig. 10b-style average delay vs local CPU capacity | `usable_with_warning` | Usable only with warning | Phase 7.3 found the sweep flat across all policies in the packaged results |
| `drop_ratio_vs_local_cpu_capacity.png` | Fig. 10e-style drop ratio vs local CPU capacity | `usable_with_warning` | Usable only with warning | Phase 7.3 found the sweep flat across all policies in the packaged results |
| `delay_vs_task_timeout.png` | Fig. 10c-style average delay vs task timeout | `usable_for_visual_comparison` | Safe to use as non-official reproduction-oriented visual comparison | Clear policy separation and trend variation are visible |
| `drop_ratio_vs_task_timeout.png` | Fig. 10f-style drop ratio vs task timeout | `usable_for_visual_comparison` | Safe to use as non-official reproduction-oriented visual comparison | Clear policy separation and trend variation are visible |
| `hoodie_action_distribution.png` | Fig. 9-style action/offloading distribution | `diagnostic_only` | Diagnostic only | Useful for structural discussion, but not a substitute for a paper-grade action-distribution reproduction |

## Result-Quality Summary

Phase 7.3 conclusion holds:

- `task_arrival_probability_sweep`: sensitive
- `local_cpu_capacity_sweep`: not sensitive in Phase 7.1 outputs
- `task_timeout_sweep`: sensitive
- no code fix required
- no Phase 7.1 rerun required

The local CPU plots are not broken, but they are weak evidence for Chapter 4 because the experiment output is flat across the sweep. That makes them warning-only rather than strong comparison material.

## Chapter 4 Recommendation

Classification for Chapter 4:

- Safe to use as non-official reproduction-oriented visual comparison:
  - `delay_vs_task_arrival_probability.png`
  - `drop_ratio_vs_task_arrival_probability.png`
  - `delay_vs_task_timeout.png`
  - `drop_ratio_vs_task_timeout.png`
- Usable only with warning:
  - `delay_vs_local_cpu_capacity.png`
  - `drop_ratio_vs_local_cpu_capacity.png`
- Diagnostic only:
  - `hoodie_action_distribution.png`
- Not suitable:
  - none of the Phase 7.1 plots are blocked outright

## Figure Mapping Notes

The paper discusses:

- average delay vs task arrival probability
- drop ratio vs task arrival probability
- average delay vs CPU computation capacity
- drop ratio vs CPU computation capacity
- average delay vs task timeout
- drop ratio vs task timeout
- action distribution / offloading behavior
- policy comparison across HOODIE, RO, FLC, VO, HO, BCO, and MLEO

The Phase 7.1 outputs line up with those paper-style metrics, but this report does not claim exact official reproduction.

## Next Step

Recommended next phase:

- `Phase 7.5 — Chapter 4 result table drafting from accepted artifacts`

That is the right move because enough plots are usable for a paper-style visual comparison, and the local CPU weakness is already understood.
