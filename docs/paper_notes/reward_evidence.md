# Reward Evidence

## Reward definition

| Item | Evidence | Paper reference | OCR support | Code location(s) | Confidence | Recovery status |
|---|---|---|---|---|---|---|
| Reward for successful processing | paper-explicit | Section 3, "Cost function", Equation (20); \(\Phi_n(t)\) defined immediately below | OCR: "reward \(r_n(t+1)\) is given by" and "negative value of \(-\Phi_n(t)\) if the task was successfully processed" | `src/environment/reward_timing.py::emit_delayed_reward()`, `src/environment/slot_boundaries.py::emit_reward_if_terminal()`, `src/training/delayed_reward_training.py::consume_ready_transition()` | high | Paper reward structure is fully recovered; the implementation still approximates \(\Phi_n(t)\) as `(completion_slot - arrival_slot)` unless a later exact formula is documented |
| Reward for dropped task | paper-explicit | Section 3, "Cost function", Equation (20); constant penalty \(C\) described immediately below | OCR: "negative penalty \(-C\) if the task was thrown" and Table 4 lists `Task Drop Penalty = 40` | `src/environment/reward_timing.py::emit_delayed_reward()`, `src/environment/slot_boundaries.py::resolve_terminal_state()`, `src/training/delayed_reward_training.py::consume_ready_transition()` | high | Fully recovered as environment-emitted drop penalty with `C = 40` |
| No-task-arrival case | paper-explicit | Section 3, Equation (20) | OCR: "reward is omitted (denoted as NaN) if no task arrived" | `src/training/training_loop.py`, `src/training/delayed_reward_training.py` | medium | Fully recovered as omitted reward signal; not a scalar training reward |
| Training reward scale | paper-implied | Section 3, Equation (20) plus training algorithm text around replay collection | OCR: rewards are collected into replay memory after completion at the current slot | `src/training/training_loop.py`, `src/training/delayed_reward_training.py`, `src/agents/replay_buffer.py` | medium | Partially recovered; the environment reward is known, but there is no separate training-only reward scale, and \(\Phi_n(t)\) remains approximation-backed in code |

## Notes

- The paper defines reward as the environment-returned cost signal, not as a distinct training-layer scalar.
- The drop penalty constant is explicit in Table 4.
- No additional reward shaping is recovered from the staged PDF/OCR resources.
