# Plan: Feature 089 HOODIE Paper Metrics & Figure Catalog

## Branch

`089-hoodie-paper-metrics-figure-catalog`

Base branch: `087-hoodie-paper-output-comparison`

## Goal

Catalog and classify HOODIE paper evaluation metrics and figures for future extraction and output generation.

## Phases

1. **Paper OCR Analysis**
   - Read `resources/papers/hoodie/ocr/merged.txt`
   - Identify metric names, figure IDs, table IDs, scenario/x-axis parameters, policy labels.
2. **PDF Text & Figures Analysis**
   - Read `resources/papers/hoodie/original/HOODIE_paper.pdf`
   - Resolve ambiguous OCR text.
   - Capture figure captions, axis labels, numeric indicators.
3. **Catalog Construction**
   - For each metric, record:
     - metric name
     - type (primary/secondary)
     - scenario(s) used
     - policy set
     - figure or table reference if numeric output exists
   - For each figure, record:
     - figure ID
     - caption
     - numeric vs qualitative
     - x-axis variable
     - scenarios covered
4. **Artifact Generation**
   - `artifacts/feature_089_paper_metrics_catalog/paper_metrics_catalog.json`
   - `artifacts/feature_089_paper_metrics_catalog/paper_figures_catalog.json`
5. **Validation**
   - Ensure all metrics referenced in figures or tables are included.
   - Ensure no duplicates or missing figure IDs.
   - This is strictly cataloging; no computation or comparison is done.