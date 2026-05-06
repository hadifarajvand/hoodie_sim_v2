# HOODIE Assumptions Log

## A-020: Runtime delay remains assumption-backed until paper unit/capacity mapping is fully recovered

- Missing detail: The OCR-backed paper material recovers the compute relationship in principle, but not every slot-level compute-capacity value and conversion needed for a fully paper-exact delay model.
- Chosen value or rule: Keep the execution-delay mapping deterministic and configuration-backed, and document any unresolved capacity-to-delay mapping explicitly rather than inventing it. The repository uses a fixed compute-capacity fixture for local, edge, and cloud execution until the exact recovered paper capacities are available.
- Justification: The simulator must model compute progression without claiming a paper-exact delay rule when the recovered text still leaves that gap open.
- Expected impact: Compute timing remains reproducible and auditable while the unresolved paper gap stays visible.
- Validation plan: Replace the assumption-backed mapping only after the paper’s compute-capacity detail is fully recovered and verified.

## A-021: Adaptive offloading ranking remains a conservative baseline unless the paper equation is recovered

- Missing detail: The recovered paper material supports dynamic offloading inputs, but not an exact recovered ranking equation for combining load, latency, balance, and execution estimates into a single adaptive decision rule.
- Chosen value or rule: Use a deterministic conservative ranking heuristic that prefers legal actions using current observation signals, and document the heuristic as a baseline/fallback rather than a learned HOODIE policy.
- Justification: The feature must stay paper-backed and conservative without inventing DRL or LSTM behavior.
- Expected impact: The adaptive policy remains reproducible and legality-preserving, but it is explicitly not claimed to be the paper’s learned controller.
- Validation plan: Replace the heuristic with the exact paper-backed rule only if the ranking equation is recovered and verified.
