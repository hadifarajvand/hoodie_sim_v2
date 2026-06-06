# Quickstart: Paper Assumption Closure and Evidence Exhaustion Pipeline

## Purpose
Generate an auditable closure report for all remaining paper-related uncovered or assumption-backed items.

## Inputs
- Paper OCR and PDF artifacts
- Recovered registries
- Prior analysis reports from Features 025, 028, and 029

## Outputs
- `artifacts/analysis/paper-assumption-closure-evidence-exhaustion/assumption-closure-report.json`
- `artifacts/analysis/paper-assumption-closure-evidence-exhaustion/assumption-closure-report.md`

## Workflow
1. Verify all required source artifacts exist.
2. Inventory unresolved or assumption-backed items from prior reports and recovered registries.
3. Search OCR text, structured registries, and prior reports for evidence.
4. Add manual-review entries only for defensible Figure 7, table, or equation cases.
5. Classify each item with the approved status vocabulary.
6. Generate JSON and Markdown closure reports.
7. Validate that the report is deterministic and that every item has exactly one final status.

## Review Expectations
- High-confidence items may be carried forward in later approved work.
- Medium-confidence items require a report caveat.
- Low-confidence items remain report-only until explicit approval.
- Invalid guesses must be rejected.
- Unrecoverable items must remain documented as unresolved.

