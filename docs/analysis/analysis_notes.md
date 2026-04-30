# Analysis Notes

## Paper-backed results

- Validation artifacts are consumed as-is from the validation layer.
- Aggregate and per-trace metrics are taken directly from the evaluation pipeline.
- Baseline and compared-policy groupings are preserved without recomputation or scaling.

## Assumption-backed results

- `A-012` remains approximation-backed for `Phi_n(t)` when the exact closed-form expression is not recovered elsewhere.
- Runtime behavior remains tied to the documented shared-runtime assumptions and recovered parameters.
- Any unresolved paper behavior not present in the staged PDF/OCR resources remains documented outside analysis.

## Limitations

- Analysis does not compute new metrics.
- Analysis does not normalize, smooth, or rescale values.
- Analysis does not touch environment, training, or evaluation execution paths.
