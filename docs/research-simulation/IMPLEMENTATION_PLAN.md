# Research Simulation Implementation Plan

## 1. Project Objective
Reproduce the HOODIE paper faithfully by implementing the distributed deep reinforcement learning framework for hybrid task offloading in the Cloud-Edge Computing Continuum (CEC) as described in "HOODIE: Hybrid Computation Offloading via Distributed Deep Reinforcement Learning in Delay-aware Cloud-Edge Continuum". The goal is to match the paper's methodology, hyperparameters, architecture, training procedure, and quantitative results (Figures 8-11) within experimental tolerance.

## 2. Paper / Source Inventory
- **Paper PDF**: `resources/papers/hoodie/original/HOODIE_paper.pdf`
- **OCR extracted text**: `resources/papers/hoodie/ocr/merged.md` (primary), `.txt`, `.json`, `.tex`
- **Recovered paper parameters**: `resources/papers/hoodie/recovered/paper-parameter-registry.json`
- **User-approved assumptions**: `resources/papers/hoodie/recovered/user-approved-assumption-registry.json`
- **Notes & reports**: `docs/analysis/*`, `docs/assumptions/*`, `docs/paper_notes/*`
- **Supplemental figures**: embedded in PDF and reproduced in `artifacts/analysis/*`
- **Simulation code**: `src/` (environment, agents, policies, training, evaluation, config, repro, reference_model)
- **Generated outputs / logs**: `artifacts/analysis/` (90+ analysis/audit directories)
- **OpenCode/Ruflo/Graphify config**: `.opencode/`

## 3. Environment & Interpreter

**All simulation, testing, and training must use the project-local virtual environment:**

```
.venv/bin/python
```

Full path: `/Users/hadi/Documents/GitHub/hoodie_sim_v2/.venv/bin/python`
- Python 3.14.3
- PyTorch 2.12.1
- NumPy 2.5.0
- Matplotlib 3.11.0
- Pandas 3.0.3
- PyYAML 6.0.3
- pytest 9.1.1

**Activation** (optional, for interactive use):
```bash
source .venv/bin/activate
```

**Direct invocation** (preferred for scripts and agents):
```bash
.venv/bin/python -m src.cli validation --config configs/smoke/smoke_validation_flc_hoodie.json --output-dir outputs/smoke --deterministic
.venv/bin/python -m pytest tests/ -q
```

## 4. Repository Structure Summary
```
.
├─ .opencode/                # OpenCode configuration, plugins, README
├─ docs/
│  ├─ analysis/            # 90+ analysis/audit directories documenting gaps and assumptions
│  ├─ assumptions/          # hoodie_assumptions.md, validation_deviations.md
│  ├─ paper_notes/          # OCR text, mapping notes, evidence files
│  └─ research-simulation/  # ← this plan file lives here
├─ resources/papers/hoodie/  # PDF, OCR, recovered parameters of the HOODIE paper
├─ src/                      # simulation source code
│  ├─ analysis/             # 90+ audit/reconstruction directories
│  ├─ agents/               # HOODIE agent, LSTM-DQN variants, replay buffer, etc.
│  ├─ config/               # config loader, freezer
│  ├─ environment/          # slot engine, runtime model, queues, tasks, rewards
│  ├─ evaluation/           # validation runner, trace protocol, metrics, fairness
│  ├─ policies/             # FLC, RO, HO, VO, MLEO, BCO, HOODIE
│  ├─ reference_model/      # reference models for comparison
│  ├─ repro/                # reproducibility packaging
│  ├─ training/             # training loop, delayed rewards, seed management
│  └─ evaluation/           # validation runner, trace protocol, metrics
├─ artifacts/analysis/       # generated logs, reports, figures from 90+ analysis directories
└─ specs/...                # spec‑kit artifacts (not part of core simulation)
```

