# HOODIE Assumptions Log

## A-020: Runtime delay remains assumption-backed until paper unit/capacity mapping is fully recovered

- Missing detail: The OCR-backed paper material recovers the compute relationship in principle, but not every slot-level compute-capacity value and conversion needed for a fully paper-exact delay model.
- Chosen value or rule: Keep the execution-delay mapping deterministic and configuration-backed, and document any unresolved capacity-to-delay mapping explicitly rather than inventing it. The repository uses a fixed compute-capacity fixture for local, edge, and cloud execution until the exact recovered paper capacities are available.
- Justification: The simulator must model compute progression without claiming a paper-exact delay rule when the recovered text still leaves that gap open.
- Expected impact: Compute timing remains reproducible and auditable while the unresolved paper gap stays visible.
- Validation plan: Replace the assumption-backed mapping only after the paper’s compute-capacity detail is fully recovered and verified.
