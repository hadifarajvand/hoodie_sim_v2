# Phase 6.10 HOODIE Small Real-Training Smoke Preflight

Phase 6.10 is a preflight only. It does not run training, does not run simulation, does not run Figure 10 validation, and does not create checkpoints.

This phase checks whether a future tiny real-training smoke could be implemented safely. It inspects bounded config support, safe tmp output routing, checkpoint export readiness, metadata sidecar readiness, and runtime loader readiness.

If checkpoint export or metadata sidecar writing is missing, the small real-training execution remains blocked.

Figure 10 remains blocked. Figure 9 remains blocked until real paper-scenario checkpointed evaluation produces validated action-distribution logs. Figure 11 remains blocked until LSTM ablation protocol and run exist.

The next phase should be either:
- Phase 6.11 - HOODIE small real-training smoke export path, if blockers remain, or
- Phase 6.11 - execute bounded small real-training smoke, only if preflight says ready.
