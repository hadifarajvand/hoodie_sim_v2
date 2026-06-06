# Tasks: Paper Figure Artifact Extraction and Comparison Scaffold

**Input**: Design documents from `/specs/015-paper-figure-artifact-extraction/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

## Phase 1: Setup

**Purpose**: Establish the read-only extraction module and focused test surface.

- [X] T001 Create `src/analysis/paper_figure_extraction.py` with deterministic report data structures and extractor entry points
- [X] T002 Create `tests/unit/test_paper_figure_extraction.py` with fixture helpers for OCR text, campaign artifacts, matrix records, and output verification

## Phase 2: Paper OCR Extraction

**Purpose**: Load the paper OCR source of truth and retain traceable evidence.

- [X] T003 Implement OCR loading from `resources/papers/hoodie/ocr/merged.tex` in `src/analysis/paper_figure_extraction.py`
- [X] T004 Implement deterministic figure caption and context extraction for Figures 7, 8, 9, 10, and 11 in `src/analysis/paper_figure_extraction.py`
- [X] T005 Implement OCR evidence snippets with source path, figure id, snippet index, character offset, and text in `src/analysis/paper_figure_extraction.py`
- [X] T006 Add unit tests in `tests/unit/test_paper_figure_extraction.py` for caption extraction from small OCR fixture text

## Phase 3: Artifact Loading

**Purpose**: Load committed campaign artifacts as read-only inputs.

- [X] T007 Implement artifact inventory loading for campaign JSON, matrix summary CSV, matrix run JSON, trace JSON, optional audit report, and optional sensitivity report in `src/analysis/paper_figure_extraction.py`
- [X] T008 Implement missing artifact reporting in `src/analysis/paper_figure_extraction.py`
- [X] T009 Add unit tests in `tests/unit/test_paper_figure_extraction.py` for missing artifact reporting and deterministic artifact ordering

## Phase 4: Figure 7 Extraction

**Purpose**: Classify topology support without reconstructing topology from source code.

- [X] T010 Implement Figure 7 support classification in `src/analysis/paper_figure_extraction.py`
- [X] T011 Ensure Figure 7 reports EA count when present and marks topology adjacency missing unless committed graph-edge artifacts exist

## Phase 5: Figure 8 Unsupported / Training Gap Classification

**Purpose**: Prevent false training-curve claims.

- [X] T012 Implement Figure 8 unsupported classification when training reward curve artifacts are absent in `src/analysis/paper_figure_extraction.py`
- [X] T013 Add required missing artifact classes for learning-rate, discount-factor, and true HOODIE DRL training logs
- [X] T014 Add unit tests in `tests/unit/test_paper_figure_extraction.py` for unsupported Figure 8 without training curves

## Phase 6: Figure 9 Artifact-Backed Behavior Extraction

**Purpose**: Extract available action behavior while keeping reward and sweep gaps explicit.

- [X] T015 Implement Figure 9 action distribution extraction from matrix raw records and optional sensitivity report in `src/analysis/paper_figure_extraction.py`
- [X] T016 Implement Figure 9 missing sweep classification for reward, CPU capacity, agent-count, and offloading data-rate dimensions
- [X] T017 Add unit tests in `tests/unit/test_paper_figure_extraction.py` for Figure 9b action distribution extraction

## Phase 7: Figure 10 Baseline Metric Extraction

**Purpose**: Extract delay and drop-ratio baseline tables from committed matrix artifacts.

- [X] T018 Implement Figure 10 average-delay and drop-ratio extraction by policy, scenario, policy-scenario, and seed in `src/analysis/paper_figure_extraction.py`
- [X] T019 Add Figure 10 caveat preserving repository metric signs and paper negative-delay convention
- [X] T020 Add unit tests in `tests/unit/test_paper_figure_extraction.py` for Figure 10 extraction from tiny `matrix-summary.csv`

## Phase 8: Figure 11 Unsupported / LSTM Gap Classification

**Purpose**: Prevent false LSTM ablation claims.

- [X] T021 Implement Figure 11 unsupported classification when HOODIE with/without LSTM training delay curves are absent in `src/analysis/paper_figure_extraction.py`
- [X] T022 Add required missing artifact classes for LSTM and non-LSTM training delay logs
- [X] T023 Add unit tests in `tests/unit/test_paper_figure_extraction.py` for unsupported Figure 11 without LSTM ablation artifacts

## Phase 9: Audit / Sensitivity Warning Integration

**Purpose**: Carry known artifact caveats into comparison readiness.

- [X] T024 Implement audit warning integration for high drop ratio, weak scenario differentiation, and identical policy signatures in `src/analysis/paper_figure_extraction.py`
- [X] T025 Implement sensitivity warning integration for scenario output collapse, policy behavior collapse, near-identical outcomes, saturation dominance, and trace comparison status in `src/analysis/paper_figure_extraction.py`

## Phase 10: Report Rendering

**Purpose**: Produce deterministic machine-readable and human-readable reports.

- [X] T026 Implement `paper-figure-extraction.json` rendering in `src/analysis/paper_figure_extraction.py`
- [X] T027 Implement `paper-figure-extraction.md` rendering in `src/analysis/paper_figure_extraction.py`
- [X] T028 Ensure output writes go only to a caller-provided output directory and no timestamps are included unless explicitly supplied

## Phase 11: Unit Tests

**Purpose**: Verify isolated extraction behavior.

- [X] T029 Ensure unit tests cover OCR extraction, missing artifacts, Figure 8 unsupported, Figure 9 action distribution, Figure 10 metrics, Figure 11 unsupported, deterministic ordering, and no input mutation

## Phase 12: Integration Tests

**Purpose**: Validate the real committed OCR and campaign artifact flow.

- [X] T030 Create `tests/integration/test_paper_figure_extraction_flow.py`
- [X] T031 Add integration test targeting `resources/papers/hoodie/ocr/merged.tex` and `artifacts/campaigns/paper-baseline-reproduction`
- [X] T032 Verify integration report includes Figures 7, 8, 9, 10, and 11
- [X] T033 Verify Figure 8 and Figure 11 are unsupported unless training artifacts exist
- [X] T034 Verify Figure 10 has artifact-backed delay/drop-ratio metrics
- [X] T035 Verify Figure 9 has artifact-backed action distribution when raw records exist
- [X] T036 Verify audit/sensitivity warnings are included when optional reports exist
- [X] T037 Verify repeated outputs are byte-identical and existing campaign artifacts are not modified

## Phase 13: Documentation

**Purpose**: Keep paper-to-code traceability current.

- [X] T038 Update `docs/paper_notes/paper_to_code_mapping.md` with paper figure extraction mapping if needed

## Phase 14: Forbidden Path Verification

**Purpose**: Prove scope stayed analysis-only.

- [X] T039 Verify no changes to `src/environment/*`, `src/policies/*`, `src/evaluation/metrics.py`, `src/training/*`, `src/agents/*`, dependency files, or packaging files
- [X] T040 Verify no simulator execution, training implementation, policy modification, metric formula modification, environment modification, dependency modification, required plotting, image digitization, or fabricated paper numeric values were introduced

## Phase 15: Determinism Verification

**Purpose**: Prove reproducibility.

- [X] T041 Run `src/.venvmac/bin/python -m unittest tests.unit.test_paper_figure_extraction tests.integration.test_paper_figure_extraction_flow`
- [X] T042 Run extraction against `artifacts/campaigns/paper-baseline-reproduction` into `artifacts/analysis/paper-figure-extraction`
- [X] T043 Verify `paper-figure-extraction.json` and `paper-figure-extraction.md` are byte-identical across repeated runs
- [X] T044 Update this task list to checked state only after validation passes

## Rejected Scope

The approved task list excludes simulator execution, training implementation, policy modification, metric formula modification, environment modification, dependency modification, required figure plotting, image digitization, and fabricated paper numeric values.
