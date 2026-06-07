# Phase 3.0 DRL/LSTM Fidelity Audit

This audit is verification only.

## Why It Exists

Phase 2 made the action contract explicit. That does not mean the rest of the DRL/LSTM stack is paper-faithful. This audit checks the state, action, reward, LSTM, and training-loop contracts against the HOODIE paper without changing runtime behavior.

## What It Checks

- State space from Section III.A.1 and Eq. (18)
- Action space from Section III.A.2 and Eq. (19)
- Reward/cost from Eq. (20) to Eq. (23)
- Problem formulation from Eq. (24)
- HOODIE model from Section IV.A
- Figure 4 Dueling DQN structure
- Figure 5 LSTM load prediction model
- Algorithm 1 training loop
- Eq. (25) dueling DQN
- Double-DQN target logic
- Replay-memory behavior
- Delayed reward collection via `D_n(t)`

## Current Runtime Interpretation

- The simulator still uses the legacy observation packing in `environment/environment.py`.
- The current training path in `decision_makers/agent.py` consumes collapsed/reconstructed state features.
- The LSTM code exists, but it is not the paper's `W x (N+1)` load forecaster.
- The replay buffer and trainer exist, but delayed task-completion replay is not yet native.

## What The Audit Does Not Change

- queue formulas
- reward formulas
- task generation
- action legality
- simulator runtime behavior
- training behavior

## Output Artifacts

- `artifacts/phase3_fidelity_audit/phase3_fidelity_report.json`
- `artifacts/phase3_fidelity_audit/phase3_fidelity_report.md`
- `artifacts/phase3_fidelity_audit/state_contract_gap_matrix.csv`
- `artifacts/phase3_fidelity_audit/action_contract_gap_matrix.csv`
- `artifacts/phase3_fidelity_audit/reward_contract_gap_matrix.csv`
- `artifacts/phase3_fidelity_audit/lstm_contract_gap_matrix.csv`
- `artifacts/phase3_fidelity_audit/training_loop_gap_matrix.csv`

## Status Values

- `PASS`: implementation directly satisfies the paper contract
- `PARTIAL`: implementation approximates or reconstructs the contract
- `FAIL`: implementation conflicts with the paper contract
- `MISSING`: the required paper element is absent

## How To Run

```bash
./.venvmac/bin/python phase3_fidelity_audit.py --output-dir artifacts/phase3_fidelity_audit
```

## Bottom Line

Runtime behavior is unchanged.
No paper-performance claim is made.

