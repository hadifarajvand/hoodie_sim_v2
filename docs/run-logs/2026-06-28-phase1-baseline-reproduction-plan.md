# Run Log: Phase 1 Paper-Faithful HOODIE Baseline Reproduction — Plan

**Date**: 2026-06-28
**Agent**: OpenCode (coder @ 70%, researcher @ 65%)
**Session**: Phase 1 planning following Phase 0 baseline fidelity closure

## What Was Done

### Evidence Gathering
Read the following source files to build the 30-row evidence table:
- `resources/papers/hoodie/recovered/paper-parameter-registry.json` — recovered Table 4 params, learning rates, discount factors, episode counts
- `src/environment/paper_traffic.py` — task sizes [2.0–5.0], arrival probability 0.5, processing density 0.297
- `src/environment/reward_timing.py` — drop penalty 40, paper reward function
- `src/agents/dueling_dqn_network.py` — 3×1024 Dueling DQN architecture
- `src/agents/multi_agent_pool.py` — N-agent pool architecture
- `src/agents/hoodie_agent.py` — HOODIE agent structure (Double DQN, replay buffer, target network)
- `src/environment/paper_lstm_forecast.py` — LSTM contract (W=10, 20 cells)
- `configs/runtime_model.yml` — service capacities (EA=0.5, Cloud=3.0), timeout_grace_slots=0
- `configs/experiments/exp_small_deterministic.json` — current smoke config (toy values: 20 eps, 50 slots, batch=4)
- `src/environment/environment.py` — environment structure
- `docs/research-simulation/IMPLEMENTATION_PLAN.md` — Phase 0–7 implementation plan

### Key Findings
1. **Most paper values are already in the codebase** — the gap is primarily configuration (active configs use toy values instead of paper Table 4 values), not source code.
2. **30 paper-critical surfaces identified and cross-referenced** — 13 already verified and wired, 17 need config/application changes.
3. **No major algorithmic gaps** — Double DQN, Dueling DQN, LSTM contract, reward function, all 6 baseline policies, topology from approved registry all exist and are verified.
4. **Data rates (30/10 Mbps) are recovered** but not yet wired into active offload latency calculation — needs implementation.
5. **Training config uses toy values** — 20 episodes (vs 5000), 50 slots (vs 110), batch=4 (vs 64), lr=0.001 (vs 7e-7, ~1414× too large).
6. **Phase 1 is primarily a config authoring task** — create paper-faithful experiment configs and a reproduction validation script.

### Files Read (for evidence)
- `resources/papers/hoodie/recovered/paper-parameter-registry.json` (334 lines)
- `src/environment/paper_traffic.py` (111 lines)
- `src/environment/reward_timing.py` (124 lines)
- `src/agents/dueling_dqn_network.py` (lines 1-60)
- `src/agents/multi_agent_pool.py` (lines 1-80)
- `src/agents/hoodie_agent.py` (lines 1-80)
- `src/environment/paper_lstm_forecast.py` (31 lines)
- `configs/runtime_model.yml` (35 lines)
- `configs/experiments/exp_small_deterministic.json` (75 lines)
- `src/environment/environment.py` (lines 1-60)
- `docs/research-simulation/IMPLEMENTATION_PLAN.md` (411 lines)

### Files Written
- `docs/plans/2026-06-28-phase1-paper-faithful-hoodie-baseline-reproduction.md` — 30-row evidence table, gap classification, implementation approach, validation gates

## Classification
**FULL_SOURCE_CONFIRMED**: All paper values already in code. Phase 1 is config + reproduction validation scripting work.

## Awaiting
Human approval before Phase 1 implementation begins.