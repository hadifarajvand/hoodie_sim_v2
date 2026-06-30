# HOODIE Paper-to-Code Gap Audit

**Date**: 2026-07-01
**Repository**: hoodie_sim_v2
**Branch**: main
**Scope**: Full HOODIE paper-to-code gap analysis, Phase 1 only, paper_default path

---

## 1. Paper Requirement Matrix

The HOODIE paper (Algorithm 1, Section 3, Tables 3-4, Figures 7-11) specifies the following reproduction requirements:

### 1.1 Network Architecture

| Requirement | Paper Reference | Status |
|-------------|----------------|--------|
| LSTM-based deep Q-network | Section 3, Algorithm 2 | Implemented |
| Dueling architecture (value + advantage streams) | Section 3, network description | Implemented |
| Double DQN target network | Section 3, training algorithm | Implemented |
| 3-layer MLP body: [1024, 1024, 1024] | Paper implied | Implemented |
| LSTM: 1 layer, hidden_size=20 | Paper implied | Implemented |
| Lookback window W=10 | Section 3, state definition | Implemented |

**Code**: `src/analysis/paper_hoodie_network_implementation/network.py:12-93` — `PaperHoodieDuelingNetwork`

### 1.2 State Representation

| Requirement | Paper Reference | Status |
|-------------|----------------|--------|
| 74-dimensional state vector | Section 3, state definition | Implemented |
| Task characteristics (size, processing_density) | Section 3 | Implemented |
| Private waiting time (psi_priv) | Section 3 | Implemented |
| Offloading waiting time | Section 3 | Implemented |
| Public queue lengths per node | Section 3 | Implemented |
| Load history matrix (W x N) | Section 3 | Implemented (zeros placeholder) |
| Forecast input matrix | Section 3 | Implemented (zeros placeholder) |
| PaperStateBuilder for state construction | Implementation pattern | Implemented |

**Code**: `src/environment/paper_state.py`, `src/agents/paper_state_builder.py`

### 1.3 Action Space

| Requirement | Paper Reference | Status |
|-------------|----------------|--------|
| 22 discrete actions | Section 3, action space | Implemented |
| Local compute (action 0) | Section 3 | Implemented |
| Horizontal offload to N-1 edge nodes (actions 1-19) | Section 3 | Implemented |
| Cloud offload (action 21) | Section 3 | Implemented |
| Legal action masking per topology | Section 3, Figure 7 | Implemented |
| Paper Figure 7 adjacency (20 nodes, degree 3) | Figure 7 | Recovered from assumption registry |

**Code**: `src/environment/paper_action_space.py`, `src/environment/topology.py`

### 1.4 Traffic Model

| Requirement | Paper Reference | Status |
|-------------|----------------|--------|
| Poisson arrival process (lambda=0.5) | Table 4, Algorithm 1 | Implemented |
| Task sizes: [2.0, 5.0] Mbits, step 0.1 | Table 4 | Implemented |
| Processing density: 0.297 Gcycles/Mbit | Table 4 | Implemented |
| Timeout: 20 slots | Table 4 | Implemented |
| Slot duration: 0.1 seconds | Table 4 | Implemented |
| 20 agents (edge nodes) | Table 4 | Implemented |

**Code**: `src/environment/traffic_config.py:61-73`, `src/environment/traffic_generator.py`

### 1.5 Reward Function

| Requirement | Paper Reference | Status |
|-------------|----------------|--------|
| Phi_n(t) = completion_slot - arrival_slot (approximation) | Section 3, Equation 20 | Implemented (approximation documented) |
| Drop penalty C=40 | Table 4 | Implemented |
| NaN reward for no-task-arrival | Section 3, Equation 20 | Implemented |
| Delayed reward emission after terminal resolution | Section 3 | Implemented |

**Code**: `src/environment/reward_timing.py`, `docs/paper_notes/reward_evidence.md`

### 1.6 Training Algorithm

