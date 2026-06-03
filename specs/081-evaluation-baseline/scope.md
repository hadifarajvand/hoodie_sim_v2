# Feature 081 Scope — HOODIE Evaluation & Baseline Benchmarking

## In Scope

Feature 081 is allowed to:
- define baseline policies for evaluation
- define deterministic scenario generation
- connect to Feature 080 as the tested HOODIE_PROPOSED method
- run evaluation rows for each policy/scenario/workload/deadline/seed combination
- compute explicit metrics
- aggregate metrics
- produce metric-by-metric ranking tables
- generate a deterministic textual/structured report

## Out of Scope

Feature 081 must not:
- modify Feature 080 internals
- introduce DCQ
- introduce the user's thesis method
- introduce deadline-aware queue redesign beyond the base HOODIE paper method already represented
- claim empirical full-paper reproduction
- claim statistical significance unless a dedicated statistical-testing feature is implemented
- train new neural networks
- silently replace baseline definitions
- merge PRs or change repository workflow

## Required Policies

Feature 081 must cover exactly these initial policies unless a later spec explicitly extends the list:
- HOODIE_PROPOSED
- ORIGINAL_HOODIE_BASELINE
- RANDOM_POLICY
- LOCAL_ONLY
- CLOUD_ONLY

## Required Scenarios

Feature 081 must cover:
- light_load_no_deadline_pressure
- tight_deadline_pressure
- legal_horizontal_offload
- illegal_horizontal_destination_attempt
- cloud_vertical_fallback
- timeout_drop_case
- mixed_local_horizontal_cloud_candidates

## Required Metric Groups

Feature 081 must cover:
- completion metrics
- drop metrics
- delay metrics
- reward metrics
- queue stability metrics
- illegal-action metrics

## Scope Gates

The feature may be marked ready only when:
- all required policies are represented
- all required scenarios are represented
- all required metric formulas are implemented or explicitly mapped to existing project formulas
- ranking is metric-by-metric and deterministic
- report includes claim boundary
- report includes scope proof
- tests reject DCQ/thesis/ranking-method drift
