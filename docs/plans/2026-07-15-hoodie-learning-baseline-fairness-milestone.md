# 2026-07-15 HOODIE learning and baseline fairness milestone

## Goal
Replace placeholder learner mechanics with real DDQN/LSTM behavior, repair baseline contracts, and add paired-evaluation primitives.

## Work
- Added `src/agents/ddqn.py` with dueling network, seeded replay, Double-DQN update, checkpoint state.
- Replaced `src/agents/lstm_dueling_dqn.py` with operational LSTM forecasting path and ablation.
- Patched baseline policies for contract fidelity and deterministic tie-breaking.
- Added paired-evaluation record and fairness validation primitives.
- Added focused regression tests.

## Validation
- `python3 -m pytest -q tests/unit/test_hoodie_learning_real.py`
- `python3 -m pytest -q tests/unit/test_phase0_baseline_policies.py tests/unit/test_policy_interface.py tests/agents/test_lstm_dueling_dqn.py tests/unit/test_hoodie_learning_real.py`
- `python3 -m pytest -q` failed during collection in vendored `resources/references/simpy`.
