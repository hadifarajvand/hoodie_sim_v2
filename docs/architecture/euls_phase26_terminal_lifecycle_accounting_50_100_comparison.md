# EULS Phase 26 - Terminal Lifecycle Accounting and 50/100 Comparison Repair

This phase adds a diagnostic analysis layer that:

- distinguishes lifecycle-only events from terminal-outcome events,
- counts canonical terminal tasks once per task identity,
- reruns the staged 50/100 diagnostic comparison,
- reports whether the completion path still appears blocked under the current trace bank.

It does not change environment semantics, reward semantics, policy semantics, DAL behavior, or replay behavior.