| Requirement | Paper Reference | Status |
|-------------|----------------|--------|
| DDQN with experience replay | Section 3, Algorithm 2 | Implemented |
| Replay buffer capacity: 10,000 | Paper implied | Implemented (deque-based, no priority) |
| Batch size: 64 | Paper implied | Implemented |
| Learning rate: 7e-7 | Paper implied | Implemented |
| Gamma (discount): 0.99 | Paper implied | Implemented |
| Target network update: every 2000 optimizer steps | Assumption-backed | Implemented |
| Adam optimizer | Paper implied | Implemented |
| MSE loss | Paper implied | Implemented |

**Code**: `src/analysis/full_training_reproduction_campaign/trainer.py:186-202`

### 1.7 Topology

| Requirement | Paper Reference | Status |
|-------------|----------------|--------|
| 20 edge nodes + 1 cloud | Figure 7 | Implemented |
| Degree-3 regular graph | Figure 7 | Recovered, validated |
| 30 undirected edges | Figure 7 | Recovered, validated |

**Code**: `src/environment/topology.py`, `resources/papers/hoodie/recovered/user-approved-assumption-registry.json`

### 1.8 Evaluation Metrics

| Requirement | Paper Reference | Status |
|-------------|----------------|--------|
| Average delay | Section 4 | Implemented |
| Drop ratio | Section 4 | Implemented |
| Throughput | Section 4 | Implemented |
| Per-task records (arrival, completion, delay, outcome) | Section 4 | Implemented |

**Code**: `src/evaluation/metrics.py`

### 1.9 Baselines

| Requirement | Paper Reference | Status |
|-------------|----------------|--------|
| FLC (Full Local Computing) | Table 3 | Implemented |
| VO (Vertical Offloading) | Table 3 | Implemented |
| HO (Horizontal Offloading) | Table 3 | Implemented |
| RO (Random Offloading) | Table 3 | Implemented |
| BCO (Balanced Cooperation) | Table 3 | Implemented |
| MLEO (Minimum Latency Estimate) | Table 3 | Implemented |
| ADAPTIVE (heuristic) | Table 3 | Implemented |
| HOODIE (DDQN learned) | Table 3 | Partially implemented |

**Code**: `src/evaluation/policy_registry.py`

### 1.10 Figures

| Figure | Paper Reference | Status |
|--------|----------------|--------|
| Fig 7: Topology | Section 3 | Recovered (adjacency matrix) |
| Fig 8: Training convergence curves | Section 4 | NOT reproducible |
| Fig 9: Action distribution heatmap | Section 4 | Partially supported (extraction stub) |
| Fig 10: Delay/drop ratio comparison | Section 4 | Partially supported (extraction stub) |
| Fig 11: CDF of delay/drop | Section 4 | NOT reproducible |

---

## 2. Code Architecture Map

### 2.1 Core Modules

