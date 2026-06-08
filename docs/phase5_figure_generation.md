# Phase 5 Diagnostic Figure Generation

Phase 5 produces diagnostic previews for Figures 8-11 from the Phase 4 validation artifacts. These figures are not claimed as exact paper reproduction.

## Scope

- Read the full Phase 4 validation artifacts
- Generate preview PNGs for Figures 8-11
- Write raw CSV summaries for each figure
- Record diagnostic-only status and paper-performance disclaimer

## Source Artifacts

- `artifacts/phase4_validation/phase4_validation_report.json`
- `artifacts/phase4_validation/phase4_validation_report.md`
- `artifacts/phase4_validation/episode_metrics_summary.csv`
- `artifacts/phase4_validation/policy_action_summary.csv`
- `artifacts/phase4_validation/state_lstm_summary.json`
- `artifacts/phase4_validation/readiness_matrix.csv`

## Figure Mapping

- Figure 8: episode-level task outcomes
- Figure 9: episode-level latency, waiting, and service metrics
- Figure 10: action distribution and legality
- Figure 11: state and LSTM readiness summary

## Commands

```bash
./.venvmac/bin/python phase5_generate_figures.py \
  --input-dir artifacts/phase4_validation \
  --output-dir artifacts/phase5_figures
```

## Outputs

- `artifacts/phase5_figures/figures/*.png`
- `artifacts/phase5_figures/data/*.csv`
- `artifacts/phase5_figures/figure_manifest.json`

## Known Limitations

- The figures are diagnostic previews, not paper reproduction claims.
- Figure 11 still reflects the current Phase 4 forecast status if the Phase 4 artifacts contain a persistence baseline.
- Terminal `next_state` copy fallback remains an inherited Phase 4 caveat.

## Caveats

- `paper_performance_claims_made` is always `false`.
- `diagnostic_only` is always `true`.
