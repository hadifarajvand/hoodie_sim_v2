# Phase 6.8 HOODIE Runtime Checkpoint Format Unification

Phase 6.8 unifies HOODIE runtime checkpoint formats.
It makes runtime loading support both full PyTorch model checkpoints and state_dict payload checkpoints.
It updates `Agent.load_model` safely.
It does not train HOODIE.
It does not run official validation.
It does not reproduce Figure 8/9/10/11.
It keeps official Figure 10 blocked.
It prepares the repo for controlled trained-checkpoint loading later.
It explicitly says trainer JSON checkpoints are not runtime-loadable HOODIE checkpoints.
