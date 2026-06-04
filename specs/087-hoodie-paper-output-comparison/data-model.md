# Data Model: Feature 087 HOODIE Paper Output Comparison

## Entity: PaperOutputItem

Fields:

- `paper_item_id`: stable identifier for the figure, table, metric, or textual result claim.
- `source_location`: paper section, figure, table, caption, or OCR line reference when available.
- `item_type`: `figure`, `table`, `text_claim`, `metric_value`, `ranking_claim`.
- `metric`: metric reported by the paper.
- `policies`: policies included in the paper output.
- `scenario_variable`: x-axis or scenario parameter.
- `paper_values`: numeric values if available.
- `value_extraction_method`: `explicit_text`, `table_value`, `figure_digitized`, `qualitative_only`, `unavailable`.
- `extraction_confidence`: `high`, `medium`, `low`.
- `notes`: extraction caveats.

## Entity: SimulatorOutputItem

Fields:

- `artifact_path`: source artifact file.
- `metric`: simulator metric.
- `policy`: policy ID.
- `scenario`: scenario ID.
- `value`: numeric simulator output.
- `aggregation_method`: aggregation method.
- `source_feature`: `085`, `086`, or `087`.
- `claim_boundary`: Feature 086 approximation boundary if applicable.

## Entity: MetricAlignment

Fields:

- `paper_metric`: paper metric name.
- `simulator_metric`: simulator metric name.
- `classification`: one of `paper_primary_metric`, `paper_secondary_or_derived_metric`, `paper_secondary_or_repository_metric`, `repository_diagnostic_metric`, `not_for_paper_comparison`.
- `mapping_status`: one of `exact_metric_match`, `derived_metric_match`, `approximate_metric_match`, `not_available_in_simulator`, `not_reported_by_paper`.
- `allowed_for_comparison`: boolean.
- `caveat`: explanation if not exact.

## Entity: OutputComparisonRow

Fields:

- `paper_item_id`: reference to PaperOutputItem.
- `metric`: metric compared.
- `policy`: policy ID.
- `scenario_or_x_axis`: scenario or x-axis bucket.
- `paper_value`: paper value if numeric.
- `simulator_value`: simulator value.
- `absolute_difference`: simulator minus paper where possible.
- `relative_difference`: percentage difference where meaningful.
- `ranking_match`: boolean or nullable.
- `qualitative_agreement`: `aligned`, `partially_aligned`, `divergent`, `not_comparable`.
- `comparison_status`: `aligned`, `partially_aligned`, `divergent`, `not_comparable`.
- `notes`: caveats and approximation boundary.

## Entity: ComparisonReport

Fields:

- `verdict`: `paper_output_comparison_ready`, `paper_output_comparison_partial`, or `paper_output_comparison_blocked`.
- `feature_086_boundary`: list of inherited approximations.
- `paper_items_extracted`: count.
- `paper_items_comparable`: count.
- `paper_items_not_comparable`: count.
- `allowed_metrics`: list.
- `diagnostic_metrics`: list.
- `ranking_agreement_summary`: object.
- `numeric_difference_summary`: object.
- `blocking_issues`: list.
- `remaining_limitations`: list.