## 5. Paper Methodology Reconstruction
The HOODIE paper describes a distributed DRL framework for hybrid task offloading with:
- **Objective**: Jointly minimize task execution delay and drop rate (negative reward formulation)
- **Environment**: Discrete-event simulation with time slots (Δ = 0.1 sec), 20 Edge Agents (EAs) arranged in topology from Figure 7
- **Agent inputs (state vector)**:
  - Local task characteristics: size [2,2.1,...,5] Mbits, processing density 0.297 Gcyc/Mbit
  - Waiting times in private/offloading queues
  - Public queue lengths of all N EAs
  - Load forecast for next slot: W=10 history of all node loads passed through LSTM (1×20 cells)
- **Action space**: {local compute, horizontal offload to any of N-1 neighbors, vertical offload to cloud}
- **Reward function**:
  - No task: NaN (omitted)
  - Success: -(completion_slot - arrival_slot)  [task delay]
  - Drop: -C where C=40 (task drop penalty)
- **Learning algorithm**: Deep Q-Learning with:
  - Experience replay (buffer size N_R = 10,000)
  - Double DQN (online and target networks)
  - Dueling DQN architecture (separate Value and Advantage streams)
  - Hyperparameters: γ=0.99, learning rate=7×10⁻⁷, batch size=64, target update every 2,000 iterations
  - Network: 3 hidden layers of 1,024 neurons each feeding into Dueling AV layer
- **Training**: 5,000 episodes, 110 time slots/episode (100 for action, 10 for queue drain)
- **Evaluation**: 200 validation episodes per agent, exploiting learned policy (ε=0)
- **Baselines compared**: FLC, RO, HO, VO, MLEO, BCO (6 baselines)
- **Metrics**: Average delay (sec), drop ratio (reported over 200 validation episodes)
- **Topology**: 20-node undirected graph from Figure 7, degree 3 for each node
- **System parameters** (Table 4):
  - Task arrival probability: 0.5
  - Horizontal data rate: 30 Mbps
  - Vertical data rate: 10 Mbps
  - CPU frequencies: 5 GHz (EA private/public), 30 GHz (Cloud)
  - Slot duration: 0.1 sec → implies capacities: 0.5 Gcyc/slot (EA), 3.0 Gcyc/slot (Cloud)
  - Task timeout: 20 slots = 2.0 sec

## 6. Current Implementation Summary
The repository contains a substantially complete simulation framework with most components present:

### What is implemented:
- ✅ **Environment**: Slot-based discrete-event simulation with private/public/offloading queues, task lifecycle, terminal resolution, delayed reward timing
- ✅ **Policies**: All 6 baselines (FLC, RO, HO, VO, MLEO, BCO) implemented as stateless SharedPolicy
- ✅ **HOODIE agent**: DuelingDQN with Double DQN structure, replay buffer, target network, TorchRL adapter
- ✅ **Training loop**: Delayed reward handling, experience replay, learning from transitions, target network updates
- ✅ **Evaluation framework**: Validation runner with shared traces, fairness checks, metric computation
- ✅ **CLI pipeline**: Unified config loader, run/validation/analysis commands, reproducibility packaging
- ✅ **Seed management**: Deterministic seeding for random, NumPy, PyTorch
- ✅ **Paper evidence**: OCR text, recovered parameter registry, user-approved assumption registry, runtime model evidence matrix, reward evidence
- ✅ **Analysis infrastructure**: 90+ analysis/audit directories documenting every aspect of paper-to-code mapping

### What is missing or incorrect:
- ❌ **HOODIE state vector**: Currently uses only `len(history) + len(trace_history)` as state features instead of the full paper state (task size, waiting times, queue lengths, LSTM load forecast)
- ❌ **HOODIE Q-network architecture**: Missing the 3×1024 neuron Dueling DQN architecture; current network is severely underspecified
- ❌ **Hyperparameters**: Active configs use toy values (1 episode, 2 slots, batch=4) instead of paper values (5000 episodes, 110 slots, batch=64, lr=7e-7)
- ❌ **CPU capacities**: Current `runtime_model.yml` sets all capacities to 1, but paper-derived values from Table 4 are:
  - EA private/public: 5 GHz × 0.1 sec = 0.5 Gcyc/slot (currently off by 64×)
  - Cloud: 30 GHz × 0.1 sec = 3.0 Gcyc/slot (currently off by 128×)
