# Feature Specification: Paper Figure Artifact Extraction and Comparison Scaffold

**Feature Branch**: `[015-paper-figure-artifact-extraction]`  
**Created**: 2026-05-07  
**Status**: Draft  
**Input**: User description: "Paper Figure Artifact Extraction and Comparison Scaffold"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Identify Figure Support (Priority: P1)

As a reviewer, I want a figure-by-figure support report for the HOODIE paper evaluation figures so I can see which figures are supported, partially supported, or unsupported by committed artifacts.

**Why this priority**: This is the minimum useful outcome. Without explicit support classification, the repository can accidentally overclaim paper reproduction readiness.

**Independent Test**: Run the extraction against the committed paper OCR and campaign artifact tree, then verify that the report includes Figures 7 through 11 with a support status and comparison readiness result for each figure.

**Acceptance Scenarios**:

1. **Given** the paper OCR and committed campaign artifacts are available, **When** the extraction runs, **Then** the report includes entries for Figures 7, 8, 9, 10, and 11.
2. **Given** a figure needs artifacts that are not committed, **When** the extraction runs, **Then** the figure is marked `unsupported` or `partially_supported` with the missing artifact classes listed.

---

### User Story 2 - Preserve Paper Evidence (Priority: P2)

As a reviewer, I want every paper-derived figure claim to include OCR evidence so I can trace each claim back to the paper text rather than trusting undocumented assumptions.

**Why this priority**: Captions and surrounding paper context are the only approved paper source for this feature. Evidence snippets prevent fabricated or hand-waved mappings.

**Independent Test**: Run the extraction and verify that every figure entry includes source evidence snippets from `resources/papers/hoodie/ocr/merged.tex`.

**Acceptance Scenarios**:

1. **Given** Figure 10 is described in the OCR text, **When** the report is generated, **Then** Figure 10 includes evidence snippets that identify the paper quantities being plotted.
2. **Given** numeric curve values are not present in OCR text, **When** the report is generated, **Then** the report marks paper numeric target data as missing instead of inventing values.

---

### User Story 3 - Extract Artifact-Backed Metrics (Priority: P3)

As a reviewer, I want artifact-backed summaries for the supported portions of Figures 9 and 10 so I can compare what the repository actually contains with what the paper figures require.

**Why this priority**: Existing matrix artifacts contain useful baseline metrics and action distributions, but they do not cover all paper figure dimensions.

**Independent Test**: Run the extraction against the committed baseline campaign artifacts and verify that Figure 10 includes delay and drop-ratio tables where available, and Figure 9 includes action distribution data where available.

**Acceptance Scenarios**:

1. **Given** matrix summary and per-run records are present, **When** Figure 10 is extracted, **Then** average delay and drop ratio are grouped by policy, scenario, policy-scenario, and seed where available.
2. **Given** raw action records or sensitivity outputs are present, **When** Figure 9 is extracted, **Then** action distributions are included while unsupported reward and sweep dimensions remain explicitly marked missing.

---

### Edge Cases

- What happens when `merged.tex` is missing or does not contain one of the target figure captions?
- What happens when matrix summary exists but per-run matrix JSON records are missing?
- What happens when audit or sensitivity reports are absent?
- What happens when existing artifacts contain positive repository delay metrics while the paper caption describes negative average delay by convention?
- What happens when topology, training, CPU-capacity, timeout, data-rate, learning-rate, discount-factor, or LSTM ablation artifacts are not committed?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The feature MUST read `resources/papers/hoodie/ocr/merged.tex` as the paper-text source of truth for figure captions, evaluation context, scenario descriptions, simulation parameter mentions, metric conventions, baseline names, and plotted-quantity claims.
- **FR-002**: The feature MUST retain deterministic paper evidence snippets from `merged.tex` for every paper-derived figure claim, including source path, figure id, snippet text, and deterministic offset or snippet index.
- **FR-003**: The feature MUST read committed artifact inputs from `artifacts/campaigns/paper-baseline-reproduction`, including campaign JSON files, `matrix-summary.csv`, per-run matrix JSON files, trace JSON files, and optional audit and sensitivity reports when present.
- **FR-004**: The feature MUST produce `paper-figure-extraction.json` and `paper-figure-extraction.md` in a caller-provided output directory only.
- **FR-005**: The report MUST include paper source inventory, artifact inventory, entries for Figures 7 through 11, global warnings, unsupported requirements, comparison readiness, and reproducibility notes.
- **FR-006**: Each figure entry MUST include `support_status` with one of `supported`, `partially_supported`, or `unsupported`.
- **FR-007**: Each figure entry MUST explicitly distinguish paper-caption-supported metadata, paper numeric target data, artifact-backed reproduction data, and unsupported or missing data.
- **FR-008**: Figure 7 MUST extract EA count when present in paper OCR or artifacts and MUST mark topology adjacency unsupported unless a committed artifact explicitly encodes graph edges.
- **FR-009**: Figure 8 MUST be marked unsupported unless committed training reward curve artifacts exist for learning-rate and discount-factor sweeps.
- **FR-010**: Figure 9 MUST extract action distribution data when available from raw matrix records or sensitivity artifacts, and MUST mark missing reward, CPU-capacity, agent-count, and offloading data-rate sweeps explicitly.
- **FR-011**: Figure 10 MUST extract average delay and drop ratio from committed matrix artifacts where available, grouped by policy, scenario, policy-scenario, and seed.
- **FR-012**: Figure 10 MUST preserve repository metric signs as stored and include a caveat when paper convention differs from repository metric convention.
- **FR-013**: Figure 11 MUST be marked unsupported unless committed HOODIE with-LSTM and without-LSTM training delay curve artifacts exist.
- **FR-014**: Audit and sensitivity findings, when present, MUST be included as comparison-readiness warnings and MUST reduce readiness where they signal collapse or saturation.
- **FR-015**: Unsupported figures MUST be reported explicitly and MUST NOT be silently skipped.
- **FR-016**: The feature MUST NOT fabricate paper results, infer graph plot points from captions, digitize figure images, rerun simulations, mutate existing artifacts, or claim paper reproduction validity.
- **FR-017**: Repeated runs on the same inputs MUST produce byte-identical JSON and Markdown outputs.

