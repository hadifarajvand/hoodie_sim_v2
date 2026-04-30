# Validation Deviations

## Paper-backed behavior

- Shared evaluation traces are generated and replayed through `EvaluationRunner`.
- Metric formulas remain centralized in the existing evaluation pipeline.
- Validation uses the same seed, trace ID base, and episode length across compared policies.

## Assumption-backed behavior

- `A-012` reward handling still depends on the documented approximation for `Phi_n(t)` when no exact recovered formula is available elsewhere.
- Runtime calibration remains tied to the recovered parameter set and documented assumptions in the shared runtime model.
- Any missing paper parameter that is not explicitly recovered in the staged resources remains documented in the corresponding assumptions and runtime evidence notes.

## Notes

- Validation does not invent alternate metrics, reward semantics, or simulation behavior.
- Any mismatch in validation inputs is treated as a failure rather than silently normalized.