- ❌ **Multi-agent distribution**: Paper describes distributed DRL agents at each EA; current implementation uses single agent only
- ❌ **LSTM integration**: Although `paper_lstm_forecast.py` and `lstm_dueling_dqn.py` exist, the LSTM forecaster is not wired into the active HOODIE agent's state vector
- ❌ **Topology scale**: Most configs use 3-4 node topologies instead of the paper's 20-node Figure 7 adjacency matrix
- ❌ **Quantitative reproduction**: No generated outputs match the paper's Figures 8-11 numerical values (reward curves, delay vs capacity, drop ratio vs timeout, etc.)

## 7. Paper-vs-Code Gap List

| Area | Paper Requirement | Current Repo State | Gap | Severity |
|------|-------------------|--------------------|-----|----------|
| **State representation** | Task size, proc density, private/offload wait times, public queue lengths (N), W=10 load history via LSTM (1×20) | `len(history) + len(trace_history)` only | Missing 95% of state features | HIGH |
| **Q-network architecture** | 3 hidden layers (1,024 neurons each) → Dueling AV layer | Simple feature extraction; no proper DQN layers | Missing deep neural network architecture | HIGH |
| **Hyperparameters** | N_E=5000, T=110, N_B=64, lr=7×10⁻⁷, γ=0.99, N_R=10,000, N_copy=2,000 | Toy configs: N_E=1, T=2, N_B=4, lr=0.001, γ=0.99, N_R=32, N_copy=2 | Wrong scale by 2-3 orders of magnitude | HIGH |
| **CPU capacities** | EA: 0.5 Gcyc/slot, Cloud: 3.0 Gcyc/slot (derived from Table 4) | All capacities = 1 in runtime_model.yml | 64×/128× error in service delay calculation | HIGH |
| **Multi-agent** | Distributed DRL agent at each of N=20 EAs | Single agent shared across all EAs | Missing distributed architecture | HIGH |
| **LSTM forecaster** | W=10 history → LSTM (1×20) → predicted load for all N nodes | LSTM files exist but not integrated into HOODIE state | Missing temporal load prediction component | MEDIUM |
| **Topology** | 20-node undirected graph from Figure 7 (degree 3) | Most configs use 3-4 node topologies | Incorrect network scale and connectivity | MEDIUM |
| **Action masking** | Legal actions based on topology (no self-offload, only neighbors for horizontal) | Policies use generic legal_action_mask | Topology-dependent legality not fully implemented | MEDIUM |
| **Reward function** | -delay on success, -C=40 on drop, NaN on no-task | Correctly implemented in delayed_reward_training.py | ✅ Implemented correctly | LOW |
| **Experience replay** | Uniform random sampling from buffer (N_B=64) | Implemented correctly | ✅ Implemented correctly | LOW |
| **Double DQN** | Online and target networks with periodic copy | Implemented correctly | ✅ Implemented correctly | LOW |
| **Dueling DQN** | Separate Value and Advantage streams | Implemented in DuelingDQN class | ✅ Implemented correctly | LOW |

## 8. Output-vs-Paper Gap List

