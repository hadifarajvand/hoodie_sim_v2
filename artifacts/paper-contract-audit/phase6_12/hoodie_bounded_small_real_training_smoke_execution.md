Phase 6.12 adds a bounded small real-training smoke execution for HOODIE.

This phase runs `main.py` in non-validation training mode with a tiny bounded configuration, routes all generated outputs outside the repository, and exports runtime-compatible checkpoints through the Phase 6.11 export path.

It does not run paper-grade training.
It does not run 5000-episode training.
It does not run official 200-episode Figure 10 validation.
It does not reproduce Figure 8, Figure 9, Figure 10, or Figure 11.
It does not make any official paper claim.

The smoke verifies that exported checkpoints and metadata sidecars are loadable through the Phase 6.8 runtime loader and that `Agent.load_model` accepts the generated runtime checkpoint format.

Figure 10 remains blocked.
Figure 9 remains blocked until real checkpointed evaluation over paper scenarios produces validated action-distribution logs.
Figure 11 remains blocked until LSTM ablation protocol and run exist.

The next phase should be controlled bounded execution hardening or evaluation wiring for the newly exported trained checkpoints, not paper-grade training.
