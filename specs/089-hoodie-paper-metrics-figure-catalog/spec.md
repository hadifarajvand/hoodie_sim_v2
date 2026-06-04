# Feature 089: HOODIE Paper Metrics & Figure Catalog

## Purpose

Feature 089 catalogs all evaluation metrics and figures from the HOODIE paper, using OCR and the PDF original text layer. The goal is to prepare the list of metrics and figures that need to be extracted or output from the simulator in a later feature.

This feature does not produce simulator outputs yet; it only identifies and records required metrics and figures for future comparison or plotting.

## Scope

- Use `resources/papers/hoodie/ocr/merged.txt` to identify text, tables, and metric names.
- Use `resources/papers/hoodie/original/HOODIE_paper.pdf` to resolve ambiguities and capture figures, captions, and axes.
- Extract metric names, scenarios, policies, x-axis / scenario parameters, and figure IDs.
- Identify primary vs secondary metrics.
- Identify which figures are numeric and suitable for simulator comparison.
- Generate a Spec Kit-backed artifact catalog:
  - `paper_metrics_catalog.json`
  - `paper_figures_catalog.json`
- Do not run any simulator outputs.

## Out of Scope

- No simulator output generation.
- No metric computation.
- No output validation.
- No comparison or ranking yet.
- No thesis, DCQ, or custom queue methods.