| Paper Figure/Table | Description | Current Repo State | Gap |
|--------------------|-------------|-------------------|-----|
| **Figure 8** | Learning curves: reward vs episodes for different α_lr (a) and γ (b) | No generated data matching these curves | Missing quantitative reproduction |
| **Figure 9a** | Reward vs task arrival probability (P) for N=[10,15,20] | No generated data | Missing |
| **Figure 9b** | Action distribution (local/horizontal/vertical) vs P | No generated data | Missing |
| **Figure 9c** | Reward vs CPU capacity (4-9 GHz) for different N | No generated data | Missing |
| **Figure 9d** | Reward vs number of agents under traffic scenarios | No generated data | Missing |
| **Figure 9e** | Reward vs number of agents under offloading data rate configs | No generated data | Missing |
| **Figure 10a** | Avg delay vs task arrival probability for all schemes | No generated data | Missing |
| **Figure 10b** | Avg delay vs CPU capacity for all schemes | No generated data | Missing |
| **Figure 10c** | Avg delay vs task timeout for all schemes | No generated data | Missing |
| **Figure 10d** | Drop ratio vs task arrival probability for all schemes | No generated data | Missing |
| **Figure 10e** | Drop ratio vs CPU capacity for all schemes | No generated data | Missing |
| **Figure 10f** | Drop ratio vs task timeout for all schemes | No generated data | Missing |
| **Figure 11** | HOODIE reward with vs without LSTM over episodes | No generated data | Missing |
| **Table 4** | System and learning parameters | Values documented in registries but not used in active configs | Not applied in training runs |

## 9. Confirmed Bugs or Suspicious Issues
- **Capacity scaling bug**: The 64×/128×/42.67× discrepancy in CPU capacities causes service delays to be off by orders of magnitude, making comparisons with paper meaningless
- **State representation deficit**: Training on a near-empty state vector prevents learning meaningful policies
- **Hyperparameter mismatch**: Toy configs prevent reaching the convergence regimes shown in the paper
- **Single-agent limitation**: Cannot study distributed decision-making or topology effects as described in paper
- **Missing LSTM**: No temporal load forecasting, which is critical for the paper's proactivity claim
- **Configs reference `@tarquinen/opencode-dcp@latest`** (unpinned) - benign but should be pinned for reproducibility

## 10. Missing Components
- **Complete HOODIE state vector** with all paper features
- **Paper-faithful Q-network** (3×1024 FC → Dueling AV)
- **Paper hyperparameter configuration set**
- **Corrected CPU capacities** in runtime config
- **Multi-agent distributed architecture** (N agents with shared topology)
- **Integrated LSTM load forecaster** in state vector
- **20-node Figure 7 topology** as default
- **Figure reproduction scripts** to generate quantitative plots matching paper
- **Comprehensive test suite** for policies, environment, training, evaluation

## 11. Prioritized Implementation Phases

### Phase 0: Baseline Fidelity Audit & Config Correction
**Goal**: Establish correct foundation by fixing known quantifiable errors and verifying baseline behaviors match paper descriptions
**Files affected**: `configs/runtime_model.yml`, `src/policies/*` (legality checks), `docs/research-simulation/IMPLEMENTATION_PLAN.md`
**Exact work**:
1. Update `runtime_model.yml` with paper-derived CPU capacities from user-approved assumption registry:
   - local_service_capacity: 0.5 (5 GHz × 0.1 sec)
   - public_service_capacity: 0.5 (5 GHz × 0.1 sec)
   - cloud_service_capacity: 3.0 (30 GHz × 0.1 sec)
   - timeout_grace_slots: 0 (keep assumption-backed for now)
   - slot_duration: 1 (in units of 0.1 sec → 0.1 sec actual)
2. Verify all 6 baseline policies (FLC, RO, HO, VO, MLEO, BCO) implement correct legality per topology:
   - FLC: always local if legal
   - RO: uniform random over legal actions
   - HO: uniform random over horizontal destinations
   - VO: always vertical to cloud if legal
   - BCO: round-robin over [local, cloud, horizontal] in that order
   - MLEO: computes delay for each option and picks minimum
3. Add topology legality helpers to ensure horizontal offload only to neighbors (per Figure 7)
4. Create baseline verification script that runs each policy with paper config and logs action distributions
**Expected output**: Configs producing correct service delays; baseline legality verified
**Validation checks**: 
- Compute service delay for known task sizes matches manual calculation
- Policy legality tests pass for all actions in Figure 7 topology
**Risk level**: LOW (mostly config updates and verification)
**Completion status**: □ pending

