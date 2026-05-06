# Data Model: Paper Result Reporting & Reproducibility Artifacts

## Entities

### ReproducibilityBundleConfig
- `matrix_output_dir`: source directory containing evaluation artifacts
- `bundle_output_dir`: destination directory for the reproducibility bundle
- `policy_names`: ordered policy names used in the matrix
- `scenario_names`: ordered scenario names used in the matrix
- `seeds`: ordered seeds used in the matrix
- `created_at_override`: deterministic timestamp override for tests and repeatability
- `dependency_change_note`: human-readable note about dependency stability

### ArtifactRecord
- `relative_path`: path inside the bundle, relative to the bundle root
- `kind`: artifact type such as `run_json`, `summary_csv`, `trace`, `manifest`, `config`, or `validation`
- `sha256`: checksum of the artifact contents
- `size_bytes`: size of the artifact in bytes

### ValidationSummary
- `expected_runs`: computed from policy count × scenario count × seed count
- `discovered_run_json_files`: count of run JSON files found in the matrix output directory
- `matrix_summary_exists`: whether `matrix-summary.csv` was found
- `missing_artifacts`: list of missing expected artifact paths or groups
- `passed`: boolean completeness result

### Bundle Outputs
- `manifest.json`: top-level provenance and checksum inventory
- `run-config.json`: snapshot of the evaluation matrix configuration
- `artifact-index.json`: relative-path listing of bundle contents
- `validation-summary.json`: completeness check result
- `README.md`: human-readable bundle guide

## Relationships

- `ReproducibilityBundleConfig` drives bundle generation.
- `ReproducibilityBundleBuilder` scans the matrix output directory, derives `ArtifactRecord` entries, and writes the bundle outputs.
- `ValidationSummary` is derived from the discovered artifacts and the expected matrix run count.

## Validation Rules

- All artifact paths in the index must be relative to the bundle root.
- Artifact records must be sorted deterministically before writing outputs.
- Missing expected artifacts must be represented in the validation summary.
- The same inputs and override timestamp must yield identical outputs.
