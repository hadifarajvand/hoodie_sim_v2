# Tasks: Feature 089 HOODIE Paper Metrics & Figure Catalog

## A. OCR Analysis

- [ ] Read `resources/papers/hoodie/ocr/merged.txt`.
- [ ] Extract metric names from text.
- [ ] Extract scenario/x-axis and policy labels.
- [ ] Identify tables and their numeric content.

## B. PDF Analysis

- [ ] Open `resources/papers/hoodie/original/HOODIE_paper.pdf`.
- [ ] Resolve any ambiguous metric names or labels.
- [ ] Extract figure captions and IDs.
- [ ] Determine numeric vs qualitative figures.

## C. Catalog Construction

- [ ] Create JSON and Markdown catalogs of metrics.
- [ ] Create JSON and Markdown catalogs of figures.
- [ ] Mark primary vs secondary metrics.
- [ ] Map metric to figures/tables where appropriate.
- [ ] Include scenario, x-axis, and policy coverage.
- [ ] Identify outputs that will require simulator extraction later.

## D. Validation

- [ ] Verify all metrics from figures/tables are present.
- [ ] Check for duplicate metric or figure IDs.
- [ ] Validate JSON schema for future pipeline consumption.
- [ ] Confirm no simulator output is generated yet.