### Phase 1: Paper-Faithful HOODIE Agent
**Goal**: Implement the complete HOODIE agent as described in the paper: proper state vector, Q-network architecture, and feature extraction
**Files affected**: `src/agents/hoodie_model.py`, `src/agents/hoodie_agent.py`, `src/agents/history_builder.py`, `src/agents/dueling_dqn.py`, `src/agents/paper_state_builder.py` (new)
**Exact work**:
1. Create `PaperStateBuilder` that constructs the full state vector:
   - Task characteristics: size (one-hot [2,2.1,...,5]), processing density (scalar)
   - Queue state: private wait time, offload wait time (slots)
   - Public queue lengths: N scalars (one per EA)
   - Load forecast: N scalars from LSTM (W=10 history → LSTM 1×20 → predict next slot)
2. Replace the current synthetic state features (`len(history)`) with the real paper state vector
3. Implement the Q-network architecture:
   - Input layer: paper state vector size
   - 3 hidden layers of 1,024 neurons each with ReLU activation
   - Dueling AV layer: split into Value stream (1→1) and Advantage stream (num_actions→1)
   - Combine: Q(s,a) = V(s) + (A(s,a) - mean_a' A(s,a'))
4. Wire the network into `HoodieModel.forward()` to compute Q-values from state
5. Ensure the network works with both DuelingDQN (online) and TargetNetwork (target) components
**Expected output**: HOODIE agent that computes Q-values using the full paper state and paper network architecture
**Validation checks**:
- State vector dimension matches paper formula: `ℋ×𝒯²×Λᴺ×{0,1,...,N}ᴡ·(𝒩⁺¹)`
- Network forward pass runs without shape errors
- Q-values change meaningfully with different state inputs
**Risk level**: MEDIUM (algorithmic correctness critical)
**Completion status**: □ pending

### Phase 2: Multi-Agent Architecture & Topology
**Goal**: Implement true distributed architecture with N=20 Edge Agents sharing the Figure 7 topology
**Files affected**: `src/agents/hoodie_agent.py` (multi-agent support), `src/evaluation/runner.py` (multi-agent sampling), `src/config/*` (default topology), `resources/papers/hoodie/recovered/topology-g.json` (verify)
**Exact work**:
1. Modify agent creation to support N independent HOODIE agents (one per EA) sharing:
   - Same network architecture (but independent weights)
   - Same topology graph (Figure 7 from paper)
   - Same hyperparameters
2. Update evaluation runner to:
   - Sample state for each agent independently based on its local observations
   - Collect actions from all N agents simultaneously
   - Apply each agent's action to its local task
3. Set default topology in configs to the 20-node Figure 7 graph (undirected, unweighted, degree 3)
4. Verify topology matches user-approved assumption registry (Figure_7_adjacency)
5. Implement inter-agent communication protocol placeholder for load vector sharing (to be completed in Phase 3)
**Expected output**: N=20 agents acting independently on their local tasks using shared topology
**Validation checks**:
- Exactly 20 agents created in evaluation
- Each agent sees only its local task state
- Actions are computed independently per agent
- Topology matches Figure 7 adjacency matrix
**Risk level**: MEDIUM (architectural change)
**Completion status**: □ pending

### Phase 3: LSTM Load Forecaster Integration
**Goal**: Integrate the temporal load forecasting LSTM into the HOODIE state vector as described in the paper
**Files affected**: `src/agents/paper_state_builder.py`, `src/agents/paper_lstm_forecast.py`, `src/agents/hoodie_model.py`, `src/training/training_loop.py`
**Exact work**:
1. Complete `PaperStateBuilder` to include load forecast:
   - For each of N nodes, collect W=10 history of public queue lengths (or load metric)
   - Pass each node's history through LSTM (1×20 cells) to predict next slot load
   - Append N predicted load scalars to state vector