### Key Entities *(include if feature involves data)*

- **Paper Source Inventory**: The OCR source path and extraction status for paper-derived evidence.
- **Artifact Inventory**: The committed campaign, matrix, trace, audit, and sensitivity artifact inputs observed by the extractor.
- **Figure Entry**: A report section for one paper figure containing support status, evidence, extractable artifact metrics, missing artifact classes, caveats, source artifacts, and comparison readiness.
- **Paper Evidence Snippet**: A deterministic quotation or nearby-context snippet from OCR text used to justify a paper-derived figure claim.
- **Extracted Artifact Metric**: A value or table derived from committed artifacts, such as average delay, drop ratio, action distribution, throughput, completed tasks, or terminal outcome distribution.
- **Unsupported Requirement**: A missing artifact class that blocks figure-level or subfigure-level comparison readiness.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The report includes exactly one entry each for Figures 7, 8, 9, 10, and 11.
- **SC-002**: Each figure entry contains at least one OCR evidence snippet from `merged.tex` when the source file is present.
- **SC-003**: Figure 10 includes artifact-backed average-delay and drop-ratio data from committed matrix artifacts where available.
- **SC-004**: Figure 9 includes artifact-backed action distribution data when raw matrix records or sensitivity data are present.
- **SC-005**: Figure 8 and Figure 11 are marked unsupported unless the required training and ablation artifacts are committed.
- **SC-006**: Missing CPU-capacity, timeout, offloading-rate, learning-rate, discount-factor, and LSTM ablation sweeps are explicitly listed in the report when absent.
- **SC-007**: The report states that current baseline artifacts do not contain true HOODIE DRL training curves when those artifacts are absent.
- **SC-008**: Audit and sensitivity collapse signals are included when the optional reports are present.
- **SC-009**: Running the extraction twice on the same inputs produces byte-identical JSON and Markdown outputs.
- **SC-010**: Existing paper and campaign artifact files remain unchanged after extraction.

## Assumptions

- The committed OCR file is the only paper-text source of truth for figure captions and paper claims in this feature.
- If OCR text names a plotted quantity but does not include numeric curve values, the paper numeric target data is treated as missing.
- Existing scenario names and baseline metrics may support partial comparison scaffolding, but they do not stand in for missing CPU-capacity, timeout, data-rate, training, or LSTM ablation sweeps.
- Positive repository delay metrics are preserved as stored; any paper convention about negative average delay is recorded as a caveat rather than transformed.

## Production Constraints

- [x] Performance budgets identified
- [x] Artifact handling rules identified
- [x] Security and secret-hygiene constraints identified
- [x] CI quality gate impact identified

## Public Interfaces Affected

- [ ] Environment reset/step
- [ ] Policy interface
- [ ] Task model
- [ ] Topology interface
- [ ] Runtime model interface
- [ ] Evaluation metric interface
- [ ] Config schema
- [x] Artifact schema

## Config / Schema Impact

- [x] Required config fields identified
- [x] Validation rules identified
- [x] Backward-compatibility impact identified

## Artifact Impact

- [x] Raw metrics
- [ ] Plots
- [x] Reports
- [ ] Checkpoints
- [x] Debug traces
- [x] Validation summaries

## Security Considerations

- [x] Secrets / tokens / credentials reviewed
- [x] Remote code execution reviewed
- [x] External references documented

## Definition of Done

- [x] Spec matched by plan
- [x] Tests identified
- [x] Assumptions documented
- [x] Configs validated or updated
- [x] Paper-to-code mapping updated
- [x] Artifacts handled per lifecycle rules
- [x] Review and merge gate satisfied
