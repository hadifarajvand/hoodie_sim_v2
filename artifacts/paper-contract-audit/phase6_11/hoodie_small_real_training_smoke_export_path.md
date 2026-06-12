# Phase 6.11 HOODIE Small Real-Training Smoke Export Path

Phase 6.11 adds the small real-training smoke export path. It does not run training, does not run simulation, does not call main.py, and does not call Figure 10 validation.

It adds runtime-compatible checkpoint export support for future bounded training runs and writes `.pth.meta.json` metadata sidecars.

It updates preflight readiness so a future small real-training smoke can be attempted.

It does not create or commit checkpoint artifacts, does not run 5000-episode paper training, does not run 200-episode official validation, and does not reproduce Figure 8/9/10/11.

Official Figure 10 remains blocked.
