# Paper-to-Code Mapping

## Current Mapping

- Paper system model and task description -> `src/environment/task.py`, `src/environment/topology.py`, `src/environment/environment.py`
- Paper reward / cost function (Section 3, Eq. 20; OCR around reward collection and delayed reward emission) -> `src/environment/reward_timing.py`, `src/environment/slot_boundaries.py`, `src/training/delayed_reward_training.py`, `src/training/training_loop.py`
- Paper slot lifecycle and environment boundary -> `src/environment/gym_adapter.py`, `src/environment/environment.py`
- One-slot step semantics, same-slot arrival ordering, and helper-only SlotEngine boundary -> `src/environment/gym_adapter.py`, `src/environment/slot_engine.py`
- Paper assumptions and gaps -> `docs/assumptions/hoodie_assumptions.md`
- Paper resource provenance -> `docs/paper_notes/hoodie_resource_log.md`

## Status

- In progress, but the final adapter boundary mapping is now explicit.
- Only paper-backed mappings may be added here.
- No queue, policy, evaluation, or training mapping is documented in Phase 1.
