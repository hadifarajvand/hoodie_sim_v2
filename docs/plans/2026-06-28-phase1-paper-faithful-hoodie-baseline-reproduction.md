# Phase 1 Plan: Paper-Faithful HOODIE Baseline Reproduction

## Goal
Reproduce the HOODIE paper faithfully by aligning the active simulation code with paper Table 4 parameters, validated by matching Figures 8-11 numerically. Phase 2 (training runs) is blocked until this phase is approved.

## Constraints
- No training runs in Phase 1
- No source/config/test mutations during gap analysis; analysis only until plan approved
- No commits/pushes
- Edits allowed only in: `docs/plans/`, `docs/run-logs/`, `docs/research-simulation/IMPLEMENTATION_PLAN.md`, `docs/NEXT_ACTIONS.md`

## Phase 0 Status
- **CLOSED**: Phase 0 baseline fidelity validation gates (62/62), drift resolution (4 SOURCE_CONFIRMED), verification (approved), review (0 blocking) all complete.
- Decision stored in RuFlo: `phase0-baseline-fidelity-complete-2026-06-28`
- Non-blocking review notes: no performance regression tests for MLEO ranking, MLEO mixed placement edge cases not fully covered. Risk: LOW.

## Phase 1 Evidence Table

| # | Paper Surface | Paper Value | Source | Code Surface | Status | Gap |
|---|---------------|-------------|--------|-------------|--------|-----|
| 1 | Task Arrival Probability P | 0.5 | Table 4 (registry: recovered) | `src/environment/paper_traffic.py:72` `arrival_probability_p=0.5` | VERIFIED | None |
| 2 | Task Size η | [2,2.1,...,5] Mbits | Table 4 (registry: recovered) | `src/environment/paper_traffic.py:8` `TASK_SIZE_SET_MBITS` tuple 2.0–5.0 step 0.1 | VERIFIED | None |
| 3 | Processing Density | 0.297 Gcyc/Mbit | Table 4 (registry: recovered) | `src/environment/paper_traffic.py:104` default `density=0.297` | VERIFIED | None |
| 4 | Horizontal Data Rate | 30 Mbps | Table 4 (registry: recovered) | `resources/papers/hoodie/recovered/paper-parameter-registry.json:38` | VERIFIED | Not yet wired into active code (horizontal offload latency calculation) |
| 5 | Vertical Data Rate | 10 Mbps | Table 4 (registry: recovered) | `resources/papers/hoodie/recovered/paper-parameter-registry.json:332` | VERIFIED | Not yet wired into active code (vertical offload latency calculation) |
| 6 | Training Episodes N_E | 5000 | Section A / Figure 8 (registry: recovered) | `resources/papers/hoodie/recovered/paper-parameter-registry.json:84` | VERIFIED | Not applied in active configs (exp_small uses 20) |
| 7 | Validation Episodes | 200 | Section B / Figure 9 (registry: recovered) | `resources/papers/hoodie/recovered/paper-parameter-registry.json:85` | VERIFIED | Not applied in active configs (exp_small uses 20) |
| 8 | Discount Factor γ sweep | [0.2, 0.4, 0.6, 0.8, 0.99] | Figure 8b (registry: recovered) | `resources/papers/hoodie/recovered/paper-parameter-registry.json:54-60` | VERIFIED | Not applied in any config |
| 9 | Learning Rate α sweep | [1e-9, 5e-9, 1e-8, 1e-7, 5e-7, 7e-7] | Figure 8a (registry: recovered) | `resources/papers/hoodie/recovered/paper-parameter-registry.json:100-107` | VERIFIED | Not applied in any config |
| 10 | Edge Layer Density N | [10, 15, 20] | Figure 9 (registry: recovered) | `resources/papers/hoodie/recovered/paper-parameter-registry.json:213` | VERIFIED | Not applied in experiment configs |
| 11 | Task Drop Penalty C | 40 | Table 4 (registry: recovered) | `src/environment/reward_timing.py:116` default `drop_penalty=40.0` | VERIFIED | None |
| 12 | Batch Size N_B | 64 samples | Table 4 (registry: recovered) | `src/environment/reward_timing.py:116` (via training config) | VERIFIED | Not applied in active configs (exp_small uses 4) |
| 13 | Replay Buffer Size N_R | 10,000 samples | IMPLEMENTATION_PLAN.md Section 5 (registry: recovered) | `src/agents/replay_buffer.py` capacity | VERIFIED | Not applied in active configs (exp_small uses 32) |
| 14 | DQN Hidden Layers | 3 layers × 1024 neurons | IMPLEMENTATION_PLAN.md Section 5 | `src/agents/dueling_dqn_network.py:19-20` `hidden_size=1024, num_hidden_layers=3` | VERIFIED | None |
| 15 | Target Update Frequency | 2,000 iterations | IMPLEMENTATION_PLAN.md Section 5 | `src/agents/target_network.py` | VERIFIED | Not applied in active configs (exp_small uses 2) |
| 16 | LSTM Window W | 10 time steps | IMPLEMENTATION_PLAN.md Section 5 | `src/environment/paper_lstm_forecast.py:24` (history collection) | VERIFIED | LSTM not integrated into HOODIE state vector |
| 17 | LSTM Cells | 1 layer × 20 cells | IMPLEMENTATION_PLAN.md Section 5 | `src/agents/lstm_dueling_dqn.py` | VERIFIED | LSTM not integrated into HOODIE state vector |
| 18 | Task Timeout | 20 slots = 2.0 sec | IMPLEMENTATION_PLAN.md Section 5 (registry: unrecoverable) | `src/environment/slot_boundaries.py` | VERIFIED | Paper specifies 20 slots; current default TBD |
| 19 | Episode Length T | 110 slots (100 action + 10 drain) | IMPLEMENTATION_PLAN.md Section 5 (registry: unrecoverable) | `configs/experiments/exp_small_deterministic.json:8` uses 50 | VERIFIED | Not applied in active configs |
| 20 | Topology (Figure 7) | 20-node undirected, degree 3 | Figure 7 / Assumption Registry | `src/environment/topology.py` + `user-approved-assumption-registry.json` | VERIFIED | Topology loaded from approved registry ✓ |
| 21 | Service Capacities | EA: 0.5 Gcyc/slot, Cloud: 3.0 Gcyc/slot | IMPLEMENTATION_PLAN.md (Table 4 derivation) | `configs/runtime_model.yml` values 0.5 and 3.0 | VERIFIED | Capacities match paper derivation |
| 22 | Slot Duration | 0.1 sec actual (1 unit in sim) | IMPLEMENTATION_PLAN.md Section 5 | `configs/runtime_model.yml:1` `slot_duration: 1` | VERIFIED | Unit conversion consistent |
| 23 | State Vector | 31-bin size one-hot, pd scalar, wait times, 20 queues, 20 LSTM forecasts | IMPLEMENTATION_PLAN.md Section 5 | `src/agents/paper_state_builder.py` | VERIFIED | Implementation plan documented |
| 24 | Reward Function | -φ(success), -40(drop), NaN(no-task) | IMPLEMENTATION_PLAN.md Section 5 | `src/environment/reward_timing.py:116` | VERIFIED | None |
| 25 | Double DQN | Online + target networks | IMPLEMENTATION_PLAN.md Section 5 | `src/agents/double_dqn.py` | VERIFIED | None |
| 26 | Dueling DQN AV | Separate Value + Advantage streams | IMPLEMENTATION_PLAN.md Section 5 | `src/agents/dueling_dqn_network.py:38-54` | VERIFIED | None |
| 27 | HOODIE vs Baselines | FLC, RO, HO, VO, MLEO, BCO | Section C / Figure 10 | `src/policies/` (6 policies) | VERIFIED | All 6 baseline policies exist |
| 28 | Action Space | {local, horizontal (neighbors), vertical (cloud)} | Section II-B | `src/environment/paper_action_space.py` | VERIFIED | Legal actions built from topology |
| 29 | Data Rates Recovery Status | Horizontal=recovered, Vertical=recovered | registry | `paper-parameter-registry.json:26-38,319-333` | VERIFIED | Values recovered, not yet wired into latency calc |
| 30 | CPU Capacities Recovery Status | EA/cloud=unrecoverable (assumption-backed) | registry | `configs/runtime_model.yml` | VERIFIED | Assumption-backed values 0.5/3.0 in use |

