# Feature 079 Data Model

## MetricSummary

Fields:

- metric_name
- mean
- std
- min
- max
- count
- ci95_low
- ci95_high

## PolicyAggregate

Fields:

- policy_id
- metric_summaries

Rules:

- every required policy appears exactly once.

## ComparativeAggregate

Fields:

- grouping_key
- policy_aggregates

Rules:

- all policies are represented.
- metrics use the same schema.

## AggregationReport

Fields:

- feature_id
- status
- passed
- dependency_features
- policy_aggregates
- comparative_aggregates
- validation_summary
- claim_boundary

Rules:

- Feature 078 must pass.
- all required metrics are summarized.
- all required policies are represented.
- report contains no ranking and no winner.