2. Verify LSTM architecture matches paper: paper specification: 1 layer, 20 hidden cells, input seq length W=10
3. Wire the LSTM forecaster into state construction so predictions are updated each slot
4. In training loop, ensure LSTM states are maintained and updated correctly (not reset per episode)
5. Add LSTM to the agent's state dict for checkpointing/reloading
**Expected output**: HOODIE state includes N load forecast values from LSTM
**Validation checks**:
- LSTM forward pass produces reasonable load predictions
- State vector includes N forecast values that change with history
- Checkpointing preserves LSTM states across episodes
**Risk level**: MEDIUM (temporal learning critical)
**Completion status**: □ pending

### Phase 4: Paper Hyperparameter Training Configuration
**Goal**: Configure and run training with the exact hyperparameters from Table 4 of the paper
**Files affected**: `configs/experiments/*`, `src/config/training_config.py`, `src/run_pipeline.py`
**Exact work**:
1. Create experiment config matching Table 4 exactly:
   - N_E = 5000 episodes
   - T = 110 time slots/episode
   - N_B = 64 batch size
   - learning_rate = 7×10⁻⁷
   - γ = 0.99
   - N_R = 10,000 replay buffer size
   - N_copy = 2,000 target update frequency
   - W = 10 LSTM lookback window
   - Task arrival probability = 0.5
   - Horizontal data rate = 30 Mbps
   - Vertical data rate = 10 Mbps
   - Task size = [2,2.1,...,5] Mbits
   - Processing density = 0.297 Gcyc/Mbit
   - CPU frequencies: 5 GHz (EA), 30 GHz (Cloud)
   - Slot duration = 0.1 sec
   - Task timeout = 20 slots = 2.0 sec
   - Task drop penalty C = 40
2. Verify config loader correctly ingests these values
3. Run a small-scale test (e.g., 2 episodes) to ensure no shape mismatches
4. Document expected memory/compute requirements for full run
**Expected output**: Configurable training run with paper hyperparameters
**Validation checks**:
- Config parses all Table 4 values correctly
- Training loop initializes without errors
- Replay buffer, LSTM, and network allocate correctly
**Risk level**: LOW (configuration update)
**Completion status**: □ pending

### Phase 5: Figure Reproduction & Comparative Analysis
**Goal**: Generate quantitative outputs matching Figures 8-11 and Tables in the paper
**Files affected**: `src/analysis/*` (new figure reproduction scripts), `docs/analysis/*` (update gap analysis), `scripts/` (figure generation)
**Exact work**:
1. Create scripts to run the paper's experimental matrix:
   - Vary α_lr: [1e-9, 5e-9, 1e-8, 1e-7, 5e-7, 7e-7] → Figure 8a
   - Vary γ: [0.2, 0.4, 0.6, 0.8, 0.99] → Figure 8b
   - Vary P: [0.0, 0.3, 0.5, 0.7, 1.0] with N=[10,15,20] → Figure 9a
   - Action categorization (local/horizontal/vertical) → Figure 9b
   - Vary CPU capacity: [4-9] GHz → Figure 9c
   - Vary N agents under traffic scenarios → Figure 9d
   - Vary offloading data rates (balanced/horizontal-centric/vertical-centric) → Figure 9e
   - Compare all 7 schemes (6 baselines + HOODIE) for:
     * Avg delay vs P (Fig 10a)
     * Avg delay vs CPU capacity (Fig 10b)
     * Avg delay vs timeout (Fig 10c)
     * Drop ratio vs P (Fig 10d)
     * Drop ratio vs CPU capacity (Fig 10e)
     * Drop ratio vs timeout (Fig 10f)
   - HOODIE with vs without LSTM → Figure 11
