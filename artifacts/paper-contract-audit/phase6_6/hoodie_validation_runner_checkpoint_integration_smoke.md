# Phase 6.6: HOODIE Validation Runner Checkpoint Integration Smoke

Phase 6.6 is a validation runner checkpoint integration smoke.

It stages runtime-compatible HOODIE checkpoints into a Figure 10 runner-like layout and verifies checkpoint copying and loadability only. It does not run `main.py`, does not execute the full `run_figure10_validation` workflow, does not run 200-episode validation, does not run official simulation, and does not reproduce Figure 8, Figure 9, Figure 10, or Figure 11.

This phase validates checkpoint staging/copying only. Figure 9 remains blocked until real checkpointed evaluation over paper scenarios exists. Figure 10 remains blocked until a real trained HOODIE checkpoint plus official 200-episode validation exists. Figure 11 remains blocked until the LSTM ablation protocol and run exist.

The next phase should be controlled tiny validation-runner execution in test mode, still non-official.