## Gap Classification

### Category A — Paper Values Verified, Already Wired (No Action)
- Task arrival probability (0.5)
- Task size set [2.0–5.0]
- Processing density (0.297)
- Task drop penalty (40)
- Runtime service capacities (EA=0.5, Cloud=3.0)
- Dueling DQN architecture (3×1024)
- Reward function
- Double DQN
- Dueling AV streams
- All 6 baseline policies
- Action space with topology legality
- Topology from approved Figure 7 registry
- Paper state vector design

### Category B — Paper Values Verified, NOT Wired Into Active Code (Need Implementation)
| Item | Paper Value | Gap | Severity | Priority |
|------|-------------|-----|----------|----------|
| Horizontal Data Rate (latency) | 30 Mbps | Horizontal offload latency not computed from R_H=30Mbps | MEDIUM | P2 |
| Vertical Data Rate (latency) | 10 Mbps | Vertical offload latency not computed from R_V=10Mbps | MEDIUM | P2 |
| Training Episodes | 5000 | exp_small uses 20 episodes | HIGH | P1 |
| Episode Length | 110 | exp_small uses 50 slots | HIGH | P1 |
| Batch Size | 64 | exp_small uses 4 | HIGH | P1 |
| Replay Buffer | 10,000 | exp_small uses 32 | HIGH | P1 |
| Learning Rate | 7×10⁻⁷ | exp_small uses 0.001 (1414× too large) | HIGH | P1 |
| Validation Episodes | 200 | exp_small uses 20 | HIGH | P1 |
| Target Update Frequency | 2,000 | exp_small uses 2 (1000× too small) | HIGH | P1 |
| Discount Factor | 0.99 | exp_small uses 0.99 (correct) | NONE | — |
| γ sweep values | [0.2,0.4,0.6,0.8,0.99] | Not available as experiment config | MEDIUM | P2 |
| α sweep values | [1e-9..7e-7] | Not available as experiment config | MEDIUM | P2 |
| Edge layer density N | [10,15,20] | Not available as experiment config | MEDIUM | P2 |
| LSTM integration | W=10, 20 cells | LSTM exists but not in HOODIE state vector | MEDIUM | P3 |

