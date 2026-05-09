# Quickstart: Paper Mechanism Registry

## Input

- Paper OCR source: `resources/papers/hoodie/ocr/merged.tex`
- Optional secondary sources:
  - `resources/papers/hoodie/ocr/merged.md`
  - `resources/papers/hoodie/ocr/merged.txt`
  - `resources/papers/hoodie/ocr/merged.json`
  - `resources/papers/hoodie/HOODIE_paper.pdf`
- Optional analysis sources:
  - `artifacts/analysis/paper-figure-extraction/paper-figure-extraction.json`
  - `artifacts/analysis/paper-figure-extraction/paper-figure-extraction.md`
  - `artifacts/campaigns/paper-baseline-reproduction/audit/audit-report.json`
  - `artifacts/campaigns/paper-baseline-reproduction/sensitivity/sensitivity-report.json`

## Output

- `paper-mechanism-registry.json`
- `paper-mechanism-registry.md`

## Expected Behavior

- The registry builder reads the OCR text as the source of truth.
- The registry builder records evidence snippets and deterministic snippet locations.
- The registry builder marks missing or ambiguous mechanisms explicitly.
- The registry builder preserves a strict boundary between paper evidence and project mappings.

## Review Checklist

- Confirm `read_only` is `true`.
- Confirm `behavior_changes` is `false`.
- Confirm all 25 required mechanism categories are present.
- Confirm topology adjacency is not invented.
- Confirm learned training mechanics are not overstated.

## Interpretation Notes

- If the paper is explicit about a mechanism but ambiguous about units or exact mapping, the registry should preserve the ambiguity rather than guess.
- If optional secondary sources add useful context, they should be treated as context only.
