# Plan: Feature 089 HOODIE Paper Figure Catalog and Simulator Output Extension

## Branch

`089-hoodie-paper-metrics-figure-catalog`

## Goal

Extract all Figure 8-11 requirements from the HOODIE paper and prepare simulator output extensions for the figure families that can be generated from the current simulator.

## Phase 1 — Paper and PDF Extraction

1. Read `resources/papers/hoodie/ocr/merged.txt`.
2. Inspect `resources/papers/hoodie/original/HOODIE_paper.pdf` directly.
3. Resolve OCR ambiguity using the PDF, especially:
   - Figure 10 timeout-axis values;
   - figure captions;
   - y-axis labels;
   - curve labels;
   - policy sets;
   - training-only vs evaluation-only interpretation.
4. Extract Table 4 parameters because they define default simulation settings.

## Phase 2 — Register Figure Catalog

Create figure catalog entries for:

- Figure 8a: accumulated reward vs training episodes for learning rate
- Figure 8b: accumulated reward vs training episodes for discount factor
- Figure 9a: average reward vs task arrival probability
- Figure 9b: action distribution vs task arrival probability
- Figure 9c: average reward vs CPU computation capacity
- Figure 9d: average reward vs number of DRL agents under traffic intensity
- Figure 9e: average reward vs number of DRL agents under data-rate configurations
- Figure 10a: average delay vs task arrival probability
- Figure 10b: average delay vs CPU computation capacity
- Figure 10c: average delay vs task timeout
- Figure 10d: drop ratio vs task arrival probability
- Figure 10e: drop ratio vs CPU computation capacity
- Figure 10f: drop ratio vs task timeout
- Figure 11: average task delay with vs without LSTM across training episodes

## Phase 3 — Classify Implementation Priority

Use these priority classes:

- `priority_1_comparative_output`: Figure 10a-10f
- `priority_2_hoodie_behavior_output`: Figure 9a-9e
- `priority_3_training_or_lstm_required`: Figure 8a, Figure 8b, Figure 11
- `reference_topology_or_parameter`: Figure 7 and Table 4 when needed, but Feature 089 focuses on Figures 8-11

## Phase 4 — Define Simulator Output Extensions

Specify output families that must be added to the simulator pipeline:

1. Arrival-probability sweep:
   - Figure 10a: delay vs P
   - Figure 10d: drop ratio vs P
   - Figure 9a: reward vs P for HOODIE
   - Figure 9b: action distribution vs P for HOODIE
2. CPU-capacity sweep:
   - Figure 10b: delay vs CPU capacity
   - Figure 10e: drop ratio vs CPU capacity
   - Figure 9c: reward vs CPU capacity for HOODIE
3. Timeout sweep:
   - Figure 10c: delay vs timeout
   - Figure 10f: drop ratio vs timeout
4. Agent-count sweep:
   - Figure 9d: reward vs number of agents under traffic intensity
   - Figure 9e: reward vs number of agents under data-rate configurations
5. Training sweeps:
   - Figure 8a and 8b only if trained HOODIE DRL is available
6. LSTM ablation:
   - Figure 11 only if trained LSTM and no-LSTM variants are available

## Phase 5 — Required Artifacts

Generate these later during implementation:

- `artifacts/feature_089_paper_metrics_catalog/paper_figures_8_11_catalog.json`
- `artifacts/feature_089_paper_metrics_catalog/paper_figures_8_11_catalog.md`
- `artifacts/feature_089_paper_metrics_catalog/paper_metrics_catalog.json`
- `artifacts/feature_089_paper_metrics_catalog/paper_metrics_catalog.md`
- `artifacts/feature_089_paper_metrics_catalog/simulator_output_requirements.json`
- `artifacts/feature_089_paper_metrics_catalog/simulator_output_requirements.md`
- `artifacts/feature_089_paper_metrics_catalog/feature_089_report.json`
- `artifacts/feature_089_paper_metrics_catalog/feature_089_report.md`

## Phase 6 — Validation

Validate that:

- every subfigure from Figures 8-11 has a catalog row;
- no training-only figure is assigned to deterministic evaluation output;
- every Priority 1 figure has a simulator-output requirement;
- all Feature 086 approximation boundaries are carried forward;
- no thesis/DCQ/custom method is introduced.
