# Contract: Paper Mechanism Registry Output

## Output Artifacts

- `paper-mechanism-registry.json`
- `paper-mechanism-registry.md`

## Contract Summary

The registry is a read-only analysis artifact that maps paper mechanisms to OCR evidence, paper references, implementation status, missing details, and assumption risk.

## Required JSON Shape

```json
{
  "input_sources": {
    "paper_ocr": "resources/papers/hoodie/ocr/merged.tex",
    "secondary_sources": []
  },
  "registry_version": "016",
  "read_only": true,
  "behavior_changes": false,
  "mechanism_entries": [],
  "blocking_gaps": [],
  "high_risk_assumptions": [],
  "implementation_gap_summary": {},
  "next_recommended_feature": "reference_task_lifecycle_kernel",
  "passed": true
}
```

## Required Markdown Shape

- Title
- Read-only warning
- Summary table
- Blocking gaps
- High-risk assumptions
- Mechanism entries
- Implementation gap summary
- Recommended next feature
- No runtime changes statement

## Determinism Contract

- JSON output must be stable in key ordering and array ordering.
- Markdown output must be stable in section order and entry ordering.

## Evidence Rules

- Every paper-derived claim must carry OCR evidence.
- Missing evidence must be explicit.
- Unsupported claims must not be fabricated.
