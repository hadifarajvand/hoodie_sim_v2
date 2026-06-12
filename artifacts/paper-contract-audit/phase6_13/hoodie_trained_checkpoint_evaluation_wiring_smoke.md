Phase 6.13 adds a trained-checkpoint evaluation wiring smoke.

It uses a Phase 6.12 bounded training smoke checkpoint created only in tmp/output scope.
It runs Figure 10 validation only in test mode.
It evaluates HOODIE only, with one validation episode.
It verifies checkpoint staging, sidecar propagation, stdout load observation, and runtime loader compatibility.
It does not run official Figure 10 validation.
It does not run 200-episode validation.
It does not run full, paper-grade, or 5000-episode training.
It does not reproduce Figure 8, Figure 9, Figure 10, or Figure 11.
It does not create official paper results.
Official Figure 10 remains blocked.
Figure 9 remains blocked until real paper-scenario action-distribution validation exists.
Figure 11 remains blocked until the LSTM ablation protocol and run exist.
The next phase should harden evaluation metrics/reporting or add paper-scenario action-distribution wiring, not official reproduction.
