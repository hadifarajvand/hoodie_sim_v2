# Tasks: Feature 089 HOODIE Paper Metrics & Figure Catalog

## A. Paper Extraction

- [X] A001 Read `resources/papers/hoodie/ocr/merged.txt`.
- [X] A002 Inspect `resources/papers/hoodie/original/HOODIE_paper.pdf` directly.
- [X] A003 Extract Table 4 simulation parameters.
- [X] A004 Extract all Figure 8 subfigures and captions.
- [X] A005 Extract all Figure 9 subfigures and captions.
- [X] A006 Extract all Figure 10 subfigures and captions.
- [X] A007 Extract Figure 11 caption and curve definitions.
- [X] A008 Verify OCR-ambiguous axis labels and ranges using the PDF.

## B. Figure Catalog

- [X] B001 Register Figure 8a: accumulated reward vs learning episodes for learning-rate sweep.
- [X] B002 Register Figure 8b: accumulated reward vs learning episodes for discount-factor sweep.
- [X] B003 Register Figure 9a: average reward vs task arrival probability.
- [X] B004 Register Figure 9b: action distribution vs task arrival probability.
- [X] B005 Register Figure 9c: average reward vs CPU computation capacity.
- [X] B006 Register Figure 9d: average reward vs number of DRL agents under traffic intensity.
- [X] B007 Register Figure 9e: average reward vs number of DRL agents under data-rate configurations.
- [X] B008 Register Figure 10a: average delay vs task arrival probability.
- [X] B009 Register Figure 10b: average delay vs CPU computation capacity.
- [X] B010 Register Figure 10c: average delay vs task timeout.
- [X] B011 Register Figure 10d: drop ratio vs task arrival probability.
- [X] B012 Register Figure 10e: drop ratio vs CPU computation capacity.
- [X] B013 Register Figure 10f: drop ratio vs task timeout.
- [X] B014 Register Figure 11: LSTM inclusion ablation.

## C. Metric Catalog

- [X] C001 Register `average_task_completion_delay` / `average_delay`.
- [X] C002 Register `task_drop_ratio`.
- [X] C003 Register `average_reward`.
- [X] C004 Register `accumulated_reward` / `cumulative_reward`.
- [X] C005 Register `action_distribution`.
- [X] C006 Register `average_task_delay_with_vs_without_lstm`.

## D. Simulator Output Requirements

- [X] D001 Define arrival-probability sweep output for Figure 10a and Figure 10d.
- [X] D002 Define CPU-capacity sweep output for Figure 10b and Figure 10e.
- [X] D003 Define timeout sweep output for Figure 10c and Figure 10f.
- [X] D004 Define HOODIE reward-vs-arrival output for Figure 9a.
- [X] D005 Define HOODIE action-distribution output for Figure 9b.
- [X] D006 Define HOODIE reward-vs-CPU output for Figure 9c.
- [X] D007 Define HOODIE reward-vs-agent-count traffic-intensity output for Figure 9d.
- [X] D008 Define HOODIE reward-vs-agent-count data-rate output for Figure 9e.
- [X] D009 Mark Figure 8a and Figure 8b as training-required outputs.
- [X] D010 Mark Figure 11 as LSTM-ablation-required output.

## E. Artifacts

- [X] E001 Generate `paper_figures_8_11_catalog.json`.
- [X] E002 Generate `paper_figures_8_11_catalog.md`.
- [X] E003 Generate `paper_metrics_catalog.json`.
- [X] E004 Generate `paper_metrics_catalog.md`.
- [X] E005 Generate `simulator_output_requirements.json`.
- [X] E006 Generate `simulator_output_requirements.md`.
- [X] E007 Generate final Feature 089 report JSON and Markdown.

## F. Validation

- [X] F001 Validate every subfigure from Figures 8-11 is cataloged.
- [X] F002 Validate every Priority 1 figure has simulator output requirements.
- [X] F003 Validate training-only figures are not scheduled as deterministic evaluation outputs.
- [X] F004 Validate LSTM-ablation figure is not scheduled without trained LSTM support.
- [X] F005 Validate Feature 086 approximation boundaries are carried forward.
- [X] F006 Validate no thesis/DCQ/custom method is introduced.
