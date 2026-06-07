# Phase 3 Roadmap Guidance — Paper-Faithful DRL/LSTM Alignment

## Purpose

This roadmap defines the controlled path for Phase 3 of the HOODIE simulator rebuild. The goal is not to add decorative training code. The goal is to verify and then repair the simulator's DRL training pipeline so that it follows the HOODIE paper's state, action, reward, LSTM, and training-loop contracts.

The accepted foundation before this roadmap is:

- Phase 1: HOODIE-aligned task record and task-generation fields.
- Phase 1.1: strict positive timeout validation.
- Phase 1.2: TaskGenerator preconstruction validation.
- Phase 2: explicit two-stage local/horizontal/vertical action model with topology legality.
- Runtime trace population for Phase 2 action semantics is present in `main.py` and `phase1_tracing.py`.
- The current topology is accepted as canonical because it comes from the provided simulator codebase associated with the paper.

## Non-negotiable rule

Do not proceed to large training, 200-episode validation, or figure generation until the Phase 3 fidelity gaps are explicitly audited and closed.

## Phase 3 sequence

### Phase 3.0 — DRL/LSTM Fidelity Audit

Objective: inspect the current training stack and report whether it matches the HOODIE paper.

Audit targets:

- State vector `s_n(t)` from Eq. (18):
  - `eta_n(t)` task size
  - `w_priv_n(t)` private queue waiting time
  - `w_off_n(t)` offloading queue waiting time
  - `l_pub_n(t-1)` public queue lengths for tasks offloaded by EA n
  - `L(t)` historical load matrix or its LSTM-predicted next-load representation
- Action vector `a_n(t)` from Eq. (19):
  - `d_n^(1)(t)`
  - `D_n(t)` / sparse `d_{n,k}^{(2)}(t)`
- Reward/cost equations from Eq. (20)–(23):
  - omitted reward when no task arrives
  - delayed reward when task completes
  - `-Phi_n(t)` for successful processing
  - `-C` for thrown/dropped tasks
  - local cost `Phi_priv_n(t)`
  - external/public cost `Phi_pub_n(t)`
- Delayed replay behavior from Algorithm 1:
  - rewards are stored when tasks complete, not immediately at action time
  - replay tuples are task-traceable: `(s_n(t'), a_n(t'), r_n(t'), s_n(t'+1))`
- LSTM historical-load contract:
  - lookback window `W`
  - input matrix `L(t)` with shape `W x (N+1)`
  - predicted next load for all EAs and cloud
- Existing implementation files:
  - `training/trace_dataset.py`
  - `training/replay_buffer.py`
  - `training/lstm_forecaster.py`
  - `training/trainers.py`
  - `training/train_phase3.py`
  - `decision_makers/agent.py`
  - `environment/environment.py`
  - `phase1_tracing.py`
  - `main.py`

Expected outputs:

- `artifacts/phase3_fidelity_audit/phase3_fidelity_report.json`
- `artifacts/phase3_fidelity_audit/phase3_fidelity_report.md`
- `artifacts/phase3_fidelity_audit/state_contract_gap_matrix.csv`
- `artifacts/phase3_fidelity_audit/action_contract_gap_matrix.csv`
- `artifacts/phase3_fidelity_audit/reward_contract_gap_matrix.csv`
- `artifacts/phase3_fidelity_audit/lstm_contract_gap_matrix.csv`
- `docs/phase3_fidelity_audit.md`

Acceptance status values:

- `PASS`: implementation matches the paper contract.
- `PARTIAL`: implementation has a traceable approximation or incomplete mapping.
- `FAIL`: implementation conflicts with the paper contract.
- `MISSING`: required paper element is absent.

This phase should not change simulator behavior.

### Phase 3.1 — State Model Repair

Objective: repair the state construction only after Phase 3.0 identifies exact gaps.

Target paper state:

`sn(t) = [eta_n(t), w_priv_n(t), w_off_n(t), l_pub_n(t-1), L(t)]`

Rules:

- Do not invent extra state fields unless explicitly marked as non-paper diagnostic fields.
- Do not collapse state to `state_dim=2` if paper variables are available.
- Preserve traceability from raw runtime fields to each state component.
- If a state component is unavailable, add instrumentation first; do not fabricate values.

### Phase 3.2 — Reward and Delayed Replay Repair

Objective: make reward handling task-completion based and replay-compatible with Algorithm 1.

Rules:

- Rewards should be associated with the originating task ID and action time.
- A replay tuple should be stored when the task completes or is thrown.
- Immediate step-aggregated reward can remain as a legacy metric, but it must not be used as a paper-faithful reward claim.
- `-C` must be used for thrown/dropped tasks.
- `-Phi_n(t)` must be used for successfully processed tasks.

### Phase 3.3 — LSTM Historical Load Integration

Objective: implement or repair the LSTM historical-load pipeline according to the paper.

Paper contract:

- ECs maintain historical load matrix `L(t)` with shape `W x (N+1)`.
- Each column is the recent active-queue count of a computing node.
- LSTM predicts next-slot load for all EAs and cloud.
- The predicted load is part of the DRL model input.

Rules:

- LSTM must be a forecasting/history pipeline, not merely hidden memory inside DQN.
- The implementation must expose input shape, output shape, lookback window, and forecast fields.
- If LSTM is disabled for a smoke run, the report must say so explicitly.

### Phase 3.4 — Paper-Faithful Training Loop

Objective: align the training loop with Algorithm 1.

Required behavior:

- Per-agent replay memory.
- Per-agent Q and target-Q models.
- epsilon-greedy action selection.
- delayed reward collection from completed task set `D_n(t)`.
- batch sampling from replay memory.
- Double-DQN target update.
- Dueling layer if enabled.
- target network copy every `Ncopy` interval.

Rules:

- Do not claim paper-level performance from a smoke run.
- Save checkpoints and reports, but clearly distinguish smoke artifacts from validation artifacts.

### Phase 4 — 200-Episode Validation

Only start after Phase 3.1–3.4 are accepted.

Objective:

- Run controlled validation using paper-faithful state/action/reward/LSTM contracts.
- Produce validation artifacts, not final paper figures yet.

### Phase 5 — Figures 8–11 Generation

Only start after Phase 4 validation passes.

Objective:

- Generate the paper-equivalent figure workflows.
- Do not fabricate results.
- Every figure must have source data, config, command, and reproducibility notes.

## Operating rules for Codex prompts

Each sub-phase must:

1. Start from a clean working tree.
2. Make the smallest scoped change possible.
3. Run relevant unit tests.
4. Run `git diff --check`.
5. Commit only phase-related files.
6. Push to `origin/100-hoodie-paper-base`.
7. Report branch, commit hash, changed files, commands run, results, and known limitations.

## Current next step

The next action is Phase 3.0: DRL/LSTM Fidelity Audit.

No Phase 3 repair should be implemented before the audit report identifies exact state/action/reward/LSTM gaps.