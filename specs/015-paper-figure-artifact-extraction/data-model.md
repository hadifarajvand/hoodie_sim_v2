# Data Model: Paper Figure Artifact Extraction and Comparison Scaffold

## Entities

### PaperSourceInventory

- `input_paper_path`: OCR file path
- `exists`: whether the OCR file is present
- `figure_ids_requested`: Figures 7, 8, 9, 10, and 11
- `evidence_snippet_count`: number of extracted snippets

### ArtifactInventory

- `input_artifact_root`: campaign artifact root
- `campaign_files`: observed campaign-level files
- `matrix_summary_path`: matrix summary path when present
- `matrix_result_files`: per-run JSON files
- `trace_files`: trace JSON files
- `audit_report_path`: optional audit report path
- `sensitivity_report_path`: optional sensitivity report path
- `missing_required_files`: missing artifact paths

### PaperEvidenceSnippet

- `source_path`: OCR source file
- `figure_id`: figure identifier
- `snippet_index`: deterministic snippet index
- `char_offset`: deterministic character offset
- `text`: evidence text from OCR

### FigureEntry

- `figure_id`: Figure 7, Figure 8, Figure 9, Figure 10, or Figure 11
- `title`: paper figure title or summary
- `paper_claim_type`: caption, evaluation context, or plotted quantity
- `paper_ocr_evidence`: evidence snippets
- `support_status`: `supported`, `partially_supported`, or `unsupported`
- `comparison_ready`: true only when paper target data and artifact reproduction data are sufficient
- `extracted_artifact_metrics`: artifact-backed data
- `missing_artifacts`: missing artifact classes
- `caveats`: scientific and artifact caveats
- `source_artifacts`: artifact paths used

### PaperFigureExtractionReport

- `input_paper_path`
- `input_artifact_root`
- `output_dir`
- `paper_evidence_inventory`
- `artifact_inventory`
- `figure_entries`
- `global_warnings`
- `unsupported_requirements`
- `comparison_readiness`
- `reproducibility_notes`
- `passed`

## Validation Rules

- Existing paper and campaign artifacts are read-only inputs.
- Output is written only to the caller-provided output directory.
- Unsupported figures are explicitly represented.
- Missing paper numeric targets are not replaced with inferred values.
- Report ordering is deterministic.

