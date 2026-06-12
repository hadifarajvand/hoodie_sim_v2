Phase 6.14 hardens the metrics contract for the smoke-checkpoint evaluation path.

It runs Phase 6.13 wiring smoke only in tmp/output-dir.
It validates raw CSV, summary JSON, readiness JSON, config snapshot, and validation manifest.
It checks policy scope, regime scope, numeric validity, task-count consistency, notes_json validity, and non-official guard fields.
It does not run official Figure 10.
It does not run 200-episode validation.
It does not run full, paper-grade, or 5000-episode training.
It does not evaluate all official policies.
It does not reproduce Figure 8, Figure 9, Figure 10, or Figure 11.
It does not create official paper results.
Official Figure 10 remains blocked.
Figure 9 remains blocked until real paper-scenario action-distribution validation exists.
Figure 11 remains blocked until LSTM ablation protocol and run exist.
The next phase should harden paper-scenario action-distribution wiring or evaluation aggregation, not official reproduction yet.
