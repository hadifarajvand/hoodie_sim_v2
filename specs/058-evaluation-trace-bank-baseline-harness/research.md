# Research: Feature 058

## Decision: separate evaluation trace bank from training trace bank

Feature 058 must define evaluation evidence separately from training evidence. Evaluation traces must be deterministic and disjoint from training traces.

## Decision: baseline harness is evaluation-only

The harness must evaluate fixed baseline policies on evaluation traces. It must not train, mutate replay, run optimizer steps, or write checkpoint binaries.

## Decision: baseline registry before full campaign

A registry of baseline policies is required before full campaign work, so later campaign outputs can be compared consistently.

## Decision: metric schema first, numbers later

Feature 058 validates metric schema and harness readiness. It must not claim performance or paper reproduction. Metric comparison belongs to later campaign/comparison features.