```
src/
├── environment/
│   ├── gym_adapter.py          # HoodieGymEnvironment — core simulation
│   ├── paper_state.py          # 74D paper state representation
│   ├── paper_action_space.py   # 22-action paper action space
│   ├── topology.py             # Topology graph (Figure 7)
│   ├── traffic_config.py       # Traffic presets (Table 4)
│   ├── traffic_generator.py    # Poisson arrival process
│   ├── reward_timing.py        # Delayed reward emission
│   ├── execution_helper.py     # Slot-based compute decrement
│   ├── slot_engine.py          # Slot-based compute
│   ├── offloading_queue.py     # Queue model
│   ├── public_queue.py         # Public queue
│   ├── private_queue.py        # Private queue
│   ├── compute_config.py       # Per-slot capacity settings
│   ├── paper_link_delay.py     # Transmission delay model
│   ├── paper_timeout.py        # Deadline/timeout model
│   ├── lifecycle_trace.py      # Lifecycle trace bridge
│   └── runtime_model.py        # Shared runtime parameters
├── agents/
│   └── paper_state_builder.py  # 74D state vector builder
├── analysis/
│   ├── full_training_reproduction_campaign/
│   │   ├── trainer.py          # DDQNTrainer (774 lines)
│   │   ├── config.py           # CampaignConfig, paper_default
│   │   ├── replay.py           # ReplayBuffer, ReplayTransition
│   │   └── readiness.py        # Readiness probe
│   ├── paper_hoodie_network_implementation/
│   │   ├── network.py          # PaperHoodieDuelingNetwork
│   │   └── report.py           # Network config
│   ├── completion_accounting_mismatch_diagnostic.py
│   ├── paper_figure_extraction.py
│   ├── campaign_audit.py
│   ├── baseline_sensitivity.py
│   └── reproducibility_bundle.py
├── evaluation/
│   ├── metrics.py              # TraceMetrics, evaluate_trace
│   ├── metric_formulas.py      # average_delay, drop_ratio, throughput
│   ├── matrix_runner.py        # EvaluationMatrixRunner
│   ├── matrix_config.py        # EvaluationMatrixConfig
│   ├── policy_registry.py      # FLC, VO, HO, RO, BCO, MLEO, ADAPTIVE
│   ├── scenario_registry.py    # paper_default, moderate, heavy, extreme
│   ├── campaign_runner.py      # Campaign orchestration
│   ├── trace_protocol.py       # EvaluationTrace, TraceTaskBlueprint
│   └── runner.py               # EvaluationRunner
├── policies/
│   ├── action_masking.py       # Legal action masking
│   ├── adaptive_offloading.py  # Conservative heuristic baseline
│   ├── policy_interface.py     # PolicyContext
│   └── [6 other baseline policies]
└── training/
    └── training_loop.py        # Training loop
```

### 2.2 Active Path (paper_default)

The paper_default path flows:

1. `CampaignConfig.paper_default()` → state_dim=74, action_count=22
2. `DDQNTrainer(config)` → builds online/target networks, replay buffer, optimizer
3. `_build_environment()` → HoodieGymEnvironment with TopologyGraph from approved registry
4. `_episode_rollout()` → slot loop: observe → choose_action → step → record transition
5. `_compute_state_vector()` → PaperStateBuilder.build_state() → 74D vector
6. `CampaignPolicy.choose_action()` → masked Q-value argmax over 22 actions
7. `evaluate()` → evaluation episodes with per-task outcome tracking

---

## 3. Active-Path Verification

### 3.1 What Is Implemented and Active

| Component | File | Active | Evidence |
|-----------|------|--------|----------|
| 74D state vector | `paper_state.py`, `paper_state_builder.py` | Yes | 5/5 tests pass (Gate 4D) |
| 22-action space | `paper_action_space.py` | Yes | Gate 4C verified |
| PaperHoodieDuelingNetwork | `network.py` | Yes | LSTM+Dueling, 22-output |
| DDQNTrainer | `trainer.py` | Yes | 3×200 bounded run complete |
| ReplayBuffer | `replay.py` | Yes | 150 transitions stored |
| CampaignPolicy | `trainer.py:142-162` | Yes | 22-action masked argmax |
| paper_default config | `config.py:261-287` | Yes | 16/16 config tests pass |
| Topology (Figure 7) | `topology.py` | Yes | 20×20 adjacency validated |
| Traffic (Table 4) | `traffic_config.py` | Yes | Poisson arrival implemented |
| Reward (Eq. 20) | `reward_timing.py` | Yes | Phi_n(t) approx, C=40 |
| Legal action masking | `paper_action_space.py`, `action_masking.py` | Yes | Topology-based mask |
| Lifecycle trace bridge | `lifecycle_trace.py`, trainer bridge | Yes | Dedup accepted |
| Accounting diagnostic | `completion_accounting_mismatch_diagnostic.py` | Yes | 8/8 tests pass |
| Evaluation metrics | `metrics.py` | Yes | average_delay, drop_ratio, throughput |
| Baseline policies | `policy_registry.py` | Yes | 7 baselines registered |
| Scenario presets | `scenario_registry.py` | Yes | 4 scenarios |
| Matrix runner | `matrix_runner.py` | Yes | Policy×Scenario×Seed matrix |
| Reproducibility bundle | `reproducibility_bundle.py` | Yes | Bundle builder exists |
| Paper figure extraction | `paper_figure_extraction.py` | Partial | Stub for Fig 9, 10 |

