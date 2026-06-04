# Feature 084: HOODIE Paper Baseline and Formula Fidelity Audit

## Purpose
Feature 084 is a blocking audit-and-repair feature for the HOODIE paper reproduction work. It exists because Feature 083 still contains a paper-fidelity defect: it uses `MQO` / "Minimum Queue Offloader" where the HOODIE paper baseline is `MLEO` / "Minimum Latency Estimation Offloader".

This feature must repair the baseline identity defect and create a rigorous formula-to-code audit before any thesis/proposed-method work is introduced.

## Non-negotiable Corrections

1. HOODIE is the paper's proposed method.
2. There must be exactly one paper proposed method named `HOODIE`.
3. `ORIGINAL_HOODIE_BASELINE` must not appear as an active method, policy, artifact policy, report row, or final paper-fidelity concept.
4. `MQO` is wrong for paper fidelity and must be removed or treated only as a historical defect label.
5. The sixth paper baseline must be `MLEO` — Minimum Latency Estimation Offloader.
6. The paper baseline set for this feature is:
   - `RO` — Random Offloader
   - `FLC` — Full Local Computing
   - `VO` — Vertical Offloader
   - `HO` — Horizontal Offloader
   - `BCO` — Balanced Cyclic Offloader
   - `MLEO` — Minimum Latency Estimation Offloader

## Scope

Feature 084 covers:

- Repairing Feature 083's `MQO` baseline naming and semantics to `MLEO`.
- Auditing HOODIE paper formulas, models, algorithms, metrics, and simulation flow against repository implementation.
- Producing explicit evidence labels: `exact`, `approximate`, `missing`, `wrong`, or `out_of_scope`.
- Updating artifacts and reports so paper-fidelity claims cannot silently include incorrect baselines.

## Out of Scope

- No thesis method.
- No DCQ method.
- No deadline-aware queue redesign beyond HOODIE paper fidelity.
- No claim of full empirical reproduction unless trained DRL, LSTM behavior, topology, traffic, and paper figures are actually reproduced and validated.

## Acceptance Criteria

- `MQO` is absent from active policy IDs, generated reports, aggregate rows, rankings, and paper-fidelity documentation.
- `MLEO` is present as the sixth paper baseline.
- Any residual `MQO` mention is allowed only in an explicit historical-defect note.
- `HOODIE` is the only proposed method.
- Formula mapping matrix exists and covers at least:
  - task completion delay
  - task drop ratio
  - reward / cost model
  - local execution delay
  - vertical offloading delay
  - horizontal offloading delay
  - private queue timing
  - public queue timing
  - offloading queue timing
  - DQN interface
  - Double-DQN target rule
  - Dueling-DQN value/advantage interface
  - LSTM forecast/recovery interface
  - replay memory
  - epsilon-greedy schedule
  - inference epsilon zero
- The audit must distinguish implementation interfaces from trained neural implementations.
- The generated report must include a readiness level no stronger than the evidence supports.
