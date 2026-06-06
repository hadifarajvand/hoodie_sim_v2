# Paper Figure Extraction Contract

## Input Contract

The extractor consumes:

- `resources/papers/hoodie/ocr/merged.tex`
- campaign summary JSON files
- campaign policy and scenario summary JSON files
- campaign determinism check JSON
- `matrix/matrix-summary.csv`
- `matrix/*.json`
- `matrix/traces/*.json`
- optional `audit/audit-report.json`
- optional `sensitivity/sensitivity-report.json`

## Output Contract

The extractor writes only to a caller-provided output directory:

- `paper-figure-extraction.json`
- `paper-figure-extraction.md`

Each report includes:

- paper source inventory
- artifact inventory
- figure entries for Figures 7 through 11
- support status per figure
- OCR evidence snippets
- artifact-backed metrics where available
- missing artifact classes
- caveats
- comparison readiness
- global warnings
- reproducibility notes

## Behavioral Contract

- The extractor is read-only with respect to paper and campaign artifacts.
- The extractor is deterministic for the same inputs.
- The extractor does not rerun simulations.
- The extractor does not train models.
- The extractor does not digitize images.
- The extractor does not fabricate paper numeric values.
- The extractor does not claim paper reproduction validity.