### 3.2 What Is Implemented But Not Wired

| Component | File | Issue |
|-----------|------|-------|
| LSTM load forecast | `paper_state.py` | Forecast matrix hardcoded to zeros |
| Load history matrix | `paper_state.py` | History matrix hardcoded to zeros |
| ReplayBuffer priority sampling | `replay.py` | List-based deque, no priority |
| Multi-seed campaign | `campaign_runner.py` | Single-seed bounded runs only |
| Full campaign execution | `config.py` | `full_campaign_enabled=False` |
| Evaluation matrix for paper_default | `matrix_runner.py` | Matrix runner exists but not exercised for paper_default comparison |

### 3.3 What Is Simplified, Diagnostic-Only, Partial, or Missing

| Component | Status | Detail |
|-----------|--------|--------|
| Phi_n(t) reward formula | Simplified | Approximated as `completion_slot - arrival_slot` (documented in `reward_evidence.md`) |
| Replay buffer | Simplified | No priority sampling, no PER, no circular buffer |
| LSTM state encoding | Missing (placeholder) | Forecast input and load history are zeros |
| Multi-agent MADRL | Missing | Single-agent only (paper_default uses 1 agent, paper describes M×N) |
| DCQ-MADRL (Phase 2) | Missing | Not started |
| Baseline comparison suite | Missing | No DDQN vs DQN vs MADDPG vs DDPG comparison |
| Multi-seed campaigns | Missing | No seed-sweep pipeline |
| Convergence curve generation | Missing | No figure pipeline |
| CDF generation | Missing | No figure pipeline |
| Action distribution heatmap | Missing | Extraction stub only |
| Topology heatmap | Missing | No pipeline |
| Training curves (Fig 8) | Missing | No convergence logging |
| CDF of delay/drop (Fig 11) | Missing | No CDF computation |

---

## 4. Paper-to-Code Gap Matrix

| # | Paper Requirement | Code Status | Gap Severity | Files |
|---|-------------------|-------------|--------------|-------|
| 1 | 74D paper state | Implemented (active) | None | `paper_state.py`, `paper_state_builder.py` |
| 2 | 22-action space | Implemented (active) | None | `paper_action_space.py` |
| 3 | Dueling LSTM DQN | Implemented (active) | None | `network.py` |
| 4 | Double DQN target | Implemented (active) | None | `trainer.py:191-192` |
| 5 | Replay buffer | Implemented (simplified) | P1 — no priority sampling | `replay.py` |
| 6 | Paper topology (20 nodes) | Implemented (active) | None | `topology.py` |
| 7 | Traffic model (Table 4) | Implemented (active) | None | `traffic_config.py` |
| 8 | Reward (Eq. 20) | Implemented (approximation) | P1 — Phi_n(t) approximation | `reward_timing.py` |
| 9 | Legal action masking | Implemented (active) | None | `paper_action_space.py` |
| 10 | LSTM load forecast | Placeholder (zeros) | P0 — state incomplete | `paper_state.py` |
| 11 | Load history matrix | Placeholder (zeros) | P0 — state incomplete | `paper_state.py` |
| 12 | Multi-agent scenario | Not implemented | P0 — paper requires M×N | N/A |
| 13 | DCQ-MADRL | Not implemented | P2 — Phase 2 | N/A |
| 14 | Baseline comparison (DDQN vs others) | Partially implemented | P0 — no comparison executed | `policy_registry.py` |
| 15 | Multi-seed campaigns | Not wired | P0 — no statistical validity | N/A |
| 16 | Convergence curves (Fig 8) | Not implemented | P0 — no figure pipeline | N/A |
| 17 | CDF plots (Fig 11) | Not implemented | P1 — no figure pipeline | N/A |
| 18 | Action distribution heatmap (Fig 9) | Stub only | P1 — extraction only | `paper_figure_extraction.py` |
| 19 | Delay/drop comparison (Fig 10) | Stub only | P1 — extraction only | `paper_figure_extraction.py` |
| 20 | Training curves logging | Not implemented | P0 — no per-epoch metrics | N/A |

