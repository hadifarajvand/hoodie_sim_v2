# Data Model: Feature 089 HOODIE Paper Metrics and Figure Catalog

## Entity: PaperFigure

Fields:

- `figure_id`: e.g. `Figure 10a`
- `family`: `Figure 8`, `Figure 9`, `Figure 10`, or `Figure 11`
- `paper_section`: section where the figure appears
- `caption`: caption or caption summary
- `metric`: y-axis metric
- `x_axis`: x-axis variable
- `sweep_values`: values or range if known
- `policies_or_curves`: list of policies or curve labels
- `scenario_setup`: setup used by the figure
- `requires_training`: boolean
- `requires_lstm`: boolean
- `requires_digitization`: boolean
- `priority`: `priority_1_comparative_output`, `priority_2_hoodie_behavior_output`, or `priority_3_training_or_lstm_required`
- `output_status`: `required_now`, `later_training_required`, `later_lstm_required`, or `reference_only`
- `extraction_confidence`: `high`, `medium`, or `low`
- `pdf_verified`: boolean
- `ocr_caveat`: optional ambiguity note
- `simulator_output_requirement_id`: optional reference

## Entity: PaperMetric

Fields:

- `metric_id`: canonical metric ID
- `paper_names`: names used by the paper
- `definition`: metric meaning
- `used_in_figures`: list of figure IDs
- `primary_or_secondary`: `primary`, `secondary`, `behavioral`, `training`, or `diagnostic`
- `simulator_metric_mapping`: simulator metric ID if available
- `requires_training`: boolean
- `requires_lstm`: boolean
- `comparison_allowed_now`: boolean
- `claim_boundary`: caveat inherited from Feature 086 or Feature 080

## Entity: SimulatorOutputRequirement

Fields:

- `requirement_id`: stable ID
- `target_figures`: list of figure IDs
- `output_family`: e.g. `arrival_probability_sweep`, `cpu_capacity_sweep`, `timeout_sweep`, `action_distribution_sweep`
- `metrics`: metrics to compute
- `policies`: policies to run
- `x_axis`: sweep variable
- `sweep_values`: concrete values if known, otherwise `needs_pdf_confirmation`
- `scenario_setup`: scenario configuration
- `artifact_outputs`: expected future output files
- `implementation_priority`: `priority_1`, `priority_2`, or `priority_3`
- `blocked_by_training`: boolean
- `blocked_by_lstm`: boolean
- `notes`: caveats and required confirmations

## Required Figure Families

Feature 089 must catalog:

- Figure 8a
- Figure 8b
- Figure 9a
- Figure 9b
- Figure 9c
- Figure 9d
- Figure 9e
- Figure 10a
- Figure 10b
- Figure 10c
- Figure 10d
- Figure 10e
- Figure 10f
- Figure 11