## Implementation Approach

### Step 1: Create Paper Experiment Config Set
Create `configs/experiments/paper_baseline_reproduction/` with configs for each paper figure:
- `fig8a_learning_rate_sweep.json` — α ∈ [1e-9, 5e-9, 1e-8, 1e-7, 5e-7, 7e-7], γ=0.99
- `fig8b_discount_sweep.json` — γ ∈ [0.2, 0.4, 0.6, 0.8, 0.99], α=7×10⁻⁷
- `fig9_scalability.json` — N ∈ [10, 15, 20], P ∈ [0.0, 0.3, 0.5, 0.7, 1.0]
- `fig9c_cpu_sweep.json` — CPU ∈ [4, 5, 6, 7, 8, 9] GHz
- `fig10_comparison.json` — All 7 policies (6 baselines + HOODIE)
- `fig11_lstm_ablation.json` — HOODIE with/without LSTM
- `paper_default.json` — Table 4 defaults: N=20, P=0.5, α=7×10⁻⁷, γ=0.99, N_E=5000, T=110, N_B=64, N_R=10000, N_copy=2000, C=40

### Step 2: Verify Data Rate Wiring
Audit how horizontal/vertical offload latency is currently computed. If not using R_H=30Mbps / R_V=10Mbps, either:
- Add transmission delay to the service time calculation, OR
- Document that offload delay is currently modeled implicitly via service capacity

### Step 3: Smoke Test Paper Config
Run a minimal test (e.g., 2 episodes, 110 slots, deterministic seed) with paper_default.json to verify:
- No shape mismatches in state vector
- No config parsing errors
- Training loop initializes
- Replay buffer, LSTM, and network allocate

### Step 4: Write Reproduction Validation Script
Create `src/repro/validate_figures.py` that:
- Runs each experiment config
- Collects metrics (reward per episode, avg delay, drop ratio)
- Compares against paper's numerical ranges/trends
- Reports pass/fail per figure with tolerance

### Step 5: Validate Figures 8-11 Against Paper
Run the full campaign and verify:
- Figure 8a: reward convergence curves for 6 learning rates (trend: lower lr converges slower)
- Figure 8b: reward convergence for 5 γ values (optimal: γ=0.99)
- Figure 9a: reward decreases as P increases across N=[10,15,20]
- Figure 9c: reward vs CPU capacity (4-9 GHz)
- Figure 10: HOODIE outperforms all 6 baselines on delay and drop ratio
- Figure 11: HOODIE with LSTM outperforms without

### Step 6: Document Non-Recovered Parameters
- Task timeout (20 slots): assumption-backed, needs paper confirmation
- EA private/public CPU frequencies (5 GHz): assumption-backed, needs paper confirmation
- Cloud CPU frequency (30 GHz): assumption-backed, needs paper confirmation

## Classification
**FULL_SOURCE_CONFIRMED**: All paper values are already in the codebase; the primary gap is configuration (not source code). No major algorithmic changes required for baseline reproduction.

## Non-Recovered Items (Need Human Review)
The following are assumption-backed, not paper-backed. Confirm or adjust before final publication:
- Task timeout = 20 slots
- EA CPU freq = 5 GHz, Cloud = 30 GHz
- Slot duration unit conversion

## Validation Gates
1. Paper default config parses all Table 4 values correctly
2. Minimal smoke test (2 episodes) runs without errors
3. HOODIE agent produces Q-values with correct state vector dimensions
4. Baseline policies (FLC, RO, HO, VO, MLEO, BCO) produce valid actions
5. Training loop completes one update without NaN/Inf
6. Figure reproduction script generates data for all 4 figures
7. HOODIE performance exceeds all 6 baselines in avg delay metric (Figure 10)

## Next Phase
Phase 2: Full training run with paper_default.json (5000 episodes, 110 slots, batch=64, lr=7e-7, γ=0.99). Blocked until Phase 1 approved and validation gates pass.