2. Store results in CSV/JSON format matching paper's numerical values
3. Generate plots matching paper's style, labels, scales
4. Compute paper's performance metrics: average delay (sec), drop ratio (%)
**Expected output**: Reproduced figures and tables within 5-10% tolerance of paper values
**Validation checks**:
- Numerical values match paper tables/figures within tolerance
- Plots reproduce trends and relative performance
- HOODIE shows improvement over baselines as claimed
**Risk level**: MEDIUM (experimental validation)
**Completion status**: □ pending

### Phase 6: Validation & Testing
**Goal**: Establish comprehensive test suite to prevent regression and verify component correctness
**Files affected**: `tests/` (new test files), `pytest.ini` (if needed), `src/*` (add test hooks if needed)
**Exact work**:
1. Unit tests for:
   - All 6 baseline policies (legality, action selection)
   - Environment components (slot engine, queues, runtime model, reward timing)
   - HOODIE agent (state building, Q-network forward, action selection)
   - Training loop (delayed rewards, experience replay, learning updates)
   - Evaluation framework (trace generation, fairness checks, metric computation)
   - Config loader and seed management
2. Integration tests:
   - Full pipeline run with smoke config produces expected outputs
   - HOODIE training converges (reward increases over episodes)
   - Paper figure reproduction matches within tolerance
3. Property-based tests for:
   - State vector dimensions
   - Action space legality
   - Reward function correctness
**Expected output**: Test suite covering >80% of critical code paths
**Validation checks**:
- `pytest -q` passes with >80% coverage
- Critical components have dedicated tests
- Smoke runs produce reproducible results
**Risk level**: LOW (safety net)
**Completion status**: □ pending

### Phase 7: Documentation & Closure
**Goal**: Lock in the verified state, update documentation, and create final verification package
**Files affected**: `docs/research-simulation/IMPLEMENTATION_PLAN.md`, `README.md`, `docs/assumptions/*`, `docs/PROJECT_CONTEXT.md`
**Exact work**:
1. Update this IMPLEMENTATION_PLAN.md with completion summaries for each phase
2. Add "Reproducing the Paper Results" section to README.md
3. Document the exact configuration used for paper reproduction
4. Archive the verified state as a reproducibility benchmark
5. Create final verification report comparing against paper numbers
**Expected output**: Self-documenting, reproducible repository state
**Validation checks**:
- Fresh clone can reproduce paper results using documented procedure
- All assumptions and gaps are documented
- No paper-backed behavior remains assumption-backed without documentation
**Risk level**: LOW (documentation)
**Completion status**: □ pending

## 12. Current Status Checklist
- [x] Phase 0: Baseline fidelity audit & config correction (CLOSED 2026-06-28: 62/62 validation gates pass, 4 drift areas SOURCE_CONFIRMED, approved)
- [ ] Phase 1: Paper-faithful HOODIE agent (PLAN WRITTEN: docs/plans/2026-06-28-phase1-...; awaiting approval)
- [ ] Phase 2: Multi-agent architecture & topology
- [ ] Phase 3: LSTM load forecaster integration
- [ ] Phase 4: Paper hyperparameter training configuration
- [ ] Phase 5: Figure reproduction & comparative analysis
- [ ] Phase 6: Validation & testing
- [ ] Phase 7: Documentation & closure

## 13. Next Recommended Phase
**Phase 0: Baseline fidelity audit & config correction**

## 13. Instructions for Future Agents
1. **Read this file first** – it is the single source of truth for implementation phases
2. **Implement only the next incomplete phase** (as marked in the checklist above)
3. **After completing a phase**, update the checklist in this file, add a brief summary of work, list files changed, and note any remaining issues
4. **Do not rely on prior chat context** – all required information is in this document
5. **Do not push or commit** unless explicitly instructed; keep changes local until final review
6. **Verify each phase** with the validation checks listed before considering it complete

---
*This plan replaces the outdated version and reflects the current state of the hoodie_sim_v2 repository. Future work must be based on this document.*
