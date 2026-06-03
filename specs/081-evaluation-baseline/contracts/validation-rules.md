# Feature 081 Contract — Validation Rules

## Policy Validation
- All required policies must be represented.
- Random policy must be seed-controlled.
- Local-only must never offload.
- Cloud-only must always attempt vertical cloud if available.
- Illegal actions must be rejected and counted.

## Scenario Validation
- All required scenarios must be represented.
- Each scenario must have deterministic output for a fixed seed.
- Workload/deadline expansions must be deterministic.

## Metric Validation
- Rate metrics must divide by total task count.
- Average delay must be null-compatible if no task completes.
- Throughput must divide completed count by scenario duration.
- Queue stability score must be deterministic and documented.

## Ranking Validation
- Ranking must be per metric.
- Direction must be explicit per metric.
- Tie-breaking must be deterministic.

## Scope Validation
Tests must reject:
- DCQ labels or logic
- thesis method labels or logic
- Feature 080 internal mutation
- hidden overall-score ranking
- unsupported empirical reproduction claims
