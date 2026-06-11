# Phase 6.7 HOODIE Controlled Validation Runner Execution Smoke

Phase 6.7 is a controlled validation runner execution smoke.
It runs the Figure 10 validation runner only in test mode.
It uses 1 episode only.
It uses HOODIE only.
It may call `main.py` only through the validation runner path.
It uses temporary non-trained runtime fixture checkpoints.
It does not train HOODIE.
It does not run official 200-episode validation.
It does not reproduce Figure 8/9/10/11.
Generated Figure 10 files are non-official smoke outputs only.
Figure 10 official remains blocked.
Figure 9 remains blocked until real checkpointed evaluation over paper scenarios produces validated action-distribution logs.
Figure 11 remains blocked until LSTM ablation protocol and run exist.
The next phase should be runtime checkpoint format unification or controlled trained-checkpoint loading, not paper-grade validation.
