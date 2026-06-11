# Phase 6.4: HOODIE Checkpointed Evaluation Wiring Smoke

Phase 6.4 adds a guarded checkpointed evaluation wiring smoke only.

This phase consumes a runtime-compatible HOODIE checkpoint directory, reconstructs the saved PyTorch model on CPU, and emits synthetic checkpointed evaluation records for action-distribution wiring verification. It does not train, does not create checkpoints, does not run simulation, and does not run the official 200-episode validation workflow.

This phase does not reproduce Figure 8, Figure 9, Figure 10, or Figure 11. Any action-distribution outputs produced here are non-official smoke artifacts and must not be committed.

The smoke uses explicit string action labels in synthetic records:
`local`, `horizontal`, `vertical`, and `unknown`.
That mapping is smoke-only. It is not the official paper taxonomy unless later validated against the paper contract and the runtime evaluation protocol.

Figure 9 remains blocked until real checkpointed evaluation over the paper's operating scenarios produces validated action-distribution logs.
Figure 10 remains blocked until a real trained HOODIE checkpoint exists and the official 200-episode validation run is completed.
Figure 11 remains blocked until the LSTM ablation protocol and run exist.

The next phase should be controlled non-official checkpointed evaluation integration with the validation runner, not official paper training.