---

## 5. P0/P1/P2 Gap Classification

### P0 — Blocking Paper Reproduction

1. **LSTM load forecast placeholder** — State vector is 74D but forecast component is zeros. The paper's state representation depends on load history and forecast for the LSTM encoder to learn meaningful temporal patterns. Without real data, the network cannot learn the paper's intended policy.
   - *Scientific impact*: High — invalidates learned policy fidelity
   - *Files*: `src/environment/paper_state.py`, `src/agents/paper_state_builder.py`

2. **Load history matrix placeholder** — Same as above; the W×N load history is zeros.
   - *Scientific impact*: High — state representation incomplete
   - *Files*: `src/environment/paper_state.py`

3. **No multi-agent scenario** — Paper describes M edge nodes each making independent offloading decisions. Current setup uses 1 agent. The paper_default traffic config specifies `number_of_agents=20` but the trainer only runs 1 agent.
   - *Scientific impact*: Critical — paper's core contribution is multi-agent coordination
   - *Files*: N/A (architectural gap)

4. **No baseline comparison executed** — Paper compares DDQN against DQN, MADDPG, DDPG, and heuristics. No comparison has been run.
   - *Scientific impact*: High — cannot validate against paper's claims
   - *Files*: `src/evaluation/policy_registry.py`, `src/evaluation/matrix_runner.py`

5. **No multi-seed campaigns** — No statistical validity for any metric.
   - *Scientific impact*: High — single-seed results are not publishable
   - *Files*: N/A (pipeline gap)

6. **No convergence curve pipeline** — Figure 8 (training convergence) cannot be generated.
   - *Scientific impact*: High — core paper figure missing
   - *Files*: N/A (pipeline gap)

7. **No per-epoch training metrics logging** — Loss, reward, completion rate over training are not logged to disk.
   - *Scientific impact*: High — cannot produce convergence analysis
   - *Files*: `src/analysis/full_training_reproduction_campaign/trainer.py`

### P1 — Partial Reproduction Limitation

8. **Replay buffer lacks priority sampling** — Paper does not specify PER, but uniform sampling may slow convergence. This is an implementation simplification, not a paper deviation.
   - *Scientific impact*: Medium — affects convergence speed, not correctness
   - *Files*: `src/analysis/full_training_reproduction_campaign/replay.py`

9. **Phi_n(t) reward approximation** — `completion_slot - arrival_slot` is a documented approximation. Paper's exact formula may differ.
   - *Scientific impact*: Medium — reward scale may differ from paper
   - *Files*: `src/environment/reward_timing.py`, `docs/paper_notes/reward_evidence.md`

10. **No CDF computation** — Figure 11 (CDF of delay/drop) cannot be generated.
    - *Scientific impact*: Medium — missing paper figure
    - *Files*: N/A (pipeline gap)

11. **Action distribution extraction stub** — Figure 9 extraction exists but produces no usable data.
    - *Scientific impact*: Medium — missing paper figure
    - *Files*: `src/analysis/paper_figure_extraction.py`

### P2 — Extended Reproduction

12. **DCQ-MADRL (Phase 2)** — Not started. Paper's Phase 2 is the distributed multi-agent coordination algorithm.
    - *Scientific impact*: Low for Phase 1 — Phase 2 is separate paper contribution
    - *Files*: N/A

13. **Full baseline suite** — DQN, MADDPG, DDPG not implemented. Only heuristic baselines and DDQN exist.
    - *Scientific impact*: Low for Phase 1 — can add incrementally
    - *Files*: N/A

---

## 6. Readiness Summary

| Dimension | Verdict |
|-----------|---------|
| Single-agent DDQN baseline | Partially ready — pipeline works but state is incomplete |
| Multi-agent HOODIE | Not ready — architectural gap |
| Paper figure reproduction | Not ready — no pipeline |
| Baseline comparison | Not ready — no comparison executed |
| Statistical validity | Not ready — no multi-seed support |
| Publication readiness | Not ready |

---

*Generated by OpenCode coordinator — 2026-07-01*
