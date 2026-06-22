# Feature 082 — Algorithm Fidelity Against Paper Repair

## Goal
Audit the current DRL implementation against the HOODIE paper and repair
paper-fidelity mismatches that block the learned policy from discovering the
mixed/load-spreading behavior already demonstrated by the oracle validation.

## Scope
- Paper audit of Algorithm 1, DDQN target calculation, dueling architecture,
  LSTM state windowing, target-network updates, epsilon-greedy exploration,
  and multi-agent handling.
- Bounded validation only: training budgets [50, 100, 200, 300, 500, 750, 1000].
- No 5000-episode run.
- No environment, reward, topology, DAL, or dependency redesign.

## Output
- Algorithm-fidelity audit artifacts under
  `artifacts/production/algorithm-fidelity-against-paper-repair/`
- Repair plan and final report with claim-safe diagnostics.

## Decision rule
Return `algorithm_fidelity_repair_ready_for_extended_validation` only if the
paper audit passes and the repaired candidate shows learning-health improvement.
Otherwise return `algorithm_fidelity_repair_blocked`.
