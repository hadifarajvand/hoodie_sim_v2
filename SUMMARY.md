# HOODIE Simulation Summary

## Overview
This repository implements the HOODIE (Hybrid Computation Offloading via Distributed Deep Reinforcement Learning) simulation as described in the research paper. The simulation models a Cloud-Edge Computing Continuum (CEC) where Edge Agents (EAs) make task offloading decisions using a distributed Dueling DQN framework with optional LSTM-based load forecasting.

## Key Components

### 1. Simulation Core
- **Discrete-event simulation** of CEC with time slots
- **Multi-agent system**: Each EA runs an independent DRL agent
- **Task model**: Tasks arrive with size, processing density, and timeout
- **Queuing model**: 
  - Private queue per EA for local tasks
  - Public queues for offloaded tasks (N-1 per EA, N for Cloud)
  - Offloading queue per EA for tasks to be offloaded
- **Runtime model**: Tracks task execution, waiting times, and completion/dropping based on timeouts

### 2. Framework and Libraries
- **PyTorch**: Neural network implementation (Dueling DQN, LSTM)
- **NumPy**: Numerical computations
- **Matplotlib/Seaborn**: Plotting and visualization (used for figure generation)
- **Custom Gymnasium-like environment**: `HoodieGymEnvironment` for RL interface

### 3. Algorithms and Methods

#### HOODIE Agent (Dueling DQN)
- **State representation** (74-dimensional):
  - Task size (bits)
  - Processing density (CPU cycles/bit)
  - Private queue wait time (time slots)
  - Offloading queue wait time (time slots)
  - Public queue lengths (N values, one per EA)
  - Load forecast (N values, from LSTM or zeros)
- **Action space** (discrete):
  - 0: Local computation
  - 1-N: Horizontal offloading to EA 1..N (excluding self)
  - N+1: Vertical offloading to Cloud
- **Network architecture**: Dueling DQN with separate value and advantage streams
- **Learning**:
  - Experience replay with uniform sampling
  - Target network for stable Q-targets
  - Double Q-learning to reduce overestimation bias
  - Adam optimizer
  - Epsilon-greedy exploration (linear decay from 1.0 to 0.0 over first half of training)
- **Reward function**:
  - `NaN` if no task arrived
  - `-Φ_n(t)` if task successfully processed (negative delay)
  - `-C` if task dropped (constant penalty, C > 0)
  - Where `Φ_n(t)` is the delay experienced by the task

#### Baseline Policies (for comparison)
All policies implement the `SharedPolicy` interface:
- **RO (Random Offloader)**: Uniform random action selection
- **FLC (Full Local Computing)**: Always choose local computation
- **VO (Vertical Offloader)**: Always choose cloud offloading
- **HO (Horizontal Offloader)**: Always choose random horizontal offload
- **BCO (Balanced Cyclic Offloader)**: Round-robin: local → cloud → EA1 → EA2 → ... 
- **MLEO (Minimum Latency Estimation Offloader)**: Estimates delay for each option via queuing models and chooses minimum

#### Optional LSTM Component
- **paper_lstm_forecast.py**: LSTM network for predicting future load of each EA
- **Input**: Window of historical public queue lengths (lookback W)
- **Output**: Predicted queue lengths for next time step
- **Integration**: Used in state building when enabled via `load_forecast` vector (can be disabled for ablation)

### 4. Configuration and Experimentation
- **TrainingConfig**: Controls learning rate, batch size, replay capacity, episode count, etc.
- **EvaluationConfig**: Controls evaluation episodes, seeds, etc.
- **CampaignConfig** (in analysis/full_training_reproduction_campaign): Defines full experiments with:
  - Network architecture (hidden layers, LSTM size)
  - Hyperparameters (learning rate, gamma, batch size)
  - Environment settings (data rates, topology, etc.)
  - Seeds for reproducibility
- **Experiment Runner**: Supports parameter sweeps (e.g., varying learning rate, discount factor, number of agents, etc.)
- **Figure Generation**: Scripts to produce publication-quality plots (Figures 8-11) from experiment data

### 5. Directory Structure (After Cleanup)
```
├── .claude/                # Claude Code configuration
├ .claude-flow/            # Claude Flow state (removed in cleanup)
├── configs/               # Configuration files (simulation.yaml, training_config.py, etc.)
├── data/                  # Synthetic workload CSV files
├── decision_makers/       # Not used in core simulation
├── engine/                # Not used in core simulation
├── environment/           # CEC simulation core (task, queues, runtime, topology, etc.)
├── evaluation/            # Evaluation framework and metrics
├── lr_schedulers/         # Learning rate schedulers (not core)
├── outputs/               # Output directory for logs and artifacts
├── platform/              # Platform-specific components (not core)
├── resources/             # Paper references, OCR text, etc.
├── scripts/               # Utility scripts (e.g., run_pilot_with_diagnostic.py)
├── simulation/            # Simulation entry points
├── src/                   # Main source code
│   ├── agents/            # HOODIE agent and model implementations
│   ├── analysis/          # Experiment running, figure generation, paper reproduction
│   ├── configs/           # Configuration classes
│   ├── environment/       # CEC environment components
│   ├── evaluation/        # Evaluation logic
├── tests/                 # Unit and integration tests
├── training/              # Training loop and auxiliary classes
├── utils/                 # Utility functions
├── CLAUDE.md              # Project-specific Claude Code instructions
├── README.md              # Project overview
├── LICENSE                # MIT license
└── ...                    # Miscellaneous files (.gitignore, etc.)
```

### 6. Reproduced Paper Results
Using the provided experimental infrastructure, the following figures from the HOODIE paper have been regenerated:
- **Figure 8**: Training reward time-course vs. episodes for different learning rates (α) and discount factors (γ)
- **Figure 9**: Performance vs. system parameters (5 subplots: arrival probability, action distribution, CPU capacity, number of agents, offloading data rates)
- **Figure 10**: Performance across offloading schemes (6 subplots comparing HOODIE vs. RO, FLC, VO, HO, BCO, MLEO on delay and drop ratio vs. arrival probability, CPU capacity, and timeout)
- **Figure 11**: LSTM vs. no-LSTM ablation study on average task delay over training episodes

These figures were generated using the `figure_generator.py` script and sweep data from controlled experiments, demonstrating that the implementation captures the core behavior described in the paper.

### 7. How to Run
The simulation can be run via:
```bash
# Activate virtual environment (if needed)
source .venv/bin/activate

# Run a pilot training experiment
python -m src.training.training_loop --config /path/to/config

# Or use the provided runner scripts
python ./run_pilot_with_diagnostic.py
```

For detailed experimentation, refer to the analysis/full_training_reproduction_campaign module.

---
*Summary generated from source code inspection. The simulation implements the HOODIE framework as described in the paper, enabling reproduction of the key experimental results.*