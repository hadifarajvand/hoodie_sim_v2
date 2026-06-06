# Data Model: Exposure Matrix Rerun and Paper Mechanism Alignment

## Entities

### ExposureMatrixRerunSummary

- Purpose: Summarizes exposure-matrix rerun output using legality evidence.
- Key fields:
  - rerun status
  - evidence source
  - decision-opportunity coverage
  - legality coverage coverage ratio
  - exposure bias indicators
  - readiness impact
- Relationships:
  - Consumes Feature 048 legality evidence.
  - References the committed Feature 047 exposure-matrix baseline artifact.

### LegalVsSelectedActionMatrix

- Purpose: Compares legal availability against selected action behavior.
- Key fields:
  - strategy
  - seed
  - action
  - legal availability
  - selected count
  - illegal selection count
  - legal-but-unselected count
  - outcome counts
- Relationships:
  - Aggregates per-strategy/per-seed/per-action exposure summaries.

### ObservationVectorAudit

- Purpose: Captures whether the current simulator observation matches the paper HOODIE mechanism.
- Key fields:
  - required observation components
  - present/missing status
  - audit outcome
  - contradiction notes
- Relationships:
  - Feeds the final training-readiness decision.

### PaperFormulaUnitAudit

- Purpose: Captures whether time, reward, deadline, and terminal-state formulas match the paper contract.
- Key fields:
  - local execution time
  - horizontal transmission delay
  - vertical/cloud transmission delay
  - queue wait
  - task age
  - deadline/timeout
  - reward timing
  - completion/drop/pending handling
  - pass/fail outcome
- Relationships:
  - Feeds the final training-readiness decision.

### TrainingReadinessDecision

- Purpose: Records the final diagnostic/alignment verdict and next recommendation.
- Key fields:
  - final verdict
  - recommended next feature
  - blocking reason
  - readiness status
- Relationships:
  - Depends on exposure rerun summary, observation audit, and formula audit.

## Validation Rules

- The exposure rerun summary must only claim readiness when legality evidence is sufficient.
- The legal-vs-selected matrix must not infer values from representative examples.
- The observation vector audit must explicitly identify missing or contradictory paper mechanism inputs.
- The formula/unit audit must distinguish pass, mismatch, and contradiction outcomes.
- The training readiness decision must route to repair or readiness only; it must not recommend training execution here.
