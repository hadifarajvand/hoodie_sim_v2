# Research: 001-hoodie-reproduction

## Decision 1: Shared simulator boundary

- Decision: Build one simulator that serves all baselines and HOODIE.
- Rationale: The constitution requires baseline fairness and shared metric computation.
- Alternatives considered: Separate simulators per policy were rejected because they would invalidate
  comparability.

## Decision 2: Evaluation replay model

- Decision: Support evaluation from saved seed sets or trace-bank identifiers.
- Rationale: The specification requires reproducible evaluation and paired/fixed-trace fairness.
- Alternatives considered: Ad hoc stochastic evaluation was rejected because it cannot be audited.

## Decision 3: Queue and timing semantics

- Decision: Preserve slot-based arrival, FIFO queue admission, FIFO service, deadline expiration, and
  delayed reward emission as first-class simulator behaviors.
- Rationale: These behaviors are required by the paper-derived specification.
- Alternatives considered: Collapsing timing into a simplified episode summary was rejected because it
  would hide queue and deadline behavior.

## Decision 4: Policy interface

- Decision: Use one policy contract for all decision makers, with action legality filtered by the
  environment before execution.
- Rationale: This keeps baselines and HOODIE on the same shared interface.
- Alternatives considered: Policy-specific environment hooks were rejected because they create unfair
  comparison paths.

## Decision 5: Configuration handling

- Decision: Load parameters, seeds, and evaluation settings from version-controlled config files and
  keep result-bearing configs immutable once used.
- Rationale: Reproducibility and configuration freeze are constitutional requirements.
- Alternatives considered: Hardcoded defaults and mutable result configs were rejected.

## Decision 6: Unknown paper gaps

- Decision: Treat missing reward scaling, exact trace banks, exact scenario parameters, and exact
  hyperparameters as recorded gaps until recovered from the source paper.
- Rationale: The constitution forbids undocumented assumptions.
- Alternatives considered: Inferring missing values from the OCR alone was rejected because OCR is
  supporting evidence, not the source of truth.

## Remaining Unknowns

- Exact paper parameter values that are not recoverable from the source PDF or OCR.
- Exact evaluation trace bank contents if not explicitly stated.
- Exact training hyperparameters if not explicitly stated.
- Exact reward scaling if not explicitly recoverable.

