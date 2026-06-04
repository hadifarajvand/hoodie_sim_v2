# Validation Rules: Feature 089

## Figure Coverage Rule

The catalog must include exactly these required figure entries:

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

## PDF Verification Rule

The implementation must use both OCR and the original PDF. OCR-only extraction is not sufficient for Feature 089 because Figure 10 axis/range values may be ambiguous.

Every figure entry must include `pdf_verified` and `extraction_confidence`.

## Priority Rule

Figure 10a-10f must be `priority_1_comparative_output`.

Figure 9a-9e must be `priority_2_hoodie_behavior_output`.

Figure 8a, Figure 8b, and Figure 11 must be `priority_3_training_or_lstm_required` unless trained HOODIE and trained LSTM support are actually available.

## Simulator Output Requirement Rule

Every Priority 1 figure must have a simulator output requirement.

Priority 2 figures should have simulator output requirements if current simulator outputs can support them without new trained DRL or LSTM claims.

Priority 3 figures must not be scheduled as deterministic evaluation outputs unless their training/LSTM blockers are removed.

## Scope Rule

Feature 089 must not introduce:

- thesis method
- DCQ
- custom queue redesign
- new proposed method
- unsupported full empirical paper reproduction claim

## Claim Boundary Rule

Feature 089 must carry forward Feature 086 approximations and Feature 080 LSTM/training claim boundaries.
